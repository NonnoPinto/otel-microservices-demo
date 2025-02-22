# Integrate Online Boutique with an external OTel collector

From the the `root` folder at the root level of this repository, execute this command:

```bash
kubectl apply -k ./kustomize
```

This will update the `kustomize/kustomization.yaml` file. This will activate code-based otel tracing.

**Note**
Currently only trace is supported.

## OpenTelemetry Collector

The collector should already be activated outside your cluster, locally! 
If you wish to experiment with different backends, you can modify the appropriate lines in [otel-collector.yaml](otel-collector.yaml) to export traces or metrics to a different backend.  See the [OpenTelemetry docs](https://opentelemetry.io/docs/collector/configuration/) for more details.

When the new Pod rolls out, you should start to see traces appear in your console.
