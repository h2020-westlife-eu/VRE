FROM python:2.7

COPY build.sh /build.sh
RUN chmod +x /build.sh && sleep 5 && /build.sh

COPY dist /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt.lock

EXPOSE 10000

CMD ["uwsgi", "--ini", "deploy/uwsgi-docker.ini"]
