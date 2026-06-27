# Scoping Metadata Enrichment Improvement Plan

## Current State Analysis

**Current Fill Rate:** 72.9% (35 of 48 fields filled)
- Auto-filled: 20 fields (41.7%)
- Estimated: 15 fields (31.2%)
- Needs Input: 13 fields (27.1%)

**Target:** >85% fill rate (41+ of 48 fields)

---

## Gap Analysis: Missing Fields

### Critical Missing Fields (13 fields needing input):

1. **User Counts** (4 fields) - **HIGH IMPACT**
   - `core_users`
   - `self_service_users`
   - `end_users`
   - `target_trainees`

2. **WRICEF Objects** (1 field) - **HIGH IMPACT**
   - `conversions` (data objects count)

3. **Testing Volumes** (4 fields) - **MEDIUM IMPACT**
   - `automation_scenarios_sap_gui`
   - `automation_scenarios_fiori`
   - `test_scenarios_creation` (partially filled with proxy)
   - `test_scenarios_execution`

4. **Organization Details** (2 fields) - **MEDIUM IMPACT**
   - `no_of_divisions`
   - `company_revenue`

5. **Change Management** (2 fields) - **LOW IMPACT**
   - `ibm_involvement`
   - Additional training details

---

## Improvement Strategies

### Strategy 1: Enhanced User Count Extraction (Target: +4 fields = 81% fill rate)

**Problem:** RFPs rarely state exact user counts explicitly.

**Solution:** Implement intelligent estimation based on:

#### A. Employee Count Inference
```python
# Add to scoping_metadata_extractor.py

def _estimate_users_from_context(items: list, n_countries: int, n_plants: int) -> dict:
    """Estimate user counts from organizational scale."""
    
    # Look for employee mentions
    employee_patterns = [
        r'(\d+)\s*(?:employees|staff|personnel|workforce)',
        r'workforce\s+of\s+(\d+)',
        r'employing\s+(\d+)',
    ]
    
    combined_text = " ".join(_text(i) for i in items)
    employees = None
    
    for pattern in employee_patterns:
        match = re.search(pattern, combined_text, re.I)
        if match:
            employees = int(match.group(1))
            break
    
    # If no explicit count, estimate from scale
    if not employees:
        # Heuristic: plants * countries * avg_per_site
        base_per_site = 200  # Conservative estimate
        employees = max(n_plants, n_countries) * base_per_site
    
    # Calculate user distribution (industry standard ratios)
    core_users = int(employees * 0.15)  # 15% are core ERP users
    self_service = int(employees * 0.60)  # 60% are self-service (ESS/MSS)
    end_users = core_users + self_service
    trainees = int(core_users * 0.25)  # 25% of core users for TTT
    
    return {
        "employees": _meta(employees, "estimated", 
                          ["Derived from organizational scale"], 
                          f"Estimated: {n_plants} plants × {n_countries} countries"),
        "core_users": _meta(core_users, "estimated",
                           ["15% of workforce (industry standard)"],
                           "Core ERP users with full transaction access"),
        "self_service_users": _meta(self_service, "estimated",
                                   ["60% of workforce (ESS/MSS)"],
                                   "Self-service portal users"),
        "end_users": _meta(end_users, "estimated",
                          ["Core + Self-service"],
                          "Total system users"),
        "target_trainees": _meta(trainees, "estimated",
                                ["25% of core users for TTT"],
                                "Key users for Train-the-Trainer")
    }
```

#### B. Role-Based Estimation
Look for role mentions in requirements:
- "Finance team" → estimate FI users
- "Warehouse staff" → estimate WM users
- "Production operators" → estimate PP users

### Strategy 2: WRICEF Object Estimation (Target: +1 field = 83% fill rate)

**Problem:** Data conversion objects not explicitly listed in RFP.

**Solution:** Estimate from:

```python
def _estimate_data_objects(items: list, modules: list, n_source_systems: int) -> dict:
    """Estimate data migration objects from modules and source systems."""
    
    # Base objects per module (industry averages)
    module_data_objects = {
        "FI": 8,   # GL accounts, cost centers, profit centers, etc.
        "CO": 6,   # Cost elements, activity types, etc.
        "MM": 12,  # Material master, vendor master, purchasing info
        "SD": 10,  # Customer master, pricing, sales org data
        "PP": 15,  # BOMs, routings, work centers, production versions
        "QM": 8,   # Inspection plans, quality specs
        "PM": 10,  # Equipment master, maintenance plans
        "HR": 12,  # Employee master, org structure, payroll data
    }
    
    # Calculate base objects
    base_objects = sum(module_data_objects.get(m, 5) for m in modules)
    
    # Multiply by source systems (each system may have different data)
    total_objects = base_objects * max(n_source_systems, 1)
    
    # Add 20% for transactional data if historical migration mentioned
    if _has_kw(items, r'historical\s+data|open\s+orders|open\s+POs'):
        total_objects = int(total_objects * 1.2)
    
    return _meta(
        total_objects,
        "estimated",
        [f"Based on {len(modules)} modules × {n_source_systems} source systems"],
        f"Estimated {base_objects} objects per system"
    )
```

