## Подготовка перед экспериментом

```bash
kubectl -n homework-2 rollout status deployment/homework-2 --timeout=180s
kubectl -n homework-2 get pods -l app=homework-2 -o wide
kubectl -n homework-2 get pods -l app=homework-2 -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,READY:.status.containerStatuses[0].ready,RESTARTS:.status.containerStatuses[0].restartCount'
```

Текущее состояние:

``` bash
deployment "homework-2" successfully rolled out
NAME                          READY   STATUS    RESTARTS   AGE   IP            NODE                        NOMINATED NODE   READINESS GATES
homework-2-845fcc4588-r24zx   1/1     Running   0          32s   10.244.0.33   hosting-lab-control-plane   <none>           <none>
homework-2-845fcc4588-tbmdx   1/1     Running   0          32s   10.244.0.34   hosting-lab-control-plane   <none>           <none>
homework-2-845fcc4588-vzfsv   1/1     Running   0          32s   10.244.0.32   hosting-lab-control-plane   <none>           <none>
NAME                          UID                                    READY   RESTARTS
homework-2-845fcc4588-r24zx   34306c1a-b0e1-4d23-80d8-1a7362aa453a   true    0
homework-2-845fcc4588-tbmdx   2d73d84b-b2c0-477c-b50b-f8843009ff63   true    0
homework-2-845fcc4588-vzfsv   6fc7daf7-a1b8-4521-b47d-93f5bb2d504c   true    0
```

Во втором терминале:
``` bash
kubectl -n homework-2 get pods -l app=homework-2 -w | tee evidence/console_pods_experiment_1.md
```

В третьем терминале:
```bash
kubectl -n homework-2 logs -f deployment/homework-2-client --timestamps | tee evidence/console_logs_experiment_1.md
```

## Сам эксперимент

Возьму под:
``` bash
homework-2-845fcc4588-r24zx   1/1     Running   0          32s  10.244.0.33 
```

Затем сделаю port-forwarding:
``` bash
 kubectl -n homework-2 port-forward pod/homework-2-845fcc4588-r24zx 8082:8000 
 ```

И в соседней консоли:
``` bash
date -u 
curl -i http://localhost:8082/
curl -i http://localhost:8082/live
curl -i http://localhost:8082/ready
curl -i http://localhost:8082/you-are-death
curl -i http://localhost:8082/live

Пн 02 ноя 2026 09:14:57 UTC
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:14:57 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 78
Connection: close

Pod Name:</b> homework-2-845fcc4588-r24zx (укоротил для логов)HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:14:57 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 10
Connection: close

live: True

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:14:57 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 11
Connection: close

ready: True

HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:14:57 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 23
Connection: close

you are no longer alive

HTTP/1.1 503 SERVICE UNAVAILABLE
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:14:57 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 120
Connection: close

<!doctype html>
<html lang=en>
<title>503 Service Unavailable</title>
<h1>Service Unavailable</h1>
<p>i am so dead!</p>
```

Затем через некоторое время:
``` bash
curl -i http://localhost:8082/live
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.8
Date: Mon, 02 Nov 2026 09:17:54 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 10
Connection: close

live: True

```

Фиксируем результаты:

Объяснение:
Почему UID сохранился, а RESTARTS вырос - перезапустился только контейнер внутри Pod, сам Pod остался прежним, отличается от просто удалением тем же.

Почему `/` может работать, но kubelet всё равно перезапускает контейнер - k8s перезапускает согласно пробам,`/` всё ещё может работать хотя, контейнер мог упасть.

Ошибок в работе client нет, почему? - потому что у нас 3 пода, и запросы могут быть обработаны, другим подом, во время падения нашего.

Под после эксперимента

``` bash
NAME                          UID                                    READY   RESTARTS
homework-2-845fcc4588-r24zx   34306c1a-b0e1-4d23-80d8-1a7362aa453a   true    1
```


``` bash 
kubectl -n homework-2 describe pod homework-2-845fcc4588-r24zx 
```

