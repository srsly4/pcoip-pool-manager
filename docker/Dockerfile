FROM python:3

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    inotify-tools \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /server

WORKDIR /server

ADD server/requirements.txt /server/
RUN pip install -r requirements.txt

COPY server /server/
COPY docker /server/docker

RUN chmod a+rx ./docker/entrypoint.sh

CMD python3 manage.py runserver 0.0.0.0:8000
ENTRYPOINT ["sh", "./docker/entrypoint.sh"]

EXPOSE 8000
