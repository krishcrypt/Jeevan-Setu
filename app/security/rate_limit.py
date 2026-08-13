from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter for public API endpoints.
# Current limit: 10 requests per minute per client IP.
limiter = Limiter(key_func=get_remote_address)