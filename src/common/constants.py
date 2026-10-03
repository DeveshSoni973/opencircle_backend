class Status:
  BAD_REQUEST = 400
  NOT_FOUND = 404
  CONFLICT = 409
  UPSTREAM_FAILED = 502


class Code:
  PROVIDER_NOT_FOUND = "provider_not_found"
  PROVIDER_IN_USE = "provider_in_use"
  INVALID_BASE_URL = "invalid_base_url"