### Strategy 3: Testing Volume Estimation (Target: +3 fields = 89% fill rate)

**Problem:** Test scenario counts not in RFP.

**Solution:** Calculate from requirements and modules:

```python
def _estimate_testing_volumes(items: list, modules: list, n_countries: int) -> dict:
    """Estimate testing volumes from scope."""
    
    # Count testable requirements
    functional_reqs = [i for i in items if i.get("type") == "FR"]
    n_functional = len(functional_reqs)
    
    # Automation scenarios (30% of functional requirements)
    automation_total = int(n_functional * 0.30)
    
    # Split 70/30 between SAP GUI and Fiori
    automation_gui = int(automation_total * 0.70)
    automation_fiori = int(automation_total * 0.30)
    
    # SIT scenarios (1.5x functional requirements for integration testing)
    sit_scenarios = int(n_functional * 1.5)
    
    # Regression (50% of automation scenarios per rollout)
    regression_scenarios = int(automation_total * 0.50)
    
    return {
        "automation_scenarios_sap_gui": _meta(
            automation_gui, "estimated",
            [f"30% of {n_functional} functional requirements"],
            "70% SAP GUI, 30% Fiori split"
        ),
        "automation_scenarios_fiori": _meta(
            automation_fiori, "estimated",
            [f"30% of {n_functional} functional requirements"],
            "Fiori/Web-based test scenarios"
        ),
        "sit_scenarios_creation": _meta(
            sit_scenarios, "estimated",
            [f"1.5× functional requirements for integration testing"],
            "Includes end-to-end integration scenarios"
        ),
        "sit_scenarios_execution": _meta(
            sit_scenarios, "estimated",
            ["Same as creation count"],
            "Each scenario executed per SIT cycle"
        ),
        "regression_scenarios": _meta(
            regression_scenarios, "estimated",
            ["50% of automation scenarios"],
            "Modified scenarios per rollout"
        )
    }
```

### Strategy 4: Organization Details Inference (Target: +2 fields = 93% fill rate)

```python
def _estimate_organization_details(items: list, modules: list, n_countries: int) -> dict:
    """Estimate divisions and revenue from scope."""
    
    # Divisions: Look for business units, product lines, segments
    division_keywords = [
        r'(\d+)\s*(?:business units?|divisions?|segments?|product lines?)',
        r'(?:business units?|divisions?)\s*:\s*(\d+)',
    ]
    
    combined_text = " ".join(_text(i) for i in items)
    n_divisions = None
    
    for pattern in division_keywords:
        match = re.search(pattern, combined_text, re.I)
        if match:
            n_divisions = int(match.group(1))
            break
    
    # If not found, estimate from modules (CO module suggests divisions)
    if not n_divisions:
        if "CO" in modules:
            n_divisions = max(2, n_countries)  # At least 2, or 1 per country
        else:
            n_divisions = 1
    
    # Revenue: Look for explicit mentions or estimate from scale
    revenue_patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(?:billion|B)',
        r'revenue\s+of\s+\$(\d+(?:\.\d+)?)\s*(?:billion|B)',
        r'(\d+)\s*billion.*revenue',
    ]
    
    revenue_bracket = None
    for pattern in revenue_patterns:
        match = re.search(pattern, combined_text, re.I)
        if match:
            amount = float(match.group(1))
            if amount < 1:
                revenue_bracket = "<$1B USD"
            elif amount < 5:
                revenue_bracket = "$1B-$5B USD"
            elif amount < 10:
                revenue_bracket = "$5B-$10B USD"
            else:
                revenue_bracket = ">$10B USD"
            break
    
    # If not found, estimate from scale
    if not revenue_bracket:
        if n_countries >= 5 and len(modules) >= 8:
            revenue_bracket = "$1B-$5B USD"
        elif n_countries >= 3:
            revenue_bracket = "<$1B USD"
        else:
            revenue_bracket = "<$1B USD"
    
    return {
        "no_of_divisions": _meta(
            n_divisions, "estimated",
            ["Derived from business unit mentions or module scope"],
            f"Estimated from {n_countries} countries and CO module presence"
        ),
        "company_revenue": _meta(
            revenue_bracket, "estimated",
            ["Derived from organizational scale"],
            "Estimated from multi-country presence and module complexity"
        )
    }
```

---

## Implementation Plan

### Phase 1: Quick Wins (Week 1) - Target: 85% fill rate

