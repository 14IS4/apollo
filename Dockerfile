FROM python:3.8-slim-buster

RUN apt-get update -y && apt-get -y install git

ARG version
RUN pip install dbt==$version

RUN mkdir /root/.dbt
ADD apollo /root/apollo
WORKDIR /root/apollo
RUN pip install -e .

CMD ["apollo"]