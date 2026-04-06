# Day 3 Notes - Services, Labels, Selectors, DNS, and Testing

This note summarizes everything covered on Day 3 of the ClusterPulse project.
It explains what was built, why it mattered, how the Service worked, how labels and selectors were used, what NodePort means, how to test the setup, and where to troubleshoot when something goes wrong.

---

## Day 3 Goal

Day 3 was about moving from just **running Pods** to a Kubernetes application that is **discoverable inside the cluster**.

On Day 2, the Flask app was running in a Deployment with 3 Pods.
That proved that the app and Deployment worked.
But Pods are temporary and their IPs can change, so directly depending on Pod IPs is not a good way to access an app.

That is why Day 3 introduced a **Service**.
A Service gives the app a stable network identity and forwards traffic to the correct Pods.

So the meaning of Day 3 is:

- Day 2 proved the app can run.
- Day 3 proved the app can be reached properly inside Kubernetes.
- Day 3 introduced real internal service discovery.

---

## What was built on top of Day 2

On top of the Day 2 Deployment, Day 3 added:

- Clean labels on the Deployment and Pods
- A `ClusterIP` Service in front of the Pods
- Testing using a throwaway curl Pod
- DNS-based service discovery checks
- Optional discussion of `NodePort`

So now the architecture is:

```text
User / Other Pod
      |
      v
Service (clusterpulse-service)
      |
      v
Deployment (clusterpulse)
      |
      v
3 Pods running Flask app
```

This means the Service sits in front of the Pods and routes traffic to them.
The Service does not talk to the Deployment by name.
It finds Pods using labels and selectors.

---

## Day 3 exact order

Day 3 was broken into this order:

1. Clean labels in the Deployment
2. Re-apply the Deployment
3. Create `service.yaml`
4. Apply the Service
5. Check the Service output
6. Check Endpoints
7. Launch a temporary curl Pod
8. Test DNS and connectivity
9. Optionally discuss NodePort

This order matters because it helps isolate problems.
If labels are wrong, the Service will not match Pods.
If the Service has no endpoints, DNS may resolve but traffic still will not reach the app.

---

## Labels and why they matter

This was one of the biggest Day 3 questions.

A **label** is just a key-value tag attached to a Kubernetes object.
Labels help identify, group, filter, and target objects.

Examples used in this project:

- `app: clusterpulse`
- `env: dev`
- `component: web`

### What each one means

- `app: clusterpulse` means the object belongs to the ClusterPulse app.
- `env: dev` means the object belongs to the development environment.
- `component: web` means this is the web-facing part of the application.

### Why these were added after Day 2

On Day 2, the goal was only to get the app running, so one simple label like `app: clusterpulse` was enough.
On Day 3, the focus changed to networking and service discovery.
That is why cleaner and more meaningful labels were introduced.

### Why not use only one label forever?

You can use only one label for a small demo, but multiple labels make the app easier to organize.
They help answer questions like:

- Which Pods belong to the app?
- Which Pods are part of the web layer?
- Which Pods are in dev and not prod?

### Very important idea

Labels are not only for humans.
Kubernetes controllers and Services also use them to decide which objects belong together.

---

## Selectors and how they work

A **selector** is the rule used to find objects by label.

For example:

```yaml
selector:
  app: clusterpulse
```

This means:

> find all Pods whose labels include `app=clusterpulse`

If you use:

```yaml
selector:
  app: clusterpulse
  component: web
```

then the match becomes stricter.
A Pod must have **both** labels.

### Easy way to remember

- Labels = stickers on objects
- Selector = rule for which stickers to look for
- Service = front door that sends traffic to objects with the right stickers

---

## Why selector changes caused an error

One of the important Day 3 issues was this error:

```text
The Deployment "clusterpulse" is invalid: spec.selector: field is immutable
```

This happened because the original Deployment was created with one selector, and later the selector was changed.
For Deployments, `spec.selector` is immutable after creation.

That means:

- You can change some parts of a Deployment
- But you cannot change its selector after it already exists

### What the safe fix was

The safer Day 3 solution was:

- Keep the Deployment selector simple and stable
- Use only `app: clusterpulse` in the Deployment selector
- Keep `env: dev` and `component: web` as extra Pod labels

That reduces errors and makes Service matching easier.

---

## Final Deployment label strategy

The practical setup for this project became:

### Deployment selector

```yaml
selector:
  matchLabels:
    app: clusterpulse
```

### Pod template labels

```yaml
labels:
  app: clusterpulse
  env: dev
  component: web
```

### Why this is a good pattern

- `app` stays stable for routing
- `env` and `component` remain useful for filtering and organization
- The Service can safely match `app: clusterpulse`
- The setup stays easy to reason about

