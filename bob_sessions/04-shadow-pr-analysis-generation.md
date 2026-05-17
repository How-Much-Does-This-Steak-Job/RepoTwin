
# Session 04: Shadow PR Analysis Generation

**Date:** 2026-05-16  
**Duration:** 3.5 hours  
**Agent:** IBM Bob  
**Focus Area:** Product Intelligence & Analysis

## Objective

Generate comprehensive Shadow PR analysis data for the UniMarket demo scenario:
- Repository: UniMarket (Android marketplace app)
- Change Request: "Add reservation flow before purchase"
- Demonstrate IBM Bob's ability to understand code impact
- Create realistic, high-quality sample data

## IBM Bob Prompts Used

### Prompt 1: Repository Context Understanding
```
Analyze the UniMarket Android application architecture:
- Kotlin/Android codebase
- MVVM architecture
- Room database for local storage
- Retrofit for API calls
- Firebase for analytics
- Jetpack Compose UI

For the change request "Add reservation flow before purchase", identify:
1. All affected files and modules
2. Impact on existing features
3. Database schema changes
4. API contract changes
5. UI/UX modifications
6. Analytics event changes
```

### Prompt 2: Blast Radius Calculation
```
Calculate the blast radius for adding a reservation flow:
1. Direct impact: Files that must be modified
2. Indirect impact: Files that depend on modified files
3. Test impact: Tests that need updates
4. Documentation impact: Docs that need updates

Categorize each affected file by:
- Impact level (critical, high, medium, low)
- Change type (modify, create, delete)
- Risk factor (breaking change, safe change)
```

### Prompt 3: Risk Assessment
```
Assess the risks of adding a reservation flow:
1. Breaking changes to existing purchase flow
2. Data consistency issues
3. Race conditions in reservation/purchase
4. Offline mode complications
5. Analytics tracking gaps
6. User experience regressions

Calculate overall risk score (0-100) with breakdown by category:
- Architecture risk
- Data risk
- Integration risk
- User experience risk
- Performance risk
```

### Prompt 4: Regression Test Pack
```
Generate a comprehensive regression test pack:
1. Unit tests for new reservation logic
2. Integration tests for reservation + purchase flow
3. UI tests for reservation screens
4. API tests for reservation endpoints
5. Edge case tests (timeouts, cancellations, conflicts)
6. Performance tests for concurrent reservations

Prioritize tests by risk level and coverage impact.
```

### Prompt 5: Implementation Contract
```
Create a safe implementation contract with phases:
1. Phase 1: Database schema and models
2. Phase 2: Backend API endpoints
3. Phase 3: Repository layer
4. Phase 4: ViewModel logic
5. Phase 5: UI components
6. Phase 6: Analytics integration
7. Phase 7: Testing and validation

For each phase, specify:
- Files to modify/create
- Dependencies on previous phases
- Validation criteria
- Rollback strategy
```

## Bob's Analysis

### Repository Understanding

Bob analyzed the UniMarket architecture and identified:

```
UniMarket/
├── app/
│   ├── data/
│   │   ├── local/
│   │   │   ├── dao/
│   │   │   │   ├── ListingDao.kt          [CRITICAL IMPACT]
│   │   │   │   └── ReservationDao.kt      [NEW FILE]
│   │   │   └── database/
│   │   │       └── AppDatabase.kt         [HIGH IMPACT]
│   │   ├── remote/
│   │   │   ├── api/
│   │   │   │   └── MarketplaceApi.kt      [CRITICAL IMPACT]
│   │   │   └── dto/
│   │   │       └── ReservationDto.kt      [NEW FILE]
│   │   └── repository/
│   │       └── ListingRepository.kt       [CRITICAL IMPACT]
│   ├── domain/
│   │   ├── model/
│   │   │   ├── Listing.kt                 [HIGH IMPACT]
│   │   │   └── Reservation.kt             [NEW FILE]
│   │   └── usecase/
│   │       ├── CreateReservationUseCase.kt [NEW FILE]
│   │       └── PurchaseListingUseCase.kt  [CRITICAL IMPACT]
│   ├── presentation/
│   │   ├── listing/
│   │   │   ├── ListingDetailScreen.kt     [HIGH IMPACT]
│   │   │   └── ListingDetailViewModel.kt  [CRITICAL IMPACT]
│   │   ├── reservation/
│   │   │   ├── ReservationScreen.kt       [NEW FILE]
│   │   │   └── ReservationViewModel.kt    [NEW FILE]
│   │   └── purchase/
│   │       └── PurchaseViewModel.kt       [HIGH IMPACT]
│   └── analytics/
│       └── AnalyticsTracker.kt            [MEDIUM IMPACT]
└── test/
    ├── unit/
    │   └── reservation/                    [NEW TESTS]
    ├── integration/
    │   └── purchase_flow/                  [UPDATE TESTS]
    └── ui/
        └── reservation/                     [NEW TESTS]
```

### Blast Radius Map

Bob identified 3 impact zones:

**Zone 1: Core Transaction Logic (Critical)**
- ListingDao.kt
- MarketplaceApi.kt
- ListingRepository.kt
- PurchaseListingUseCase.kt
- ListingDetailViewModel.kt

**Zone 2: State Management (High)**
- AppDatabase.kt
- Listing.kt
- ListingDetailScreen.kt
- PurchaseViewModel.kt

**Zone 3: Supporting Systems (Medium)**
- AnalyticsTracker.kt
- Navigation.kt
- ErrorHandler.kt

### Risk Score Breakdown

Bob calculated a total risk score of **72/100** (High Risk):

```json
{
  "overall": 72,
  "breakdown": {
    "architecture": 65,
    "data": 80,
    "integration": 75,
    "userExperience": 60,
    "performance": 70
  },
  "factors": [
    {
      "category": "data",
      "risk": "Race condition between reservation and purchase",
      "severity": "critical",
      "mitigation": "Implement optimistic locking with version field"
    },
    {
      "category": "architecture",
      "risk": "Breaking change to existing purchase flow",
      "severity": "high",
      "mitigation": "Feature flag for gradual rollout"
    },
    {
      "category": "integration",
      "risk": "Offline mode complications",
      "severity": "high",
      "mitigation": "Queue reservations for sync when online"
    }
  ]
}
```

## Implementation

### Generated Shadow PR Data

Bob generated a complete Shadow PR JSON with:

1. **Repository Metadata**
```json
{
  "name": "UniMarket",
  "url": "https://github.com/example/unimarket",
  "branch": "main",
  "language": "Kotlin",
  "framework": "Android/Jetpack Compose",
  "linesOfCode": 45230,
  "lastCommit": "2026-05-10T14:23:00Z"
}
```

2. **Affected Files (23 files)**
   - 5 critical impact
   - 8 high impact
   - 7 medium impact
   - 3 low impact

3. **Blast Radius Visualization**
```json
{
  "zones": [
    {
      "name": "Core Transaction Logic",
      "impact": "critical",
      "files": 5,
