# Refactoring Patterns

> Level: Advanced | File: `refactoring-patterns.md`
> 
> Systematic code improvement without changing behavior: from Martin Fowler's catalog
> to production-scale patterns for legacy code, large-scale migration, and continuous refactoring.

---

## Table of Contents
1. [Refactoring Mindset](#1-refactoring-mindset)
2. [Working with Legacy Code](#2-working-with-legacy-code)
3. [Composing Methods](#3-composing-methods)
4. [Moving Features Between Objects](#4-moving-features-between-objects)
5. [Organizing Data](#5-organizing-data)
6. [Simplifying Conditional Logic](#6-simplifying-conditional-logic)
7. [Making Method Calls Simpler](#7-making-method-calls-simpler)
8. [Dealing with Generalization](#8-dealing-with-generalization)
9. [Large-Scale Refactoring Patterns](#9-large-scale-refactoring-patterns)
10. [Refactoring and Testing](#10-refactoring-and-testing)

---

## 1. Refactoring Mindset

### 1.1 The Two Hats
> "When you add function, you shouldn't be refactoring. When you refactor, you shouldn't be adding function."

```
Hat 1: Adding functionality
  - Write new code
  - Add tests for new features
  - You can change existing tests if API behavior changes (rare)

Hat 2: Refactoring
  - Improve code structure
  - DO NOT change any observable behavior
  - Existing tests must all pass without modification
```

### 1.2 When to Refactor
```
✅ The Rule of Three: "When you do something similar three times, refactor"
✅ When adding a feature: clean up to make the feature easier to add
✅ When fixing a bug: clarify the code first, then fix the bug
✅ During code review: suggest refactoring for clarity, not style
✅ Before a major change: prepare the code for the coming change

❌ Don't refactor to:
  - Show off ("Look, I can do it in 3 lines!")
  - Apply the latest trendy pattern without reason
  - Fix something that's not broken (unless it blocks a feature)
  - In a rush (one refactor at a time, test between each)
```

### 1.3 Signs You Shouldn't Refactor
```
❌ The code will be replaced soon anyway (and it works)
❌ The code is in a legacy system with zero tests (write tests first)
❌ The refactoring has no clear benefit (code works, is readable enough)
❌ The code is from a library you don't control
❌ The refactoring would take longer than the feature itself
```

---

## 2. Working with Legacy Code

### 2.1 The Legacy Code Dilemma
> "Code without tests is bad code." — Michael Feathers

```
Working Effectively with Legacy Code:
  Before you can refactor legacy code:
  1. Find the seams — places where you can inject testability
  2. Write characterization tests — verify current behavior
  3. Refactor to add testability
  4. Write unit tests
  5. Now you can safely refactor
```

### 2.2 Seam Types

| Seam Type | Description | Example |
|-----------|-------------|---------|
| **Preprocessing** | Conditional compilation | `#ifdef TESTING` |
| **Link/Compile** | Swap library at link time | Dependency injection framework |
| **Object** | Override method in subclass | Testable subclass overrides |
| **Static method** | Replace static call | Extract interface from static method |

### 2.3 Sprout Method / Sprout Class

```
Sprout Method: When you need to add a new behavior to legacy code

// BAD: Add new code inside the existing method
function processOrder(order) {
  // ... 200 lines of existing legacy code ...
  // ... hard to understand ...
  
  // NEW: validate coupon (mixed with legacy)
  if (order.coupon && !validateCoupon(order.coupon)) {
    throw new Error('Invalid coupon');
  }
  
  // ... more legacy code ...
}

// GOOD: Sprout a new method
function processOrder(order) {
  validateCouponOrThrow(order.coupon);
  // ... 200 lines of existing legacy code (untouched) ...
}

function validateCouponOrThrow(coupon) {
  if (coupon && !validateCoupon(coupon)) {
    throw new Error('Invalid coupon');
  }
}
```

### 2.4 Characterization Tests
```typescript
// Write these BEFORE refactoring legacy code
describe('LegacyOrderProcessor (characterization)', () => {
  it('processes a valid order', () => {
    const input = { id: '1', items: [{ product: 'A', qty: 2 }] };
    const result = orderProcessor.process(input);
    // Capture actual output, not expected
    expect(result.total).toBe(2998);     // Observed value from running it
    expect(result.status).toBe('pending'); // Observed value
  });
  
  it('throws on invalid coupon', () => {
    const input = { id: '2', items: [], coupon: 'INVALID' };
    expect(() => orderProcessor.process(input)).toThrow();
  });
});
```

---

## 3. Composing Methods

### 3.1 Extract Method

```typescript
// ❌ Before: all logic in one block
function printOwing(invoice) {
  let outstanding = 0;
  console.log('******************');
  console.log('* Customer Owes *');
  console.log('******************');
  for (const o of invoice.orders) outstanding += o.amount;
  const today = new Date();
  invoice.dueDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 30);
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
  console.log(`due: ${invoice.dueDate.toLocaleDateString()}`);
}

// ✅ After: extracted to smaller methods
function printOwing(invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  recordDueDate(invoice);
  printDetails(invoice, outstanding);
}

function printBanner() {
  console.log('******************');
  console.log('* Customer Owes *');
  console.log('******************');
}

function calculateOutstanding(invoice): number {
  return invoice.orders.reduce((sum, o) => sum + o.amount, 0);
}

function recordDueDate(invoice) {
  const today = new Date();
  invoice.dueDate = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 30);
}
```

### 3.2 Inline Method

```typescript
// ❌ Before: method adds no value
function getRating(driver) {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}
function moreThanFiveLateDeliveries(driver) {
  return driver.numberOfLateDeliveries > 5;
}

// ✅ After: inline the trivial method
function getRating(driver) {
  return driver.numberOfLateDeliveries > 5 ? 2 : 1;
}
```

### 3.3 Extract Variable / Inline Temp

```typescript
// ❌ Before: inline expression repeated
if (order.basePrice > 1000 && order.basePrice > 500) {
  return order.basePrice * 0.95;
} else {
  return order.basePrice * 0.98;
}

// ✅ After: extracted variable
const basePrice = order.basePrice;
if (basePrice > 1000) {
  return basePrice * 0.95;
} else {
  return basePrice * 0.98;
}

// Inline Temp (opposite): when temp adds no value
// ❌ Before:
const basePrice = order.basePrice;
return basePrice > 1000;
// ✅ After:
return order.basePrice > 1000;
```

### 3.4 Replace Temp with Query

```typescript
// ❌ Before
const quantity = order.quantity;
const itemPrice = order.itemPrice;
const basePrice = quantity * itemPrice;
const quantityDiscount = Math.max(0, quantity - 500) * itemPrice * 0.05;
const shipping = basePrice > 1000 ? 0 : quantity * 10;
return basePrice - quantityDiscount + shipping;

// ✅ After
function getPrice(order) {
  return basePrice(order) - quantityDiscount(order) + shipping(order);
}
function basePrice(order) { return order.quantity * order.itemPrice; }
function quantityDiscount(order) {
  return Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
}
function shipping(order) {
  return basePrice(order) > 1000 ? 0 : order.quantity * 10;
}
```

---

## 4. Moving Features Between Objects

### 4.1 Move Method

```typescript
// ❌ Before: method on wrong class
class Order {
  get daysOverdue(): number {
    // Uses customer's payment terms to calculate
    const terms = this.customer.paymentTerms;
    return Math.floor((Date.now() - this.dueDate.getTime()) / (1000 * 86400));
  }
}

// ✅ After: method lives on the data it primarily uses
class Order {
  get daysOverdue(): number {
    return this.customer.calculateDaysOverdue(this.dueDate);
  }
}

class Customer {
  calculateDaysOverdue(dueDate: Date): number {
    return Math.floor((Date.now() - dueDate.getTime()) / (1000 * 86400));
  }
}
```

### 4.2 Extract Class

```typescript
// ❌ Before: class doing too much
class Person {
  name: string;
  officeAreaCode: string;
  officeNumber: string;
  get telephoneNumber(): string {
    return `(${this.officeAreaCode}) ${this.officeNumber}`;
  }
}

// ✅ After: extracted Phone class
class Person {
  name: string;
  officePhone: Phone;
  get telephoneNumber(): string {
    return this.officePhone.toString();
  }
}

class Phone {
  constructor(public areaCode: string, public number: string) {}
  
  toString(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
```

### 4.3 Introduce Foreign Method / Local Extension

```typescript
// ❌ Before: repeated utility code
function formatDate(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

// ✅ After: extension method (TypeScript)
declare global {
  interface Date {
    toISOShort(): string;
  }
}

Date.prototype.toISOShort = function(): string {
  return `${this.getFullYear()}-${pad(this.getMonth() + 1)}-${pad(this.getDate())}`;
};
```

---

## 5. Organizing Data

### 5.1 Self Encapsulate Field

```typescript
// ❌ Before: direct field access (hard to add behavior later)
class Order {
  private _quantity: number;
  private _itemPrice: number;
  
  getPrice(): number {
    return this._quantity * this._itemPrice;
  }
}

// ✅ After: access through getter (easier to add discount later)
class Order {
  private _quantity: number;
  private _itemPrice: number;
  
  get quantity(): number { return this._quantity; }
  get itemPrice(): number { return this._itemPrice; }
  
  getPrice(): number {
    return this.basePrice - this.quantityDiscount + this.shipping;
  }
  
  private get basePrice(): number { return this.quantity * this.itemPrice; }
  private get quantityDiscount(): number {
    return Math.max(0, this.quantity - 500) * this.itemPrice * 0.05;
  }
  private get shipping(): number {
    return this.basePrice > 1000 ? 0 : this.quantity * 10;
  }
}
```

### 5.2 Replace Type Code with Class / Subclasses

```typescript
// ❌ Before: type code as string/number
type OrderType = 'standard' | 'express' | 'overnight';

class Order {
  constructor(public type: OrderType) {}
  get shippingCost(): number {
    switch (this.type) {
      case 'standard': return 5;
      case 'express': return 15;
      case 'overnight': return 30;
    }
  }
}

// ✅ After: Replace with class hierarchy (Strategy pattern)
abstract class ShippingStrategy {
  abstract get cost(): number;
  abstract get estimatedDays(): number;
}

class StandardShipping extends ShippingStrategy {
  get cost(): number { return 5; }
  get estimatedDays(): number { return 5; }
}

class ExpressShipping extends ShippingStrategy {
  get cost(): number { return 15; }
  get estimatedDays(): number { return 2; }
}

class OvernightShipping extends ShippingStrategy {
  get cost(): number { return 30; }
  get estimatedDays(): number { return 1; }
}
```

### 5.3 Replace Magic Number with Symbolic Constant

```typescript
// ❌ Before: magic numbers everywhere
function calculateInterest(amount: number): number {
  return amount * 0.085;  // What is 0.085? When was it last updated?
}
function calculateLateFee(amount: number): number {
  return amount * 0.085;  // Is this the same constant? Or a different one?
}

// ✅ After: named constant
const ANNUAL_INTEREST_RATE = 0.085;
const LATE_PAYMENT_FEE_RATE = 0.085;

function calculateInterest(amount: number): number {
  return amount * ANNUAL_INTEREST_RATE;
}
function calculateLateFee(amount: number): number {
  return amount * LATE_PAYMENT_FEE_RATE;
}
```

---

## 6. Simplifying Conditional Logic

### 6.1 Decompose Conditional

```typescript
// ❌ Before: complex condition
function getCharge(date: Date, quantity: number, plan: Plan): number {
  if (!date.isBefore(plan.summerStart) && !date.isAfter(plan.summerEnd)) {
    return quantity * plan.summerRate + plan.summerServiceCharge;
  } else {
    return quantity * plan.regularRate + plan.regularServiceCharge;
  }
}

// ✅ After: extracted conditions and branches
function getCharge(date: Date, quantity: number, plan: Plan): number {
  return isSummer(date, plan) 
    ? summerCharge(quantity, plan) 
    : regularCharge(quantity, plan);
}

function isSummer(date: Date, plan: Plan): boolean {
  return !date.isBefore(plan.summerStart) && !date.isAfter(plan.summerEnd);
}

function summerCharge(quantity: number, plan: Plan): number {
  return quantity * plan.summerRate + plan.summerServiceCharge;
}

function regularCharge(quantity: number, plan: Plan): number {
  return quantity * plan.regularRate + plan.regularServiceCharge;
}
```

### 6.2 Consolidate Conditional Expression

```typescript
// ❌ Before: scattered condition checks
function disabilityAmount(employee: Employee): number {
  if (employee.seniority < 2) return 0;
  if (employee.monthsDisabled > 12) return 0;
  if (employee.isPartTime) return 0;
  // ... actual calculation
  return 500;
}

// ✅ After: consolidated
function disabilityAmount(employee: Employee): number {
  if (isNotEligibleForDisability(employee)) return 0;
  return 500;
}

function isNotEligibleForDisability(employee: Employee): boolean {
  return employee.seniority < 2 
    || employee.monthsDisabled > 12 
    || employee.isPartTime;
}
```

### 6.3 Replace Nested Conditional with Guard Clauses

```typescript
// ❌ Before: deeply nested
function getPayAmount(employee: Employee): number {
  let result;
  if (employee.isRetired) {
    result = 0;
  } else {
    if (employee.isOnVacation) {
      result = employee.vacationPay;
    } else {
      result = employee.regularPay;
    }
  }
  return result;
}

// ✅ After: guard clauses
function getPayAmount(employee: Employee): number {
  if (employee.isRetired) return 0;
  if (employee.isOnVacation) return employee.vacationPay;
  return employee.regularPay;
}
```

### 6.4 Replace Switch with Polymorphism

```typescript
// ❌ Before: switch on type
class Bird {
  constructor(public type: string) {}
  
  get speed(): number {
    switch (this.type) {
      case 'european': return 35;
      case 'african': return 40;
      case 'norwegian': return 30;
      default: return 0;
    }
  }
}

// ✅ After: polymorphism
interface Bird {
  get speed(): number;
}

class EuropeanBird implements Bird {
  get speed(): number { return 35; }
}

class AfricanBird implements Bird {
  get speed(): number { return 40; }
}

class NorwegianBird implements Bird {
  get speed(): number { return 30; }
}

// Factory
function createBird(type: string): Bird {
  const birds = { european: EuropeanBird, african: AfricanBird, norwegian: NorwegianBird };
  const BirdClass = birds[type];
  if (!BirdClass) throw new Error(`Unknown bird type: ${type}`);
  return new BirdClass();
}
```

---

## 7. Making Method Calls Simpler

### 7.1 Rename Method

```typescript
// ❌ Before: unclear name
function calc(a: number, b: number, c: string): number { ... }

// ✅ After: descriptive name
function calculateDiscountedTotal(baseAmount: number, discountPercent: number, customerTier: string): number {
}
```

### 7.2 Add / Remove Parameter

```typescript
// ❌ Before: missing context
function getAddress(userId: string): Address { ... }

// ✅ After: additional parameter for future flexibility
function getAddress(userId: string, includeDeleted: boolean = false): Address { ... }
```

### 7.3 Preserve Whole Object

```typescript
// ❌ Before: passing individual fields
function isTemperatureWithinRange(low: number, high: number, minTemp: number, maxTemp: number): boolean {
  return low >= minTemp && high <= maxTemp;
}
// Caller:
const range = room.daysTempRange;
isTemperatureWithinRange(range.low, range.high, plan.minTemp, plan.maxTemp);

// ✅ After: pass the object
function isTemperatureWithinRange(range: TempRange, plan: Plan): boolean {
  return range.low >= plan.minTemp && range.high <= plan.maxTemp;
}
```

### 7.4 Replace Parameter with Explicit Methods

```typescript
// ❌ Before: flag parameter
function setEngine(name: string, value: number, isElectric: boolean) {
  if (isElectric) {
    this.engine = { type: 'electric', watts: value, name };
  } else {
    this.engine = { type: 'gas', horsepower: value, name };
  }
}

// ✅ After: separate methods
function setElectricEngine(name: string, watts: number) {
  this.engine = { type: 'electric', watts, name };
}
function setGasEngine(name: string, horsepower: number) {
  this.engine = { type: 'gas', horsepower, name };
}
```

---

## 8. Dealing with Generalization

### 8.1 Pull Up / Pull Down

```typescript
// Pull Up: Move common code to superclass
class Manager extends Employee {
  get annualCost(): number {
    return this.monthlySalary * 12 + this.bonus;
  }
}
class Engineer extends Employee {
  get annualCost(): number {
    return this.monthlySalary * 12;
  }
}
// After pull up:
class Employee {
  get annualCost(): number {
    return this.monthlySalary * 12;  // Common part
  }
}
class Manager extends Employee {
  get annualCost(): number {
    return super.annualCost + this.bonus;  // Extension
  }
}

// Pull Down: Move subclass-specific method to subclass
class Employee {
  get quota(): number { return this.isSalesperson ? 100 : 0; }  // Only applies to sales
}
// After pull down:
class Employee {}  // No quota
class Salesperson extends Employee {
  get quota(): number { return 100; }
}
```

### 8.2 Extract / Collapse Hierarchy

```typescript
// Extract Interface (when two unrelated classes share behavior)
class Order {
  total(): number { ... }
}
class Quote {
  total(): number { ... }
}
// Extract:
interface Priced {
  total(): number;
}

// Collapse Hierarchy (when subclass adds nothing)
class Vehicle {}
class Car extends Vehicle {}  // Car adds nothing
// Collapse:
class Vehicle {}  // Merge Car into Vehicle
```

### 8.3 Form Template Method

```typescript
// ❌ Before: duplicate algorithm structure
class HtmlStatement {
  value(customer: Customer): string {
    let result = `<h1>Statement for ${customer.name}</h1>\n`;
    for (const rental of customer.rentals) {
      result += `<p>${rental.movie.title}: ${rental.amount}</p>\n`;
    }
    result += `<p>Total: ${customer.totalAmount}</p>\n`;
    return result;
  }
}

class TextStatement {
  value(customer: Customer): string {
    let result = `Statement for ${customer.name}\n`;
    for (const rental of customer.rentals) {
      result += `${rental.movie.title}: ${rental.amount}\n`;
    }
    result += `Total: ${customer.totalAmount}\n`;
    return result;
  }
}

// ✅ After: Template Method
abstract class Statement {
  value(customer: Customer): string {
    return this.header(customer) 
      + this.body(customer) 
      + this.footer(customer);
  }
  
  protected abstract header(customer: Customer): string;
  protected abstract formatLine(rental: Rental): string;
  protected abstract footer(customer: Customer): string;
  
  private body(customer: Customer): string {
    return customer.rentals.map(r => this.formatLine(r)).join('');
  }
}

class HtmlStatement extends Statement {
  protected header(c): string { return `<h1>Statement for ${c.name}</h1>\n`; }
  protected formatLine(r): string { return `<p>${r.movie.title}: ${r.amount}</p>\n`; }
  protected footer(c): string { return `<p>Total: ${c.totalAmount}</p>\n`; }
}

class TextStatement extends Statement {
  protected header(c): string { return `Statement for ${c.name}\n`; }
  protected formatLine(r): string { return `${r.movie.title}: ${r.amount}\n`; }
  protected footer(c): string { return `Total: ${c.totalAmount}\n`; }
}
```

---

## 9. Large-Scale Refactoring Patterns

### 9.1 Strangler Fig Pattern

```
Replace a system incrementally by gradually routing functionality to the new system.
The old system is "strangled" over time.

Steps:
  1. Identify a bounded functional area (e.g., "order creation")
  2. Build the replacement in parallel with the old system
  3. Route new traffic to the new system (feature flag)
  4. Monitor and validate
  5. Migrate existing data if needed
  6. Decommission the old code for that area

Phase 1:        [Old System]
                    
Phase 2:  [New: orders] + [Old: everything else]
            10% traffic         90% traffic

Phase 3:  [New: orders] + [Old: everything else]
            100% traffic         0% traffic (can be removed)

Diagram:
   Before:  User → OldMonolith
   During:  User → Router → {OldMonolith (90%), NewOrders (10%)}
   After:   User → NewOrders + rest of OldMonolith
```

### 9.2 Feature Flags for Refactoring

```typescript
// Feature flag-based large refactoring
class OrderService {
  async createOrder(request: CreateOrderRequest): Promise<Order> {
    if (featureFlags.isEnabled('new-order-pipeline')) {
      return this.newOrderPipeline.create(request);
    }
    return this.legacyOrderPipeline.create(request);
  }
}

// Deployment strategy:
// 1. Deploy both implementations side by side (flag = off)
// 2. Enable for internal testers (flag = internal)
// 3. Enable for 10% of users (flag = 10% canary)
// 4. Enable for all users (flag = on)
// 5. Remove old code (delete flag and legacy path)
```

### 9.3 Migrating Between APIs

```typescript
// Replace method signature without breaking callers

// Step 1: Add new method, keep old one (deprecated)
/** @deprecated Use createOrderV2 */
async function createOrder(data: OldFormat): Promise<Order> {
  return createOrderV2(migrateToV2(data));
}

async function createOrderV2(data: NewFormat): Promise<Order> {
  // new implementation
}

// Step 2: Migrate all callers to V2
// Step 3: Remove old method
```

### 9.4 Repackage / Reorganize Modules

```
Monolith → Modular monolith → Extracted services

Migration steps:
  1. Identify module boundaries (bounded contexts)
  2. Move code into bounded packages (no behavior change)
  3. Extract interfaces for cross-module communication
  4. Replace direct calls with interface calls
  5. Extract each module into its own service (if needed)

File structure migration:
  Before: src/models/, src/services/, src/controllers/
  After:  src/orders/, src/payments/, src/inventory/
          Each has: models/, services/, controllers/, events/
```

---

## 10. Refactoring and Testing

### 10.1 The TDD Flow for Refactoring

```
Red:   Write a test that fails → Green: Make it pass → Refactor: Clean up

When refactoring:
  1. Don't write new tests (you're not adding behavior)
  2. Existing tests must ALL still pass (they validate behavior hasn't changed)
  3. If you need to add a test during refactoring → it's a characterization test
```

### 10.2 Refactoring Safely: The Two-Step

```typescript
// Step 1: Add tests based on current behavior
// (Characterization tests — verify the code does what it does)

// Step 2: Refactor in small, testable increments

// ❌ Large change (too risky):
function oldImpl() {
  // 100 lines — change ALL AT ONCE
}

// ✅ Small changes (one refactoring per commit):
// Commit 1: Extract Method for part A
// Commit 2: Extract Class for part B  
// Commit 3: Rename variables for clarity
// Commit 4: Replace switch with polymorphism
```

### 10.3 Refactoring Checklist

```
Before starting:
□ Do I have tests for the code I'm changing?
  → Yes: good
  → No: Write characterization tests first
□ Can I articulate what I'm refactoring and why?
□ Have I prepared a rollback plan? (Git commit before starting)

During:
□ One refactoring at a time
□ Run tests after each refactoring (they must pass)
□ No behavior changes mixed with refactoring
□ Commit after each successful refactoring

After:
□ Did the tests pass? (all of them, not just the ones I ran)
□ Is the code more readable / maintainable?
□ Is there a clear "next step" for further improvement?
```

### 10.4 Common Refactoring Code Smells (Quick Reference)

```
🏷️ Bloaters
  - Long Method → Extract Method
  - Large Class → Extract Class
  - Primitive Obsession → Replace with Value Object
  - Long Parameter List → Preserve Whole Object, Introduce Parameter Object
  - Data Clumps → Extract Class

🔧 Tool Users
  - Switch Statements → Replace with Polymorphism
  - Temporary Field → Extract Class
  - Refused Bequest (inherits but doesn't use) → Replace Inheritance with Delegation
  - Alternative Classes with Different Interfaces → Rename Method, Move Method

📦 Couplers
  - Feature Envy → Move Method
  - Inappropriate Intimacy → Move Method, Change Bidirectional to Unidirectional
  - Message Chains → Hide Delegate
  - Middle Man → Remove Middle Man, Inline Method
```
