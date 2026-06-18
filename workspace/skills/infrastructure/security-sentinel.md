# Security Sentinel

> Level: Advanced | File: `security-sentinel.md`
> 
> Production-grade security practices: threat modeling, secure coding, dependency scanning,
> secret management, infrastructure hardening, and incident response.

---

## Table of Contents
1. [Threat Modeling](#1-threat-modeling)
2. [Secure Coding — By Layer](#2-secure-coding--by-layer)
3. [OWASP Top 10 Deep Dive](#3-owasp-top-10-deep-dive)
4. [API Security](#4-api-security)
5. [Dependency & Supply Chain Security](#5-dependency--supply-chain-security)
6. [Secrets Management](#6-secrets-management)
7. [Infrastructure Hardening](#7-infrastructure-hardening)
8. [Audit & Compliance](#8-audit--compliance)
9. [Security Incident Response](#9-security-incident-response)
10. [Tool Quick Reference](#10-tool-quick-reference)

---

## 1. Threat Modeling

### 1.1 STRIDE Methodology
| Threat | Property Violated | Example |
|--------|-------------------|---------|
| **S**poofing | Authentication | Attacker impersonates another user |
| **T**ampering | Integrity | Attacker modifies API request in transit |
| **R**epudiation | Non-repudiation | User denies performing an action (no audit log) |
| **I**nformation Disclosure | Confidentiality | API returns password hash in error response |
| **D**enial of Service | Availability | Abusing expensive operation at scale |
| **E**levation of Privilege | Authorization | Regular user accesses admin endpoint |

### 1.2 Threat Modeling Process
```
1. Decompose the system: data flow diagram, trust boundaries
2. Identify threats: STRIDE per component
3. Prioritize: DREAD scoring (Damage, Reproducibility, Exploitability, Affected Users, Discoverability)
4. Mitigate: controls for each threat
5. Validate: penetration test / security review
```

### 1.3 Data Flow Diagram Checklist
```
□ Every external actor is identified (user, admin, 3rd-party service, batch job)
□ Every data store has classification (PII, credentials, logs, public)
□ Every trust boundary is drawn (Internet → WAF → LB → App → DB)
□ Every entry point is documented (endpoint, queue consumer, file ingest)
□ Every exit point is documented (response, callback, webhook, log output)
□ Encryption state is labeled at each step (plaintext → TLS → plaintext in memory → encrypted at rest)
```

---

## 2. Secure Coding — By Layer

### 2.1 Input Validation
```typescript
// ❌ BAD: Direct eval / No validation
const data = JSON.parse(userInput);                    // prototype pollution risk
db.query(`SELECT * FROM users WHERE id = ${userId}`);  // SQL injection

// ✅ GOOD: Schema validation + parameterized queries
import { z } from 'zod';

const OrderSchema = z.object({
  userId: z.string().ulid(),
  amount: z.number().positive().max(1000000),
  items: z.array(z.string()).min(1).max(100),
});

const validated = OrderSchema.parse(req.body);
await db.query('SELECT * FROM orders WHERE user_id = $1', [validated.userId]);
```

### 2.2 Authentication
```typescript
// ✅ JWT Best Practices
const token = jwt.sign(
  { sub: userId, role: 'user' },
  process.env.JWT_SECRET,
  {
    algorithm: 'RS256',           // not HS256 — asymmetric
    expiresIn: '15m',             // short-lived access token
    audience: 'api.example.com',
    issuer: 'auth.example.com',
  }
);

// Refresh token: opaque, stored in DB, HTTP-only cookie
res.cookie('refresh_token', refreshToken, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days
  path: '/api/auth/refresh',
});
```

### 2.3 Authorization (RBAC / ABAC)
```typescript
// ✅ RBAC middleware
function requireRole(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// ✅ ABAC (Attribute-Based Access Control) — check ownership
function requireOwnership(resourceFn: (req: Request) => Promise<{ ownerId: string }>) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const resource = await resourceFn(req);
    if (resource.ownerId !== req.user.sub) {
      return res.status(403).json({ error: 'Not your resource' });
    }
    next();
  };
}
```

### 2.4 IDOR Prevention Checklist
```
□ Every resource access checks ownership via user context (not URL params alone)
□ UUIDs / ULIDs for resource identifiers (never sequential ints)
□ Batch endpoints check ALL items, not just the first one
□ GraphQL field-level authorization (not just query-level)
```

---

## 3. OWASP Top 10 Deep Dive

### A01: Broken Access Control
- **Fix**: Default-deny, server-side authorization check on every endpoint
- **Tool**: OPA (Open Policy Agent) for policy-as-code

### A02: Cryptographic Failures
- **Fix**: 
  - TLS 1.3 mandatory, no ancient ciphers
  - Passwords: bcrypt (cost 12+), Argon2id
  - Encrypt PII at rest (AES-256-GCM)
  - Never roll your own crypto

### A03: Injection
- **Fix**: Parameterized queries always. ORM is NOT sufficient — it can be bypassed with raw() methods
- **Tool**: sqlmap for testing

### A04: Insecure Design
- **Fix**: Rate limiting, request size limits, proper session management
- **Process**: Threat modeling in design review

### A05: Security Misconfiguration
- **Fix**: 
  - Disable directory listing
  - Remove debug endpoints in production
  - Default credentials must be changed
  - CORS: specific origins, never `Access-Control-Allow-Origin: *`

### A06: Vulnerable & Outdated Components
- **Fix**: Automated dependency scanning (Dependabot, Snyk, Renovate)
- **Policy**: Auto-merge patch updates, manual review for minor/major

### A07: Identification & Authentication Failures
- **Fix**: MFA mandatory, rate-limit login attempts, session timeout
- **Anti-pattern**: Self-register → auto-login without email verification

### A08: Software & Data Integrity Failures
- **Fix**: 
  - CI/CD pipeline integrity (signed commits, SBOM)
  - Third-party CDN assets: SRI (Subresource Integrity)
  - Verify checksums on downloaded dependencies

### A09: Security Logging & Monitoring Failures
- **Fix**: 
  - Log all auth events (login success/failure, password change, privilege escalation)
  - Monitor: brute force attempts, unusual API patterns, data exfiltration
  - Centralized SIEM or at minimum structured logs + alert rules

### A10: SSRF (Server-Side Request Forgery)
- **Fix**:
  - Deny-list internal IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
  - Allow-list external URLs only if possible
  - Timeout all outbound requests (5s default)

---

## 4. API Security

### 4.1 Rate Limiting
```yaml
General API:         100 req/min per IP
Authentication:       5 req/min per IP (login, register, password reset)
Data export:         10 req/min per user
Webhook callbacks:  200 req/min per source
```

### 4.2 API Security Headers
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0             # (deprecated but defense-in-depth)
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### 4.3 API Authentication Schemes
| Scheme | Best For | Notes |
|--------|----------|-------|
| **JWT (Bearer token)** | Service-to-service, SPAs | Short expiry (15m), refresh token rotation |
| **API Key** | 3rd-party integrations | Static, must be rotatable |
| **OAuth 2.0 + PKCE** | Public clients (mobile, SPA) | Authorization code flow with PKCE |
| **mTLS** | High-security service mesh | Zero-trust, mutual authentication |
| **HMAC signing** | Idempotent API requests | Prevents replay, verify signature per request |

---

## 5. Dependency & Supply Chain Security

### 5.1 Dependency Scanning Integration (CI)
```yaml
# GitHub Actions — security scan step
- name: Dependency scan
  run: |
    npm audit --audit-level=high     # Node.js
    pip-audit                         # Python
    govulncheck ./...                 # Go
    cargo audit                       # Rust

- name: Container scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: sarif
    severity: CRITICAL,HIGH
    output: trivy-results.sarif

- name: Upload scan results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

### 5.2 SBOM (Software Bill of Materials)
```bash
# Generate SPDX or CycloneDX format
syft packages your-image:latest -o spdx-json > sbom.json

# Store SBOM alongside release artifacts
gh release upload v1.2.3 sbom.json

# Verify against known vulnerabilities
grype sbom.json
```

### 5.3 Dependency Management Policy
```
Patch updates (< 1.0.x → 1.0.y):     Auto-merge via Renovate/Dependabot
Minor updates (1.x → 1.x+1):          Automated PR, requires CI pass
Major updates (1.x → 2.x):            Human review + staging validation
Critical CVEs (CVSS >= 9.0):          Auto-PR, can bypass CI on confirmed fix
```

---

## 6. Secrets Management

### 6.1 Never in Code
```
❌ Hardcoded in source:        process.env.API_KEY = "sk-..."
❌ In config files in repo:    config/production.yaml with password
❌ In Dockerfile as ARG:       ARG DB_PASSWORD
❌ In CI variables as plain:   secrets: PASSWORD=${{ secrets.PASSWORD }}
                              (only if masked — secure by default is fine,
                               but never print or log)
```

### 6.2 Tools Comparison
| Tool | Strongest For | Self-Hosted | Cost |
|------|---------------|-------------|------|
| **HashiCorp Vault** | Dynamic secrets, PKI, multi-cloud | ✅ | Free (OSS) |
| **AWS Secrets Manager** | AWS-native auto-rotation | ❌ (managed) | Pay-per-secret |
| **Google Secret Manager** | GCP-native | ❌ (managed) | Pay-per-secret |
| **Sealed Secrets (Bitnami)** | GitOps-friendly K8s | ✅ | Free |
| **External Secrets Operator** | Sync cloud secrets to K8s | ✅ | Free |
| **1Password Connect** | SMB-friendly | ✅ | Per-seat |

### 6.3 Secret Rotation Strategy
```
Database passwords:         90-day rotation, zero-downtime (dual credentials)
API keys (3rd-party):       On-demand, allow a grace period for old key
JWT signing keys:           180-day rotation, key ID in token header
Encryption keys (AES):      Every 1-3 years unless regulatory mandate says otherwise
TLS certificates:           90-day (Let's Encrypt) or according to CA
```

---

## 7. Infrastructure Hardening

### 7.1 Docker Security
```dockerfile
# ✅ Secure Dockerfile
FROM node:20-alpine AS base
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

FROM base AS build
COPY --chown=appuser:appgroup . .
RUN npm ci --only=production

FROM scratch   # or distroless
COPY --from=build --chown=appuser:appgroup /app /app
USER appuser
ENTRYPOINT ["/app/server"]
```

```yaml
# ✅ Secure Docker Compose / K8s deployment
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  allowPrivilegeEscalation: false
```

### 7.2 Kubernetes Security Checklist
```
□ RBAC enabled with least privilege (no cluster-admin service accounts)
□ Pod Security Standards: restricted (baseline as minimum)
□ NetworkPolicies: default-deny, allow by app label
□ Secrets: not stored in etcd unencrypted (encryption at rest)
□ ServiceMesh: mTLS (Istio/Cilium)
□ Admission Controller: OPA/Gatekeeper or Kyverno for policy enforcement
□ Non-root containers: enforced
□ Image scanning: before deployment (not during)
```

### 7.3 Network Security
```
WAF (Cloudflare/AWS WAF/ModSecurity) → TLS termination → LB → App

─ Ingress:
  - Rate limit per IP
  - Block known malicious IPs (threat intelligence feeds)
  - Request size limits (e.g., 10MB for API, 100MB for file uploads)

─ Egress:
  - Default deny outbound (allow-list only)
  - No direct internet access for database pods
  - DNS filtering for known malware domains
```

---

## 8. Audit & Compliance

### 8.1 Audit Log Standard
```json
{
  "event_id": "evt_abc123",
  "timestamp": "2026-05-02T14:30:00.123Z",
  "actor": {
    "user_id": "usr_789",
    "role": "admin"
  },
  "action": "user.deleted",
  "target": {
    "user_id": "usr_456",
    "email_hash": "sha256$...$..."   // hashed, never raw
  },
  "context": {
    "ip": "203.0.113.1",
    "user_agent": "Mozilla/5.0...",
    "session_id": "sess_xyz"
  },
  "result": "success",
  "metadata": {}
}
```

### 8.2 Compliance Frameworks
| Framework | Key Requirements |
|-----------|-----------------|
| **SOC 2** | Access control, monitoring, encryption, change management, vendor management |
| **ISO 27001** | Risk assessment, security policy, asset management, incident management |
| **PCI-DSS** | Card data encryption, network segmentation, quarterly scans, access logs |
| **GDPR** | Data inventory, retention limits, DPIAs, breach notification (72h), right to deletion |
| **HIPAA** | BAA with providers, access logs, encryption, audit controls, integrity controls |

---

## 9. Security Incident Response

### 9.1 Incident Flow
```
1. Detection (automated alert, user report, partner notification)
2. Triage (severity: SEV-1 data breach / SEV-2 compromise / SEV-3 policy violation)
3. Containment (isolate affected system, revoke credentials, block IPs)
4. Eradication (patch vulnerability, remove backdoor, rotate all exposed secrets)
5. Recovery (restore from clean backup, verify integrity)
6. Postmortem (< 48h for SEV-1, < 7d for others)
```

### 9.2 Communication Templates

**Preliminary notification (internal)**
```
⚠️ SECURITY INCIDENT — PRELIMINARY

What happened: [brief description]
Time detected: [UTC]
Severity: [SEV-1/SEV-2/SEV-3]
Affected: [systems, data, users]
Current action: [containing / investigating / resolved]
Next update: [time + 1h / TBD]
IC: [name]
```

**Data breach notification (external — GDPR 72h)**
```
SUBJECT: Data Security Incident Notification

To Whom It May Concern,

[Company] is notifying you of a data security incident detected on [date].
The incident involved [systems/data]. We have taken the following steps:
1. [Containment actions]
2. [Notification of relevant authorities]
3. [Engaged external forensic team]

The following types of data may have been affected: [PII categories].
We recommend you take the following precautions: [recommendations].

We apologize for this incident and are committed to your data security.

Sincerely,
[DPO/CSO name]
```

### 9.3 Postmortem Template (Security)
```markdown
# Security Incident Postmortem — ID: SEC-2026-XXX

Date: _______________
Severity: SEV-1 / SEV-2 / SEV-3
Duration: ____ hours ____ minutes

## Timeline
| Time (UTC) | Event |
|------------|-------|
|            | Initial detection (source: [alert / report]) |
|            | Triage complete, severity declared |
|            | Containment initiated |
|            | Containment confirmed |
|            | Recovery complete |
|            | Postmortem meeting |

## Root Cause
[3-5 sentences describing the vulnerability or failure]

## Impact
- Systems affected: [list]
- Data exposed: [PII categories / number of records]
- Users affected: [count]
- Financial impact: [if known]

## Action Items
| # | Action | Owner | Due | Status |
|---|--------|-------|-----|--------|
| 1 | Rotate all credentials in affected system | | | |
| 2 | Implement [control] to prevent recurrence | | | |

## Lessons Learned
1. What went well: [e.g., detection worked, team responded fast]
2. What went wrong: [e.g., lack of runbook for this scenario]
3. What to improve: [e.g., faster credential rotation process]
```

---

## 10. Tool Quick Reference

| Category | Tool | Use Case |
|----------|------|----------|
| **SAST** | SonarQube / Semgrep / CodeQL / Checkmarx | Static analysis in CI |
| **DAST** | OWASP ZAP / Burp Suite | Dynamic scanning (pre-prod) |
| **Dependency** | Dependabot / Snyk / Renovate / Trivy / Grype | CVE scanning |
| **Secrets** | GitLeaks / TruffleHog / ggshield | Detect secrets in code |
| **Container** | Trivy / Clair / Anchore / Docker Scout | Image scanning |
| **K8s** | Kube-bench / Kube-hunter / Popeye / Kyverno | Cluster hardening |
| **Cloud** | ScoutSuite / Prowler / CloudSploit | Cloud posture audit |
| **Network** | Nmap / Masscan / Zmap | Port scanning |
| **Pentest** | Metasploit / Cobalt Strike | Red team exercises |
| **IAM** | OPA / Cedar / Casbin | Policy-as-code |

### Installation Quick Reference
```bash
# Trivy — Full image/filesystem/git scanning
brew install trivy
trivy image your-app:latest --severity CRITICAL,HIGH

# GitLeaks — Scan repo for secrets
brew install gitleaks
gitleaks detect --source . -v

# Semgrep — SAST with custom rules
pip install semgrep
semgrep --config=auto .

# OPA — Policy engine
brew install opa
opa eval -d policy.rego "data.playbooks.allow"
```