---

## ClusterIP Service and why it was used first

The first Service type used on Day 3 was `ClusterIP`.

A `ClusterIP` Service creates a stable internal endpoint inside the cluster.
It is meant for communication **inside Kubernetes**.
That is why it is the best first Service type for learning service discovery.

### Why ClusterIP first?

Because the main Day 3 goal was not external browser access.
The main goal was to understand:

- how Services find Pods
- how labels and selectors work together
- how Service DNS works
- how a Pod can call another app by Service name

### Simple idea

ClusterIP means:

> make the app reachable from other Pods in the cluster by a stable Service name and IP

---

## Service YAML thinking

When writing a Service manifest, the mental order should be:

1. What object am I creating?
2. What is its name?
3. Which Pods should it send traffic to?
4. Which port should clients use?
5. Which container port should traffic go to?

### Service example used for Day 3

```yaml
apiVersion: v1
kind: Service
metadata:
  name: clusterpulse-service
  labels:
    app: clusterpulse
    env: dev
    component: web
spec:
  type: ClusterIP
  selector:
    app: clusterpulse
  ports:
  - protocol: TCP
    port: 5000
    targetPort: 5000
```

### What each part means

- `kind: Service` means this object is a Service.
- `name: clusterpulse-service` is the DNS/service name.
- `type: ClusterIP` means it is internal to the cluster.
- `selector: app: clusterpulse` means it should find Pods with that label.
- `port: 5000` means clients use port 5000 on the Service.
- `targetPort: 5000` means traffic is forwarded to container port 5000.

---

## How internal discovery worked

This was the most important Day 3 concept.

Internal discovery worked in this chain:

1. The Pods had labels.
2. The Service had a selector.
3. Kubernetes matched the selector to the Pods.
4. Matching Pods became Service endpoints.
5. DNS made the Service reachable by name.
6. Another Pod could call the app using `clusterpulse-service`.

### The key insight

The Service does **not** discover Pods using the Deployment name.
It discovers Pods using labels.

### The real flow

```text
Pod labels -> Service selector -> Endpoints -> DNS name -> traffic reaches Flask Pods
```

That is the whole Day 3 networking story in one line.

---

## Endpoints and why they matter

An **endpoint** is a backend Pod IP attached to the Service.
If the Service selector matches real Pods, Kubernetes creates endpoints for those Pods.

So the Service is the front door, and endpoints are the actual backend addresses.

### Why endpoints are important

Because a Service can exist even when it is useless.
If the selector matches nothing, the Service object still exists, but it has no endpoints.
That means traffic cannot actually reach the app.

### Important lesson

Do not stop at `kubectl get svc`.
Always also check endpoints.

---

## Day 3 commands used

### Re-apply Deployment and check labels

```bash
kubectl apply -f manifests/deployment.yaml
kubectl get pods --show-labels
kubectl get deployment clusterpulse --show-labels
```

### Apply and inspect Service

```bash
kubectl apply -f manifests/service.yaml
kubectl get svc
kubectl describe svc clusterpulse-service
kubectl get endpoints clusterpulse-service
```

### Launch test Pod

```bash
kubectl run curlpod --image=curlimages/curl --rm -it --restart=Never -- sh
```

### Inside the curl Pod

```sh
nslookup clusterpulse-service
curl http://clusterpulse-service:5000/
curl http://clusterpulse-service:5000/healthz
curl http://clusterpulse-service:5000/ready
```

---

## How to read the outputs

### 1. `kubectl get pods --show-labels`

What to look for:

- Pod status should be `Running`
- Ready count should look healthy
- Labels should include `app=clusterpulse`
- Extra labels like `env=dev` and `component=web` should also appear if added

### 2. `kubectl get svc`

What to look for:

- `clusterpulse-service` exists
- Type is `ClusterIP`
- Port shows `5000`

### 3. `kubectl describe svc clusterpulse-service`

What to focus on:

- `Selector`
- `Type`
- `Port`
- `TargetPort`
- `Endpoints`

If endpoints appear, the Service matched the Pods.
If endpoints are empty, the selector probably does not match the Pod labels, or the Pods are not ready.

### 4. `kubectl get endpoints clusterpulse-service`

What to look for:

- Pod IPs should appear
- Port `5000` should appear

If nothing appears, the Service is not wired correctly to the Pods.

### 5. `nslookup clusterpulse-service`

What to look for:

- DNS resolution should return a Service IP

That proves cluster DNS can resolve the Service name.

### 6. `curl http://clusterpulse-service:5000/healthz`

What to look for:

- A valid Flask response
- HTTP success output

That proves the request path works end to end.

---

