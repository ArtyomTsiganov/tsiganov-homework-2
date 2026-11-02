## Подготовка перед экспериментом

```bash
kubectl -n homework-2 rollout status deployment/homework-2 --timeout=180s
kubectl -n homework-2 get pods -l app=homework-2 -o wide
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
```

Текущее состояние:

``` bash
deployment "homework-2" successfully rolled out
NAME                          READY   STATUS    RESTARTS      AGE   IP            NODE                        NOMINATED NODE   READINESS GATES
homework-2-845fcc4588-r24zx   1/1     Running   1 (32m ago)   40m   10.244.0.33   hosting-lab-control-plane   <none>           <none>
homework-2-845fcc4588-tbmdx   1/1     Running   0             40m   10.244.0.34   hosting-lab-control-plane   <none>           <none>
homework-2-845fcc4588-vzfsv   1/1     Running   0             40m   10.244.0.32   hosting-lab-control-plane   <none>           <none>
NAME                          UID                                    READY   RESTARTS
homework-2-845fcc4588-r24zx   34306c1a-b0e1-4d23-80d8-1a7362aa453a   true    1
homework-2-845fcc4588-tbmdx   2d73d84b-b2c0-477c-b50b-f8843009ff63   true    0
homework-2-845fcc4588-vzfsv   6fc7daf7-a1b8-4521-b47d-93f5bb2d504c   true    0
```

Во втором терминале:
``` bash
kubectl -n homework-2 get pods -l app=homework-2 -w | tee evidence/console_pods_experiment_2.md
```

В третьем терминале:
```bash
kubectl -n homework-2 logs -f deployment/homework-2-client --timestamps | tee evidence/console_logs_experiment_2.md
```

## Сам эксперимент
Возьму под `homework-2-845fcc4588-r24zx`:

``` bash
NAME                          READY   STATUS    RESTARTS      AGE   IP            NODE                        NOMINATED NODE   READINESS GATES
homework-2-845fcc4588-r24zx   1/1     Running   1 (32m ago)   40m   10.244.0.33   hosting-lab-control-plane   <none>           <none>
```

Затем сделаю port-forwarding:
``` bash
 kubectl -n homework-2 port-forward pod/homework-2-845fcc4588-r24zx 8082:8000 
 ```

 ``` bash
curl -i http://localhost:8082/  
curl -i http://localhost:8082/live
curl -i http://localhost:8082/ready

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:52:36 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 78
Connection: close

Pod Name:</b> homework-2-845fcc4588-r24zx (укоротил для логов)

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:52:36 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 10
Connection: close

live: True

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:52:36 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 11
Connection: close

ready: True
```

Исходный endpointslice

``` bash
kubectl -n homework-2 get endpointslices -l kubernetes.io/service-name=homework-2 -o yaml
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.32
    conditions:
      ready: true 
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-vzfsv
      namespace: homework-2
      uid: 6fc7daf7-a1b8-4521-b47d-93f5bb2d504c
  - addresses:
    - 10.244.0.34
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-tbmdx
      namespace: homework-2
      uid: 2d73d84b-b2c0-477c-b50b-f8843009ff63
  - addresses:
    - 10.244.0.33
    conditions:
      ready: true <-------------------------------------------------------- тут true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-r24zx
      namespace: homework-2
      uid: 34306c1a-b0e1-4d23-80d8-1a7362aa453a
  kind: EndpointSlice
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-11-02T09:15:45Z"
    creationTimestamp: "2026-11-02T09:07:24Z"
    generateName: homework-2-
    generation: 9
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: homework-2
    name: homework-2-k4649
    namespace: homework-2
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: homework-2
      uid: 90a86394-8e32-4337-b8dd-9f8480b7dd23
    resourceVersion: "626673"
    uid: d48c547e-5a2c-4b02-9f04-152b30217bd1
  ports:
  - name: ""
    port: 8000
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""

```


### not-ready

Далее делаем not-ready и смотрим на запросы клиента в `console_logs_experiment_2.md` (1430 строка), как видно далее получают запросы только остальные 2 пода.

``` bash
date -u
curl -i http://localhost:8082/not-ready
curl -i http://localhost:8082/ready
curl -i http://localhost:8082/live
curl -i http://localhost:8082/


Пн 02 ноя 2026 09:54:58 UTC
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:54:58 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 23
Connection: close

you are no longer ready

HTTP/1.1 503 SERVICE UNAVAILABLE
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:54:58 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 116
Connection: close

<!doctype html>
<html lang=en>
<title>503 Service Unavailable</title>
<h1>Service Unavailable</h1>
<p>not ready</p>
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:54:58 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 10
Connection: close

live: True

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:54:58 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 78
Connection: close

Pod Name:</b> homework-2-845fcc4588-r24zx (укоротил для логов)

```

