## Подготовка перед экспериментом


Добавляем в образ "Version: v1.4" и перезапускаем

```bash
kubectl -n homework-2 rollout status deployment/homework-2 --timeout=180s
kubectl -n homework-2 get pods -l app=homework-2 -o wide
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
```

Текущее состояние:

``` bash
deployment "homework-2" successfully rolled out
NAME                          READY   STATUS    RESTARTS   AGE   IP            NODE                        NOMINATED NODE   READINESS GATES
homework-2-764db6b8b5-btm27   1/1     Running   0          62s   10.244.0.37   hosting-lab-control-plane   <none>           <none>
homework-2-764db6b8b5-fs8fc   1/1     Running   0          49s   10.244.0.38   hosting-lab-control-plane   <none>           <none>
homework-2-764db6b8b5-lwjfg   1/1     Running   0          74s   10.244.0.36   hosting-lab-control-plane   <none>           <none>
NAME                          UID                                    READY   RESTARTS
homework-2-764db6b8b5-btm27   6b7f13e3-5350-43f0-8bbe-39475bea28c2   true    0
homework-2-764db6b8b5-fs8fc   15064502-982a-4745-9d06-b05a4e611c7c   true    0
homework-2-764db6b8b5-lwjfg   97511e58-66ae-46e0-8947-ce23dc71093a   true    0
```

В логах видно что добавили версию.
``` bash
2026-11-02T10:29:17.395399700Z 2026-11-02T10:29:17.3953286+00:00 GET http://homework-2.homework-2.svc.cluster.local/ -> 200 pod=Pod Name: homework-2-764db6b8b5-fs8fc Version: v1.4
```


Далее применяем стратегию и дожидаемся результата:

``` yaml
replicas: 4
  minReadySeconds: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

``` bash

kubectl --context kind-hosting-lab apply -f deployment-probes.yaml
deployment.apps/homework-2 configured
                                                                                                             
◄ 0s ◎ kubectl -n homework-2 rollout status deployment/homework-2 --timeout=180s
       kubectl -n homework-2 get pods -l app=homework-2 -o wide
       kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
Waiting for deployment "homework-2" rollout to finish: 3 of 4 updated replicas are available...
deployment "homework-2" successfully rolled out
NAME                          READY   STATUS    RESTARTS   AGE     IP            NODE                        NOMINATED NODE   READINESS GATES
homework-2-764db6b8b5-btm27   1/1     Running   0          7m45s   10.244.0.37   hosting-lab-control-plane   <none>           <none>
homework-2-764db6b8b5-fs8fc   1/1     Running   0          7m32s   10.244.0.38   hosting-lab-control-plane   <none>           <none>
homework-2-764db6b8b5-lwjfg   1/1     Running   0          7m57s   10.244.0.36   hosting-lab-control-plane   <none>           <none>
homework-2-764db6b8b5-zxtns   1/1     Running   0          17s     10.244.0.39   hosting-lab-control-plane   <none>           <none>
NAME                          UID                                    READY   RESTARTS
homework-2-764db6b8b5-btm27   6b7f13e3-5350-43f0-8bbe-39475bea28c2   true    0
homework-2-764db6b8b5-fs8fc   15064502-982a-4745-9d06-b05a4e611c7c   true    0
homework-2-764db6b8b5-lwjfg   97511e58-66ae-46e0-8947-ce23dc71093a   true    0
homework-2-764db6b8b5-zxtns   c5a02199-23db-4449-bbf6-4fea540ef612   true    0
                                                                                                             
◄ 4s ◎ kubectl -n homework-2 get deployment homework-2 -o wide
       kubectl -n homework-2 get rs -l app=homework-2
       kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,IMAGE:.spec.containers[0].image,RS:.metadata.ownerReferences[0].name,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
NAME         READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                                    SELECTOR
homework-2   4/4     4            4           87m   homework-2   localhost:5001/tsiganov-homework-2:v1.4   app=homework-2
NAME                    DESIRED   CURRENT   READY   AGE
homework-2-764db6b8b5   4         4         4       9m2s
homework-2-845fcc4588   0         0         0       87m
NAME                          UID                                    IMAGE                                     RS                      READY   RESTARTS
homework-2-764db6b8b5-btm27   6b7f13e3-5350-43f0-8bbe-39475bea28c2   localhost:5001/tsiganov-homework-2:v1.4   homework-2-764db6b8b5   true    0
homework-2-764db6b8b5-fs8fc   15064502-982a-4745-9d06-b05a4e611c7c   localhost:5001/tsiganov-homework-2:v1.4   homework-2-764db6b8b5   true    0
homework-2-764db6b8b5-lwjfg   97511e58-66ae-46e0-8947-ce23dc71093a   localhost:5001/tsiganov-homework-2:v1.4   homework-2-764db6b8b5   true    0
homework-2-764db6b8b5-zxtns   c5a02199-23db-4449-bbf6-4fea540ef612   localhost:5001/tsiganov-homework-2:v1.4   homework-2-764db6b8b5   true    0