## Troubleshooting flow for Day 3

This was the best troubleshooting order:

1. Check Pods
2. Check labels
3. Check Service
4. Check Service selector
5. Check endpoints
6. Check DNS
7. Check curl response
8. Check logs if needed

### Suggested command order

```bash
kubectl get pods -o wide --show-labels
kubectl get svc
kubectl describe svc clusterpulse-service
kubectl get endpoints clusterpulse-service
kubectl logs -l app=clusterpulse
kubectl run curlpod --image=curlimages/curl --rm -it --restart=Never -- sh
```

Then inside the Pod:

```sh
nslookup clusterpulse-service
curl http://clusterpulse-service:5000/
```

---

## Common Day 3 problems and what they mean

### Problem 1: Service exists but no endpoints

**Meaning:**
The selector did not match the Pods, or the Pods were not ready.

**Where to look:**

- `kubectl describe svc clusterpulse-service`
- `kubectl get pods --show-labels`

**How to mitigate:**

- Compare Service selector and Pod labels carefully
- Make sure `app: clusterpulse` matches exactly
- Make sure Pods are running

### Problem 2: DNS fails

**Meaning:**
The Service name could not be resolved inside the cluster.

**Where to look:**

- `nslookup clusterpulse-service`
- Cluster DNS health if needed

**How to mitigate:**

- Confirm the Service exists
- Confirm you are testing from another Pod
- Recheck namespace and Service name

### Problem 3: DNS works but curl fails

**Meaning:**
The Service name resolves, but traffic is not reaching the app correctly.

**Where to look:**

- Service `port`
- Service `targetPort`
- App logs
- Pod status

**How to mitigate:**

- Make sure the Service sends traffic to port 5000
- Make sure Flask listens on port 5000
- Check `kubectl logs -l app=clusterpulse`

### Problem 4: Pods are not running

**Meaning:**
This is not a Service issue yet.
The app or Deployment itself has a problem.

**Where to look:**

- `kubectl get pods`
- `kubectl describe pod <pod-name>`
- `kubectl logs <pod-name>`

**How to mitigate:**

- Fix the Pod/container issue first
- Then retry Service testing

---

## NodePort explanation

NodePort was discussed as an optional step, not the main Day 3 goal.

A `NodePort` Service exposes the app outside the cluster by opening a chosen port on every node.
That means you can access the app using:

```text
http://<NodeIP>:<nodePort>
```

### Example used

```yaml
apiVersion: v1
kind: Service
metadata:
  name: clusterpulse-nodeport
spec:
  type: NodePort
  selector:
    app: clusterpulse
  ports:
  - protocol: TCP
    port: 5000
    targetPort: 5000
    nodePort: 30050
```

### What the ports mean

- `port: 5000` = Service port inside the cluster
- `targetPort: 5000` = container port
- `nodePort: 30050` = external port opened on every node

### Why use NodePort?

NodePort is useful for quick browser testing from outside the cluster.
It is easier than repeated port-forwarding in some learning setups.

### Why not start with NodePort?

Because ClusterIP is the core Day 3 learning topic.
NodePort is built on top of the Service concept.
If the internal Service setup is broken, NodePort will not fix the real problem.

---

## What Day 3 proved

By the end of Day 3, the project was no longer just “3 Pods running”.
It became a small but proper Kubernetes application with:

- a Deployment managing Pods
- labels describing those Pods
- a Service in front of those Pods
- selector-based Pod matching
- endpoints created from matching Pods
- DNS-based service discovery inside the cluster

That is a major step forward because it turns raw Pods into a reachable application service.

---

## Best memory lines from Day 3

Keep these in mind:

- Pods run the app.
- Labels describe the Pods.
- Selectors find the Pods.
- Services route traffic to the Pods.
- Endpoints are the actual backend Pod IPs.
- DNS lets other Pods call the Service by name.

And the most important one:

**Pod labels -> Service selector -> Endpoints -> DNS name -> traffic reaches the app**

---

## Good Day 3 revision checklist

Use this when reviewing later:

- Do I know what a ClusterIP Service is?
- Do I know why Pods should not be reached by Pod IP directly?
- Do I know what labels are?
- Do I know what selectors do?
- Do I know why `env=dev` and `component=web` were added?
- Do I know why keeping the selector simple is safer?
- Do I know what endpoints are?
- Do I know how DNS service discovery works?
- Do I know the difference between ClusterIP and NodePort?
- Do I know the basic Day 3 troubleshooting flow?

If the answer is yes to all of these, Day 3 concepts are solid.
'''
Path('output').mkdir(exist_ok=True)
Path('output/day3-notes.md').write_text(md)
print('output/day3-notes.md')