``` bash
Name:             homework-2-845fcc4588-r24zx
Namespace:        homework-2
Priority:         0
Service Account:  default
Node:             hosting-lab-control-plane/172.21.0.2
Start Time:       Mon, 02 Nov 2026 14:07:24 +0500
Labels:           app=homework-2
                  pod-template-hash=845fcc4588
Annotations:      <none>
Status:           Running
IP:               10.244.0.33
IPs:
  IP:           10.244.0.33
Controlled By:  ReplicaSet/homework-2-845fcc4588
Containers:
  homework-2:
    Container ID:   containerd://6025ff72ca4d85d9f111b1cd6460c636e7ac92a37d7e3179b8432f97737fb65e
    Image:          localhost:5001/tsiganov-homework-2:v1.3
    Image ID:       localhost:5001/tsiganov-homework-2@sha256:077f741d6bbd698589564abde7a0bdbcd88c25739e0ca77c74f15792ca74c534
    Port:           8000/TCP (http)
    Host Port:      0/TCP (http)
    State:          Running
      Started:      Mon, 02 Nov 2026 14:15:33 +0500
    Last State:     Terminated
      Reason:       Error
      Exit Code:    137
      Started:      Mon, 02 Nov 2026 14:07:25 +0500
      Finished:     Mon, 02 Nov 2026 14:15:33 +0500
    Ready:          True
    Restart Count:  1
    Limits:
      cpu:                500m
      ephemeral-storage:  256Mi
      memory:             1Gi
    Requests:
      cpu:                100m
      ephemeral-storage:  64Mi
      memory:             64Mi
    Liveness:             http-get http://:http/live delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=3
    Readiness:            http-get http://:http/ready delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=1
    Startup:              http-get http://:http/live delay=0s timeout=1s period=2s successThreshold=1 failureThreshold=30
    Environment Variables from:
      homework-2-config  ConfigMap  Optional: false
    Environment:
      APP_TOKEN:  <set to the key 'APP_TOKEN' in secret 'homework-2-credentials'>  Optional: false
      POD_NAME:   homework-2-845fcc4588-r24zx (v1:metadata.name)
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-fjfkb (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       True 
  ContainersReady             True 
  PodScheduled                True 
Volumes:
  kube-api-access-fjfkb:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason     Age                    From               Message
  ----     ------     ----                   ----               -------
  Normal   Scheduled  12m                    default-scheduler  Successfully assigned homework-2/homework-2-845fcc4588-r24zx to hosting-lab-control-plane
  Normal   Pulling    12m                    kubelet            spec.containers{homework-2}: Pulling image "localhost:5001/tsiganov-homework-2:v1.3"
  Normal   Pulled     12m                    kubelet            spec.containers{homework-2}: Successfully pulled image "localhost:5001/tsiganov-homework-2:v1.3" in 50ms (156ms including waiting). Image size: 157628109 bytes.
  Normal   Killing    4m42s                  kubelet            spec.containers{homework-2}: Container homework-2 failed liveness probe, will be restarted
  Normal   Created    4m12s (x2 over 12m)    kubelet            spec.containers{homework-2}: Container created
  Normal   Started    4m12s (x2 over 12m)    kubelet            spec.containers{homework-2}: Container started
  Normal   Pulled     4m12s                  kubelet            spec.containers{homework-2}: Container image "localhost:5001/tsiganov-homework-2:v1.3" already present on machine and can be accessed by the pod
  Warning  Unhealthy  4m12s                  kubelet            spec.containers{homework-2}: Readiness probe failed: Get "http://10.244.0.33:8000/ready": dial tcp 10.244.0.33:8000: connect: connection refused
  Warning  Unhealthy  4m11s                  kubelet            spec.containers{homework-2}: Readiness probe failed: HTTP probe failed with statuscode: 503
  Warning  Unhealthy  4m10s (x4 over 4m46s)  kubelet            spec.containers{homework-2}: Liveness probe failed: HTTP probe failed with statuscode: 503
  Warning  Unhealthy  4m2s (x9 over 12m)     kubelet            spec.containers{homework-2}: Startup probe failed: HTTP probe failed with statuscode: 503
                                                                            

```

``` bash
kubectl -n homework-2 logs homework-2-845fcc4588-r24zx --previous
```

