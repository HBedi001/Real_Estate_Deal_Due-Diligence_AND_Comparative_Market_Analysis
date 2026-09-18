import os
import operator
from typing import TypedDict, Annotated, List, Dict, Any
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

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
    # Reducer operator.add allows parallel branches to append findings without overwriting
    analysis_reports: Annotated[List[str], operator.add]
    financial_metrics: Dict[str, Any]
    final_memo: str

# Model initialization
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


# ==========================================
# 2. Node Implementations
# ==========================================

def intake_node(state: CMAGraphState) -> dict:
    """Validates data and logs start of analysis."""
    prop = state["property_data"]
    print(f"\n[Intake] Initializing deal analysis for: {prop['address']}")
    return {
        "analysis_reports": [
            f"INTAKE: Verified {prop['property_type']} at {prop['address']} | Asking: ${prop['asking_price']:,}"
        ]
    }

def comps_analyst_node(state: CMAGraphState) -> dict:
    """Parallel Node 1: Analyzes pricing against market comps and square footage."""
    prop = state["property_data"]
    price_per_sqft = round(prop["asking_price"] / prop["sqft"], 2)
    
    prompt = f"""You are a Comparative Market Analysis (CMA) specialist.
Analyze this property's pricing metrics:
- Asking Price: ${prop['asking_price']:,}
- SqFt: {prop['sqft']} (Price/SqFt: ${price_per_sqft})
- Beds/Baths: {prop['bedrooms']} bed / {prop['bathrooms']} bath
- Asset Type: {prop['property_type']}

Provide a 3-bullet assessment evaluating whether this price/sqft is competitive, reasonable market adjustments, and fair-value recommendation."""
    
    response = llm.invoke([
        SystemMessage(content="You are an expert real estate appraiser and CMA specialist."),
        HumanMessage(content=prompt)
    ])
    
    return {
        "analysis_reports": [f"--- COMPS ANALYSIS ---\n{response.content.strip()}"]
    }

def financial_modeler_node(state: CMAGraphState) -> dict:
    """Parallel Node 2: Computes cash-flow metrics, Gross Yield, and Cap Rate."""
    prop = state["property_data"]
    
    gross_annual_rent = prop["estimated_monthly_rent"] * 12
    # Standard underwriting: 10% maintenance & vacancy reserve + annual taxes
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
        f"- Est. NOI: ${noi:,.2f}\n"
        f"- Gross Yield: {gross_yield}%\n"
        f"- Projected Cap Rate: {cap_rate}%"
    )
    
    return {
        "analysis_reports": [report],
        "financial_metrics": metrics
    }

def risk_assessor_node(state: CMAGraphState) -> dict:
    """Parallel Node 3: Assesses tax burden and investment vulnerability."""
    prop = state["property_data"]
    tax_burden_ratio = round((prop["annual_taxes"] / prop["asking_price"]) * 100, 2)
    
    prompt = f"""You are a Real Estate Risk Auditor. Evaluate risks for:
- Property: {prop['address']}
- Annual Taxes: ${prop['annual_taxes']:,} ({tax_burden_ratio}% tax-to-price ratio)
- Property Type: {prop['property_type']}

List the top 2-3 specific financial or market risks an investor must verify during physical/legal inspection."""

    response = llm.invoke([
        SystemMessage(content="You are a conservative real estate risk analyst."),
        HumanMessage(content=prompt)
    ])

    return {
        "analysis_reports": [f"--- RISK ASSESSMENT ---\n{response.content.strip()}"]
    }

def aggregator_memo_node(state: CMAGraphState) -> dict:
    """Fan-in Node: Synthesizes reports from parallel workers into an executive memo."""
    prop = state["property_data"]
    combined_reports = "\n\n".join(state["analysis_reports"])
    
    prompt = f"""Synthesize these deal reports for {prop['address']} into a high-level Executive Investment Memo:

{combined_reports}

Format the response strictly with:
1. Executive Verdict (Pass, Buy, or Counter-Offer with Target Price)
2. Deal Highlights & Core Strengths
3. Critical Red Flags / Conditions Required for Closing"""

    response = llm.invoke([
        SystemMessage(content="You are the Chief Investment Officer (CIO) for an institutional real estate acquisition fund."),
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

    # 1. Start to Intake
    builder.add_edge(START, "intake")

    # 2. Parallel Fan-Out: Intake branches to 3 workers simultaneously
    builder.add_edge("intake", "comps_analyst")
    builder.add_edge("intake", "financial_modeler")
    builder.add_edge("intake", "risk_assessor")

    # 3. Fan-In: All 3 workers converge on the aggregator node
    builder.add_edge("comps_analyst", "aggregator_memo")
    builder.add_edge("financial_modeler", "aggregator_memo")
    builder.add_edge("risk_assessor", "aggregator_memo")

    # 4. Aggregator to End
    builder.add_edge("aggregator_memo", END)

    return builder.compile()


# ==========================================
# 4. Test Runner
# ==========================================
if __name__ == "__main__":
    app = build_cma_graph()
    
    sample_deal: PropertyInput = {
        "address": "42 Meadow Lane, Huntington, NY",
        "property_type": "Single Family Residence",
        "asking_price": 625000.0,
        "sqft": 2100,
        "bedrooms": 4,
        "bathrooms": 2,
        "estimated_monthly_rent": 4200.0,
        "annual_taxes": 12800.0,
    }

    initial_state: CMAGraphState = {
        "property_data": sample_deal,
        "analysis_reports": [],
        "financial_metrics": {},
        "final_memo": ""
    }

    print(">>> Executing LangGraph CMA Pipeline...")
    output = app.invoke(initial_state)

    print("\n" + "="*50)
    print("FINAL EXECUTIVE INVESTMENT MEMO")
    print("="*50)
    print(output["final_memo"])