Снимок pods и endpointslices
``` bash
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
NAME                          UID                                    READY   RESTARTS
homework-2-845fcc4588-r24zx   34306c1a-b0e1-4d23-80d8-1a7362aa453a   false   1
homework-2-845fcc4588-tbmdx   2d73d84b-b2c0-477c-b50b-f8843009ff63   true    0
homework-2-845fcc4588-vzfsv   6fc7daf7-a1b8-4521-b47d-93f5bb2d504c   true    0

```

``` bash
kubectl -n homework-2 get endpointslices -l kubernetes.io/service-name=homework-2 -o yaml
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.32
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-vzfsv
      namespace: homework-2
      uid: 6fc7daf7-a1b8-4521-b47d-93f5bb2d504c
  - addresses:
    - 10.244.0.34
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-tbmdx
      namespace: homework-2
      uid: 2d73d84b-b2c0-477c-b50b-f8843009ff63
  - addresses:
    - 10.244.0.33
    conditions:
      ready: false <------------------------------------  тут false
      serving: false
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-r24zx
      namespace: homework-2
      uid: 34306c1a-b0e1-4d23-80d8-1a7362aa453a
  kind: EndpointSlice
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-11-02T09:54:59Z"
    creationTimestamp: "2026-11-02T09:07:24Z"
    generateName: homework-2-
    generation: 10
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: homework-2
    name: homework-2-k4649
    namespace: homework-2
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: homework-2
      uid: 90a86394-8e32-4337-b8dd-9f8480b7dd23
    resourceVersion: "629947"
    uid: d48c547e-5a2c-4b02-9f04-152b30217bd1
  ports:
  - name: ""
    port: 8000
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
```

## ready-again

Далее посылаем, что под ready-again. И смотрим в логи клиента (1546), реплика, вновь начала отвечать. 

```bash
date -u
curl -i http://localhost:8082/ready-again
curl -i http://localhost:8082/ready

Пн 02 ноя 2026 09:58:32 UTC
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:58:32 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 21
Connection: close

you are ready again !

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:58:32 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 11
Connection: close

ready: True⏎
```


Снимок pods и endpointslices

``` bash
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
NAME                          UID                                    READY   RESTARTS
homework-2-845fcc4588-r24zx   34306c1a-b0e1-4d23-80d8-1a7362aa453a   true    1
homework-2-845fcc4588-tbmdx   2d73d84b-b2c0-477c-b50b-f8843009ff63   true    0
homework-2-845fcc4588-vzfsv   6fc7daf7-a1b8-4521-b47d-93f5bb2d504c   true    0
```


``` bash
kubectl -n homework-2 get endpointslices -l kubernetes.io/service-name=homework-2 -o yaml
apiVersion: v1
items:
- addressType: IPv4
  apiVersion: discovery.k8s.io/v1
  endpoints:
  - addresses:
    - 10.244.0.32
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-vzfsv
      namespace: homework-2
      uid: 6fc7daf7-a1b8-4521-b47d-93f5bb2d504c
  - addresses:
    - 10.244.0.34
    conditions:
      ready: true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-tbmdx
      namespace: homework-2
      uid: 2d73d84b-b2c0-477c-b50b-f8843009ff63
  - addresses:
    - 10.244.0.33
    conditions:
      ready: true <----------------------------------------------- тут снова true
      serving: true
      terminating: false
    nodeName: hosting-lab-control-plane
    targetRef:
      kind: Pod
      name: homework-2-845fcc4588-r24zx
      namespace: homework-2
      uid: 34306c1a-b0e1-4d23-80d8-1a7362aa453a
  kind: EndpointSlice
  metadata:
    annotations:
      endpoints.kubernetes.io/last-change-trigger-time: "2026-11-02T09:58:32Z"
    creationTimestamp: "2026-11-02T09:07:24Z"
    generateName: homework-2-
    generation: 11
    labels:
      endpointslice.kubernetes.io/managed-by: endpointslice-controller.k8s.io
      kubernetes.io/service-name: homework-2
    name: homework-2-k4649
    namespace: homework-2
    ownerReferences:
    - apiVersion: v1
      blockOwnerDeletion: true
      controller: true
      kind: Service
      name: homework-2
      uid: 90a86394-8e32-4337-b8dd-9f8480b7dd23
    resourceVersion: "630266"
    uid: d48c547e-5a2c-4b02-9f04-152b30217bd1
  ports:
  - name: ""
    port: 8000
    protocol: TCP
kind: List
metadata:
  resourceVersion: ""
```

## Объяснения:
Почему контейнер не перезапустился - потому-что контейнер перезапускает liveness проба, а readness - отвечает за готовность принимать трафик
Почему port-forward продолжает работать - он подключается напрямую к поду, поэтому его исключение из endpointslice не мешает соединению
Почему команду восстановления нельзя надёжно отправлять через Service - запрос на восстановление может попасть в другую реплику