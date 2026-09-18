# Real Estate Due-Diligence & CMA LangGraph Agent

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
```

### Key Workflow Concepts
* **Parallel Execution (Fan-Out):** The intake node dispatches the property payload to three worker nodes (`comps_analyst`, `financial_modeler`, `risk_assessor`) simultaneously.
* **State Management & Reducers:** Uses `Annotated[List[str], operator.add]` to enable concurrent nodes to append their findings to the shared `analysis_reports` state without race conditions or data overwrites.
* **Aggregator Node (Fan-In):** Waits for all parallel branches to complete, then synthesizes technical metrics and risk flags into an institutional-grade investment verdict.

---

## Project Structure

```text
.
├── .env.example              # Template for API keys
├── .gitignore                # Ignored virtual environments and keys
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── architecture.md           # Graph mechanics and topology details
└── real_estate_cma_graph.py  # Standalone LangGraph pipeline & runner
```

---

## Prerequisites & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd <your-repo-folder>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell):
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   ```

---

## Usage

Run the graph directly from your terminal:

```bash
python real_estate_cma_graph.py
```

### Interactive Address Input
When prompted, enter a full street address or type `Quit` to exit:

```text
Type Quit to exit. Please enter address: 42 Meadow Lane, Huntington, NY
```

---

## Sample Terminal Output

```text
--- GRAPH TOPOLOGY ---
                               +-----------+                                   
                               | __start__ |                                   
                               +-----------+                                   
                                     *                                         
                                +--------+                                     
                               *| intake |***                                  
                          ***** +--------+   *****                             
                     *****          *             *****                        
+---------------+          +-------------------+          +---------------+    
| comps_analyst |          | financial_modeler |          | risk_assessor |    
+---------------+****      +-------------------+       ***+---------------+    
                     *****          *             *****                        
                          *****     *        *****                             
                            +-----------------+                                
                            | aggregator_memo |                                
                            +-----------------+                                
                                     *                                         
                                +---------+                                    
                                | __end__ |                                    
                                +---------+                                    

>>> Executing LangGraph CMA Pipeline...
[Intake] Initializing deal analysis for: 42 Meadow Lane, Huntington, NY

==================================================
FINAL EXECUTIVE INVESTMENT MEMO
==================================================
**Executive Investment Memo**

**1. Executive Verdict:** Counter-Offer with Target Price: $600,000.00

**2. Deal Highlights & Core Strengths:**
- **Competitive Pricing:** Asking price of $625,000 translates to $297.62/sqft, fitting the competitive range for Huntington comps ($280 - $320/sqft).
- **Strong Rental Yield:** $50,400 projected gross annual rent yields an estimated NOI of $32,560, representing an 8.06% Gross Yield and 5.21% Cap Rate.
- **Location Demand:** Strong residential rental demand supports stable appreciation and occupancy.

**3. Critical Red Flags / Conditions Required for Closing:**
- **Tax Ratio Drag:** Annual taxes of $12,800 represent a 2.05% tax-to-price ratio; historical assessments and grievance potential must be confirmed.
- **Due Diligence Checklist:** Full structural and MEP inspection required to ensure deferred maintenance does not erode cash flow.
==================================================
```

---

## Built For
Developed as part of **Nisarg's AI Master Class (LangGraph Parallel Workflow Module)**.