```

Пересобираю приложение с новым тегом v1.5

``` bash
docker build -t localhost:5001/tsiganov-homework-2:v1.5 .
docker push localhost:5001/tsiganov-homework-2:v1.5  
```

Далее в отдельных консолях:
``` bash
kubectl -n homework-2 get pods -l app=homework-2 -w | tee evidence/console_pods_experiment_3.md
```
``` bash
kubectl -n homework-2 get rs -l app=homework-2 -w | tee evidence/console_rs_experiment_3.md
```
``` bash
kubectl -n homework-2 get deployment -l app=homework-2 -w | tee evidence/console_deployment_experiment_3.md
```


Обновил версию в deployment-probes.yaml:

``` bash
date -u
kubectl apply -f deployment-probes.yaml
kubectl -n homework-2 rollout status deployment/homework-2 --timeout=300s
```

Вывод:

``` bash
Пн 02 ноя 2026 10:46:13 UTC
deployment.apps/homework-2 configured
Waiting for deployment "homework-2" rollout to finish: 1 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 1 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 1 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 1 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 2 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 2 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 2 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 2 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 3 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 3 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 3 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 3 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 3 out of 4 new replicas have been updated...
Waiting for deployment "homework-2" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "homework-2" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "homework-2" rollout to finish: 1 old replicas are pending termination...
Waiting for deployment "homework-2" rollout to finish: 1 old replicas are pending termination...
deployment "homework-2" successfully rolled out
```

Так и происходит


Повторяю снимки:

``` bash
kubectl -n homework-2 get deployment homework-2 -o wide
kubectl -n homework-2 get rs -l app=homework-2
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,IMAGE:.spec.containers[0].image,RS:.metadata.ownerReferences[0].name,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'

NAME         READY   UP-TO-DATE   AVAILABLE   AGE    CONTAINERS   IMAGES                                    SELECTOR
homework-2   4/4     4            4           105m   homework-2   localhost:5001/tsiganov-homework-2:v1.5   app=homework-2
NAME                    DESIRED   CURRENT   READY   AGE
homework-2-764db6b8b5   0         0         0       26m
homework-2-7bc667698b   4         4         4       6m15s
homework-2-845fcc4588   0         0         0       105m
NAME                          UID                                    IMAGE                                     RS                      READY   RESTARTS
homework-2-7bc667698b-8qfc2   bc55b401-371a-4dc5-b977-842f578c9ccf   localhost:5001/tsiganov-homework-2:v1.5   homework-2-7bc667698b   true    0
homework-2-7bc667698b-ffthf   878dd6ee-511d-4333-aaa3-99c55b24db1c   localhost:5001/tsiganov-homework-2:v1.5   homework-2-7bc667698b   true    0
homework-2-7bc667698b-jrszh   b70de6d6-1075-43b1-8d84-42ad39095b20   localhost:5001/tsiganov-homework-2:v1.5   homework-2-7bc667698b   true    0
homework-2-7bc667698b-wnghq   2976fcb0-0940-48b0-b44c-6740deed8055   localhost:5001/tsiganov-homework-2:v1.5   homework-2-7bc667698b   true    0

```

Ошибок в логах как видно в логах клиента, не было

### Объяснения
В задании написано то нужно 3 реплики то 4 создать, я в yaml 4 указал.

Почему в итоге созданы четыре новых Pod при `maxSurge: 1` - потому что он ограничивает только количество дополнительных подов одновременно, а не общее количество, сколько нужно создать новых подов.

Чем обновление отличается от перезапуска liveness пробами - в liveness пересоздаётся только контейнер внутри пода, а обновление делает новые поды и удаляет старые.

Как readiness и minReadySeconds влияют на удаление старых реплик - старые реплики удаляются только после того, как новые становятся доступными, а их мы проверяем по этой пробе.ё