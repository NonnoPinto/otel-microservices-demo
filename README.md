<p align="center">
<img src="/src/frontend/static/icons/Hipster_HeroLogoMaroon.svg" width="300" alt="Online Boutique" />
</p>

![Continuous Integration](https://github.com/GoogleCloudPlatform/microservices-demo/workflows/Continuous%20Integration%20-%20Main/Release/badge.svg)

## Online boutique with OTel Collector outside cluster
In this repo i made some sligth changes to `\kustomize\components\google-cloud-operations` to be able to inject [OTel kubernetes operator](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/) in `adservice` (Java) ad `recommendationservice` (Python). Everything is sent to an OTel collector OUTSIDE the cluster, then to a few different backend.
### How to test it
First, you need to start the collector (with this command you will save all the logs to a txt file).
```sh
nohup otelcol-contrib --config \kustomize\components\google-cloud-operations\otel-collector-config.yaml > collector.log 2>&1
```
(Optional) You can ran a py script that does a bk txt every 5000 lines.
```sh
python3 monitor_log.py
```
Start your cluster (I've used [k3d](https://k3d.io/stable/)).
```sh
k3d cluster create my-cluster -p "8081:80@loadbalancer" --api-port localhost:8080 --k3s-arg "--disable=traefik@server:0"
```
Here I explicitly expose the port and disable traefik that would occupy the same port we need for the certificate cluster.

Now it's time to start a couple of utility clusters:
```sh
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```
And the OTel operator.
```sh
kubectl apply -f ./release/otel-utils.yaml
```
(Optional) You can check if the operator succeefully started with
```sh
kubectl describe otelinst
```
output should be something like this:
```sh
Name:         auto-instrumentation
Namespace:    default
Labels:       app=otel-auto-instrumentation
Annotations:  instrumentation.opentelemetry.io/default-auto-instrumentation-apache-httpd-image:
                ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-apache-httpd:1.0.4
              instrumentation.opentelemetry.io/default-auto-instrumentation-dotnet-image:
                ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-dotnet:1.2.0
                 [...]
API Version:  opentelemetry.io/v1alpha1
Kind:         Instrumentation
Metadata:
  Creation Timestamp:  2025-02-20T22:33:23Z
  Generation:          1
  Resource Version:    16237
  UID:                 1706f54a-e7f2-454a-876b-85e7a79aa8e8
Spec:
  [...]
  Java:
    Env:
      Name:   COLLECTOR_SERVICE_ADDR
      Value:  http://172.29.92.175:4317
      Name:   OTEL_EXPORTER_OTLP_ENDPOINT
      Value:  http://172.29.92.175:4317
      Name:   OTEL_SERVICE_NAME
      Value:  adservice
      Name:   ENABLE_TRACING
      Value:  1
      Name:   ENABLE_LOGGING
      Value:  1
      Name:   ENABLE_PROFILER
      Value:  0
    Image:    ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:1.33.6
    Resources:
      Limits:
        Cpu:     500m
        Memory:  64Mi
      Requests:
        Cpu:     50m
        Memory:  64Mi
    Volume Claim Template:
      Metadata:
      Spec:
        Resources:
  [...]
Events:        <none>
```
Then install the services.
```sh
kubectl apply -f ./release/kubernetes-manifests.yaml
```
Check [localhost:8081](localhost:8081), the app should be up!


(Optional) Check if the operator succesfully injected the auto instrumentation in `adservice` and `recommendationservice`.
```sh
kubectl describe pod <pod name>
```
You should see something like this:
```sh
Normal  Pulled     38m   kubelet            Container image "ghcr.io/open-telemetry/opentelemetry-operator/autoinstrumentation-java:1.33.6" already present on machine
  Normal  Created    38m   kubelet            Created container opentelemetry-auto-instrumentation-java
  Normal  Started    38m   kubelet            Started container opentelemetry-auto-instrumentation-java
```
Lastly, start all code based telemetries:
```sh
kubectl apply -k ./kustomize
```
And you are good to go with your favourite backend!

### Metrics configuration
Both code based and injected otel are here configured to send metrics to the OTel collector outside the cluster. In this case, you need to manually set the right bridge port to make cluster and host machine able to share data. The one used in yaml file should be default, but you can verify with this command:
```sh
ip a | grep inet
```
From the result, chose the `eth0` ip. You can check if a pod is able to connect to it.
```sh
kubectl exec -it <pod> -- nc -zv <IP>
```

The operator is also configured to send data to a local [SigNoz docker](https://signoz.io/docs/install/docker/) (you will find it ready but disabled). If needed, first start the docker.