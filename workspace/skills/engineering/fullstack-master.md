# Fullstack Master

> Level: Advanced | File: `fullstack-master.md`
> 
> Complete full-stack application design: from API architecture and backend patterns 
> to frontend state management, auth flows, performance optimization, and deployment.

---

## Table of Contents
1. [Application Architecture](#1-application-architecture)
2. [API Design Patterns](#2-api-design-patterns)
3. [Backend Engineering](#3-backend-engineering)
4. [Frontend Engineering](#4-frontend-engineering)
5. [State Management](#5-state-management)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Performance Optimization](#7-performance-optimization)
8. [Testing Strategy](#8-testing-strategy)
9. [Error Handling & Observability](#9-error-handling--observability)
10. [Deployment Architecture](#10-deployment-architecture)

---

## 1. Application Architecture

### 1.1 Monolith-First (then Modular)
```
Start with a well-structured monolith. Extract services when you hit team/code boundaries.

Monolith:                Modular Monolith:           Microservices:
┌─────────────┐         ┌─────┬─────┬─────┐         ┌───┐ ┌───┐ ┌───┐
│ app/         │         │orders│users│pay │         │ord│ │usr│ │pay│
│  orders/     │         │───   │───   │─── │         │ █ │ │ █ │ │ █ │
│  users/      │         │mod  │mod  │mod │         │ █ │ │ █ │ │ █ │
│  payments/   │         └─────┴─────┴─────┘         └───┘ └───┘ └───┘
└─────────────┘         Shared DB/schema              Separate DBs/APIs
Easy to refactor         Good for 3-8 teams            Required for 8+ teams
```

### 1.2 Layer Structure (Clean Architecture)
```
┌─────────────────────────────────────────────────┐
│                Presentation Layer                │  HTTP handlers, GraphQL resolvers, gRPC
├─────────────────────────────────────────────────┤
│                Application Layer                 │  Use cases, DTOs, commands/queries
├─────────────────────────────────────────────────┤
│                   Domain Layer                   │  Entities, value objects, domain events
├─────────────────────────────────────────────────┤
│                Infrastructure Layer              │  Repositories, DB, cache, external APIs
└─────────────────────────────────────────────────┘

Rules:
  - Inner layers know nothing about outer layers (Dependency Inversion)
  - Domain layer has zero imports from frameworks
  - Infrastructure implements interfaces defined in Domain
```

### 1.3 Package Structure (Monorepo)
```
project/
├── apps/
│   ├── web/                # Next.js (frontend)
│   ├── api/                # Node.js/Go/Python (backend API)
│   └── worker/             # Background job processor
├── packages/
│   ├── shared/             # Shared types (TypeScript)
│   ├── db/                 # Database schema & migrations
│   └── config/             # Shared configuration
├── docker-compose.yml
├── turbo.json              # Turborepo (if monorepo)
└── .github/workflows/
```

---

## 2. API Design Patterns

### 2.1 RESTful API Conventions

**URL Structure:**
```
GET    /api/v1/orders              # List orders
POST   /api/v1/orders              # Create order
GET    /api/v1/orders/:id          # Get order
PUT    /api/v1/orders/:id          # Replace order
PATCH  /api/v1/orders/:id          # Partial update
DELETE /api/v1/orders/:id          # Delete order
GET    /api/v1/orders/:id/items    # Sub-resource collection
```

**Standard Response Envelope:**
```typescript
// Success
{
  "data": { ... },
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Order amount exceeds max allowed",
    "details": [
      { "field": "amount", "message": "Max 1000000", "code": "max_exceeded" }
    ],
    "requestId": "req_abc123"
  }
}
```

**Pagination:**
```typescript
// Offset-based (default for small-medium datasets)
GET /api/v1/orders?page=1&pageSize=20

// Cursor-based (for large datasets — stable ordering)
GET /api/v1/orders?cursor=eyJpZCI6MTAwMDAwfQ==&limit=20
// Response:
{
  "data": [...],
  "nextCursor": "eyJpZCI6MTAwMDIwfQ==",
  "hasMore": true
}
```

### 2.2 GraphQL Patterns
```graphql
# Schema design: avoid deeply nested queries (>3 levels)
type Query {
  order(id: ID!): Order
  orders(first: Int, after: String, filter: OrderFilter): OrderConnection
}

type Order {
  id: ID!
  total: Money!
  items: [OrderItem!]!
  user: User!       # ❌ Nested query — consider dataloader pattern
}

# Use connections for pagination (Relay spec)
type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
}
```

### 2.3 API Versioning
```
URL-based:    /api/v1/orders, /api/v2/orders
Header-based: Accept: application/vnd.myapp.v2+json

Rule:
  - V1 stays alive for at least 6 months after V2 deprecation notice
  - Breaking changes only in major version bumps
  - Non-breaking additions are backward-compatible within same version
```

---

## 3. Backend Engineering

### 3.1 Framework Selection Guide
| Stack | Framework | Best For | Performance |
|-------|-----------|----------|-------------|
| Node.js | Fastify | I/O-heavy, real-time | 45k req/s |
| Node.js | Express | Wide ecosystem | 25k req/s |
| Python | FastAPI | ML, data apps | 15k req/s (async) |
| Python | Django | Admin, CMS | 5k req/s |
| Go | Gin / Chi | High throughput | 100k+ req/s |
| Rust | Axum / Actix | Latency-critical | 200k+ req/s |

### 3.2 Request Validation & Error Handling
```typescript
// TypeScript — Fastify with Zod validation
import { z } from 'zod';
import { FastifySchema } from 'fastify';

const CreateOrderSchema: FastifySchema = {
  body: z.object({
    userId: z.string().ulid(),
    items: z.array(z.object({
      productId: z.string().ulid(),
      quantity: z.number().int().positive().max(100),
    })).min(1).max(100),
    coupon: z.string().optional(),
  }),
};

// Global error handler
app.setErrorHandler((error, request, reply) => {
  request.log.error(error, `Request ${request.id} failed`);
  
  if (error.statusCode === 400) {
    return reply.status(400).send({
      error: { code: 'VALIDATION_ERROR', message: error.message }
    });
  }
  if (error.statusCode === 409) {
    return reply.status(409).send({
      error: { code: 'CONFLICT', message: 'Resource already modified' }
    });
  }
  
  // Internal error (500) — don't leak details
  return reply.status(500).send({
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' }
  });
});
```

### 3.3 Background Jobs
```typescript
// BullMQ — Redis-backed job queue
import { Queue, Worker } from 'bullmq';

const orderQueue = new Queue('order-processing');

// Producer
await orderQueue.add('process-payment', { orderId: 'ord_123' }, {
  attempts: 3,
  backoff: { type: 'exponential', delay: 2000 },
});

// Consumer (separate worker process)
const worker = new Worker('order-processing', async job => {
  switch (job.name) {
    case 'process-payment':
      await paymentService.process(job.data.orderId);
      break;
    case 'send-email':
      await emailService.send(job.data);
      break;
  }
}, { concurrency: 10 });
```

---

## 4. Frontend Engineering

### 4.1 Component Architecture
```
Feature-first, not type-first:

components/
├── ui/                    # Primitive components (Button, Input, Modal)
│   ├── Button.tsx
│   ├── Input.tsx
│   └── index.ts           # barrel export
├── features/              # Feature composites
│   ├── OrderList/
│   │   ├── OrderList.tsx
│   │   ├── OrderCard.tsx
│   │   ├── OrderFilters.tsx
│   │   ├── useOrders.ts    # Data fetching hook
│   │   └── index.ts
│   └── CheckoutFlow/
│       ├── CheckoutForm.tsx
│       ├── PaymentSection.tsx
│       └── useCheckout.ts
├── layouts/               # Page layouts
└── shared/                # Cross-feature shared components
```

### 4.2 Data Fetching with TanStack Query
```typescript
// React — TanStack Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch hook
function useOrders(page: number) {
  return useQuery({
    queryKey: ['orders', { page }],
    queryFn: () => fetch(`/api/v1/orders?page=${page}`).then(r => r.json()),
    staleTime: 30_000,              // 30s before refetch
    gcTime: 5 * 60_000,             // Keep in cache for 5 min
    placeholderData: keepPreviousData,  // Smooth pagination
  });
}

// Mutation with optimistic update
function useCreateOrder() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (newOrder) => fetch('/api/v1/orders', {
      method: 'POST',
      body: JSON.stringify(newOrder),
    }),
    onMutate: async (newOrder) => {
      await queryClient.cancelQueries({ queryKey: ['orders'] });
      const previous = queryClient.getQueryData(['orders']);
      // Optimistically add to cache
      queryClient.setQueryData(['orders'], old => ({
        ...old, data: [newOrder, ...(old?.data || [])]
      }));
      return { previous }; // pass to rollback
    },
    onError: (err, newOrder, context) => {
      // Rollback on error
      queryClient.setQueryData(['orders'], context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
}
```

### 4.3 Performance (Frontend)
```typescript
// Dynamic import — lazy load heavy components
const OrderChart = dynamic(() => import('@/features/OrderChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false,  // Client-only if chart library doesn't support SSR
});

// Virtual list for large datasets
import { useVirtualizer } from '@tanstack/react-virtual';

function OrderTable({ orders }: { orders: Order[] }) {
  const parentRef = useRef(null);
  const virtualizer = useVirtualizer({
    count: orders.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map(virtualItem => (
          <div key={virtualItem.key} style={{
            position: 'absolute',
            top: 0,
            transform: `translateY(${virtualItem.start}px)`,
          }}>
            {orders[virtualItem.index].id}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 5. State Management

### 5.1 State Categories
```
Server State: Data persisted on server (orders, users, products)
  → TanStack Query / RTK Query / SWR
  → Cache with stale-while-revalidate pattern

Client State: UI-only data (modal open/close, form draft, selected tab)
  → Zustand / Jotai / Context + useReducer
  → Keep local to feature, avoid global store

URL State: Data encoded in URL (search params, filters, page number)
  → Next.js useSearchParams / react-router useSearchParams
  → Source of truth for sharable app state
```

### 5.2 Zustand (Client State Example)
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
}

// Persist cart to localStorage
const useCartStore = create<CartStore>()(
  persist(
    (set) => ({
      items: [],
      addItem: (item) => set((state) => ({ 
        items: [...state.items, item] 
      })),
      removeItem: (id) => set((state) => ({ 
        items: state.items.filter(i => i.id !== id) 
      })),
      clearCart: () => set({ items: [] }),
    }),
    { name: 'cart-storage' }
  )
);
```

---

## 6. Authentication & Authorization

### 6.1 JWT Auth Flow
```typescript
// Backend — Token creation (Fastify)
app.post('/api/v1/auth/login', async (req, reply) => {
  const { email, password } = req.body;
  const user = await authenticateUser(email, password);
  
  const accessToken = jwt.sign(
    { sub: user.id, role: user.role },
    process.env.JWT_SECRET!,
    { algorithm: 'RS256', expiresIn: '15m' }
  );
  
  const refreshToken = crypto.randomUUID();
  await redis.set(`refresh:${refreshToken}`, user.id, 'EX', 7 * 86400);

  reply.send({
    access_token: accessToken,
    refresh_token: refreshToken,
    expires_in: 900,
  });
});

// Backend — Middleware
async function authMiddleware(req: FastifyRequest) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) throw new Error('Missing token');
  
  try {
    req.user = jwt.verify(token, process.env.JWT_PUBLIC_KEY!);
  } catch {
    throw new Error('Invalid token');
  }
}
```

### 6.2 Frontend Auth Pattern
```typescript
// React — Auth provider
function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // On mount, try to refresh token
    const storedRefreshToken = localStorage.getItem('refreshToken');
    if (storedRefreshToken) {
      fetch('/api/v1/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: storedRefreshToken }),
      })
        .then(res => res.json())
        .then(data => {
          setAccessToken(data.access_token);
          setUser(decodeToken(data.access_token));
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Axios interceptor — auto-refresh on 401
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      response => response,
      async error => {
        if (error.response?.status === 401 && !error.config._retry) {
          error.config._retry = true;
          const newToken = await refreshAccessToken();
          error.config.headers.Authorization = `Bearer ${newToken}`;
          return axios(error.config);
        }
        return Promise.reject(error);
      }
    );
    return () => axios.interceptors.response.eject(interceptor);
  }, []);
}
```

---

## 7. Performance Optimization

### 7.1 Database Level
- Use connection pooling (PgBouncer, max 25-50 connections per service)
- N+1 prevention: eager loading, dataloader patterns
- Covering indexes for read-heavy queries
- Query caching: Redis cache-Aside pattern (TTL 5-60 min for stable data)

### 7.2 API Level
```typescript
// Response compression (Fastify)
import compress from '@fastify/compress';
app.register(compress, { global: true, threshold: 1024 });

// ETag for conditional requests
app.get('/api/v1/products', async (req, reply) => {
  const products = await getProducts();
  const etag = crypto.createHash('md5').update(JSON.stringify(products)).digest('hex');
  
  if (req.headers['if-none-match'] === etag) {
    return reply.status(304).send();              // Not modified
  }
  
  reply.header('ETag', etag);
  return products;
});
```

### 7.3 Frontend Level
```
Bundler:
  - Code splitting by route (Next.js pages automatically)
  - Tree shaking (ESM imports)
  - Bundle analysis: `npx next build` → .next/analyze

Images:
  - Next/Image (auto WebP/AVIF, lazy loading, responsive sizes)
  - CDN: Cloudflare/Imgix for transformations

CSS:
  - Tailwind CSS (purges unused styles in production)
  - CSS-in-JS runtime impact: consider zero-runtime (Linaria, Panda CSS)

Fonts:
  - next/font (auto-optimized, self-hosted, no FOIT)
  - Subset fonts to used characters (Google Fonts subsetting)
```

---

## 8. Testing Strategy

### 8.1 Testing Trophy (not pyramid)
```
Frontend:
  ┌─────────────────────────┐
  │   E2E (Cypress/Playwright)  │  Critical user flows (10-15 tests)
  ├─────────────────────────┤
  │ Integration (React Testing Lib) │  Component + hook behavior (majority)
  ├─────────────────────────┤
  │ Unit (Vitest)                 │  Pure logic, utilities (minimal)
  └─────────────────────────┘

Backend:
  ┌─────────────────────────┐
  │ Contract / E2E              │  Provider verification, smoke tests
  ├─────────────────────────┤
  │ Integration                  │  Route handler + DB (supertest + test DB)
  ├─────────────────────────┤
  │ Unit                         │  Business logic, pure functions
  └─────────────────────────┘
```

### 8.2 Integration Test Example (Backend)
```typescript
// Fastify + test DB
import { buildApp } from '@/app';
import { createTestUser, createTestOrder } from './helpers';

describe('POST /api/v1/orders', () => {
  let app: FastifyInstance;
  
  beforeAll(async () => {
    app = await buildApp({ testing: true });
    await app.ready();
  });
  
  afterAll(async () => {
    await app.close();
  });

  it('creates an order successfully', async () => {
    const user = await createTestUser();
    
    const response = await app.inject({
      method: 'POST',
      url: '/api/v1/orders',
      headers: { Authorization: `Bearer ${user.token}` },
      payload: {
        items: [{ productId: 'prod_1', quantity: 2 }],
      },
    });
    
    expect(response.statusCode).toBe(201);
    const body = JSON.parse(response.payload);
    expect(body.data.id).toBeDefined();
    expect(body.data.total).toBeGreaterThan(0);
  });
  
  it('rejects orders with negative quantity', async () => {
    // ... validation test
  });
});
```

---

## 9. Error Handling & Observability

### 9.1 Error Taxonomy
```typescript
// Domain errors (predictable business logic failures)
class DomainError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message);
    this.name = 'DomainError';
  }
}

class InsufficientInventoryError extends DomainError {
  constructor(productId: string) {
    super(`Insufficient inventory for product ${productId}`, 'INSUFFICIENT_INVENTORY');
  }
}

class OrderNotFoundError extends DomainError {
  constructor(orderId: string) {
    super(`Order ${orderId} not found`, 'ORDER_NOT_FOUND', 404);
  }
}
```

### 9.2 Full-Stack Error Boundary
```typescript
// Frontend — Global error boundary + toast
function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <pre>{process.env.NODE_ENV === 'development' ? error.message : ''}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

// Backend — Structured error response
app.setErrorHandler((error, request, reply) => {
  if (error instanceof DomainError) {
    return reply.status(error.statusCode).send({
      error: { code: error.code, message: error.message }
    });
  }
  
  // Log full trace for internal errors
  request.log.error({ err: error, requestId: request.id }, 'Unhandled error');
  return reply.status(500).send({
    error: { code: 'INTERNAL_ERROR', message: 'Unexpected error', requestId: request.id }
  });
});
```

---

## 10. Deployment Architecture

### 10.1 Canonical Production Setup
```
Internet ──→ Cloudflare ──→ Load Balancer (ALB/NGINX) ──→ API Service (multi-AZ)
                  │                                                │
                  ↓                                                ↓
            CDN (static assets)                              PostgreSQL (RDS Multi-AZ)
                                                             Redis (ElastiCache)
                                                             Queue (SQS/BullMQ)
```

### 10.2 Dockerfile (Production Multi-Stage)
```dockerfile
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=build --chown=nextjs:nodejs /app/public ./public
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "server.js"]
```

### 10.3 Docker Compose (Local Dev)
```yaml
version: '3.8'
services:
  api:
    build:
      context: .
      target: deps
    command: npm run dev
    volumes:
      - .:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://app:pass@db:5432/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```
