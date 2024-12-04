# Cloud SQL Instance On-Off

A cloud function that expects the following payload from a Pub/Sub topic to stop/start intended instances:

```json
{
  "project": "myproject",
  "instance": [
    { "name": "alpha-database", "state": "on" },
    { "name": "beta-cache", "state": "on" },
    { "name": "gamma-processor", "state": "on" },
    { "name": "delta-worker", "state": "on" },
    { "name": "epsilon-backend", "state": "on" },
    { "name": "zeta-frontend", "state": "on" },
    { "name": "theta-api", "state": "on" }
  ]
}
```
