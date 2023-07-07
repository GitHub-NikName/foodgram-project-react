# build env
ARG VERSION=13.12.0-alpine

FROM node:$VERSION as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD cp -r build/. /static
