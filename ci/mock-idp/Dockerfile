# Mock OIDC IdP for local dev and e2e ONLY. TEST ONLY, NEVER PRODUCTION.
# Build once before `just up` (which runs compose with --no-build):
#   docker compose --profile infra build mock-idp
FROM python:3.14-slim-trixie

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8443

# main.py bootstraps TLS (mounted mkcert certs, else ephemeral self-signed)
# and runs uvicorn on 8443 to match the issuer https://localhost:8443/...
CMD ["python", "main.py"]
