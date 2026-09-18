import os
import operator
from typing import TypedDict, Annotated, List, Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

"""Address: 42 Meadow Lane, Huntington, NY  """

# Load environment variables from .env
load_dotenv()

# ==========================================
# 1. State Definition
# ==========================================
class PropertyInput(TypedDict):
    address: str
    property_type: str
    asking_price: float
    sqft: int
    bedrooms: int
    bathrooms: int
    estimated_monthly_rent: float
    annual_taxes: float

class CMAGraphState(TypedDict):
    property_data: PropertyInput
    # operator.add reducer lets parallel branches append reports without collision
    analysis_reports: Annotated[List[str], operator.add]
    financial_metrics: Dict[str, Any]
    final_memo: str

# Model initialization
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


# ==========================================
# 2. Node Implementations
# ==========================================

def intake_node(state: CMAGraphState) -> dict:
    """Validates property input and initializes pipeline logs."""
    prop = state["property_data"]
    print(f"\n[Intake] Initializing deal analysis for: {prop['address']}")
    return {
        "analysis_reports": [
            f"INTAKE: Verified {prop['property_type']} at {prop['address']} | Asking Price: ${prop['asking_price']:,.2f}"
        ]
    }

def comps_analyst_node(state: CMAGraphState) -> dict:
    """Parallel Worker 1: Evaluates pricing vs. market comps and square footage."""
    prop = state["property_data"]
    price_per_sqft = round(prop["asking_price"] / prop["sqft"], 2)
    
    prompt = f"""You are a Comparative Market Analysis (CMA) specialist.
Analyze this property's pricing metrics:
- Address: {prop['address']}
- Asking Price: ${prop['asking_price']:,}
- Square Footage: {prop['sqft']} sqft (Price/SqFt: ${price_per_sqft})
- Layout: {prop['bedrooms']} bed / {prop['bathrooms']} bath
- Asset Type: {prop['property_type']}

Provide a 3-bullet assessment evaluating whether this price/sqft is competitive, reasonable market adjustments, and a fair-value baseline."""
    
    response = llm.invoke([
        SystemMessage(content="You are an expert real estate appraiser and CMA specialist."),
        HumanMessage(content=prompt)
    ])
    
    return {
        "analysis_reports": [f"--- COMPS ANALYSIS ---\n{response.content.strip()}"]
    }

def financial_modeler_node(state: CMAGraphState) -> dict:
    """Parallel Worker 2: Computes cash-flow metrics, Gross Yield, and Cap Rate."""
    prop = state["property_data"]
    
    gross_annual_rent = prop["estimated_monthly_rent"] * 12
    # Underwriting model: 10% maintenance & vacancy reserve + annual property taxes
    estimated_operating_expenses = prop["annual_taxes"] + (gross_annual_rent * 0.10)
    noi = gross_annual_rent - estimated_operating_expenses
    cap_rate = round((noi / prop["asking_price"]) * 100, 2)
    gross_yield = round((gross_annual_rent / prop["asking_price"]) * 100, 2)

    metrics = {
        "gross_annual_rent": gross_annual_rent,
        "operating_expenses": estimated_operating_expenses,
        "noi": noi,
        "cap_rate": cap_rate,
        "gross_yield": gross_yield
    }
    
    report = (
        f"--- FINANCIAL UNDERWRITING ---\n"
        f"- Annual Gross Rent: ${gross_annual_rent:,.2f}\n"
        f"- Operating Expenses (Taxes + 10% Reserve): ${estimated_operating_expenses:,.2f}\n"
        f"- Estimated Net Operating Income (NOI): ${noi:,.2f}\n"
        f"- Gross Rental Yield: {gross_yield}%\n"
        f"- Projected Cap Rate: {cap_rate}%"
    )
    
    return {
        "analysis_reports": [report],
        "financial_metrics": metrics
    }

def risk_assessor_node(state: CMAGraphState) -> dict:
    """Parallel Worker 3: Assesses tax drag, physical risks, and market exposure."""
    prop = state["property_data"]
    tax_burden_ratio = round((prop["annual_taxes"] / prop["asking_price"]) * 100, 2)
    
    prompt = f"""You are a Real Estate Risk Auditor. Evaluate risks for:
- Property Address: {prop['address']}
- Annual Taxes: ${prop['annual_taxes']:,} ({tax_burden_ratio}% tax-to-price ratio)
- Asset Type: {prop['property_type']}

List the top 2-3 specific financial or physical risks an investor must verify during inspection and title review."""

    response = llm.invoke([
        SystemMessage(content="You are a conservative institutional real estate risk analyst."),
        HumanMessage(content=prompt)
    ])

    return {
        "analysis_reports": [f"--- RISK ASSESSMENT ---\n{response.content.strip()}"]
    }

