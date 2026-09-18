# Real_Estate_Deal_Due-Diligence_AND_Comparative_Market_Analysis
Markdown# Real Estate Due-Diligence & CMA LangGraph Agent

An autonomous, multi-agent real estate due-diligence system built with [LangGraph](https://github.com/langchain-ai/langgraph) and OpenAI. The graph implements a **Parallel Fan-Out / Fan-In Workflow** to evaluate residential properties, benchmark comparative market data, calculate investment yields, assess exposure risks, and generate an executive acquisition memo.

---

## Architecture Overview

The system uses a stateful directed graph where an initial intake node fans out concurrently into three specialized evaluation agents, which converge into an aggregator node.

```text
                  ┌─────────────────┐
                  │      START      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Intake Node   │
                  └────────┬────────┘
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │Comps Analyst│  │ Fin Modeler │  │ Risk Auditor│
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          └────────────────┼────────────────┘
                           ▼
                  ┌─────────────────┐
                  │ Aggregator Memo │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │       END       │
                  └─────────────────┘
Key Workflow ConceptsParallel Execution (Fan-Out): The intake node dispatches the property payload to three worker nodes (comps_analyst, financial_modeler, risk_assessor) simultaneously.State Management & Reducers: Uses Annotated[List[str], operator.add] to enable concurrent nodes to append their findings to the shared analysis_reports state without race conditions or data clobbering.Aggregator Node (Fan-In): Waits for all parallel branches to complete, then synthesizes technical metrics and risk flags into an institutional-grade investment verdict.Project StructurePlaintext.
├── .env.example              # Template for API keys
├── .gitignore                # Ignored environments and caches
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── architecture.md           # Graph mechanics and topology details
└── real_estate_cma_graph.py  # Standalone LangGraph pipeline & runner
Prerequisites & InstallationClone the repository:Bashgit clone <your-repo-link>
cd <your-repo-folder>
Create and activate a virtual environment:Bashpython -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
Install dependencies:Bashpip install -r requirements.txt
Set up environment variables:
Copy .env.example to .env and add your OpenAI API key:  Bashcp .env.example .env
Edit .env:Code snippetOPENAI_API_KEY=your-openai-api-key-here
UsageRun the graph directly from your terminal:Bashpython real_estate_cma_graph.py
Sample Input PayloadPythonsample_deal = {
    "address": "42 Meadow Lane, Huntington, NY",
    "property_type": "Single Family Residence",
    "asking_price": 625000.0,
    "sqft": 2100,
    "bedrooms": 4,
    "bathrooms": 2,
    "estimated_monthly_rent": 4200.0,
    "annual_taxes": 12800.0,
}
Sample Output SummaryThe agent outputs structured console logs showing each execution stage, followed by the final decision memo:Executive Verdict: Counter-offer, Buy, or PassDeal Highlights: Cap rate, Gross Yield, Price per SqFt comparisonRed Flags: Property tax burden ratio, inspection requirements, and vacancy exposureBuilt ForDeveloped as part of Nisarg's AI Master Class (LangGraph Parallel Workflow Module).
---

### Comprehension Check

1. Why is it beneficial to explicitly outline the state reducer (`operator.add`) inside the README's **Key Workflow Concepts** section when submitting this to an evaluator?
2. If an evaluator runs `pip install -r requirements.txt` on a clean machine, what environment issue could cause `langchain_openai` to fail at runtime if not clearly documented in the prerequisites?

<ElicitationsGroup message="Next steps for your documentation and code:">
  <Elicitation label="Draft architecture.md file" query="Write the architecture.md file matching the exact repository standards."/>
  <Elicitation label="Add sample output to README" query="Add a full sample terminal output section to the README.md."/>
  <Elicitation label="Prepare GitHub push commands" query="Give me the Git commands to initialize, commit, and push this to GitHub."/>
</ElicitationsGroup>
