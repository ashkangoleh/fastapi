FROM python:3.9
WORKDIR /home/core_api
COPY . /home/core_api/
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install -U pip \
    && pip install psycopg2 \ 
    && pip install -r /home/core_api/requirements.txt

COPY . /home/core_api/
EXPOSE 8000
CMD python main.py