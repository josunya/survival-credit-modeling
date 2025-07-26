# Why skpro May Be Too Sophisticated for Phase 1

## Phase 1 Explicit Requirements vs. skpro Capabilities

**Phase 1 calls for "Simple empirical methods":**
- Manual rate calculations: `Payment Rate = Total Payments / Starting Principal`
- Basic survival probability adjustments for censoring
- Transparent, table-based outputs that stakeholders can verify by hand

**skpro provides:**
- Advanced probabilistic regression models
- Sophisticated distribution fitting algorithms
- Complex statistical transformations
- Abstract probabilistic prediction interfaces

## Stakeholder Management Concerns

**Phase 1 Priority: "Stakeholder buy-in and trust"**
- PRD emphasizes outputs "stakeholders can understand without technical explanation"
- Business users need to see intermediate calculation steps
- Manual validation requires ability to reproduce results in Excel

**skpro Challenge:**
- Black-box probabilistic models harder to explain
- Model internals not easily inspectable
- Predictions come as distributions, not simple rates
- Requires statistical sophistication to interpret outputs

## Implementation Complexity

**Phase 1 Goal: "Process single vintage/segment in <1 hour"**
- Simple CSV input/output
- Basic data quality checks
- Straightforward business logic validation

**skpro Requirements:**
- Understanding probabilistic prediction frameworks
- Learning new API and data structures
- Debugging model fitting issues
- Interpreting probabilistic metrics

## Risk Assessment

**Using skpro in Phase 1 risks:**
1. **Scope creep**: Team gets distracted by advanced features
2. **Stakeholder confusion**: Business users can't validate methodology
3. **Timeline delays**: Learning curve and debugging complex models
4. **Trust erosion**: "Black box" perception undermines confidence

**Better Phase 1 approach:**
- Start with pandas/numpy calculations
- Build stakeholder confidence with transparency
- Establish validation framework with simple methods
- **Then** introduce skpro in Phase 2 when sophistication is explicitly required

The PRD wisely sequences complexity - Phase 1 is about methodology acceptance, not technical sophistication.