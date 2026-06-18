# Clean Architecture

> Level: Advanced | File: `clean-architecture.md`
> 
> Practical application of Clean Architecture, Hexagonal Architecture, and Domain-Driven Design 
> across TypeScript, Go, Python, and Java/Spring ecosystems.

---

## Table of Contents
1. [Core Principles](#1-core-principles)
2. [Architecture Layers](#2-architecture-layers)
3. [The Dependency Rule](#3-the-dependency-rule)
4. [Hexagonal (Ports & Adapters)](#4-hexagonal-ports--adapters)
5. [Implementation in TypeScript](#5-implementation-in-typescript)
6. [Implementation in Go](#6-implementation-in-go)
7. [Implementation in Python](#7-implementation-in-python)
8. [Domain-Driven Design Integration](#8-domain-driven-design-integration)
9. [Enforcing Boundaries](#9-enforcing-boundaries)
10. [Testing Strategy](#10-testing-strategy)

---

## 1. Core Principles

```
1. Independence of Frameworks
   - The architecture does not depend on the existence of any framework
   - Framework = tool, not constraint

2. Testability
   - Business rules can be tested without UI, database, or external services

3. Independence of UI
   - The UI can change without changing the business rules
   - Web UI, CLI, REST API are all interchangeable delivery mechanisms

4. Independence of Database
   - You can swap PostgreSQL for MongoDB (or file-based storage)
   - Database is a detail, not a foundation

5. Independence of External Systems
   - Business rules know nothing about the outside world
   - External services are abstracted behind interfaces
```

---

## 2. Architecture Layers

### 2.1 Classical Clean Architecture (Uncle Bob)

```
┌──────────────────────────────────────────────────────┐
│                    Frameworks & Drivers                 │  Outer ring
│   Web, DB, Device, UI, External APIs                  │
│                                                        │
│  ┌────────────────────────────────────────────────┐   │
│  │              Interface Adapters                   │   │
│  │   Controllers, Presenters, Gateways              │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │          Application / Use Cases           │   │   │
│  │  │   Request/Response models, Interactors     │   │   │
│  │  │                                              │   │   │
│  │  │  ┌────────────────────────────────────┐   │   │   │
│  │  │  │        Enterprise Business Rules     │   │   │   │
│  │  │  │   Entities, Value Objects            │   │   │   │
│  │  │  │   Domain Events                       │   │   │   │
│  │  │  └────────────────────────────────────┘   │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Contains | Knows About | Testable Without |
|-------|----------|-------------|------------------|
| **Domain (Entity)** | Entities, Value Objects, Domain Events, Business Rules | Nothing | Everything |
| **Application (Use Case)** | Interactors, DTOs, Repository Interfaces | Domain | DB, UI, Framework |
| **Interface Adapters** | Controllers, Presenters, Gateways | Application | DB (can mock), UI routing |
| **Frameworks & Drivers** | HTTP handlers, ORM, Queue consumers | Interface Adapters | Integration tests |

### 2.3 Package Structure (TypeScript)
```
src/
├── domain/
│   ├── entities/
│   │   ├── Order.ts
│   │   └── User.ts
│   ├── value-objects/
│   │   ├── Money.ts
│   │   ├── OrderStatus.ts
│   │   └── Email.ts
│   ├── events/
│   │   └── OrderCreatedEvent.ts
│   └── services/
│       └── PricingService.ts          # pure domain logic only
│
├── application/
│   ├── ports/                          # interfaces (driven ports)
│   │   ├── OrderRepository.ts
│   │   ├── PaymentGateway.ts
│   │   └── UserRepository.ts
│   ├── use-cases/
│   │   ├── CreateOrderUseCase.ts
│   │   ├── CancelOrderUseCase.ts
│   │   └── GetOrderUseCase.ts
│   └── dto/
│       ├── CreateOrderRequest.ts
│       └── OrderResponse.ts
│
├── infrastructure/
│   ├── persistence/
│   │   ├── PostgresOrderRepository.ts  # implements port
│   │   └── InMemoryOrderRepository.ts  # for testing
│   ├── http/
│   │   ├── FastifyOrderController.ts
│   │   └── OrderRoutes.ts
│   ├── payment/
│   │   └── StripePaymentGateway.ts
│   └── config/
│       └── container.ts                # DI wiring
│
└── main.ts                             # composition root
```

---

## 3. The Dependency Rule

### 3.1 The Rule in One Sentence
> **Source code dependencies can only point inward. Nothing in an inner circle can know about something in an outer circle.**

```
Outer (Framework) → Inner (Domain)
  Adapters → core
  DB/HTTP → Application port
  Application → Domain interfaces
  Domain → nothing
```

### 3.2 What Inversion Looks Like in Code
```typescript
// ❌ VIOLATION: Domain depends on Infrastructure
// domain/entities/Order.ts
import { Database } from '../infrastructure/database/Database';  // OUTER layer imported!
export class Order {
  save() {
    Database.save(this);  // coupling to infrastructure detail
  }
}

// ✅ CORRECT: Inversion of Control
// domain/entities/Order.ts — NO infrastructure imports
export class Order {
  constructor(
    public id: string,
    public userId: string,
    public amount: Money,
    public status: OrderStatus
  ) {}
  
  // Pure domain logic — no side effects
  cancel(): void {
    if (this.status === OrderStatus.SHIPPED) {
      throw new Error('Cannot cancel shipped order');
    }
    this.status = OrderStatus.CANCELLED;
    // Domain event — handler is in outer layer
  }
}

// infrastructure/persistence/PostgresOrderRepository.ts
// Implements the PORT defined in application layer
export class PostgresOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    await db.query('INSERT INTO orders ...');
  }
}
```

### 3.3 Crossing Boundaries
```
Controller (outer) → UseCase (inner)
  |                    |
  calls →              ← returns response DTO
  |                    |
  MUST use simple data structures (no framework types)

Bad:
  controller.send(Response.status(200).json(data));  // Framework type crosses boundary

Good:
  const response = await useCase.execute(request);   // Plain object
  controller.send(response);                          // Framework code stays in adapter
```

---

## 4. Hexagonal (Ports & Adapters)

### 4.1 Visual
```
        ┌───────────────────────────────────────┐
        │          Primary Adapters               │
        │   (Driving — initiate the call)        │
        │                                         │
        │   REST Controller ──┐                   │
        │   CLI ──────────────┤──→ Use Case       │
        │   GraphQL ──────────┘   (inbound port)  │
        └───────────────────────┬───────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │    Application Core    │
                    │  (Use Cases, Domain)   │
                    └───────────┬───────────┘
                                │
        ┌───────────────────────┴───────────────────┐
        │          Secondary Adapters                │
        │   (Driven — called by the core)           │
        │                                            │
        │   OrderRepository ──→ PostgresAdapter     │
        │   PaymentGateway ────→ StripeAdapter       │
        │   NotificationService → SQSAdapter        │
        └────────────────────────────────────────────┘
```

### 4.2 Port Definitions (Interfaces in Application Layer)
```typescript
// application/ports/OrderRepository.ts
export interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  findByUserId(userId: string, page: number): Promise<Order[]>;
  save(order: Order): Promise<void>;
  update(order: Order): Promise<void>;
  delete(id: string): Promise<void>;
  countByUserId(userId: string): Promise<number>;
}

// application/ports/PaymentGateway.ts
export interface PaymentGateway {
  charge(amount: Money, sourceId: string): Promise<ChargeResult>;
  refund(chargeId: string): Promise<RefundResult>;
}

export type ChargeResult = 
  | { status: 'success'; chargeId: string }
  | { status: 'declined'; reason: string }
  | { status: 'error'; message: string };
```

---

## 5. Implementation in TypeScript

### 5.1 Use Case (Application Layer)
```typescript
// application/use-cases/CreateOrderUseCase.ts
export class CreateOrderUseCase {
  constructor(
    private readonly orderRepo: OrderRepository,
    private readonly productRepo: ProductRepository,
    private readonly paymentGateway: PaymentGateway,
    private readonly eventBus: EventBus
  ) {}

  async execute(request: CreateOrderRequest): Promise<OrderResponse> {
    // 1. Validate products exist and have inventory
    const products = await this.productRepo.findByIds(
      request.items.map(i => i.productId)
    );
    
    // 2. Calculate total
    const lineItems = request.items.map(item => {
      const product = products.find(p => p.id === item.productId);
      if (!product) throw new ProductNotFoundError(item.productId);
      return new LineItem(product, item.quantity);
    });
    const total = Money.sum(lineItems.map(li => li.subtotal));
    
    // 3. Create domain entity
    const order = new Order(
      generateId(),
      request.userId,
      lineItems,
      total,
      OrderStatus.PENDING
    );
    
    // 4. Charge payment
    const charge = await this.paymentGateway.charge(
      total,
      request.paymentSourceId
    );
    if (charge.status === 'declined') {
      throw new PaymentDeclinedError(charge.reason);
    }
    
    // 5. Mark order as paid
    order.markAsPaid(charge.chargeId);
    
    // 6. Save
    await this.orderRepo.save(order);
    
    // 7. Publish event
    await this.eventBus.publish(new OrderCreatedEvent(order.id, order.userId));
    
    return OrderResponse.fromDomain(order);
  }
}
```

### 5.2 Dependency Injection (Composition Root)
```typescript
// infrastructure/config/container.ts
import { createContainer, asClass, asFunction } from 'awilix';

const container = createContainer();

container.register({
  // Use cases
  createOrderUseCase: asClass(CreateOrderUseCase),
  cancelOrderUseCase: asClass(CancelOrderUseCase),
  
  // Repositories (ports → adapters)
  orderRepository: asClass(PostgresOrderRepository).singleton(),
  productRepository: asClass(RedisProductRepository).singleton(),
  
  // Gateways
  paymentGateway: asClass(StripePaymentGateway).singleton(),
  eventBus: asClass(KafkaEventBus).singleton(),
});

export { container };
```

---

## 6. Implementation in Go

### 6.1 Package Structure
```
internal/
├── domain/
│   ├── order.go         # entity + value objects
│   ├── user.go
│   ├── money.go         # value object
│   └── errors.go        # domain errors
├── application/
│   ├── port/
│   │   ├── repository.go    # interfaces
│   │   └── gateway.go       # interfaces
│   └── usecase/
│       ├── create_order.go
│       └── cancel_order.go
├── infrastructure/
│   ├── persistence/
│   │   └── postgres_order_repo.go
│   ├── payment/
│   │   └── stripe_gateway.go
│   └── di/
│       └── wire.go          # google/wire DI
└── api/
    └── handler/
        └── order_handler.go  # HTTP adapter
```

### 6.2 Domain Entity (Go)
```go
// internal/domain/order.go
package domain

import (
    "errors"
    "time"
)

type OrderStatus string

const (
    OrderStatusPending   OrderStatus = "pending"
    OrderStatusPaid      OrderStatus = "paid"
    OrderStatusShipped    OrderStatus = "shipped"
    OrderStatusCancelled OrderStatus = "cancelled"
)

type Order struct {
    ID        string
    UserID    string
    Items     []OrderItem
    Total     Money
    Status    OrderStatus
    ChargeID  string
    CreatedAt time.Time
}

func (o *Order) Cancel() error {
    if o.Status == OrderStatusShipped {
        return errors.New("cannot cancel shipped order")
    }
    if o.Status == OrderStatusCancelled {
        return errors.New("order already cancelled")
    }
    o.Status = OrderStatusCancelled
    return nil
}

func (o *Order) MarkAsPaid(chargeID string) error {
    if o.Status != OrderStatusPending {
        return errors.New("cannot pay non-pending order")
    }
    o.ChargeID = chargeID
    o.Status = OrderStatusPaid
    return nil
}
```

### 6.3 Port Interface (Go)
```go
// internal/application/port/repository.go
package port

import "example/internal/domain"

type OrderRepository interface {
    FindByID(ctx context.Context, id string) (*domain.Order, error)
    FindByUserID(ctx context.Context, userID string, page, pageSize int) ([]*domain.Order, error)
    Save(ctx context.Context, order *domain.Order) error
    Update(ctx context.Context, order *domain.Order) error
}
```

---

## 7. Implementation in Python

### 7.1 Package Structure
```
src/
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── order.py
│   │   └── user.py
│   ├── value_objects/
│   │   ├── money.py
│   │   └── order_status.py
│   └── events/
│       └── order_events.py
├── application/
│   ├── ports/
│   │   ├── order_repository.py     # ABC
│   │   └── payment_gateway.py      # ABC
│   └── use_cases/
│       ├── __init__.py
│       ├── create_order.py
│       └── cancel_order.py
├── infrastructure/
│   ├── persistence/
│   │   ├── postgres_order_repo.py
│   │   └── in_memory_order_repo.py
│   ├── payment/
│   │   └── stripe_gateway.py
│   └── di/
│       └── container.py
└── api/
    ├── fastapi_app.py
    └── routes/
        └── order_routes.py
```

### 7.2 Domain Entity with Validation (Python)
```python
# src/domain/value_objects/money.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int    # cents
    currency: str  # ISO 4217
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be ISO 4217 format")
    
    @classmethod
    def from_decimal(cls, amount: float, currency: str = "USD") -> "Money":
        return cls(amount=int(round(amount * 100)), currency=currency)
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
```

### 7.3 Use Case with DI (Python)
```python
# src/application/use_cases/create_order.py
from dataclasses import dataclass

@dataclass
class CreateOrderRequest:
    user_id: str
    items: list[dict]
    payment_source_id: str

class CreateOrderUseCase:
    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        payment_gateway: PaymentGateway,
        event_bus: EventBus,
    ):
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._payment_gateway = payment_gateway
        self._event_bus = event_bus
    
    async def execute(self, request: CreateOrderRequest) -> OrderResponse:
        # ... same logic as TypeScript version
        pass
```

---

## 8. Domain-Driven Design Integration

### 8.1 Bounded Contexts
```
E-commerce bounded contexts:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Ordering    │  │   Inventory  │  │    Shipping   │
│              │  │              │  │              │
│  Order       │  │  Stock       │  │  Shipment    │
│  LineItem    │  │  Warehouse   │  │  Tracking    │
│  Payment     │  │  Supplier    │  │  Carrier     │
└──────────────┘  └──────────────┘  └──────────────┘

Each context has its own:
  - Ubiquitous Language (terms specific to that domain)
  - Domain model (entities, value objects may differ across contexts)
  - Data store (no shared DB)
  - Clean Architecture (independent layers)
```

### 8.2 Aggregates
```
Aggregate: A cluster of domain objects treated as a unit

Order (Aggregate Root)
├── id: string
├── user_id: string
├── items: OrderItem[]     (Value Objects, accessed via Order)
├── status: OrderStatus    (Value Object)
├── total: Money           (Value Object)
└── events: DomainEvent[]  (collected for dispatch)

Rules:
  - External references to the aggregate go through the root (Order)
  - Invariants are enforced at the aggregate boundary
  - Transactions span only one aggregate (not multiple)
```

### 8.3 Domain Events
```typescript
// domain/events/OrderCreatedEvent.ts
export class OrderCreatedEvent {
  constructor(
    public readonly orderId: string,
    public readonly userId: string,
    public readonly amount: Money,
    public readonly timestamp: Date = new Date()
  ) {}
}

// In the entity:
export class Order {
  private events: DomainEvent[] = [];
  
  markAsPaid(chargeId: string): void {
    this.events.push(new OrderPaidEvent(this.id, chargeId));
  }
  
  // Called by repository after save
  popEvents(): DomainEvent[] {
    const events = [...this.events];
    this.events = [];
    return events;
  }
}
```

---

## 9. Enforcing Boundaries

### 9.1 Compile-Time Checks
```json
// TypeScript — no outer-layer imports in domain
// tsconfig.json — per-layer tsconfigs
{
  "compilerOptions": {
    "paths": {
      "@domain/*": ["./src/domain/*"],
      "@application/*": ["./src/application/*"],
      "@infrastructure/*": ["./src/infrastructure/*"]
    }
  }
}
```

### 9.2 Import Linting with ESLint
```javascript
// .eslintrc.js — enforce clean architecture boundaries
module.exports = {
  overrides: [
    {
      files: ['src/domain/**/*.ts'],
      rules: {
        'no-restricted-imports': [
          'error',
          {
            patterns: [
              '@application/*',   // Domain can't see up
              '@infrastructure/*',
              '@api/*',
            ],
          },
        ],
      },
    },
    {
      files: ['src/application/**/*.ts'],
      rules: {
        'no-restricted-imports': [
          'error',
          {
            patterns: [
              '@infrastructure/*',  // Application can't see infrastructure
              '@api/*',
            ],
          },
        ],
      },
    },
  ],
};
```

### 9.3 Testing Boundaries
```typescript
// ✅ Domain tests — no mock, pure logic
describe('Order Entity', () => {
  it('prevents cancellation of shipped orders', () => {
    const order = createShippedOrder();
    expect(() => order.cancel()).toThrow('Cannot cancel shipped order');
  });
});

// ✅ Application tests — mocked ports
describe('CreateOrderUseCase', () => {
  it('creates order and charges payment', async () => {
    const orderRepo = new InMemoryOrderRepository();     // Not mocked!
    const paymentGateway = { charge: vi.fn() };           // Port mock
    const eventBus = { publish: vi.fn() };
    
    const useCase = new CreateOrderUseCase(orderRepo, productRepo, paymentGateway, eventBus);
    const result = await useCase.execute(request);
    
    expect(paymentGateway.charge).toHaveBeenCalled();
    expect(result.id).toBeDefined();
  });
});
```

---

## 10. Testing Strategy

### 10.1 Testing Pyramid in Clean Architecture
```
                ┌─────┐
                │ E2E │  Smoke tests: deploy and verify against staging
               ┌┴─────┴┐
               │Integration│  Test adapters with real DB/API
              ┌┴─────────┴┐
              │Application │  Use case tests with port mocks
             ┌┴───────────┴┐
             │   Domain     │  Pure unit tests — fastest, most valuable
             └─────────────┘
```

| Layer | Test Type | Mock? | Speed | Coverage Target |
|-------|-----------|-------|-------|-----------------|
| Domain | Unit (Vitest/Jest/JUnit) | Nothing | Instant | 100% |
| Application | Unit + Integration | Port interfaces | Fast | 95% |
| Interface Adapters | Integration | Port implementations | Medium | 80% |
| Infrastructure | Integration | Real DB/file | Slow | 70% |

### 10.2 In-Memory Repositories for Testing
```typescript
// infrastructure/persistence/InMemoryOrderRepository.ts
export class InMemoryOrderRepository implements OrderRepository {
  private orders = new Map<string, Order>();
  
  async findById(id: string): Promise<Order | null> {
    return this.orders.get(id) ?? null;
  }
  
  async save(order: Order): Promise<void> {
    this.orders.set(order.id, order);
  }
  
  // Pop events after save (simulates real repository behavior)
  getAndClearEvents(): DomainEvent[] {
    const events: DomainEvent[] = [];
    for (const order of this.orders.values()) {
      events.push(...order.popEvents());
    }
    return events;
  }
}
```

### 10.3 Port Mocking Without a Framework
```typescript
// Simple manual mock (no external mocking library needed)
const mockPaymentGateway: PaymentGateway = {
  charge: vi.fn().mockResolvedValue({
    status: 'success',
    chargeId: 'ch_abc123',
  }),
  refund: vi.fn().mockResolvedValue({
    status: 'success',
  }),
};

// Tests are fast, focused, and framework-independent
```
