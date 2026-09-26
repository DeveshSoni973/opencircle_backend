import uvicorn
from fastapi import FastAPI
from src.config import config

app = FastAPI()


@app.get("/")
def read_root():
  return {"Hello": "World"}


def main():
  
  uvicorn.run(
      "src.main:app",
      host=config.server.host,
      port=config.server.port,
      reload=config.server.reload,
  )


if __name__ == "__main__":
  main()