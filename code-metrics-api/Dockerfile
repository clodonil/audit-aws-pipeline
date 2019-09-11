FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"


ENV enviroment development


EXPOSE 8080                  
COPY . /src
WORKDIR /src
RUN pip install -r requirements
CMD ["./start.sh"]
