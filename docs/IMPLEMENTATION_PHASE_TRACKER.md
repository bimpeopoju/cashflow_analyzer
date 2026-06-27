# MarketFlow Implementation Phase Tracker

This tracker converts the project knowledge base into executable phases. Keep it
updated as implementation decisions change.

## Phase 0: Stabilize Current MVP

Status: Complete

- [x] Fix frontend text encoding artifacts.
- [x] Add protected frontend routes for authenticated app pages.
- [x] Add an auth bootstrap around the current `me` endpoint.
- [x] Improve create/delete loading and error handling.
- [x] Add confirmation before destructive deletes.
- [x] Verify backend tests, frontend lint, and frontend build.

## Phase 1: Business Ownership Boundary

Status: Complete

- [x] Add `Business` model.
- [x] Add `BusinessMembership` model.
- [x] Backfill existing `BusinessProfile` rows into businesses.
- [x] Backfill sales, expenses, and inventory items to businesses.
- [x] Replace direct user ownership on financial records with business scope.
- [x] Add business list/create endpoints.
- [x] Update frontend to select an active business.

## Phase 2: Finance Service Layer

Status: Complete

- [x] Add finance serializers.
- [x] Add finance selectors for scoped reads.
- [x] Add finance services for writes.
- [x] Add finance calculation services.
- [x] Add reusable business permission checks.
- [x] Thin out finance HTTP views.

## Phase 3: Sales, Sale Lines, And Inventory Movements

Status: Complete

- [x] Add `SaleLine`.
- [x] Add `StockMovement`.
- [x] Support single-line itemized sales through the existing sale API.
- [x] Reduce inventory when linked inventory items are sold.
- [x] Preserve unit price and unit cost snapshots on sale lines.
- [x] Update dashboard gross profit calculation.

## Phase 4: Cash Flow Versus Profit

Status: Complete

- [x] Add `CashEntry`.
- [x] Record sale payments as cash inflows.
- [x] Record expense and inventory payments as cash outflows.
- [x] Separate cash position from profit in dashboard calculations.
- [x] Add outstanding credit/payment status support.

## Phase 5: Expense Classification And Audit Trail

Status: Complete

- [x] Add expense type/status fields.
- [x] Add created actor fields to financial records.
- [x] Replace hard deletes with void/reversal flows.
- [x] Add void reasons and timestamps.
- [x] Update frontend delete flows to use void actions.

## Phase 6: Modular App Split

Status: Complete

- [x] Create `businesses` app for ownership and membership.
- [x] Create `sales` app for sale lines and void flows.
- [x] Create `inventory` app for stock records and stock movements.
- [x] Create `expenses` app for expense records and void flows.
- [x] Create `cashflow` app for cash entries and cash position.
- [x] Create `reports` app for dashboard and derived metrics.
- [x] Leave `finance` as a compatibility layer during migration.

## Phase 7: Reports And Analytics

Status: In progress

- [ ] Add profit and loss report.
- [ ] Add cash-flow report.
- [x] Add product burn-rate report.
- [x] Add break-even calculator.
- [x] Add weekly growth and trend analysis dashboard.
- [x] Add initial forecasting service. See `docs/FORECASTING_IMPLEMENTATION_PLAN.md`.

## Phase 8: Tax Rules And Estimates

Status: In progress

- [x] Add versioned `TaxRule`.
- [x] Add `TaxEstimate`.
- [x] Replace placeholder tax set-aside logic with tax estimate page.
- [x] Preserve assumptions and rule versions on estimates.
- [x] Label estimates clearly as estimates, not filed tax.

## Phase 9: Team Access And OAuth

Status: Not started

- [ ] Add staff invitations.
- [ ] Add membership role management.
- [ ] Add permission-aware frontend views.
- [ ] Implement Google OAuth when credentials and redirects are available.

## Phase 10: Frontend App Architecture

Status: Not started

- [ ] Add `AuthProvider`.
- [ ] Add `BusinessProvider`.
- [ ] Add active business switcher.
- [ ] Make API client business-aware.
- [ ] Add global loading, empty, error, and toast patterns.
- [ ] Replace hardcoded sidebar user/footer details.

## Phase 11: Release Readiness

Status: Not started

- [ ] Add backend tests for business isolation.
- [ ] Add backend tests for sales/inventory/cash calculations.
- [ ] Add backend tests for void/reversal behavior.
- [ ] Add manual QA script.
- [ ] Keep `python manage.py test`, `npm run lint`, and `npm run build` green.
