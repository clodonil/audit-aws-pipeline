# Code-Metrics - Metrics de Pipeline full AWS

A proposta do Code-Metrics é obter métricas das utilização das ferramentas de pipelines da AWS, tais como `code-pipeline`, `code-build` e `code-deploy`. Além das métricas, também é disponibilizado a estrutura semática da pipeline com os `stages` que foram executados, muito oportuno para áreas como governança e auditória em gestão de mudança.

A solução do Code-Metrics envolve os seguintes recursos:

- **Lambda**: O Lambda recebe os logs da pipeline através de uma regra do cloud-watch, trata o log e armazena no `dynamodb`.
- **Api**: Disponibiliza os dados armazenados no `dynamodb`.

O desenho da solução basicamente é essa:

