## Collect telemetry from Llamastack

This assumes you have an observability stack running in OpenShift. To deploy the necessary components,
follow the [observability-guide](./README.md).

### Updated manifests for Llama Stack telemetry trace collection with opentelemetry receiver endpoint

This is for traces only. There is a similar `otel_metric` sink and `otel_metric_endpoint`, however, there are currently
only 4 metrics generated within Llamastack, and these are duplicates of what vLLM provides.

[kubernetes/llama-stack/run.yaml](../llama-stack/run.yaml)

```yaml
---
  telemetry:
  - provider_id: meta-reference
    provider_type: inline::meta-reference
    config:
      service_name: ${env.OTEL_SERVICE_NAME:llama-stack}
      sinks: ${env.TELEMETRY_SINKS:console, sqlite} <- add env var in deployment to add otel_trace, otel_metric
      otel_trace_endpoint: ${env.OTEL_TRACE_ENDPOINT:} <- add ONLY if opentelemetry receiver endpoint is available.
      sqlite_db_path: ${env.SQLITE_DB_PATH:~/.llama/distributions/starter/trace_store.db}
---
```
And, in [kubernetes/llama-stack/deployment.yaml](../llama-stack/deployment.yaml)

```yaml
---
  template:
    metadata:
      labels:
        app: llama-stack
      annotations:
        sidecar.opentelemetry.io/inject: llamastack-otelsidecar # <- be sure to add this annotation to the **template.metadata**
    spec:
      containers:
---
        env:
        - name: TELEMETRY_SINKS
          value: 'console, sqlite, otel_trace'
        - name: OTEL_TRACE_ENDPOINT
          value: http://localhost:4318/v1/traces
       #-  name: OTEL_METRIC_ENDPOINT
       #-  value: http://localhost:4318/v1/metrics
---
```

The example above assumes an opentelemetry-collector sidecar is added to the llama-stack deployment (hence, sending over localhost).
You can send to any in-cluster opentelemetry-collector by setting the
`OTEL_TRACE_ENDPOINT` to `http://service-name-otc.namespace-of-otc.svc.cluster.local:4318/v1/traces(or v1/metrics)`.

In this example, each server would use `localhost` for the receiver endpoint, and the `opentelemetry-collector` would be
configured to export all telemetry to a Tempostack in the same namespace.
To deploy an OpenTelemetryCollector in the `llama-stack` namespace alongside a llama stack deployment:

> **📝 NOTE:** Don't update the Llamastack deployment until _after_
> the [OpentelemetryCollector Sidecar](./otel-collector/otel-collector-llamastack-sidecar.yaml)
See [OpenTelemetryCollector Sidecar](./otel-collector/otel-collector-llamastack-sidecar.yaml) for how to send to Tempo.
