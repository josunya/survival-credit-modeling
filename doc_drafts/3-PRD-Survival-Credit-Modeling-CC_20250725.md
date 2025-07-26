# Product Requirements Document: Survival Credit Modeling Tool
**Comprehensive Phased Approach for Forecasting and Performance Monitoring**

---

## Executive Summary

This PRD outlines the development of a comprehensive survival credit modeling tool designed to forecast loan performance and systematically monitor variance from expectations across product segments, credit qualities, and vintages. The approach emphasizes explainability and transparency, starting with a simple foundation and progressively adding sophistication over four distinct phases.

The tool will enable lenders to:
- Forecast monthly principal payments, remaining balances, and charge-offs
- Systematically process multiple segment/vintage combinations
- Identify performance trends above or below expectations
- Provide clear explanations for variance to management and stakeholders

---

## 1. Business Objective

**Primary Goal**: Build a systematic forecasting tool that uses survival/hazard modeling to predict loan performance at the segment and vintage level, with clear explainability for business stakeholders.

**Key Business Questions to Address**:
- How will each vintage/segment perform over its remaining life?
- Where is actual performance trending vs. our expectations?
- What factors are driving performance variance?
- How confident should we be in our forecasts?

---

## 2. Stakeholders

**Primary Stakeholders**:
- Portfolio Analytics Team (Primary Users)
- Data Science Team (Technical Development)
- Finance/Risk Teams (Business Consumers)

**Secondary Stakeholders**:
- Executive Management (Strategic Oversight)
- Credit Risk Management (Policy Implications)
- Investor Relations (External Reporting)

---

## 3. Methodology Overview (For Non-Technical Stakeholders)

### What is Survival Modeling?
Survival modeling is a statistical approach originally developed for medical research to predict patient outcomes over time. In lending, we adapt this methodology to predict loan outcomes:

- **Survival**: A loan "survives" when it continues to make payments without charging off
- **Hazard Rate**: The probability that a loan will experience an event (payment or charge-off) in a given month, given it has survived to that point
- **Censoring**: Some loans are still active at the end of our observation period, requiring special statistical handling

### How It Works (Simple Explanation)
1. **Historical Analysis**: We analyze how similar loans performed in the past
2. **Pattern Recognition**: We identify patterns in payment and charge-off behavior over loan age
3. **Rate Estimation**: We calculate monthly probabilities for payments and charge-offs
4. **Forecasting**: We apply these probabilities to predict future performance
5. **Monitoring**: We compare actual performance to predictions and investigate differences

### Why This Approach?
- **Handles Time Dynamics**: Loan behavior changes as loans age
- **Accounts for Uncertainty**: Provides confidence intervals, not just point estimates
- **Flexible**: Can accommodate different loan types and market conditions
- **Explainable**: Clear connection between historical patterns and future predictions

---

## 4. Phased Development Approach

### Overview of Phases
This project follows a four-phase approach, with each phase building upon the previous while maintaining backward compatibility and transparency:

**Phase 1**: Foundation & Explainability (Months 1-3)
**Phase 2**: Enhanced Modeling (Months 4-6)
**Phase 3**: Systematic Tool (Months 7-9)
**Phase 4**: Advanced Analytics (Months 10-12)

---

## 5. Phase 1: Foundation & Explainability

### Objective
Establish a simple, transparent foundation with clear methodology that stakeholders can understand and trust.

### Scope
- **Single vintage/segment focus**: Process one combination at a time
- **Simple empirical methods**: Use straightforward rate calculations
- **Transparent outputs**: Clear tabular results with intermediate steps shown
- **Manual validation**: Human-in-the-loop verification

### Data Requirements
- Historical loan-level data aggregated by month of age
- Fields required:
  - Loan age (months since origination)
  - Starting principal balance
  - Principal payments made
  - Principal charged off
  - Number of loans (for aggregated data)

### Functional Requirements

#### Core Functionality
1. **Data Ingestion**
   - Accept CSV/Excel files with historical performance data
   - Basic data quality checks and error reporting
   - Handle right-censored observations (active loans)

