FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"


ENV AWS_ACCESS_ID='ACCESS_ID'
ENV AWS_SECRET_KEY='ACCESS_KEY'
ENV AWS_REGION='us-east-1'
ENV DYNAMODB_TABLE='code-metrics'
#ENV DYNAMODB="http://dynamodb:8000"
ENV DYNAMODB=''
ENV enviroment local


EXPOSE 8080                  
COPY . /app
WORKDIR /app
RUN pip install -r requirements
CMD ["./start.sh"]
