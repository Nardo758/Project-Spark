# Consultant Studio Roadmap
## OppGrid Consultant Studio and Workhub Execution Plan

Created: January 20, 2026
Based on: Consultant Studio Comprehensive Code Scan Report (v2.0)

---

## Goals

- Launch a secure Consultant Studio MVP with reliable payments and AI outputs.
- Complete Consultant Studio feature set with robust performance and monitoring.
- Build Workhub foundation and migrate Deep Clone as a premium feature.

---

## Scope

### In Scope (Consultant Studio)
- Idea Validation (paid) with verified payments
- AI Validate, AI Match, AI Roadmap
- Search Ideas and trend detection
- Location Analysis
- Clone Success (Deep Clone moved to Workhub)
- Activity logging and basic analytics

### In Scope (Workhub)
- Project system foundation
- Deep Clone integration
- Team collaboration (baseline)

### Out of Scope (for this roadmap)
- Full Business Plan Builder
- Financial Modeling toolset
- Enterprise white-label features

---

## Guiding Principles

1. Security before new features.
2. Payments must be verified server-side before releasing premium data.
3. AI integrations must include rate limiting, cost tracking, and fallback paths.
4. Frontend should never hardcode API base URLs.
5. Every release should include tests and monitoring updates.

---

## Phase 0: Readiness and Baseline (Days 0-2)

### Objectives
- Align configuration and ensure shared utilities exist.

### Deliverables
- Centralized API config used by all HTML pages.
- Inventory of consultant endpoints and owner mapping (frontend/backend).
- Defined success metrics per feature (conversion, error rate, latency).

### Tasks
- Standardize API base URL in js/config.js and update HTML pages to use it.
- Create shared API error handling helper for HTML pages.
- Add a minimal "ops checklist" for deployments (env vars, secrets).

---

## Phase 1: Security, Auth, and Payment Gate (Week 1)

### Objectives
- Eliminate critical security risks before new feature work.
- Protect revenue by verifying payments server-side.

### Must-Fix Issues (P0)
- Replace hardcoded user_id with authenticated user dependency.
- Add authentication middleware to all consultant endpoints.
- Add payment verification (Stripe PaymentIntent status + reuse check).
- Update timeout handling to return 504 instead of fake results.
- Add user_id to cache keys to avoid cross-user leaks.

### Deliverables
- All consultant endpoints require auth and use current_user.id.
- Payment verification enforced for idea validation.
- Cache keys include user_id for all relevant caches.
- Timeout behavior returns a proper HTTP error.

### Acceptance Criteria
- Anonymous requests to consultant endpoints return 401.
- PaymentIntent must be succeeded and unused before validation.
- Cache entries are user-scoped and cannot be reused across users.

---

## Phase 2: AI Integration and Reliability (Weeks 2-3)

### Objectives
- Complete DeepSeek and Claude integrations with safe outputs.
- Ensure AI errors do not break user flows.

### Tasks
- Integrate DeepSeek for pattern analysis and trend detection.
- Integrate Claude for viability reports and market summaries.
- Add prompt templates, response validation, and safe JSON parsing.
- Implement AI cost tracking (ai_costs table).
- Add rate limiting for all AI endpoints.
- Add retries and fallbacks for external API failures.

### Deliverables
- Dual AI pipeline operational for validate_idea, search_ideas, roadmap, match.
- Cost metrics recorded per user and endpoint.
- AI error handling provides actionable user messages.

### Acceptance Criteria
- AI responses validated against schema; invalid outputs trigger fallback.
- Rate limiting in place for high-cost endpoints (validate, clone, location).

---

## Phase 3: Frontend Completion and UX Hardening (Weeks 3-4)

### Objectives
- Finish missing Consultant Studio UIs.
- Provide consistent error handling and loading states.

### Tasks
- Build Location Analysis page with map rendering and results.
- Build Clone Success page with match cards and results.
- Add try/catch blocks around all fetch calls in AI pages.
- Add user-facing error states and retry actions.
- Add progress indicators for long-running AI calls.

### Deliverables
- Location Analysis and Clone Success UIs live and wired.
- Standardized loading, error, and empty states across AI pages.

### Acceptance Criteria
- All AI pages handle failed requests gracefully.
- Users see clear next steps after any failure.