2. **Hazard Rate Estimation**
   - Calculate empirical monthly payment rates: `Payment Rate = Total Payments / Starting Principal`
   - Calculate empirical monthly charge-off rates: `Charge-off Rate = Total Charge-offs / Starting Principal`
   - Account for right-censoring using simple survival probability adjustments

3. **Forecasting Engine**
   - Accept user input of actual performance through a specific month
   - Apply estimated hazard rates to forecast remaining months
   - Calculate: Starting Balance → Payments → Charge-offs → Ending Balance

4. **Output Generation**
   - Produce simple tabular format (CSV/Excel compatible)
   - Columns: Month, Starting_Principal, Payment_Amount, Chargeoff_Amount, Ending_Principal, Payment_Rate, Chargeoff_Rate

### Validation Requirements (Phase 1)
1. **Business Logic Validation**
   - Payment rates should be between 0-100%
   - Charge-off rates should be between 0-100%
   - Ending principal should equal starting principal minus payments minus charge-offs
   - Rates should generally decrease as loans mature (business reasonableness)

2. **Manual Review Process**
   - Generate summary statistics for stakeholder review
   - Provide visual plots of estimated rates by loan age
   - Compare estimated rates to business expectations/benchmarks
   - Document assumptions and limitations clearly

3. **Holdout Validation**
   - Train model on data up to month X
   - Test predictions on months X+1 through Y
   - Calculate simple error metrics (MAPE, RMSE)
   - Report accuracy in business-friendly terms

### Success Criteria (Phase 1)
- [ ] Process single vintage/segment from raw data to forecast in <1 hour
- [ ] Generate outputs that stakeholders can understand without technical explanation
- [ ] Achieve prediction accuracy within 10% MAPE on holdout validation
- [ ] Gain stakeholder sign-off on methodology and approach
- [ ] Complete documentation suitable for business users

### Deliverables (Phase 1)
1. **Technical Deliverables**
   - Python/R scripts for data processing and modeling
   - Forecasting engine with clear, commented code
   - Input/output specifications and data dictionary

2. **Business Deliverables**
   - Methodology documentation for non-technical stakeholders
   - Sample forecasts with interpretation
   - Validation report with accuracy metrics
   - User guide for running forecasts

---

## 6. Phase 2: Enhanced Modeling

### Objective
Expand to multiple segments/vintages with sophisticated statistical methods while maintaining transparency.

### Scope
- **Multi-segment processing**: Handle multiple vintage/segment combinations
- **Advanced survival models**: Implement Kaplan-Meier, Cox proportional hazards
- **Statistical validation**: Comprehensive backtesting and model comparison
- **Performance analysis**: Compare actual vs predicted performance

### Enhanced Data Requirements
- **Segmentation variables**: Credit score bands, product types, origination channels
- **Time-varying covariates**: Economic indicators, seasonal factors
- **Expanded historical data**: Multiple vintages for cross-validation

### Functional Requirements

#### Advanced Modeling
1. **Kaplan-Meier Estimation**
   - Non-parametric survival function estimation
   - Handle right-censoring more rigorously
   - Generate survival curves by segment

2. **Cox Proportional Hazards Model**
   - Incorporate covariates (credit score, loan amount, etc.)
   - Estimate hazard ratios and confidence intervals
   - Test proportional hazards assumption

3. **Model Comparison Framework**
   - Compare simple empirical vs. Kaplan-Meier vs. Cox models
   - Use AIC/BIC for model selection
   - Cross-validation across vintages

#### Multi-Segment Processing
1. **Batch Processing Capability**
   - Process multiple segment/vintage combinations
   - Parallel processing for efficiency
   - Error handling and logging

2. **Segment-Specific Models**
   - Allow different models for different segments
   - Automatic model selection based on data characteristics
   - Minimum sample size requirements

### Validation Requirements (Phase 2)
1. **Statistical Validation Framework**
   - **Cross-validation**: Train on vintages 1-N, test on vintage N+1
   - **Backtesting**: Rolling window validation across time periods
   - **Model diagnostics**: Residual analysis, goodness-of-fit tests

