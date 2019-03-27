FROM python:3.6.5-alpine3.7
  

RUN apk add --update --no-cache --virtual .fetch-deps \
    gcc libc-dev bash g++ make 

RUN wget https://github.com/edenhill/librdkafka/archive/v0.11.5.tar.gz && \
    tar xf v0.11.5.tar.gz && \
    rm v0.11.5.tar.gz && \
    cd librdkafka-0.11.5 && \
    ./configure && \
    make && \
    make install 

ADD requirements.txt /
ADD test-producer.py /

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD [ "python", "test-producer.py" ]
