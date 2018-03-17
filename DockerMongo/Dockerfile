FROM python:3
MAINTAINER Qianyi Feng "noemail@website.domain"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
#ENTRYPOINT ["python"]
#CMD ["app.py"]

#FROM python:2
#ADD . /app
#WORKDIR /app
#RUN pip install -r requirements.txt
