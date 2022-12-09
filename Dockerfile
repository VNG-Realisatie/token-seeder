FROM python:3.9-alpine

# set working directory
RUN mkdir -p /app
WORKDIR /app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /app/requirements.txt

# install requirements
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

# add app
ADD . /app

CMD python3 main.py