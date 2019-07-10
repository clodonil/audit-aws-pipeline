# Audit de Pipeline AWS


API:

```
curl -X GET -H 'Content-type: application/json'   http://localhost:8080/api/v1/pipelines

GET /api/v1/pipelines        # Retorna o id, status atual e número de execução da pipeline

    Saída:
       { 
           id: xxxx, status: Green, NumExec: 10 
       }

curl -X GET -H 'Content-type: application/json' -d '{"id":"arn:aws:codepipeline:us-east-1:325847872862:Clair-CI"}'  http://localhost:8080/api/v1/pipeline
GET /api/v1/pipeline/id      # Retorna as informação completa de um pipeline

    Saída:
{
  "id": "xxxxx",  
  "detail": {
    "running": [
      {
        "5071630b": {
          "account": "xxxxxx",
          "finished": "2019-04-17T21:22:10Z",
          "log": { },
          "source": "aws.codepipeline",
          "start": "2019-04-17T21:19:54Z",
          "status": "FAILED",
          "stages": [
            {
              "Source": {
                "execute": [],
                "output": [],
                "provider": "CodeCommit",
                "start": "2019-04-17T21:20:00Z",
                "finished": "2019-04-17T21:22:07Z",
                "status": "SUCCEEDED"
              }
            },
            {
              "Build": {
                "eventid": "4ea498df-ea29-3961-3fcc-bf72b51c25ad",
                "execute": [],
                "output": [],
                "provider": "CodeBuild",
                "start": "2019-04-17T21:20:01Z",
                "status": "SUCCEEDED"
              }
            }
          ]
        }
      }
    ]
  }
}

GET /api/v1/metrics
GET /api/v1/status
```