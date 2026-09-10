FROM node:24.21.0-alpine AS build-stage

WORKDIR /app
RUN corepack enable

COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/root/.pnpm-store \
  pnpm install --frozen-lockfile

COPY . .
# Vite vars bake into the static bundle at build time; runtime env cannot
# change them (compose's VITE_API_ENDPOINT is inert here). Defaults match the
# ci compose stack (frontend :8080, api :8000, mock IdP :8443); pass explicit
# --build-args for other deployments. redirect/post_logout URIs fall back to
# the runtime window origin in auth.ts, so they are not baked.
ARG VITE_API_ENDPOINT=http://localhost:8000/api/v1
ARG VITE_OIDC_AUTHORITY=https://localhost:8443/realms/fmv
ARG VITE_OIDC_CLIENT_ID=fmv-web
ENV VITE_API_ENDPOINT=${VITE_API_ENDPOINT} \
    VITE_OIDC_AUTHORITY=${VITE_OIDC_AUTHORITY} \
    VITE_OIDC_CLIENT_ID=${VITE_OIDC_CLIENT_ID}
RUN pnpm build

FROM nginx:stable-alpine AS production-stage
RUN  touch /tmp/nginx.pid && \
  chown -R nginx:nginx /var/cache/nginx /tmp/nginx.pid
COPY nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 8080
USER nginx

# Start Nginx directly with custom config
ENTRYPOINT ["nginx", "-c", "/etc/nginx/nginx.conf"]
CMD ["-g", "daemon off;"]