def aggregator_memo_node(state: CMAGraphState) -> dict:
    """Fan-In Aggregator: Combines reports into a structured investment memo."""
    prop = state["property_data"]
    combined_reports = "\n\n".join(state["analysis_reports"])
    
    prompt = f"""Synthesize these deal reports for {prop['address']} into a concise Executive Investment Memo:

{combined_reports}

Format your output strictly with:
1. Executive Verdict (Pass, Buy, or Counter-Offer with Target Price)
2. Deal Highlights & Core Strengths
3. Critical Red Flags / Conditions Required for Closing"""

    response = llm.invoke([
        SystemMessage(content="You are the Chief Investment Officer (CIO) of an institutional real estate fund."),
        HumanMessage(content=prompt)
    ])

    return {"final_memo": response.content.strip()}


# ==========================================
# 3. Graph Assembly (Parallel Fan-Out / Fan-In)
# ==========================================
def build_cma_graph():
    builder = StateGraph(CMAGraphState)

    # Register Nodes
    builder.add_node("intake", intake_node)
    builder.add_node("comps_analyst", comps_analyst_node)
    builder.add_node("financial_modeler", financial_modeler_node)
    builder.add_node("risk_assessor", risk_assessor_node)
    builder.add_node("aggregator_memo", aggregator_memo_node)

    # 1. Start -> Intake
    builder.add_edge(START, "intake")

    # 2. Parallel Fan-Out: Intake branches to 3 workers simultaneously
    builder.add_edge("intake", "comps_analyst")
    builder.add_edge("intake", "financial_modeler")
    builder.add_edge("intake", "risk_assessor")

    # 3. Fan-In: All workers converge on aggregator
    builder.add_edge("comps_analyst", "aggregator_memo")
    builder.add_edge("financial_modeler", "aggregator_memo")
    builder.add_edge("risk_assessor", "aggregator_memo")

    # 4. Aggregator -> End
    builder.add_edge("aggregator_memo", END)

    return builder.compile()


# ==========================================
# 4. Helper Functions & Interactive Runner
# ==========================================
def validate_address_with_llm(user_input: str) -> bool:
    """Uses LLM to verify if input represents a plausible, complete real estate address."""
    verification_prompt = (
        f"Determine if the following text is a plausible, well-formed real estate address "
        f"(must include at minimum a street number, street name, and city/state or zip code).\n"
        f"Input: \"{user_input}\"\n"
        f"Answer with ONLY the word 'VALID' or 'INVALID'."
    )
    res = llm.invoke([HumanMessage(content=verification_prompt)])
    return res.content.strip().upper() == "VALID"


if __name__ == "__main__":
    # Compile graph
    app = build_cma_graph()

    # Display Graph Topology in Terminal
    print("\n--- GRAPH TOPOLOGY ---")
    try:
        print(app.get_graph().draw_ascii())
    except ImportError:
        print(app.get_graph().draw_mermaid())

    print("\n" + "=" * 50)
    print("REAL ESTATE DUE-DILIGENCE & CMA PIPELINE")
    print("=" * 50)

    # Interactive Execution Loop
    while True:
        user_input = input("\nType Quit to exit. Please enter address: ").strip()

        if user_input.lower() == "quit":
            print("Exiting pipeline. Goodbye!")
            break

        if not user_input:
            print("[Error] Address cannot be empty. Please enter a valid address.")
            continue

        print(f"Validating address: '{user_input}'...")
        if not validate_address_with_llm(user_input):
            print("[Validation Error] That does not appear to be a complete or valid address.")
            print("Please provide a valid street address (e.g., '123 Main St, Huntington, NY 11743').")
            continue

        # Validated deal payload
        deal_payload: PropertyInput = {
            "address": user_input,
            "property_type": "Single Family Residence",
            "asking_price": 625000.0,
            "sqft": 2100,
            "bedrooms": 4,
            "bathrooms": 2,
            "estimated_monthly_rent": 4200.0,
            "annual_taxes": 12800.0,
        }

        initial_state: CMAGraphState = {
            "property_data": deal_payload,
            "analysis_reports": [],
            "financial_metrics": {},
            "final_memo": ""
        }

        print("\n>>> Executing LangGraph CMA Pipeline...")
        output = app.invoke(initial_state)

        print("\n" + "=" * 50)
        print("FINAL EXECUTIVE INVESTMENT MEMO")
        print("=" * 50)
        print(output["final_memo"])
        print("=" * 50)