2. **Performance Metrics**
   - **Accuracy**: MAPE, RMSE, MAE by segment and forecast horizon
   - **Calibration**: Are predicted probabilities well-calibrated?
   - **Discrimination**: Can model distinguish high-risk from low-risk segments?

3. **Comparison Analysis**
   - Compare multiple model approaches
   - Identify best-performing model by segment type
   - Document when simple methods outperform complex ones

### Success Criteria (Phase 2)
- [ ] Process 10+ segment/vintage combinations simultaneously
- [ ] Achieve 15% improvement in accuracy over Phase 1 methods
- [ ] Complete statistical validation meeting data science standards
- [ ] Demonstrate model generalization across different vintages
- [ ] Stakeholder approval for production deployment

---

## 7. Phase 3: Systematic Tool

### Objective
Create an automated, systematic tool for monthly business processes with trend detection and root cause analysis.

### Scope
- **Production automation**: Monthly batch processing of all combinations
- **Trend detection**: Identify performance above/below expectations
- **Root cause analysis**: Explain why performance differs from forecasts
- **Management reporting**: Executive dashboards and alerts

### Functional Requirements

#### Automation & Orchestration  
1. **Monthly Processing Pipeline**
   - Automated data ingestion from source systems
   - Batch processing of all segment/vintage combinations
   - Automated quality checks and exception handling
   - Scheduled execution with monitoring and alerting

2. **Configuration Management**
   - Model parameters by segment stored in configuration files
   - Business rules and thresholds centrally managed
   - Version control for model changes and updates

#### Performance Monitoring & Analysis
1. **Variance Detection**
   - Compare actual vs. predicted performance monthly
   - Statistical significance testing for differences
   - Automated flagging of segments with material variance

2. **Root Cause Analysis**
   - Decompose variance into components (timing, magnitude, mix)
   - Correlate with external factors (economic conditions, policy changes)
   - Generate automated hypotheses for performance differences

3. **Trend Analysis**
   - Identify systematic trends over multiple months
   - Distinguish between random variation and systematic shifts
   - Early warning system for emerging risks

#### Management Reporting
1. **Executive Dashboard**
   - High-level performance summary across all segments
   - Key variance alerts and explanations
   - Trend indicators and forward-looking insights

2. **Detailed Analytics**
   - Drill-down capability by segment, vintage, and time period
   - Interactive visualizations with narrative explanations
   - Export capabilities for further analysis

### Validation Requirements (Phase 3)
1. **Automated Validation Pipeline**
   - **Champion/Challenger Framework**: Test new models against production models
   - **Performance Monitoring**: Track model performance over time
   - **Drift Detection**: Identify when models need retraining

2. **Business Validation**
   - **Materiality Thresholds**: Define when variance requires action
   - **False Positive Management**: Minimize unnecessary alerts
   - **Stakeholder Feedback Loop**: Incorporate business judgment

### Success Criteria (Phase 3)
- [ ] Process 100+ segment/vintage combinations monthly without manual intervention
- [ ] Detect material variance within 2 business days of data availability
- [ ] Provide actionable explanations for 80% of detected variances
- [ ] Executive dashboard adoption by senior management
- [ ] Integration with existing business processes and reporting

---

## 8. Phase 4: Advanced Analytics

### Objective
Implement state-of-the-art techniques for maximum accuracy and sophistication while maintaining explainability.

### Scope
- **Machine learning enhancement**: Advanced algorithms with explainable AI
- **Real-time monitoring**: Near real-time performance tracking
- **Scenario analysis**: Stress testing and sensitivity analysis
- **Regulatory compliance**: Documentation and validation for regulatory requirements

### Advanced Functional Requirements

#### Machine Learning Enhancements
1. **Ensemble Methods**
   - Combine multiple model approaches (statistical + ML)
   - Gradient boosting, random forests with survival objectives
   - Maintain explainability through SHAP values and feature importance

2. **Deep Learning**
   - Neural networks for complex pattern recognition
   - Attention mechanisms for time series forecasting
   - Explainable AI techniques for model interpretation

#### Real-Time Capabilities
1. **Streaming Data Processing**
   - Near real-time ingestion of performance data
   - Continuous model updating and recalibration
   - Real-time alerts and notifications

