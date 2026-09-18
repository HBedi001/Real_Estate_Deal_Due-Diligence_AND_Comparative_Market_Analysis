# Parallel Workflow: Real Estate CMA & Due-Diligence Engine

## Graph Topology
```text
                  ┌─────────┐
                  │  START  │
                  └────┬────┘
                       │
                       ▼
                  ┌─────────┐
                  │ Intake  │
                  └────┬────┘
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
  ┌─────────────┐┌────────────┐┌───────────┐
  │Comps Analyst││Fin. Modeler││Risk Audit │
  └──────┬──────┘└─────┬──────┘└─────┬─────┘
         └─────────────┼─────────────┘
                       ▼
              ┌─────────────────┐
              │ Aggregator Memo │
              └────────┬────────┘
                       │
                       ▼
                    ┌─────┐
                    │ END │
                    └─────┘