FROM python:3.8

ENV PYTHONUNBUFFERED 1
RUN apt-get update \
    && apt-get install -y vim \
    && apt-get install -y --no-install-recommends
RUN mkdir /code
WORKDIR /code 
ADD . /code/ 
RUN pip install --upgrade pip \
    && pip install -r requirements.txt 

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]