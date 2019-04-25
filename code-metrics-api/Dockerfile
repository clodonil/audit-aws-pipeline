FROM python:3
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"
                  
EXPOSE 8080                  
COPY . /app
ENV enviroment local
WORKDIR /app
RUN pip install -r requirements
CMD ["/bin/bash", "-c", "python run.py"]
