from typing import Any, Dict

from fastapi.security import HTTPAuthorizationCredentials


class AccessTokenCredentials(HTTPAuthorizationCredentials):
    token: Dict[str, Any]
