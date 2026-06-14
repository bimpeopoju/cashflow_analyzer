# MarketFlow Backend Reconstruction Blueprint

## Objective

Reconstruct the backend as a modular Django monolith whose boundaries match the
client workflow. Keep deployment simple while separating transaction capture,
accounting calculations, analytics, planning, tax, and forecasting.

## Why Reconstruction Is Necessary

The current `finance` app is a prototype boundary rather than a sustainable
domain boundary.

- `finance/views.py` owns authentication, request parsing, validation,
  serialization, CRUD, dashboard queries, and financial calculations.
- `BusinessProfile`, `Sale`, `Expense`, and `InventoryItem` are unrelated
  records linked directly to users.
- Sales do not capture unit price, cost of goods sold, payment status, or line
  items, so real profit cannot be calculated reliably.
- Inventory quantities have no stock movement history.
- Expenses have free-text categories and cannot support burn rate,
  break-even, or tax classification reliably.
- Current capital is calculated as initial capital plus net profit, which
  incorrectly treats profit and cash as interchangeable.
- Deletes permanently remove source financial records.
- Dashboard calculations are embedded in an HTTP view and will be duplicated by
  reports, tax, and forecasting features.

## Target Architecture

Use a modular monolith. Each Django app owns its models, commands, queries, API,
and tests. Cross-domain calculations consume public query/service interfaces.

```text
backend/
  config/              project settings and root URLs
  common/              shared money, dates, API errors, audit primitives
  users/               identity, authentication, user preferences
  businesses/          businesses, stalls, memberships, permissions
  sales/               sales, sale lines, sale payments
  expenses/            expenses, categories, expense payments
  inventory/           products, stock movements, purchasing, valuation
  ledger/              normalized cash and capital movements
  analytics/           profit summaries, dashboards, trends
  planning/            burn rate and break-even scenarios
  taxes/               versioned tax rules, VAT/FIRS estimates
  forecasting/         forecast runs, assumptions, projected periods
```

Do not create every app in one change. Introduce them through the phases below.

## Dependency Direction

```text
users
  |
businesses
  |--------------------|--------------------|
sales               expenses             inventory
  |                    |                    |
  |------------------ ledger ---------------|
                         |
          |--------------|--------------|
       analytics       planning        taxes
                         |
                     forecasting
```

- Transaction domains may publish normalized entries to `ledger`.
- Analytics and planning read transaction domains and ledger data.
- Taxes read classified source records and versioned tax rules.
- Forecasting reads historical aggregates and explicit assumptions.
- Lower-level transaction apps must not import analytics, planning, taxes, or
  forecasting.

## Workflow to Domain Mapping

| Workflow stage | Owning domain | Primary responsibility |
| --- | --- | --- |
| Trader registers | `users`, `businesses` | Identity, session, business creation, membership |
| Log daily sales | `sales` | Revenue, line items, payment status, sale timestamps |
| Log daily expenses | `expenses` | Costs, categories, payment status, evidence |
| Profit calculation | `analytics` | Revenue, COGS, gross profit, operating expenses, net profit |
| Analytics dashboard | `analytics` | Read-optimized summaries and comparisons |
| Burn rate tracker | `planning` | Operating cash outflow rate and runway |
| Break-even calculator | `planning` | Fixed cost and contribution margin scenarios |
| Tax calculator | `taxes` | Versioned VAT/FIRS estimates and assumptions |
| Trend analysis | `analytics` | Period comparisons, moving averages, anomalies |
| Forecasting engine | `forecasting` | Historical projections and scenario assumptions |

## Core Entity Structure

### Users and Businesses

```text
User
Business
BusinessMembership(user, business, role, status)
BusinessLocation(business, name, location)
```

All operational records reference `business`. Records may also reference
`created_by` for auditing.

### Sales

```text
Sale(business, reference, status, occurred_at, subtotal, discount, tax, total)
SaleLine(sale, product, description, quantity, unit_price, unit_cost, line_total)
SalePayment(sale, amount, method, paid_at, reference)
```

`SaleLine.unit_cost` preserves the cost basis at the time of sale. That allows
historical COGS and profit calculations to remain stable if product costs later
change.

### Expenses

```text
ExpenseCategory(business/null, name, classification, tax_category)
Expense(business, category, status, amount, occurred_at, description, vendor)
ExpensePayment(expense, amount, method, paid_at, reference)
```

Initial expense classifications:

- `operating_fixed`
- `operating_variable`
- `inventory_purchase`
- `capital_asset`
- `owner_withdrawal`
- `tax_payment`
- `other`

### Inventory

```text
Product(business, name, sku, unit, selling_price, reorder_level, active)
StockMovement(business, product, type, quantity, unit_cost, occurred_at, source)
Purchase(business, supplier, status, occurred_at, total)
PurchaseLine(purchase, product, quantity, unit_cost)
```

Inventory balance is derived from stock movements. Do not update a product's
quantity without recording a movement.

Initial stock movement types:

- `opening`
- `purchase`
- `sale`
- `return_in`
- `return_out`
- `adjustment`
- `damage`
- `loss`

### Ledger and Capital

```text
CashAccount(business, name, account_type, opening_balance)
CashEntry(business, account, direction, amount, occurred_at, source)
CapitalEntry(business, type, amount, occurred_at, description)
```

Initial capital entry types:

- `owner_contribution`
- `owner_withdrawal`
- `retained_profit`
- `adjustment`

The ledger is not a full general ledger in the first phase. It is a normalized
cash and capital movement layer that prevents analytics from conflating profit,
cash, and capital.

