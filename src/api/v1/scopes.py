"""Explicit scope constants for protected endpoints (decision D3).

Endpoints declare required scopes in code with these constants. The IdP
delivers matching role/scope strings in the token claim named by each
provider's ``role_claims`` setting (see ``config.oidc``). At login the
matched provider's role claims are extracted and stored in the session
(``request.session["scopes"]``); ``api.v1.dependencies.require_scope``
enforces them on protected routes.

Naming convention: ``<resource>:<action>``.

- ``robot:read``  read robot profiles (all authenticated users)
- ``robot:write`` create or modify robots
- ``robot:run``   trigger a robot task (side effects via workers)
"""

ROBOT_READ = "robot:read"
ROBOT_WRITE = "robot:write"
ROBOT_RUN = "robot:run"

__all__ = ["ROBOT_READ", "ROBOT_WRITE", "ROBOT_RUN"]
