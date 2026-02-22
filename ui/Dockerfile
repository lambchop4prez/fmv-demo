FROM node:24.13.1-alpine AS build-stage

WORKDIR /app
RUN corepack enable

COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/root/.pnpm-store \
  pnpm install --frozen-lockfile

COPY . .
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
