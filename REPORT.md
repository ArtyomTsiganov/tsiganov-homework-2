Вот основные команды для сборки образов и для очистки после себя.

Эксперементы записаны в одноимённых файлах, а логи от их команды в одноименных `evidence/`

``` bash
docker build -t localhost:5001/tsiganov-homework-2:v1.4 .
docker push localhost:5001/tsiganov-homework-2:v1.4  
docker build -t localhost:5001/tsiganov-homework-2:v1.5 .
docker push localhost:5001/tsiganov-homework-2:v1.5  
docker build -t localhost:5001/client:v1 ./local/client
docker push localhost:5001/client:v1

kubectl create -f namespace.yaml
kubectl config use-context kind-hosting-lab
kubectl config set-context kind-hosting-lab --namespace=homework-2

kubectl --context kind-hosting-lab apply -f namespace.yaml
kubectl --context kind-hosting-lab apply -f service-probes.yaml
kubectl --context kind-hosting-lab apply -f configmap-probes.yaml
kubectl --context kind-hosting-lab apply -f secret-probes.yaml
kubectl --context kind-hosting-lab apply -f deployment-probes.yaml

kubectl --context kind-hosting-lab apply -f configmap-client.yaml
kubectl --context kind-hosting-lab apply -f deployment-client.yaml

kubectl --context kind-hosting-lab -n homework-2 rollout status deployment/homework-2 --timeout=180s
kubectl --context kind-hosting-lab -n homework-2 rollout status deployment/homework-2-client --timeout=180s
kubectl --context kind-hosting-lab -n homework-2 logs -f deployment/homework-2-client
```

Очистить после себя:

``` bash
kubectl delete namespace homework-2
```