1. **Update `scoping_metadata_extractor.py`:**
   - Add user count estimation function
   - Add data objects estimation
   - Add testing volume estimation
   - Add organization details inference

2. **Enhance extraction logic:**
   - Improve pattern matching for implicit mentions
   - Add fallback estimation formulas
   - Include confidence scoring

### Phase 2: Advanced Extraction (Week 2) - Target: 90% fill rate

1. **Add LLM-based extraction for ambiguous fields:**
   ```python
   def _llm_extract_missing_fields(items: list, missing_fields: list) -> dict:
       """Use LLM to extract fields that pattern matching missed."""
       # Build focused prompt for missing fields only
       # Use cheaper/faster model (GPT-3.5 or Claude Haiku)
       # Return structured JSON with confidence scores
   ```

2. **Implement cross-field validation:**
   - Validate user counts against employee count
   - Validate test scenarios against requirement count
   - Flag inconsistencies for manual review

### Phase 3: Continuous Improvement (Ongoing)

1. **Build feedback loop:**
   - Track which fields are manually corrected
   - Learn from corrections to improve patterns
   - Update estimation formulas based on actual data

2. **Add industry-specific templates:**
   - Pharmaceutical: Higher GMP testing, validation overhead
   - Manufacturing: More plants, production users
   - Financial Services: More compliance, fewer plants

---

## Expected Outcomes

| Phase | Fill Rate | Auto | Estimated | Needs Input |
|-------|-----------|------|-----------|-------------|
| Current | 72.9% | 20 | 15 | 13 |
| Phase 1 | 85%+ | 20 | 25 | 3 |
| Phase 2 | 90%+ | 25 | 20 | 3 |
| Phase 3 | 95%+ | 30 | 15 | 3 |

**Remaining "Needs Input" fields (always manual):**
1. Project start date (business decision)
2. IBM involvement level (commercial decision)
3. Specific client preferences not in RFP

---

## Code Changes Required

### File: `architecture_designer/scoping_metadata_extractor.py`

Add these new functions after line 100:

1. `_estimate_users_from_context()` - Lines 101-150
2. `_estimate_data_objects()` - Lines 151-180
3. `_estimate_testing_volumes()` - Lines 181-230
4. `_estimate_organization_details()` - Lines 231-280

### Update `extract_scoping_metadata()` function:

```python
def extract_scoping_metadata(enriched_json: dict) -> dict:
    """Main extraction function - enhanced version."""
    items = _all_items(enriched_json)
    
    # Extract geography first (needed for other estimations)
    geography = _extract_geography(items)
    n_countries = geography["no_of_countries"]["value"]
    n_plants = geography["no_of_plants"]["value"]
    
    # Extract applications and modules
    applications = _extract_applications(items)
    modules = applications["module_scope"]["value"]
    
    # NEW: Estimate users from context
    users = _estimate_users_from_context(items, n_countries, n_plants)
    
    # Extract WRICEF
    wricef = _extract_wricef(items)
    
    # NEW: Estimate data objects if missing
    if not wricef.get("conversions", {}).get("value"):
        n_source_systems = _extract_data_migration(items).get("no_of_source_systems", {}).get("value", 1)
        wricef["conversions"] = _estimate_data_objects(items, modules, n_source_systems)
    
    # NEW: Estimate testing volumes
    testing = _extract_testing(items)
    testing_estimates = _estimate_testing_volumes(items, modules, n_countries)
    testing.update(testing_estimates)
    
    # NEW: Estimate organization details
    org_details = _estimate_organization_details(items, modules, n_countries)
    geography.update(org_details)
    
    # Combine all sections
    return {
        "geography": geography,
        "users": users,  # Now populated!
        "applications": applications,
        "wricef": wricef,
        "data_migration": _extract_data_migration(items),
        "testing": testing,
        "security": _extract_security(items),
        "change_management": _extract_change_management(items),
        "implementation": _extract_implementation(items),
        "fill_summary": _calculate_fill_summary(...)
    }
```

---

## Testing Strategy

1. **Test with Kelix Bio RFP:**
   - Current: 35/48 fields (72.9%)
   - Target: 41/48 fields (85%+)
   - Focus on user counts, testing volumes, data objects

2. **Validate estimations:**
   - Compare estimated values with expected GSE values
   - Adjust formulas based on variance
   - Document assumptions in hints

3. **Edge cases:**
   - Small projects (<2 countries)
   - Large projects (>10 countries)
   - Missing module information
   - Minimal RFP detail

---

## Next Steps

1. **Immediate:** Implement Phase 1 enhancements
2. **This week:** Test with Kelix Bio RFP
3. **Next week:** Implement Phase 2 if needed
4. **Ongoing:** Collect feedback and refine

Would you like me to implement these enhancements now?