# Documentação sobre o Code-Metrics-API

# Validando o retorno


## API

Retornar a informação de todas as pipelines:

```
curl -X GET localhost:8080/api/v1/pipelines
{
    "status": "success",
    "message": [
        {
            "id": "arn:aws:codepipeline:us-east-1:3422334324:Homolog",
            "status": "FAILED",
            "NumExecSuccess": 0,
            "NumExecFail": 1,
            "AvgTime": ""
        }
    ]
}
```

Retorna a informação detalhada de uma pipeline:

```
curl -X GET localhost:8080/api/v1/pipeline -H "Content-Type: application/json"  -d '{"id":"arn:aws:codepipeline:us-east-1:3422334324:Homolog"}'
{
    "status": "success",
    "message": {
        "detail": {
            "running": [
                {
                    "5071630b-3d1b-4f84-9cc8-1582f64f93f3": {
                        "log": {},
                        "stages": [
                            {
                                "Source": {
                                    "output": [],
                                    "start": "2019-04-17T21:20:00Z",
                                    "execute": [],
                                    "provider": "CodeCommit",
                                    "status": "SUCCEEDED"
                                }
                            },
                            {
                                "Build": {
                                    "output": [],
                                    "start": "2019-04-17T21:20:01Z",
                                    "finished": "2019-04-17T21:22:07Z",
                                    "execute": [],
                                    "provider": "CodeBuild",
                                    "status": "SUCCEEDED"
                                }
                            }
                        ],
                        "start": "2019-04-17T21:19:54Z",
                        "finished": "2019-04-17T21:22:10Z",
                        "source": "aws.codepipeline",
                        "account": "32584782372862",
                        "status": "FAILED"
                    }
                }
            ],
            "pipeline_status": "FAILED"
        },
        "id": "arn:aws:codepipeline:us-east-1:3422334324:Homolog"
    }
}
```


## Metrics

curl http://localhost:8080/metrics/