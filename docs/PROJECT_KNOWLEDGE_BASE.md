# MarketFlow Project Knowledge Base

This document is the durable source of truth for product expectations and
domain decisions. Update it whenever the client clarifies a workflow, formula,
policy, or business rule.

## Product Purpose

MarketFlow helps Nigerian market traders record daily business activity,
understand real profit and cash position, protect business capital, plan for
future costs, and maintain records needed for tax compliance.

The product must remain usable for traders who do not have formal accounting
knowledge. The interface may use simple language, but the backend must preserve
correct accounting distinctions.

## Agreed System Workflow

1. Trader registers.
2. Trader creates or joins a business.
3. Trader records daily sales.
4. Trader records daily expenses.
5. The system calculates profit and cash position.
6. The analytics dashboard summarizes business performance.
7. The burn-rate tracker estimates how quickly available cash is being spent.
8. The break-even calculator estimates the sales required to cover costs.
9. The tax calculator estimates applicable FIRS and VAT obligations.
10. Trend analysis identifies historical patterns.
11. The forecasting engine projects future performance.

## Core Domain Principles

### Business Is the Ownership Boundary

Financial records belong to a business, not directly to a user. A user may own
or work in more than one business. Every query and command must be scoped to an
authorized business.

### Cash Flow Is Not Profit

- Cash flow measures cash entering and leaving the business.
- Profit measures revenue less the costs required to earn that revenue.
- Inventory purchases reduce cash immediately but normally affect profit as
  cost of goods sold when inventory is sold.
- Owner deposits and withdrawals affect cash and capital, not operating profit.

### Calculations Are Derived

Profit, burn rate, break-even, tax estimates, trends, and forecasts are derived
from source records. They should live in dedicated calculation services, not in
HTTP views or model `save()` methods.

### Source Records Need an Audit Trail

Financial records should not disappear without explanation. The target design
uses statuses, reversals, or soft deletion for important financial entries and
records who created or changed them.

### Tax Rules Must Be Versioned

Tax rates, thresholds, exemptions, and effective dates must be stored as
versioned rules. Tax logic must not be scattered as hard-coded constants.
Calculated tax values are estimates until reviewed or filed.

## Domain Vocabulary

| Term | Meaning |
| --- | --- |
| Business | The trader's financial and operational workspace. |
| Membership | A user's role and permissions within a business. |
| Sale | A completed exchange that produces revenue. |
| Sale line | A product, quantity, price, discount, and cost within a sale. |
| Expense | A business cost classified for reporting and planning. |
| Inventory item | A product or stock type tracked by the business. |
| Stock movement | An auditable increase, decrease, sale, adjustment, or loss of stock. |
| Cash entry | A normalized inflow or outflow used to calculate cash position. |
| Cost of goods sold | The inventory cost attributable to sold items. |
| Gross profit | Revenue less cost of goods sold. |
| Net profit | Gross profit less operating expenses and other applicable costs. |
| Burn rate | Average operating cash outflow over a selected period. |
| Break-even point | The revenue or unit volume required to cover fixed and variable costs. |
| Tax estimate | A calculation based on a versioned tax rule and recorded business activity. |
| Forecast | A projection generated from historical data and explicit assumptions. |

## Initial Calculation Definitions

These definitions are the reconstruction baseline. Client clarification may
change them.

```text
revenue = sum(completed sale totals)
cost_of_goods_sold = sum(cost attributed to completed sale lines)
gross_profit = revenue - cost_of_goods_sold
operating_expenses = sum(approved operating expenses)
net_profit = gross_profit - operating_expenses

cash_inflow = sales received + owner deposits + other cash inflows
cash_outflow = expenses paid + inventory purchases paid + owner withdrawals + tax paid
cash_position = opening cash + cash_inflow - cash_outflow

average_daily_burn = operating cash outflows / number of days in period
runway_days = available operating cash / average_daily_burn

contribution_margin = selling price - variable cost
break_even_units = fixed costs / contribution margin per unit
break_even_revenue = fixed costs / contribution margin ratio
```

## Tax Guardrails

- VAT and FIRS calculations require current legal and accounting validation.
- The system must preserve the rule version used for every estimate.
- VAT-capable records need tax-inclusive/tax-exclusive amounts and tax category.
- Input VAT and output VAT must be distinguishable.
- Tax estimates must show assumptions and should not be presented as filed tax.

## Current Technical Reality

- Backend: Django 6 modular monolith using SQLite for development.
- Frontend: React, TypeScript, and Vite.
- Authentication currently uses Django session authentication.
- Current backend financial models are `BusinessProfile`, `Sale`, `Expense`,
  and `InventoryItem` in the `finance` app.
- Current records are scoped directly to users.
- Authentication, validation, serialization, CRUD, dashboard queries, and
  calculations are compressed into `finance/views.py`.
- An untracked scaffold exists at `backend/users/`; it contains no domain logic
  yet and must not be overwritten without review.

## Authentication Decisions

- The initial application authentication method is email/password with JWT
  access and rotating refresh tokens.
- Django's existing user model remains in place during the first reconstruction
  phase to avoid a risky user-table migration.
- OAuth support begins with a provider-neutral linked-identity scaffold.
- Google is the first planned OAuth provider, but remains disabled until client
  credentials and redirect URLs are configured.
- Session authentication remains temporarily available for Django admin and
  compatibility while the frontend transitions to bearer tokens.

## Product Decisions Still Required

1. Can one trader operate multiple businesses or stalls?
2. Can staff members record transactions, and which roles are required?
3. Are sales recorded as totals only, or must every sale contain product lines?
4. Are credit sales, partial payments, and customer debt required?
5. Which inventory valuation method is required: weighted average, FIFO, or a
   simpler trader-entered cost?
6. Which expense categories are fixed, variable, personal withdrawal, capital
   purchase, inventory purchase, and tax?
7. What exactly counts as available cash for runway calculations?
8. Which Nigerian tax obligations and taxpayer types are in scope?
9. What forecast horizon and forecast method should the first release support?
10. Are offline entry, synchronization, and multiple currencies required?

## Change Log

### 2026-06-14

- Established the system workflow and modular-monolith reconstruction baseline.
- Defined business ownership, accounting distinctions, derived calculations,
  auditability, and versioned tax rules as core principles.
- Agreed to begin authentication reconstruction with email/password JWT and an
  OAuth-ready identity scaffold.
