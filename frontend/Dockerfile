# ========================
# BUILD (React / Vite)
# ========================
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# ========================
# PRODUÇÃO (NGINX ESTÁTICO)
# ========================
FROM nginx:alpine

# Remove config default do nginx (boa prática)
RUN rm /etc/nginx/conf.d/default.conf

# Copia o build do React
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
