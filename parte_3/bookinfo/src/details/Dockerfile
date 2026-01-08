FROM ruby:2.7.1-slim

WORKDIR /opt/microservices/

ENV ENABLE_EXTERNAL_BOOK_SERVICE=true

COPY details.rb .

EXPOSE 7070

CMD ["ruby", "details.rb", "7070"]
