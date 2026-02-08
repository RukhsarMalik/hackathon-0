---
type: business_goals_config
last_updated: 2026-02-06
version: 1.0
---

# Business Goals Configuration

## Monthly Revenue Targets

```yaml
monthly_revenue_target: 50000
current_month: 2026-02
revenue_targets:
  - month: 2026-02
    target: 50000
    description: "February revenue goal"
    stretch_goal: 60000
  - month: 2026-03
    target: 55000
    description: "March revenue goal"
    stretch_goal: 65000
```

## Project Deadlines

```yaml
project_deadlines:
  - name: "Q1 Product Launch"
    due_date: 2026-03-15
    description: "Critical milestone delivery for Q1"
    priority: high
    status: in_progress
  - name: "System Migration"
    due_date: 2026-04-30
    description: "Migration to new infrastructure"
    priority: medium
    status: planned
```

## Subscriptions

```yaml
subscriptions:
  - name: "Cloud Service Pro"
    monthly_cost: 199.99
    renewal_date: 2026-03-01
    last_used: 2026-02-06
    category: "Infrastructure"
    owner: "Engineering Team"
  - name: "Analytics Platform"
    monthly_cost: 299.00
    renewal_date: 2026-02-15
    last_used: 2026-02-05
    category: "Business Intelligence"
    owner: "Business Team"
```

## KPIs

```yaml
kpis:
  - name: "Customer Acquisition Rate"
    target: 10
    unit: "customers/month"
    description: "New customers acquired per month"
  - name: "Task Completion Rate"
    target: 95
    unit: "%"
    description: "Percentage of tasks completed within SLA"
  - name: "Revenue Growth"
    target: 10
    unit: "%"
    description: "Month-over-month revenue growth percentage"
```
