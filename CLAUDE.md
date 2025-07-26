# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains the design and planning documents for a **Survival Credit Modeling Tool** - a comprehensive system for forecasting loan performance using survival/hazard modeling at the segment and vintage level. The project is in the planning/requirements phase with no code implementation yet.

## Project Structure & Key Documents

### Requirements Documents
- **`Comprehensive-PRD-Survival-Credit-Modeling.md`**: Primary PRD with 4-phase development approach
- **`1-PRD-DRAFT-GPT41_20250725.md`**: Initial comprehensive PRD draft
- **`2-PRD-DRAFT-GPT41_20250725.md`**: Focused V1 scope PRD draft
- **`3-PRD-Survival-Credit-Modeling-CC_20250725.md`**: Alternative PRD version

### Technical Analysis Documents
- **`4-skpro-evaluation-plan_20250725.md`**: Analysis of skpro package suitability for the project
- **`5-skpro-phase1-complexity-assessment.md`**: Assessment of using skpro in Phase 1 vs later phases

## Development Approach

The project follows a **4-phase approach** emphasizing explainability first:

### Phase 1: Foundation & Explainability (Months 1-3)
- Simple empirical hazard rate estimation
- Single vintage/segment processing
- Transparent tabular outputs
- Manual validation and stakeholder buy-in

### Phase 2: Enhanced Modeling (Months 4-6)
- Statistical survival models (Kaplan-Meier, Cox)
- Multi-segment processing capability
- Comprehensive validation framework

### Phase 3: Systematic Tool (Months 7-9)
- Automated monthly processing pipeline
- Performance monitoring and variance detection
- Management dashboards and reporting

### Phase 4: Advanced Analytics (Months 10-12)
- Machine learning enhancements
- Real-time monitoring capabilities
- Regulatory compliance features

## Technical Stack Considerations

### Recommended for Phase 1
- **Python** with basic data science libraries (pandas, numpy, matplotlib)
- Simple empirical calculations for transparency
- CSV/Excel output formats for stakeholder review

### Recommended for Phase 2+
- **skpro package**: Evaluated as strong fit for probabilistic survival modeling
- Advanced statistical libraries for survival analysis
- Automated validation and backtesting frameworks

## Core Business Logic

### Key Concepts
- **Survival Modeling**: Predicting loan payment and charge-off behavior over time
- **Hazard Rates**: Monthly probabilities of payment/charge-off events
- **Right Censoring**: Handling loans still active at data cutoff
- **Segment/Vintage Analysis**: Grouping loans by origination period and risk characteristics

### Critical Calculations
```
Payment Rate = Total Payments / Starting Principal
Charge-off Rate = Total Charge-offs / Starting Principal
Ending Principal = Starting Principal - Payments - Charge-offs
```

## Data Requirements

### Input Data Structure
- Loan-level or aggregated data by segment/vintage
- Required fields: loan age, starting principal, payments, charge-offs, loan count
- Time series format with monthly observations
- Proper handling of right-censored observations

### Output Requirements
- Tabular format (CSV/Excel compatible)
- Columns: Month, Starting_Principal, Payment_Amount, Chargeoff_Amount, Ending_Principal, Payment_Rate, Chargeoff_Rate
- Transparent intermediate calculations for validation

## Validation Requirements

### Phase-Appropriate Validation
- **Phase 1**: Business logic validation, manual review, simple backtesting
- **Phase 2**: Statistical validation, cross-validation, model comparison
- **Phase 3**: Production monitoring, champion/challenger framework
- **Phase 4**: Regulatory validation, stress testing

### Key Metrics
- **Accuracy**: MAPE (Mean Absolute Percentage Error), RMSE, MAE
- **Business Reasonableness**: Rates within 0-100%, logical progression over loan age
- **Stakeholder Acceptance**: Understanding and trust in methodology

## Implementation Notes

### Phase 1 Emphasis
- **Explainability is paramount**: Every calculation must be transparent and manually verifiable
- **Start simple**: Resist temptation to use sophisticated methods initially
- **Stakeholder engagement**: Business users must understand and approve methodology
- **Documentation**: Extensive business-friendly documentation required

### Technical Debt Management
- Each phase builds upon previous while maintaining backward compatibility
- Modular design to accommodate increasing sophistication
- Clear interfaces between business logic and modeling components

## Current Status

**Status**: Planning/Requirements phase - no code implementation exists yet

**Next Steps**: Begin Phase 1 implementation with focus on:
1. Simple data ingestion and processing
2. Basic empirical hazard rate calculation
3. Transparent forecasting engine
4. Tabular output generation
5. Comprehensive business documentation