FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./app /app
ENV STATIC_URL /static
ENV STATIC_PATH /app/static
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt