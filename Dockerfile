FROM python:3.12-slim-bullseye

ENV TZ=Asia/Almaty
ENV PYTHONUNBUFFERED=1
ENV TAG=0.1
ENV APP=reporterapi

RUN apt-get update && apt-get install -y wget unzip libaio1 python3-svn

WORKDIR /opt/oracle
RUN wget http://192.168.100.23:8081/repository/dist/oracle-client/instantclient-basiclite-linuxx64.zip && \
    unzip instantclient-basiclite-linuxx64.zip && rm -f instantclient-basiclite-linuxx64.zip && \
    cd /opt/oracle/instantclient* && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig

WORKDIR /$APP
COPY . .
RUN pip install --upgrade pip -r req.txt

EXPOSE 8110

# ENTRYPOINT gunicorn --name $APP -b 0.0.0.0:8110 --max-requests 100 -k uvicorn.workers.UvicornWorker 'app.main:app'
# ENTRYPOINT uvicorn app.main:app --host 0.0.0.0 --port 8110
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8110"]
