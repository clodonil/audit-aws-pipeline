# Desenvolvimento 

Na pasta `code-metrics-dev`, contém tudo que é necessário para você começar a desenvolver novas funcionalidades.

# Infra 

Para instanciar localmente os serviços de `Grafana`, `Prometheus`, `Dynamodb` e `Code-Metrics-API`, basicamente execute o seguinte comando:

> É necessário ter o docker instalado localmente, juntamente como docker-compose.

```
docker-compose up -d
```

# Populando o DynamoDB

Para trabalhar na API, é necessário ter valores gravados no `Dynamodb-local`. Em produção o `Dynamodb` será populado pelo `lambda` da AWS. Entretanto nesse caso local, podemos quere apenas popular o dynamodb para seguirmos o desenvolvimento.

Para esse caso utilize o script `save_pipeline_in_dynamodb.py`.

```
python3 save_pipeline_in_dynamodb.py
```


```
docker run -p 9090:9090 -e API_URL='ec2co-ecsel-1jcx7bgvhei2q-944124367.us-east-1.elb.amazonaws.com:8080rometheus:latest
```

# Docker Image

- [AWS-lambda](https://github.com/lambci/docker-lambda)
- [Prometheus](https://hub.docker.com/r/prom/prometheus/)
- [Grafana](https://hub.docker.com/r/grafana/grafana)
- [Dynamodb](https://hub.docker.com/r/amazon/dynamodb-local)