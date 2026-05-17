# Skill: Analyze Shadow PR Impact

## Description
Generate a comprehensive Shadow PR analysis for a given repository and change request, identifying affected files, calculating blast radius, assessing risks, and creating an implementation plan.

## Inputs
- `repository_name`: Name of the target repository
- `change_request`: Natural language description of the proposed change
- `analysis_mode`: "demo" (use sample data) or "live" (perform real analysis)

## Process

### 1. Understand the Change Request
- Parse the natural language change request
- Identify key entities (models, APIs, UI components)
- Determine the scope (backend, frontend, database, etc.)

### 2. Analyze Repository Structure
- Read repository file structure
- Identify main modules and their relationships
- Map dependencies between components
- Understand the technology stack

### 3. Calculate Blast Radius
- Identify directly affected files (files that must be modified)
- Identify indirectly affected files (files that depend on changed files)
- Calculate impact metrics:
  - Total files affected
  - Functions/classes affected
  - Tests that need updates
  - Percentage of codebase impacted

### 4. Assess Risks
- Identify breaking changes
- Evaluate state management complexity
- Check for race conditions
- Assess performance impact
- Consider backward compatibility
- Calculate overall risk score (0-100)

### 5. Generate Regression Pack
- List breaking changes with migration paths
- Identify behavior changes
- Recommend new tests needed
- Identify existing tests to update
- Calculate coverage gaps

### 6. Create Implementation Contract
- Break work into phases
- Estimate effort per phase
- Define checkpoints for each phase
- Create rollback strategy
- List prerequisites

### 7. Generate PR Brief
- Write summary of changes
- List key impact points
- Include risk assessment
- Provide implementation guidance
- Add testing recommendations

## Outputs
- `shadow_pr.json`: Complete Shadow PR analysis
- `affected_files`: List of files with impact details
- `risk_assessment`: Risk factors and mitigation strategies
- `implementation_plan`: Phase-by-phase implementation guide
- `test_recommendations`: Testing strategy

## Example Usage

```
Analyze Shadow PR for:
Repository: UniMarket
Change Request: Add reservation flow before purchase
Mode: demo
```

## Quality Checks
- [ ] All affected files have reasoning
- [ ] Risk score is justified by factors
- [ ] Implementation plan is actionable
- [ ] Test recommendations are specific
- [ ] PR brief is copy-ready

## Related Skills
- `parse-repository-structure`
- `calculate-code-dependencies`
- `assess-change-risk`
- `generate-test-plan`

---

**Built with IBM Bob IDE**