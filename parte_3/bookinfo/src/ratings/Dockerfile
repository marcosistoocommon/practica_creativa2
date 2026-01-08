FROM node:24-slim

WORKDIR /opt/microservices/

ENV APP_VERSION=v1

COPY package.json .
COPY ratings.js .

RUN npm install

EXPOSE 9080

CMD ["node", "ratings.js", "9080"]
