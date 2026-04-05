# Day 2 Commands and Manifest Thinking

This note captures the exact commands used on Day 2 for ClusterPulse and the mental model for writing the first Kubernetes Deployment manifest.

---

## Day 2 Goal

Day 2 focused on:

- Building a tiny Flask app
- Containerizing it
- Deploying it to Kubernetes
- Verifying that the Deployment created a ReplicaSet and Pods
- Accessing it locally with port-forwarding
- Checking logs and debugging basics

---

## Command Flow

The command flow for Day 2 should be remembered in this order:

**Implement -> Build -> Load image -> Apply -> Verify -> Access -> Debug**

That order helps separate app problems from container problems and Kubernetes problems.

---

## 1. App Setup Commands

Run the Flask app locally first:

```bash
cd ClusterPulse/app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Test the endpoints locally:

```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/healthz
curl http://127.0.0.1:5000/ready
```

### Why this matters

This confirms the app itself works before Kubernetes is involved.

---

## 2. Docker Image Build

Build the image from the `app/` folder:

```bash
docker build -t clusterpulse:dev .
```

### Common mistake

If you forget the final `.`, Docker does not know the build context.

Correct pattern:

```bash
docker build -t <image-name>:<tag> .
```

---

## 3. Load Image into the Cluster

If using Minikube:

```bash
minikube image load clusterpulse:dev
```

If using kind:

```bash
kind load docker-image clusterpulse:dev
```

### Why this matters

The Kubernetes cluster must be able to see the image before it can start Pods from it.

---

## 4. Apply the Deployment Manifest

From the project root:

```bash
cd ..
kubectl apply -f manifests/deployment.yaml
```

---

## 5. Verify the Deployment

Check the Deployment, ReplicaSet, and Pods:

```bash
kubectl get deployments
kubectl get rs
kubectl get pods -o wide
kubectl rollout status deployment/clusterpulse
```

### What success looks like

You want to see:

- Deployment exists
- One ReplicaSet exists
- Three Pods are running
- Rollout completes successfully

---

## 6. Access the App Locally

Use port-forwarding:

```bash
kubectl port-forward deployment/clusterpulse 5000:5000
```

Then test:

```bash
curl http://localhost:5000/
curl http://localhost:5000/healthz
curl http://localhost:5000/ready
```

### Important note

A Deployment alone does not automatically expose your app to your laptop browser.
For Day 2, port-forwarding is the fastest way to access it.

---

## 7. Logs and Debugging Commands

Check logs from all matching Pods:

```bash
kubectl logs -l app=clusterpulse
```

Get the Pod list:

```bash
kubectl get pods -l app=clusterpulse
```

Check logs for a specific Pod:

```bash
kubectl logs <pod-name>
```

Check previous logs if a container restarted:

```bash
kubectl logs <pod-name> --previous
```

Describe the Deployment:

```bash
kubectl describe deployment/clusterpulse
```

Describe a Pod:

```bash
kubectl describe pod <pod-name>
```

Check recent cluster events:

```bash
kubectl get events --sort-by=.lastTimestamp | tail -20
```

---

## Useful Day 2 Interpretation

If logs show three separate Flask startup blocks with three different Pod IPs, that means all three Pods started correctly.

If only one Pod shows request lines like:

```text
127.0.0.1 - - [time] "GET / HTTP/1.1" 200 -
```

that usually means the current local tunnel or request path is reaching one Pod at that moment.
That does **not** mean the other Pods are broken.

---

# Manifest Thinking

For the first manifest, do not start by thinking about YAML syntax.
Start by thinking about decisions.

## Mental Order

Keep this order in your head every time you write a manifest:

1. What object am I creating?
2. What is its identity?
3. What behavior do I want from it?
4. What Pods should it create?
5. What must run inside those Pods?

---

## Best Beginner Rule

Use this memory line:

**Type -> Name -> Desired count -> Match rule -> Pod labels -> Container**

That is the cleanest way to mentally build a Deployment manifest.

---

## Deployment Manifest Thinking

Here is the beginner-friendly order:

### 1. Type

What object is this?

```yaml
apiVersion: apps/v1
kind: Deployment
```

### 2. Name

What is this object called?

```yaml
metadata:
  name: clusterpulse
```

### 3. Desired Count

How many copies should Kubernetes keep running?

```yaml
spec:
  replicas: 3
```

### 4. Match Rule

How does the Deployment know which Pods belong to it?

```yaml
spec:
  selector:
    matchLabels:
      app: clusterpulse
```

### 5. Pod Labels

What labels should the Pods have?

```yaml
template:
  metadata:
    labels:
      app: clusterpulse
```

### 6. Container

What actually runs inside the Pod?

```yaml
spec:
  containers:
  - name: clusterpulse
    image: clusterpulse:dev
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 5000
```

---

## Why Labels Confuse Beginners

This is one of the biggest beginner pain points.

You will see `app: clusterpulse` repeated in multiple places, and it feels unnecessary at first.
But each place has a different job.

### 1. Deployment Labels

```yaml
metadata:
  labels:
    app: clusterpulse
```

These labels belong to the Deployment object itself.

### 2. Selector Labels

```yaml
spec:
  selector:
    matchLabels:
      app: clusterpulse
```

These tell the Deployment which Pods it should manage.

### 3. Pod Template Labels

```yaml
template:
  metadata:
    labels:
      app: clusterpulse
```

These are the labels that will actually be attached to the Pods created by the Deployment.

## The Key Rule

The selector labels and Pod template labels must match.

If they do not match:

- The Deployment cannot correctly manage its Pods
- The manifest may fail validation
- Or the controller behavior becomes wrong

## Easy Way to Remember Labels

Think of it like this:

- Deployment label = label on the manager
- Selector = manager’s rule for finding workers
- Pod template labels = labels placed on the workers

The manager can only manage the workers if the finding rule matches the labels placed on the workers.

---

## Example Full Manifest

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: clusterpulse
  labels:
    app: clusterpulse

spec:
  replicas: 3
  selector:
    matchLabels:
      app: clusterpulse
  template:
    metadata:
      labels:
        app: clusterpulse
    spec:
      containers:
      - name: clusterpulse
        image: clusterpulse:dev
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
```

---

## Final Day 2 Quick Cheat Sheet

```bash
cd ClusterPulse/app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py

curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/healthz
curl http://127.0.0.1:5000/ready

docker build -t clusterpulse:dev .

minikube image load clusterpulse:dev
# or
kind load docker-image clusterpulse:dev

cd ..
kubectl apply -f manifests/deployment.yaml

kubectl get deployments
kubectl get rs
kubectl get pods -o wide
kubectl rollout status deployment/clusterpulse

kubectl port-forward deployment/clusterpulse 5000:5000

curl http://localhost:5000/
curl http://localhost:5000/healthz
curl http://localhost:5000/ready

kubectl logs -l app=clusterpulse
kubectl get pods -l app=clusterpulse
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl describe deployment/clusterpulse
kubectl describe pod <pod-name>
kubectl get events --sort-by=.lastTimestamp | tail -20
```

---

## Suggested Commit

```bash
git add .
git commit -m "Add Day 2 deployment workflow notes and command cheat sheet"
```