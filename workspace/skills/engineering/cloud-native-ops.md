# Cloud Native Operations

> Level: Expert | File: `cloud-native-ops.md`
> 
> Production-grade cloud native operations: containerization, Kubernetes at scale,
> service mesh, GitOps, multi-cluster management, cost optimization, and CNCF ecosystem.

---

## Table of Contents
1. [Containerization Deep Dive](#1-containerization-deep-dive)
2. [Kubernetes: Production Best Practices](#2-kubernetes-production-best-practices)
3. [Kubernetes Security: Pod Security, RBAC, Network Policies](#3-kubernetes-security-pod-security-rbac-network-policies)
4. [Helm & Package Management](#4-helm--package-management)
5. [Infrastructure as Code (Terraform, Pulumi, Crossplane)](#5-infrastructure-as-code-terraform-pulumi-crossplane)
6. [GitOps: ArgoCD & Flux](#6-gitops-argocd--flux)
7. [Service Mesh: Istio, Linkerd, Cilium](#7-service-mesh-istio-linkerd-cilium)
8. [Observability Stack on K8s](#8-observability-stack-on-k8s)
9. [Cost Optimization](#9-cost-optimization)
10. [CNCF Ecosystem & Toolchain Reference](#10-cncf-ecosystem--toolchain-reference)

---

## 1. Containerization Deep Dive

### 1.1 Dockerfile Best Practices

```dockerfile
# ✅ Production-grade Dockerfile

# 1. Use distroless or minimal base
FROM node:20-alpine AS build
WORKDIR /app

# 2. Leverage build cache (copy package files first)
COPY package*.json ./
RUN npm ci --only=production

# 3. Copy app code AFTER deps (cache layer)
COPY . .

# 4. Build in separate stage
RUN npm run build

# 5. Production image: minimal
FROM gcr.io/distroless/nodejs20-debian12 AS runtime
WORKDIR /app

# 6. Non-root user
USER nonroot:nonroot

# 7. Copy only what's needed
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules

# 8. Read-only filesystem
EXPOSE 3000
ENTRYPOINT ["node", "dist/server.js"]
```

### 1.2 Image Optimization
```dockerfile
# Layer reduction
RUN apk add --no-cache --virtual .build-deps curl \
    && curl -fsSL https://example.com/package.tar.gz | tar xz \
    && apk del .build-deps

# Multi-stage: copy only build output
COPY --from=builder /app/dist /app/dist

# .dockerignore (prevents sending build context)
.git/
node_modules/
*.md
tests/
.env*
```

### 1.3 Container Security Scanning
```yaml
# CI integration (Trivy)
- name: Scan container image
  run: |
    trivy image \
      --severity CRITICAL,HIGH \
      --exit-code 1 \
      --no-progress \
      --format sarif \
      --output trivy-results.sarif \
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

---

## 2. Kubernetes: Production Best Practices

### 2.1 Resource Requests & Limits
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
  labels:
    app: api-server
    version: v2
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0         # Zero-downtime deploy
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      # Pod-level resources
      # topologySpreadConstraints for HA
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api-server
      containers:
        - name: api-server
          image: registry/api:v2.5.0
          ports:
            - containerPort: 8080
              protocol: TCP
          resources:
            requests:
              cpu: "250m"        # 0.25 vCPU
              memory: "256Mi"
            limits:
              cpu: "1"           # Burst up to 1 vCPU
              memory: "512Mi"    # OOM if exceeds
          # Probes
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 15
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          startupProbe:           # K8s 1.18+ — for slow-starting containers
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 30  # Allow up to 150s startup
          envFrom:
            - configMapRef:
                name: api-config
            - secretRef:
                name: api-secrets
```

### 2.2 Pod Disruption Budgets
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
spec:
  minAvailable: 2            # At least 2 pods always available
  # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app: api-server
```

### 2.3 Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods              # Custom metric — RPS per pod
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5min before scaling down
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0    # Scale up immediately
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
```

### 2.4 Cluster Autoscaler / Karpenter
```yaml
# Cluster Autoscaler (K8s native)
# Scales node pool up/down when pods are pending
# Configuration:
#   - min: 3 nodes, max: 50 nodes
#   - Scale-down delay: 10 minutes
#   - Skip nodes with local storage

# Karpenter (AWS-specific, better)
# Provisioner YAML:
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand", "spot"]
        - key: kubernetes.io/arch
          operator: In
          values: ["arm64", "amd64"]
      nodeClassRef:
        name: default
  limits:
    cpu: "1000"              # Max 1000 vCPU
  disruption:
    consolidationPolicy: WhenUnderutilized
    expireAfter: 720h        # Replace nodes every 30 days
```

### 2.5 ConfigMap & Secret Management
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  FEATURE_FLAGS: '{"new_checkout":true,"dark_mode":false}'
---
apiVersion: v1
kind: Secret
metadata:
  name: api-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgres://user:pass@host:5432/db"
  JWT_SECRET: "encrypted-or-external"   # NEVER in git
---
# External Secrets Operator — sync cloud secrets to K8s
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-secret
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secret-store
    kind: ClusterSecretStore
  target:
    name: api-secrets
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: /production/api/DATABASE_URL
```

---

## 3. Kubernetes Security: Pod Security, RBAC, Network Policies

### 3.1 Pod Security Standards
```yaml
# Restricted (strictest — for workloads handling sensitive data)
securityContext:
  runAsNonRoot: true
  runAsUser: 1000                    # Explicit UID
  runAsGroup: 3000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop: ["ALL"]
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
```

### 3.2 Pod Security Admission (PSA)
```yaml
# Namespace-level enforcement (K8s 1.23+)
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: v1.29
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline
```

### 3.3 RBAC (Minimum Privilege)
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "watch", "list"]
---
# ServiceAccount for each app (don't use default!)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api-server
automountServiceAccountToken: true  # Explicit
---
# RoleBinding with least privileges
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: api-server-rolebinding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: api-server
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 3.4 Network Policies
```yaml
# Default deny all ingress (enable per namespace)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress

# Allow API server to talk to DB
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-server
      ports:
        - port: 5432
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-monitoring
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: monitoring
      ports:
        - port: 9090           # Metrics endpoint
```

---

## 4. Helm & Package Management

### 4.1 Chart Structure
```
my-app/
├── Chart.yaml          # Metadata: name, version, dependencies
├── values.yaml         # Default values
├── values.production.yaml    # Environment overrides
├── values.staging.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── _helpers.tpl    # Reusable templates
│   └── hpa.yaml
└── charts/             # Sub-charts (dependencies)
```

### 4.2 Best Practices
```yaml
# Chart.yaml
apiVersion: v2
name: api-server
description: Production API server
type: application
version: 2.5.0
appVersion: "2.5.0"
dependencies:
  - name: postgresql
    version: "~12.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "~18.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

```yaml
# values.yaml — always document every value
replicaCount: 3

image:
  repository: registry/api-server
  tag: ""          # Set by CI
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: "250m"
    memory: "256Mi"
  limits:
    cpu: "1"
    memory: "512Mi"

ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.example.com
      paths: ["/"]

postgresql:
  enabled: true
  auth:
    database: api
    username: api
  primary:
    persistence:
      size: 100Gi
```

### 4.3 Helm CI/CD
```yaml
# GitLab CI / GitHub Actions
helm dependency update
helm lint
helm template --validate ./my-app
helm diff upgrade --install my-app ./my-app -f values.production.yaml
# After review:
helm upgrade --install my-app ./my-app \
  -f values.production.yaml \
  --set image.tag=$CI_COMMIT_SHA \
  --namespace production \
  --atomic \
  --timeout 5m
```

---

## 5. Infrastructure as Code (Terraform, Pulumi, Crossplane)

### 5.1 Terraform: Production Modules
```hcl
# modules/eks-cluster/main.tf
resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks.arn
  version  = "1.29"

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn
    }
  }
}

resource "aws_eks_node_group" "this" {
  cluster_name    = aws_eks_cluster.this.name
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids
  instance_types  = ["m7i.large", "m7i.xlarge"]
  capacity_type   = "ON_DEMAND"
  disk_size       = 100

  scaling_config {
    desired_size = 3
    min_size     = 3
    max_size     = 30
  }

  update_config {
    max_unavailable_percentage = 33
  }
}
```

### 5.2 State Management
```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "terraform-state-prod"
    key            = "eks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"   # State locking
  }
}
```

### 5.3 Crossplane (Control Plane IaC)
```yaml
# Crossplane: Kubernetes-native infrastructure provisioning
apiVersion: eks.aws.upbound.io/v1beta1
kind: Cluster
metadata:
  name: production-eks
spec:
  forProvider:
    region: us-east-1
    version: "1.29"
    vpcConfig:
      endpointPrivateAccess: true
      subnetIdsRefs:
        - name: private-subnet-a
        - name: private-subnet-b
  providerConfigRef:
    name: aws-provider
```

---

## 6. GitOps: ArgoCD & Flux

### 6.1 ArgoCD — Application Definition
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-server
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/company/manifests.git
    targetRevision: HEAD
    path: apps/api-server/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true               # Auto-delete removed resources
      selfHeal: true            # Auto-fix drift
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### 6.2 Multi-Environment with Kustomize
```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
patches:
  - target:
      kind: Deployment
      name: api-server
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 5
      - op: replace
        path: /spec/template/spec/containers/0/envFrom
        value:
          - configMapRef:
              name: api-config-production
```

### 6.3 Flux v2 — GitOps Toolkit
```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: GitRepository
metadata:
  name: api-server
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/company/manifests
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: api-server
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps/api-server/overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: api-server
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: api-server
      namespace: production
```

---

## 7. Service Mesh: Istio, Linkerd, Cilium

### 7.1 Istio — VirtualService & DestinationRule
```yaml
# Canary release — 10% traffic to v3
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-server
spec:
  hosts:
    - api-server
  http:
    - match:
        - sourceLabels:
            version: v3
      route:
        - destination:
            host: api-server
            subset: v3
          weight: 100
    - route:
        - destination:
            host: api-server
            subset: v2
          weight: 90
        - destination:
            host: api-server
            subset: v3
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-server
spec:
  host: api-server
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL         # mTLS between services
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
  subsets:
    - name: v2
      labels:
        version: v2
    - name: v3
      labels:
        version: v3
```

### 7.2 Istio mTLS
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT               # All services require mTLS
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-server
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-server
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/payment-service"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/charges"]
```

### 7.3 Istio Observability
```yaml
# Telemetry API
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  accessLogging:
    - providers:
        - name: envoy
  metrics:
    - overrides:
        - match:
            metric: ALL_METRICS
          tagOverrides:
            response_code:
              value: "response.code"
```

### 7.4 Linkerd vs Istio Decision
```
| Feature              | Istio           | Linkerd         | Cilium         |
|----------------------|-----------------|------------------|----------------|
| Architecture         | Sidecar (Envoy) | Sidecar (Rust)   | eBPF (no sidecar) |
| Performance overhead | 5-10% latency   | 1-3% latency     | < 1% latency    |
| Resource usage       | High (Envoy)    | Low              | Lowest          |
| Feature richness     | Most features   | Core features    | K8s networking |
| mTLS                 | ✅              | ✅               | ✅              |
| Traffic splitting    | ✅ (weight/header)| ✅ (weight)     | ✅              |
| Circuit breaking     | ✅              | ✅               | ✅ (via LB)     |
| Authorization        | ✅ (fine-grained)| ✅ (HTTP methods)| ✅ (network-aware)|
| Observability        | ✅ (Kiali, Grafana)| ✅ (Linkerd-viz) | ✅ (Hubble)     |
| Complexity           | High            | Low              | Medium          |

Choose:
  - Linkerd: small team, want simple zero-trust mTLS with low overhead
  - Istio: need rich traffic management, can handle Envoy's resource usage
  - Cilium: already using Cilium for networking, want eBPF-based security
```

---

## 8. Observability Stack on K8s

### 8.1 Prometheus Stack (kube-prometheus-stack)
```yaml
# Helm values for kube-prometheus-stack
prometheus:
  prometheusSpec:
    retention: 15d
    retentionSize: "50GB"
    resources:
      requests:
        memory: 4Gi
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi
    ruleSelectorNilUsesHelmValues: false
    serviceMonitorSelectorNilUsesHelmValues: false

grafana:
  adminPassword: "from-secret"
  persistence:
    enabled: true
    size: 10Gi
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
        - name: default
          orgId: 1
          folder: ""
          type: file
          disableDeletion: false
          editable: true
          options:
            path: /var/lib/grafana/dashboards/default
  dashboards:
    default:
      kubernetes-cluster:
        gnetId: 315
        revision: 1
      node-exporter:
        gnetId: 1860
        revision: 29

alertmanager:
  config:
    global:
      resolve_timeout: 5m
    route:
      receiver: slack-critical
      routes:
        - match:
            severity: critical
          receiver: pagerduty-critical
        - match:
            severity: warning
          receiver: slack-warning
    receivers:
      - name: pagerduty-critical
        pagerduty_configs:
          - routing_key: "${PAGERDUTY_KEY}"
            severity: critical
      - name: slack-warning
        slack_configs:
          - channel: "#alerts-k8s"
            api_url: "${SLACK_WEBHOOK}"
```

### 8.2 Loki for Log Aggregation
```yaml
# Loki — log aggregation
loki:
  auth_enabled: false
  storage_config:
    boltdb_shipper:
      active_index_directory: /data/loki/index
      cache_location: /data/loki/index_cache
      shared_store: s3
    aws:
      s3: s3://us-east-1/loki-data
      s3forcepathstyle: true
  schema_config:
    configs:
      - from: 2024-01-01
        store: boltdb-shipper
        object_store: s3
        schema: v12
        index:
          prefix: loki_index_
          period: 24h

# Promtail — log agent
promtail:
  config:
    snippets:
      scrapeConfigs:
        - job_name: kubernetes-pods
          pipeline_stages:
            - cri: {}
          kubernetes_sd_configs:
            - role: pod
          relabel_configs:
            - source_labels: [__meta_kubernetes_pod_label_app]
              target_label: app
```

### 8.3 OpenTelemetry Collector on K8s
```yaml
# OpenTelemetry Collector DaemonSet
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel-collector
  namespace: monitoring
spec:
  mode: daemonset
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    processors:
      batch:
        timeout: 1s
        send_batch_size: 8192
      memory_limiter:
        check_interval: 1s
        limit_mib: 512
    exporters:
      prometheus:
        endpoint: 0.0.0.0:8889
      otlp:
        endpoint: tempo.monitoring:4317
        tls:
          insecure: true
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [otlp]
        metrics:
          receivers: [otlp]
          processors: [memory_limiter, batch]
          exporters: [prometheus]
```

---

## 9. Cost Optimization

### 9.1 Resource Right-Sizing
```yaml
# Analyze actual usage vs requests
# Kube-resource-report or kubecost
# Strategy:

# Step 1: Find over-provisioned workloads
kubectl top pods -n production | sort -k 3 -rn

# Step 2: VPA in recommendation mode
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  updatePolicy:
    updateMode: "Off"          # Auto mode = change, Off = recommend
  resourcePolicy:
    containerPolicies:
      - containerName: '*'
        minAllowed:
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:
          cpu: "2"
          memory: "2Gi"

# Step 3: Apply VPA recommendations → update requests/limits
```

### 9.2 Spot Instances
```yaml
# Karpenter: use spot for stateless workloads
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: spot-workers
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot"]
      taints:
        - key: spot
          value: "true"
          effect: NoSchedule  # Only pods with toleration can use spot

# Pod toleration (for stateless services):
tolerations:
  - key: spot
    operator: Equal
    value: "true"
    effect: NoSchedule

# PDB for spot (handle interruptions)
podDisruptionBudget:
  minAvailable: 2
```

### 9.3 Cluster Right-Sizing
```
Strategy:
  1. Overprovision by 20% for bursts (Karpenter autoscaling)
  2. Use ARM (Graviton) for 30-40% cost reduction
  3. Reserved instances for baseline (1yr = ~30% savings, 3yr = ~60%)
  4. Binpack pods efficiently (avoid 10% CPU usage with 1 CPU request)
  5. Hibernate dev/staging clusters on nights and weekends
```

### 9.4 Storage Cost Optimization
```
EBS:
  gp3 vs gp2: gp3 baseline 3000 IOPS free, 20% cheaper
  Snapshots: incremental, use lifecycle policies (monthly, quarterly)

S3:
  Intelligent Tiering for logs with unknown access patterns
  Lifecycle: standard → IA → Glacier (after 90 days)
  Delete unused buckets
```

---

## 10. CNCF Ecosystem & Toolchain Reference

### 10.1 Tool Selection Matrix
```
Orchestration:
  ├── K8s distribution: EKS, GKE, AKS (managed) / kOps, Kubespray (self-managed)
  └── Lightweight: K3s, MicroK8s, Kind (dev/test)

CI/CD:
  ├── GitOps: ArgoCD, Flux
  ├── CI: GitHub Actions, GitLab CI, Tekton
  └── Image build: Kaniko (no Docker socket), BuildKit, ko

Networking:
  ├── CNI: Cilium, Calico, AWS VPC CNI
  ├── Ingress: NGINX Ingress, Traefik, Contour, HAProxy
  └── Gateway API: for multi-team ingress management

Storage:
  ├── CSI: Amazon EBS CSI, Azure Disk CSI, Rook (Ceph)
  ├── Backup: Velero, Kasten K10
  └── Snapshot: VolumeSnapshot via CSI

Security:
  ├── Pod Security: PSA, Kyverno, OPA/Gatekeeper
  ├── Secrets: External Secrets Operator, Sealed Secrets, Vault
  └── Image: Trivy, Sysdig, Falco (runtime security)

Monitoring:
  ├── Metrics: Prometheus, Thanos (long-term), VictoriaMetrics (HA)
  ├── Logs: Loki, Grafana + Loki
  ├── Tracing: Tempo, Jaeger, SigNoz
  └── Dashboards: Grafana, Perses

Service Mesh:
  ├── Full: Istio
  ├── Lightweight: Linkerd
  └── eBPF: Cilium
```

### 10.2 Getting Started with a New Cluster Checklist
```
□ Cluster creation (EKS/GKE/AKS or self-managed)
□ Node groups configured (spot + on-demand)
□ CNI installed (Cilium recommended)
□ Ingress controller installed (NGINX or Gateway API)
□ Cert Manager (auto-TLS with Let's Encrypt)
□ External Secrets Operator
□ Cluster Autoscaler / Karpenter
□ kube-prometheus-stack (Prometheus + Grafana + AlertManager)
□ Loki + Promtail (or Grafana Alloy)
□ ArgoCD / Flux (GitOps)
□ Velero (backup)
□ RBAC configured (least privilege)
□ Network Policies (default deny)
□ Pod Security Standards (baseline or restricted)
□ Container image scanning in CI/CD
□ Cost monitoring (Kubecost or OpenCost)
□ Cross-cluster connectivity (if multi-cluster)
```

### 10.3 Daily/Weekly Ops Checklist
```
Daily:
  □ Prometheus AlertManager acknowledged
  □ Node health (NotReady nodes?)
  □ Pod restarts (CrashLoopBackOff?)
  □ Disk pressure on nodes

Weekly:
  □ Certificate expiry (cert-manager or manual check)
  □ Container image vulnerabilities (new CVEs published?)
  □ Cluster autoscaler events (scale up/down behavior)
  □ Kubernetes version: any patch releases?

Monthly:
  □ Node group health: spot interruptions, node replacement
  □ Resource right-sizing: VPA recommendations reviewed
  □ Cost review: Kubecost dashboard
  □ Backup restore test (Velero)
  □ Audit RBAC: remove unused ServiceAccounts and Roles
  □ Helm chart updates: check for upstream changes
```