---

## Phase 4: Performance, Data, and Observability (Weeks 4-6)

### Objectives
- Improve query performance and reliability at scale.
- Add monitoring and test coverage for critical flows.

### Tasks
- Add pagination to search_ideas queries and endpoints.
- Add missing indexes on consultant_activity.
- Enforce cache expiration in all cache queries.
- Add daily cache cleanup job.
- Add Sentry (or equivalent) for frontend and backend.
- Add unit tests for ConsultantStudioService caching and timeouts.
- Add integration tests for consultant endpoints with auth.

### Deliverables
- Measurable improvements in query latency and error rate.
- Tests for high-risk paths (payments, auth, caching).

### Acceptance Criteria
- Search endpoints paginate without loading full datasets.
- Cache cleanup job runs and expired entries are removed.
- Test suite covers at least 70 percent of service logic.

---

## Phase 5: Consultant Studio Full Launch (Weeks 6-8)

### Objectives
- Finish remaining backend integrations and polish user flows.

### Tasks
- Complete AI Match backend implementation.
- Complete AI Roadmap backend implementation.
- Add activity log UI and basic analytics dashboard.
- Add download/export for validation reports (PDF optional).
- Run beta testing and collect feedback.

### Deliverables
- Consultant Studio feature set at 100 percent functional readiness.
- Beta feedback integrated into UI and flow adjustments.

---

## Phase 6: Workhub Foundation and Deep Clone Migration (Weeks 7-10)

### Objectives
- Establish Workhub project model and migrate Deep Clone.

### Tasks
- Implement WorkhubProject model and CRUD endpoints.
- Add project activity logging and permissions.
- Integrate Deep Clone in Workhub context with payment gating.
- Add project-level storage of analyses and exports.

### Deliverables
- Workhub MVP with project creation and Deep Clone analysis.

---

## Phase 7: Workhub Collaboration and Premium Tools (Weeks 10-14)

### Objectives
- Enable team collaboration and premium workflow tools.

### Tasks
- Team member invites and roles.
- Comments/annotations on analyses.
- Version history for Deep Clone analyses.
- PDF export pipeline for premium reports.

### Deliverables
- Workhub Pro baseline (collaboration, exports, premium gating).

---

## Work Breakdown by Area

### Backend
- Auth dependencies for consultant endpoints.
- Payment verification and webhook handling.
- Cache key updates with user_id.
- AI integration and schema validation.
- Pagination, indexing, cache cleanup.

### Frontend (HTML)
- Use js/config.js for API base in all pages.
- Error boundaries and standardized loading states.
- New UIs: Location Analysis, Clone Success.

### Data and Infra
- Add idea_validations, consultant_sessions, ai_costs tables.
- Add indexes for consultant_activity.
- Enable monitoring and error reporting.

---

## Dependencies and Sequencing

- Auth fixes must land before any public launch.
- Payment verification must land before enabling paid validation flows.
- AI integrations depend on env keys and secret management.
- Workhub migration depends on project system completion.

---

## Success Metrics

### Consultant Studio
- Validation conversion rate >= 5 percent of eligible sessions.
- Cache hit rate >= 70 percent on repeat validations.
- AI error rate < 3 percent of requests.
- Payment verification failure rate < 1 percent.

### Workhub
- Project creation rate >= 10 percent of Consultant Studio users.
- Deep Clone purchase conversion >= 5 percent of eligible users.

---

## Risks and Mitigations

1. AI cost spikes
   - Mitigation: rate limiting, caching, cost tracking, prompt trimming.
2. External API instability
   - Mitigation: retries, fallbacks, circuit breaker behavior.
3. Payment disputes or reuse
   - Mitigation: strict PaymentIntent verification and uniqueness constraints.
4. Data leakage risk
   - Mitigation: user-scoped cache keys and auth enforcement.

---

## Open Questions

1. Which rate limiting strategy should be used (per IP vs per user)?
2. Should paid validations support refunds and dispute handling now or later?
3. Which analytics provider is preferred for event tracking?

---

## Immediate Next Steps

1. Approve Phase 1 scope and sequencing.
2. Choose rate limiting approach and provider.
3. Confirm AI provider keys and environment variable names.
4. Confirm Stripe webhook endpoint and event types to support.