2. **Dynamic Modeling**
   - Adaptive models that evolve with changing conditions
   - Concept drift detection and automatic retraining
   - A/B testing framework for model improvements

#### Advanced Analytics
1. **Scenario Analysis**
   - Stress testing under adverse economic conditions
   - Sensitivity analysis for key model parameters
   - Monte Carlo simulation for uncertainty quantification

2. **Regulatory Features**
   - Model documentation meeting regulatory standards
   - Audit trail for all model decisions and changes
   - Compliance reporting and validation

### Success Criteria (Phase 4)
- [ ] Achieve best-in-class forecasting accuracy
- [ ] Maintain explainability despite model complexity
- [ ] Meet regulatory requirements for model validation
- [ ] Enable real-time decision making
- [ ] Establish competitive advantage through advanced analytics

---

## 9. Comprehensive Validation Framework

### Validation Philosophy
Validation rigor increases with model complexity, but explainability remains paramount at all phases.

### Phase-Specific Validation Approach

#### Phase 1: Foundation Validation
- **Focus**: Business reasonableness and stakeholder acceptance
- **Methods**: Manual review, simple backtesting, business logic checks
- **Frequency**: End of development, before Phase 2 progression
- **Stakeholders**: Business users, portfolio analytics team

#### Phase 2: Statistical Validation  
- **Focus**: Statistical rigor and model comparison
- **Methods**: Cross-validation, model diagnostics, formal backtesting
- **Frequency**: During development and before production deployment
- **Stakeholders**: Data science team, risk management

#### Phase 3: Production Validation
- **Focus**: Ongoing performance monitoring and business impact
- **Methods**: Champion/challenger, performance tracking, drift detection
- **Frequency**: Continuous monitoring with monthly formal reviews
- **Stakeholders**: All stakeholders, automated systems

#### Phase 4: Advanced Validation
- **Focus**: Regulatory compliance and competitive benchmarking
- **Methods**: Stress testing, regulatory validation, external benchmarking
- **Frequency**: Quarterly formal validation with ongoing monitoring
- **Stakeholders**: Regulatory affairs, executive management

### Key Validation Metrics

#### Accuracy Metrics
- **Mean Absolute Percentage Error (MAPE)**: Primary business metric
- **Root Mean Square Error (RMSE)**: Technical accuracy measure
- **Median Absolute Error (MAE)**: Robust accuracy measure

#### Model Quality Metrics
- **Calibration**: Are predicted probabilities accurate?
- **Discrimination**: Can model distinguish different risk levels?
- **Stability**: How consistent are predictions over time?

#### Business Impact Metrics
- **Decision Quality**: Do forecasts lead to better business decisions?
- **Early Warning**: How quickly does model detect problems?
- **Stakeholder Satisfaction**: User adoption and feedback scores

---

## 10. Implementation Roadmap

### Timeline Overview
- **Total Duration**: 12 months
- **Phase Gates**: Formal review and approval required between phases
- **Parallel Development**: Some components can be developed concurrently

### Detailed Timeline

#### Months 1-3: Phase 1 Development
**Month 1**: Requirements finalization, data preparation, initial modeling
**Month 2**: Core functionality development, basic validation
**Month 3**: Testing, documentation, stakeholder review and approval

#### Months 4-6: Phase 2 Development  
**Month 4**: Advanced modeling implementation, multi-segment capability
**Month 5**: Statistical validation framework, model comparison
**Month 6**: Production readiness, performance testing, stakeholder training

#### Months 7-9: Phase 3 Development
**Month 7**: Automation framework, batch processing, monitoring systems
**Month 8**: Dashboard development, reporting, root cause analysis
**Month 9**: Integration testing, user acceptance testing, production deployment

#### Months 10-12: Phase 4 Development
**Month 10**: Advanced analytics implementation, ML model development
**Month 11**: Real-time capabilities, regulatory compliance features
**Month 12**: Final validation, documentation, knowledge transfer

### Resource Requirements

#### Technical Team
- **Lead Data Scientist**: Full-time across all phases
- **Senior Data Scientist**: Full-time Phases 2-4
- **Data Engineer**: Full-time Phases 3-4  
- **MLOps Engineer**: Part-time Phases 3-4

