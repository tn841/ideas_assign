FROM python:3.8
MAINTAINER sumin kim "tn841@naver.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python3-dev default-libmysqlclient-dev

COPY ./requirements.txt /ideas_assign/requirements.txt

WORKDIR /ideas_assign

RUN pip install -r requirements.txt

COPY . /ideas_assign

ENTRYPOINT [ "python" ]

CMD [ "run.py" ]