---
name: kubernetes
description: "Manage Kubernetes clusters via kubectl. Use when the mission involves pods, deployments, services, namespaces, debugging, or any k8s operations."
---

# Kubernetes

Use this skill when the mission requires managing Kubernetes resources via `kubectl`.

## Prerequisites

- `kubectl` must be installed and a valid kubeconfig available (`~/.kube/config` or `KUBECONFIG` env var).
- Verify before starting: `kubectl cluster-info` and `kubectl config current-context`

## Workflow

1. **Verify access** — `kubectl cluster-info`. Confirm context with `kubectl config current-context`.
2. **Always specify namespace** — Use `-n <namespace>` on every command. Never rely on the default.
3. **Read first** — `get`, `describe`, `logs`, `events` before any mutations.
4. **Backup before modifying** — `kubectl get <resource> -o yaml > backup.yaml`
5. **Dry-run** — `--dry-run=client` (fast) or `--dry-run=server` (validates against cluster).
6. **Apply** — `kubectl apply -f <manifest.yaml>`
7. **Verify** — `kubectl rollout status`, check pods, check events.

## Output formatting

```bash
# JSON for parsing
kubectl get pods -n $NS -o json | jq '.items[].metadata.name'

# JSONPath for specific fields
kubectl get pods -n $NS -o jsonpath='{.items[*].metadata.name}'

# Custom columns for readable tables
kubectl get pods -n $NS -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# YAML for full resource inspection
kubectl get deployment $NAME -n $NS -o yaml

# Names only (for scripting)
kubectl get pods -n $NS -o name
```

## Common operations

**Context and namespace:**
```bash
kubectl config get-contexts
kubectl config use-context $CTX
kubectl config set-context --current --namespace=$NS
kubectl get namespaces
```

**Inspection:**
```bash
kubectl get pods -n $NS -o wide
kubectl describe pod $POD -n $NS
kubectl get events --sort-by='.lastTimestamp' -n $NS
kubectl logs $POD -n $NS [-c $CONTAINER] [--previous] [-f]
kubectl top pods -n $NS
kubectl top nodes
```

**Deployments:**
```bash
kubectl apply -f manifest.yaml --dry-run=client
kubectl apply -f manifest.yaml
kubectl set image deployment/$NAME $CONTAINER=$IMAGE:$TAG -n $NS
kubectl rollout status deployment/$NAME -n $NS -w
kubectl rollout undo deployment/$NAME -n $NS
kubectl scale deployment/$NAME --replicas=$N -n $NS
kubectl rollout history deployment/$NAME -n $NS
```

**Debugging:**
```bash
kubectl exec -it $POD -n $NS -- /bin/sh
kubectl port-forward $POD $LOCAL:$REMOTE -n $NS
kubectl get events --field-selector involvedObject.name=$POD -n $NS
kubectl explain deployment.spec.template.spec.containers
kubectl run debug --image=busybox --rm -it --restart=Never -- sh
```

**Services and networking:**
```bash
kubectl get svc -n $NS
kubectl get ingress -n $NS
kubectl get endpoints $SVC -n $NS
```

**Node operations:**
```bash
kubectl get nodes -o wide
kubectl cordon $NODE
kubectl drain $NODE --ignore-daemonsets --delete-emptydir-data
kubectl uncordon $NODE
```

**Secrets and ConfigMaps:**
```bash
kubectl get secrets -n $NS
kubectl create secret generic $NAME --from-literal=key=value -n $NS
kubectl get secret $NAME -n $NS -o jsonpath='{.data.key}' | base64 -d
kubectl get configmap $NAME -n $NS -o yaml
```

## Guardrails

- Always specify `-n <namespace>`. Use `-A` only for cluster-wide reads.
- Always use `--dry-run=client` before applying manifests for the first time.
- Back up resources with `-o yaml` before modifying or deleting.
- Never `delete` pods/deployments in production without explicit confirmation.
- Never use `latest` image tags in production deployments.
- Use declarative `apply -f` over imperative commands for anything persistent.
- Use `--field-selector` and `-l` (label selectors) to narrow results.
- For large clusters, always use selectors — unbounded `get` can be slow and flood context.
- Use `kubectl explain` to check field schemas instead of guessing YAML structure.
