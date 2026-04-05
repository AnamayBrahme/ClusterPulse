# ClusterPulse

ClusterPulse is a Kubernetes learning project built to demonstrate core workload and operations concepts from Kubernetes Section 3.

## Project Goal

The goal of this project is to build a small but practical Kubernetes demo environment that shows how different Kubernetes objects work together in a real setup.

## Topics Covered

This project includes:

- Deployment
- Service
- Probes
- Secrets
- Labels
- Annotations
- Job
- CronJob
- DaemonSet

## Planned Architecture

The project will contain:

- A small web application running in a Deployment
- A Service to expose the application
- Readiness, liveness, and startup probes
- A Secret injected into the application
- A Job for a one-time task
- A CronJob for a scheduled task
- A DaemonSet to run one Pod on every node

## Repository Structure

- `app/` → application code
- `manifests/` → Kubernetes YAML files
- `docs/` → architecture and project notes
- `screenshots/` → proof of working setup

## Sprint Plan

- Day 1: Project setup and documentation
- Day 2: App setup and Deployment
- Day 3: Service and labels
- Day 4: Probes
- Day 5: Secrets and annotations
- Day 6: Job, CronJob, and DaemonSet
- Day 7: Rollout, rollback, and troubleshooting
- Day 8: Final polish and GitHub cleanup