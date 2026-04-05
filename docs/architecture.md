# ClusterPulse Architecture Notes

## Purpose

This project is designed to demonstrate practical Kubernetes workload management and troubleshooting concepts.

## Main Components

1. Deployment
- Runs the main web app
- Uses multiple replicas
- Supports rollout updates and rollback

2. Service
- Exposes the app inside or outside the cluster
- Routes traffic to Pods using labels

3. Probes
- Startup probe checks whether the app has finished starting
- Readiness probe controls whether the Pod should receive traffic
- Liveness probe checks whether the container should be restarted

4. Secret
- Stores configuration or environment variables securely

5. Job
- Runs a one-time background task

6. CronJob
- Runs a scheduled recurring task

7. DaemonSet
- Runs one Pod on every node for logging or node-level monitoring

## Labels and Annotations

- Labels will be used for grouping and selection
- Annotations will be used for metadata and rollout tracking