#### Business Team
- **Portfolio Analytics Lead**: Part-time across all phases
- **Business Analyst**: Full-time Phases 1-2, part-time Phases 3-4
- **Risk Management SME**: Part-time across all phases

### Success Criteria by Phase

#### Phase 1 Gate Criteria
- [ ] Methodology approved by all stakeholders
- [ ] Single segment forecasting accuracy <10% MAPE
- [ ] Documentation complete and stakeholder-approved
- [ ] User training completed

#### Phase 2 Gate Criteria  
- [ ] Multi-segment processing capability demonstrated
- [ ] Statistical validation framework complete
- [ ] Model accuracy improvement >15% vs Phase 1
- [ ] Production deployment readiness confirmed

#### Phase 3 Gate Criteria
- [ ] Automated monthly processing operational
- [ ] Management dashboards deployed and adopted
- [ ] Variance detection and explanation capability proven
- [ ] Integration with business processes complete

#### Phase 4 Gate Criteria
- [ ] Advanced analytics capabilities operational
- [ ] Regulatory validation requirements met
- [ ] Real-time monitoring system deployed
- [ ] Competitive advantage demonstrated

---

## 11. Risk Management

### Technical Risks

#### Data Quality Risk
- **Risk**: Poor data quality leads to unreliable forecasts
- **Mitigation**: Comprehensive data validation, multiple data sources, manual review processes
- **Contingency**: Fallback to external benchmarks or conservative assumptions

#### Model Risk
- **Risk**: Models fail to generalize to new conditions
- **Mitigation**: Robust validation framework, champion/challenger approach, ongoing monitoring
- **Contingency**: Manual override capabilities, rapid model retraining procedures

#### Technical Risk
- **Risk**: System failures disrupt business processes
- **Mitigation**: Redundant systems, automated monitoring, comprehensive testing
- **Contingency**: Manual backup processes, rapid recovery procedures

### Business Risks

#### Stakeholder Adoption Risk
- **Risk**: Users don't adopt or trust the new system
- **Mitigation**: Extensive stakeholder engagement, gradual rollout, comprehensive training
- **Contingency**: Extended support period, additional training, system modifications

#### Regulatory Risk
- **Risk**: Models don't meet regulatory requirements
- **Mitigation**: Early regulatory engagement, comprehensive documentation, formal validation
- **Contingency**: Regulatory remediation plan, external validation, system modifications

---

## 12. Success Metrics

### Technical Success Metrics
- **Accuracy**: MAPE <5% for established segments, <10% for new segments
- **Coverage**: Process 95% of segment/vintage combinations successfully
- **Performance**: Complete monthly processing within 4 hours
- **Reliability**: >99% system uptime, <1% data processing errors

### Business Success Metrics
- **Decision Quality**: Demonstrate improved business outcomes from forecasting
- **Early Detection**: Identify material variances within 2 business days
- **User Adoption**: >90% of target users actively using the system
- **Stakeholder Satisfaction**: >4.0/5.0 average rating on user surveys

### Strategic Success Metrics
- **Competitive Advantage**: Best-in-class forecasting accuracy vs industry benchmarks
- **Regulatory Compliance**: Pass all regulatory examinations and audits
- **Business Impact**: Quantifiable improvement in risk management and capital planning
- **Innovation**: Recognition as industry leader in survival modeling applications

---

## Conclusion

This comprehensive PRD provides a structured, phased approach to developing a state-of-the-art survival credit modeling tool. By starting with a simple, explainable foundation and progressively adding sophistication, we ensure stakeholder buy-in, technical rigor, and business value at each stage.

The emphasis on explainability, systematic processing, and performance monitoring addresses the core business need to understand not just what will happen, but why performance differs from expectations. This approach positions the organization to make better-informed decisions and maintain competitive advantage in credit risk management.

The phased development approach manages risk while ensuring continuous delivery of business value, with clear gates and success criteria at each stage. The comprehensive validation framework ensures model reliability and regulatory compliance while maintaining the transparency essential for stakeholder confidence.