### Analytics, Planning, Taxes, and Forecasting

Derived metrics should normally be computed by services and cached only when
performance requires it.

```text
DailyBusinessMetric(business, date, revenue, cogs, expenses, cash_in, cash_out)
BreakEvenScenario(business, name, fixed_costs, variable_cost_ratio, target_price)
TaxRule(code, jurisdiction, effective_from, effective_to, configuration)
TaxEstimate(business, period_start, period_end, rule_version, assumptions, result)
ForecastRun(business, horizon, method, assumptions, generated_at)
ForecastPeriod(forecast_run, period_start, revenue, expenses, cash_position)
```

## Application-Layer Pattern

Models preserve data integrity and relationships. Business workflows belong in
commands/services. Read-heavy calculations belong in query services.

```text
sales/
  models.py
  commands/
    create_sale.py
    void_sale.py
  queries/
    list_sales.py
  api/
    urls.py
    views.py
    serializers.py
  tests/
    test_create_sale.py
    test_sales_api.py
```

Example command boundary:

```python
create_sale(
    *,
    business,
    actor,
    occurred_at,
    lines,
    payments,
) -> Sale
```

The command validates permissions and invariants, creates the sale atomically,
records inventory movements, and records cash entries. The API view only parses
the request, calls the command, and returns a response.

## API Direction

Introduce versioned business-scoped endpoints:

```text
/api/v1/auth/*
/api/v1/businesses/*
/api/v1/businesses/{business_id}/sales/*
/api/v1/businesses/{business_id}/expenses/*
/api/v1/businesses/{business_id}/inventory/*
/api/v1/businesses/{business_id}/analytics/dashboard/
/api/v1/businesses/{business_id}/planning/burn-rate/
/api/v1/businesses/{business_id}/planning/break-even/
/api/v1/businesses/{business_id}/taxes/estimates/
/api/v1/businesses/{business_id}/forecasts/
```

Keep the current `/api/*` endpoints operational through a temporary compatibility
layer while the frontend moves to `/api/v1/*`.

## Required Invariants

- Monetary values use `Decimal`, never floating point.
- Operational records always reference a business.
- The authenticated user must have an active membership in the requested
  business.
- Sale and expense totals cannot be negative.
- Completed sales must contain at least one line.
- Payments cannot exceed the document balance unless overpayments are explicitly
  supported.
- Stock-affecting operations always create stock movements.
- Posted financial records are voided or reversed rather than hard-deleted.
- Calculations use explicit periods and the business timezone.
- Tax estimates preserve the exact rule version and assumptions used.

## Reconstruction Phases

### Phase 0: Characterization and Safety

- Freeze the current API behavior with characterization tests.
- Record all current endpoint response contracts.
- Add shared test factories for users and financial records.
- Decide whether existing local data needs preservation.

Exit condition: existing behavior is covered well enough to refactor safely.

### Phase 1: Business Ownership and Authentication Separation

- Activate and complete the existing `users` scaffold.
- Create `businesses` with `Business` and `BusinessMembership`.
- Move registration/login/profile behavior out of `finance`.
- Backfill one business and owner membership per existing `BusinessProfile`.
- Add business authorization helpers.

Exit condition: users authenticate independently and all new records can be
scoped to a business.

### Phase 2: Transaction Capture

- Create `sales`, `expenses`, and `inventory` domain apps.
- Introduce product, sale line, expense category, and stock movement models.
- Add command services and transaction-level tests.
- Keep compatibility reads for current frontend payloads.

Exit condition: daily sales and expenses produce auditable source records.

### Phase 3: Cash, Capital, and Profit

- Introduce the normalized cash/capital ledger.
- Build a single profit calculation service.
- Replace the current `initial_capital + net_profit` shortcut.
- Expose explainable profit and cash summaries.

Exit condition: profit, cash position, and capital are separately correct.

### Phase 4: Dashboard and Trend Analysis

- Move dashboard logic into analytics query services.
- Add daily aggregates only if measured query performance requires them.
- Add period comparison and trend endpoints.

Exit condition: dashboards and reports consume the same calculation definitions.

### Phase 5: Burn Rate and Break-Even

- Define expense classification and available-cash rules with the client.
- Implement burn rate, runway, and break-even scenario services.
- Return formulas and assumptions with every result.

Exit condition: planning metrics are explainable and reproducible.

### Phase 6: Tax Calculator

- Confirm tax scope with a Nigerian tax professional.
- Add versioned tax rules and classifications.
- Implement estimates with assumptions and audit history.

Exit condition: estimates are rule-versioned and clearly distinguished from
filed obligations.

### Phase 7: Forecasting

- Begin with transparent baseline methods such as moving average or linear
  trend.
- Store forecast assumptions and generated periods.
- Measure forecast error before introducing complex models.

Exit condition: forecasts are reproducible, explainable, and evaluated.

## Immediate Next Implementation Slice

The first code reconstruction should be Phase 0 plus the smallest part of Phase
1:

1. Add characterization tests for every existing API endpoint.
2. Create `businesses.Business` and `businesses.BusinessMembership`.
3. Complete the existing `users` app and move auth endpoints into it.
4. Add a data migration from `BusinessProfile` to `Business`.
5. Add nullable `business` ownership to existing finance records, backfill it,
   then make it required.
6. Keep existing endpoint payloads unchanged until the frontend migration is
   planned.

This creates the ownership boundary required by every later workflow without
attempting a risky all-at-once rewrite.

