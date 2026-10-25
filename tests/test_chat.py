import time

from sqlmodel import Session, select

from src.db.db_connection import engine
from src.db.messages import Message
from src.modules.chat.manager import chat_manager
from tests.conftest import collect_until_run_done


def send(ws, group_id, content):
    ws.send_json({"type": "send", "group_id": group_id, "content": content})


def test_messages_stream_one_by_one_as_agents_finish(client, make_group):
    group_id, ids = make_group("fast", "slow")
    with client.websocket_connect("/realtime/ws") as ws:
        send(ws, group_id, "hello")
        events = collect_until_run_done(ws, group_id)

    types = [e["type"] for e in events]
    assert types[0] == "user_message"
    replies = [e["message"] for e in events if e["type"] == "agent_message"]
    # fast agent's reply arrives on its own, before the slow one: real time, not batched at the end
    assert [m["agent_id"] for m in replies] == [ids["fast"], ids["slow"]]
    assert types[-1] == "run_done"


def test_every_turn_is_saved_but_silent_and_errors_are_not_streamed(client, make_group):
    group_id, ids = make_group("fast", "quiet", "broken")
    with client.websocket_connect("/realtime/ws") as ws:
        send(ws, group_id, "hi")
        events = collect_until_run_done(ws, group_id)

    streamed = [e["message"]["agent_id"] for e in events if e["type"] == "agent_message"]
    assert ids["fast"] in streamed and ids["quiet"] not in streamed and ids["broken"] not in streamed

    with Session(engine) as s:
        rows = s.exec(select(Message).where(Message.group_id == group_id)).all()
    by_agent = {r.agent_id: r for r in rows}
    assert by_agent[ids["quiet"]].content == "[SILENT]" and by_agent[ids["quiet"]].is_silent
    assert by_agent[ids["broken"]].content.startswith("[ERROR]") and by_agent[ids["broken"]].is_silent
    assert client.get(f"/chat/{group_id}").json()[-1]["content"].startswith("fast:")  # history hides them


def test_every_connected_client_gets_the_events(client, make_group):
    group_id, _ = make_group("fast")
    with client.websocket_connect("/realtime/ws") as tab1, client.websocket_connect("/realtime/ws") as tab2:
        send(tab1, group_id, "hi")
        events1 = collect_until_run_done(tab1, group_id)
        events2 = collect_until_run_done(tab2, group_id)
    assert [e["type"] for e in events1] == [e["type"] for e in events2]


def mid_run_contents(ws, group_id):
    send(ws, group_id, "plan Japan")
    time.sleep(0.1)  # doner has said [DONE], slow is still writing
    send(ws, group_id, "make it Korea")
    events = collect_until_run_done(ws, group_id)
    assert [e["type"] for e in events].count("run_done") == 1  # one run, not two
    return [e["message"]["content"] for e in events if e["type"] in ("user_message", "agent_message")]


def test_message_sent_mid_run_joins_the_same_run(client, make_group):
    group_id, _ = make_group("slow", "doner", max_rounds=2)
    with client.websocket_connect("/realtime/ws") as ws:
        contents = mid_run_contents(ws, group_id)
    assert "slow: Japan" in contents       # mid-reply agent finished and posted what it had
    assert "slow: Korea" in contents    # then answered the follow-up (it had rounds left)
    assert contents.count("all good") == 2      # [DONE] agent woke up for the follow-up; tag stripped


def test_mid_reply_agent_with_no_rounds_left_just_finishes(client, make_group):
    group_id, _ = make_group("slow", "doner", max_rounds=1)
    with client.websocket_connect("/realtime/ws") as ws:
        contents = mid_run_contents(ws, group_id)
    assert "slow: Japan" in contents and "slow: Korea" not in contents
    assert contents.count("all good") == 2      # the idle agent is still invoked for the follow-up


def test_chat_stays_alive_between_messages_and_rebuilds_after_edits(client, make_group):
    group_id, ids = make_group("fast")
    with client.websocket_connect("/realtime/ws") as ws:
        send(ws, group_id, "one")
        collect_until_run_done(ws, group_id)
        chat = chat_manager._chats[group_id]

        send(ws, group_id, "two")
        collect_until_run_done(ws, group_id)
        assert chat_manager._chats[group_id] is chat  # same GroupChat, the module keeps the history

        client.patch(f"/agents/{ids['fast']}", json={"temperature": 0.1})
        assert group_id not in chat_manager._chats  # edit drops it

        send(ws, group_id, "three")
        events = collect_until_run_done(ws, group_id)
        assert chat_manager._chats[group_id] is not chat  # rebuilt from the DB
        assert any(e["type"] == "agent_message" for e in events)


def test_post_send_streams_over_the_socket(client, make_group):
    group_id, _ = make_group("fast")
    with client.websocket_connect("/realtime/ws") as ws:
        r = client.post(f"/chat/{group_id}", json={"content": "via post"})
        assert r.status_code == 202 and r.json()["content"] == "via post"
        events = collect_until_run_done(ws, group_id)
    assert any(e["type"] == "agent_message" for e in events)


def test_socket_errors(client):
    with client.websocket_connect("/realtime/ws") as ws:
        ws.send_text("not json")
        assert ws.receive_json()["code"] == "invalid_message"
        send(ws, "no-such-group", "hi")
        event = ws.receive_json()
        assert event["type"] == "error" and event["code"] == "group_not_found"
    assert client.post("/chat/no-such-group", json={"content": "x"}).status_code == 404
