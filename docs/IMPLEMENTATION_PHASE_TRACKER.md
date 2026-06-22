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

Status: In progress

- [ ] Add `CashEntry`.
- [ ] Record sale payments as cash inflows.
- [ ] Record expense and inventory payments as cash outflows.
- [ ] Separate cash position from profit in dashboard calculations.
- [ ] Add outstanding credit/payment status support.

## Phase 5: Expense Classification And Audit Trail

Status: Not started

- [ ] Add expense type/status fields.
- [ ] Add created/updated actor fields to financial records.
- [ ] Replace hard deletes with void/reversal flows.
- [ ] Add void reasons and timestamps.
- [ ] Update frontend delete flows to use void actions.

## Phase 6: Reports And Analytics

Status: Not started

- [ ] Add profit and loss report.
- [ ] Add cash-flow report.
- [ ] Add burn-rate report.
- [ ] Add break-even calculator.
- [ ] Add trend analysis.
- [ ] Add initial forecasting service.

## Phase 7: Tax Rules And Estimates

Status: Not started

- [ ] Add versioned `TaxRule`.
- [ ] Add `TaxEstimate`.
- [ ] Replace placeholder tax set-aside logic.
- [ ] Preserve assumptions and rule versions on estimates.
- [ ] Label estimates clearly as estimates, not filed tax.

## Phase 8: Team Access And OAuth

Status: Not started

- [ ] Add staff invitations.
- [ ] Add membership role management.
- [ ] Add permission-aware frontend views.
- [ ] Implement Google OAuth when credentials and redirects are available.

## Phase 9: Frontend App Architecture

Status: Not started

- [ ] Add `AuthProvider`.
- [ ] Add `BusinessProvider`.
- [ ] Add active business switcher.
- [ ] Make API client business-aware.
- [ ] Add global loading, empty, error, and toast patterns.
- [ ] Replace hardcoded sidebar user/footer details.

## Phase 10: Release Readiness

Status: Not started

- [ ] Add backend tests for business isolation.
- [ ] Add backend tests for sales/inventory/cash calculations.
- [ ] Add backend tests for void/reversal behavior.
- [ ] Add manual QA script.
- [ ] Keep `python manage.py test`, `npm run lint`, and `npm run build` green.