```
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://10.244.0.33:8000
Press CTRL+C to quit
10.244.0.1 - - [02/Nov/2026 09:07:27] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:07:29] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:07:31] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:07:33] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:07:35] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:07:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:37] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:39] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:41] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:07:41] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:43] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:07:43] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:45] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:49] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:51] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:07:51] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:53] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:07:59] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:07:59] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:01] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:01] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:03] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:05] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:05] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:07] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:07] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:09] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:11] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:13] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:13] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:17] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:17] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:19] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:21] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:23] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:23] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:25] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:27] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:27] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:29] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:29] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:33] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:35] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:37] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:39] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:41] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:43] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:45] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:45] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:49] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:51] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:53] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:08:53] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:08:59] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:01] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:03] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:03] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:05] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:05] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:09] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:09] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:11] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:17] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:19] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:19] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:21] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:23] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:25] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:27] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:29] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:29] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:33] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:33] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:35] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:37] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:39] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:41] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:41] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:43] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:43] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:45] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:49] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:51] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:53] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:53] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:55] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:55] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:09:59] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:09:59] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:01] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:03] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:09] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:09] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:11] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:13] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:13] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:17] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:19] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:21] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:23] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:25] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:27] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:27] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:29] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:31] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:31] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:33] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:35] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:37] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:37] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:39] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:41] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:43] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:45] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:49] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:51] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:51] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:53] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:10:53] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:10:59] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:01] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:03] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:03] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:07] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:07] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:09] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:11] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:11] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:17] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:17] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:19] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:21] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:21] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:23] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:25] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:27] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:29] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:29] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:31] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:31] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:33] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:33] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:35] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:35] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:37] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:37] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:39] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:39] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:41] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:41] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:43] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:45] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:45] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:49] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:51] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:11:51] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:53] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:11:59] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:01] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:01] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:03] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:09] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:11] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:11] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:15] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:15] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:17] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:17] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:19] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:19] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:21] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:21] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:23] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:25] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:27] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:29] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:29] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:33] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:33] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:35] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:37] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:39] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:39] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:41] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:41] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:43] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:45] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:45] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:47] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:47] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:49] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:49] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:51] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:53] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:12:53] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:12:59] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:01] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:03] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:03] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:09] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:09] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:11] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:11] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:15] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:15] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:17] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:17] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:19] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:19] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:21] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:23] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:23] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:25] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:25] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:27] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:27] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:29] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:29] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:33] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:35] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:35] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:37] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:37] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:39] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:39] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:41] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:43] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:43] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:45] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:47] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:47] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:49] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:49] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:51] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:51] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:53] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:53] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:57] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:59] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:13:59] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:13:59] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:01] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:01] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:01] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:03] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:03] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:05] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:07] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:09] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:09] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:11] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:11] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:13] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:15] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:17] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:17] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:19] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:19] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:21] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:21] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:21] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:23] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:23] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:23] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:25] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:25] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:25] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:27] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:27] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:29] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:29] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:31] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:33] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:33] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:33] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:35] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:35] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:37] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:37] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:37] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:39] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:39] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:41] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:41] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:43] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:43] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:45] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:45] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:45] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:47] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:47] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:49] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:49] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:49] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:51] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:51] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:53] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:53] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:55] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:55] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:57] "GET /live HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:14:57] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:57] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [02/Nov/2026 09:14:57] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [02/Nov/2026 09:14:57] "GET /live HTTP/1.1" 200 -
127.0.0.1 - - [02/Nov/2026 09:14:57] "GET /ready HTTP/1.1" 200 -
127.0.0.1 - - [02/Nov/2026 09:14:57] "GET /you-are-death HTTP/1.1" 200 -
127.0.0.1 - - [02/Nov/2026 09:14:57] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:14:59] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:14:59] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:14:59] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:01] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:15:01] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:15:01] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:03] "GET /live HTTP/1.1" 503 -
10.244.0.1 - - [02/Nov/2026 09:15:03] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:05] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:07] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:09] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:15:09] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:11] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:13] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:15] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:17] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:19] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:21] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:23] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:25] "GET /ready HTTP/1.1" 200 -
10.244.0.35 - - [02/Nov/2026 09:15:25] "GET / HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:27] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:29] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:31] "GET /ready HTTP/1.1" 200 -
10.244.0.1 - - [02/Nov/2026 09:15:33] "GET /ready HTTP/1.1" 200 -
                      
```