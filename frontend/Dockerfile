# build env
ARG VERSION=18-alpine3.18

FROM node:$VERSION as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD cp -r build/. /static
