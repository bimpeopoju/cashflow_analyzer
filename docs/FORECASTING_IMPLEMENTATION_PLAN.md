# Financial Forecasting Module Implementation Plan

Objective: develop a forecasting module that uses historical sales, expense,
cash-flow, and inventory trends to project short-term business performance in a
way that is explainable, reproducible, and safe for small traders.

## Scope

The first release should forecast weekly or monthly revenue, expenses, net
profit, cash position, and inventory pressure from existing business records.
It should not pretend to be a complex AI model. The forecast must show the
historical window, method, assumptions, confidence notes, and data limitations.

## Architecture Decision

Create a dedicated `forecasting` Django app.

The `forecasting` app should read from:

- `sales` for completed sales and sale-line revenue.
- `expenses` for approved expenses by type.
- `cashflow` for paid inflows and outflows.
- `inventory` for stock value and stock movement pressure.
- `reports` and `planning` only when reusing derived metrics is cleaner than
  recalculating them.

The `forecasting` app must not own source transactions. It owns forecast runs,
forecast periods, assumptions, and forecast evaluation results.

## Forecasting Method

Start with deterministic statistical methods before adding advanced models.

Initial method:

- Aggregate historical data into daily buckets.
- Support `7`, `30`, `60`, and `90` day lookback windows.
- Forecast `7`, `14`, and `30` days ahead.
- Use moving average plus recent trend adjustment:
  - `baseline = average daily value over lookback`
  - `recent_average = average daily value over last third of lookback`
  - `trend_adjustment = recent_average - baseline`
  - `forecast_daily_value = max(baseline + trend_weight * trend_adjustment, 0)`
- Use separate lines for sales, operating expenses, inventory purchases, and
  cash movement.
- Project cash position from current cash position plus forecasted net cash
  flow.

This keeps the output explainable and testable.

## Data Readiness Rules

The backend should reject or degrade forecasts cleanly when data is weak.

- No transactions: return `409 forecast_data_unavailable`.
- Fewer than 7 days of activity: return a forecast with `confidence = low` and
  a warning.
- Missing sale lines: use sale totals for revenue but mark cost/profit forecast
  confidence as low.
- No expenses: forecast expenses as zero but include a warning that expense
  history is missing.
- Negative trend outputs should floor at zero for sales and expenses.

## Phase 1: Backend App Scaffold

Deliverables:

- Create `backend/forecasting/`.
- Add `ForecastRun` model.
- Add `ForecastPeriod` model.
- Add migration and app registration.
- Add business-scoped selectors.
- Add serializer helpers for API payloads.

Recommended model shape:

- `ForecastRun`
  - `business`
  - `method`
  - `lookback_days`
  - `horizon_days`
  - `period_granularity`
  - `confidence`
  - `warnings`
  - `assumptions`
  - `created_by`
  - `created_at`
- `ForecastPeriod`
  - `forecast_run`
  - `period_start`
  - `period_end`
  - `projected_sales`
  - `projected_expenses`
  - `projected_gross_profit`
  - `projected_net_profit`
  - `projected_cash_position`
  - `projected_inventory_cost`

Acceptance checks:

- Migrations apply cleanly.
- Models are business-scoped.
- Forecast records can be created without touching source transactions.

## Phase 2: Forecast Calculation Service

Deliverables:

- Add `forecasting/calculations.py`.
- Build daily historical buckets for sales, expenses, COGS, and cash flow.
- Implement moving-average trend projection.
- Add warning/confidence rules.
- Return a full JSON-ready forecast result without requiring persistence.
- Add optional `persist=True` mode to save the forecast run and periods.

Core output shape:

```json
{
  "id": null,
  "method": "moving_average_trend",
  "lookbackDays": 30,
  "horizonDays": 14,
  "confidence": "medium",
  "warnings": [],
  "assumptions": {},
  "history": [],
  "periods": [],
  "summary": {
    "projectedSales": "0.00",
    "projectedExpenses": "0.00",
    "projectedNetProfit": "0.00",
    "projectedEndingCash": "0.00"
  }
}
```

Acceptance checks:

- Empty businesses receive a clear error.
- Forecast calculations are deterministic for the same inputs.
- Unit tests cover rising, falling, flat, and empty historical patterns.

## Phase 3: API Endpoints

Deliverables:

- Add `forecasting/views.py`.
- Add `forecasting/urls.py`.
- Register URLs in `config/urls.py`.
- Add endpoints:
  - `GET /api/forecasts/?lookbackDays=30&horizonDays=14`
  - `POST /api/forecasts/`
  - `GET /api/businesses/<id>/forecasts/?lookbackDays=30&horizonDays=14`
  - `POST /api/businesses/<id>/forecasts/`

Endpoint behavior:

- `GET` returns a preview forecast without saving.
- `POST` persists the forecast run and periods.
- Both endpoints must enforce business membership.
- Both endpoints must return useful no-data errors for new users.

Acceptance checks:

- Auth required.
- Unrelated business IDs return `404`.
- Preview does not create database records.
- Save creates one run and the expected periods.

## Phase 4: Frontend Forecasting Page

Deliverables:

- Add frontend API types and methods.
- Add a `/forecasts` route and navigation item.
- Build a forecasting dashboard with:
  - lookback selector
  - horizon selector
  - projected sales
  - projected expenses
  - projected net profit
  - projected ending cash
  - trend chart
  - warning/confidence panel
  - save forecast button
- Add empty-state flow that sends new users to record sales and expenses first.

UI rules:

- Make the first screen the actual forecast workspace.
- Do not present forecasts as guarantees.
- Show the method and assumptions close to the numbers.
- Use charts for historical versus projected values.

Acceptance checks:

- Works for empty, weak, and healthy data.
- Long labels do not overflow on mobile.
- Frontend lint and build pass.

## Phase 5: Forecast Evaluation

Deliverables:

- Add a way to compare old forecast periods against actual results after time
  passes.
- Store forecast error metrics:
  - sales absolute error
  - expense absolute error
  - net profit absolute error
  - percentage error where valid
- Add backend test coverage for evaluation.

Acceptance checks:

- Forecast accuracy can be measured before introducing advanced models.
- Users can see whether previous forecasts were reliable.

## Phase 6: Release Hardening

Deliverables:

- Add backend tests for business isolation.
- Add backend tests for calculation edge cases.
- Add frontend loading, error, and no-data states.
- Add manual QA steps to release docs.
- Keep `python manage.py test`, frontend lint, and frontend build green.

## Implementation Order

1. Backend app scaffold and migrations.
2. Calculation service with unit tests.
3. Business-scoped forecast API.
4. Frontend API contract.
5. Forecasting page and navigation.
6. Forecast persistence.
7. Forecast evaluation.

## Out Of Scope For First Release

- Machine learning models.
- External economic data.
- Seasonality by public holidays.
- Per-product demand forecasting.
- Automatic purchasing recommendations.

Those can come later after the app has enough historical records and forecast
error data.
