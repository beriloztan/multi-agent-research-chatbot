"""
LangGraph ile tum agent'lari tek bir akista birlestiriyoruz.
"""
from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.router import router_node
from agents.search_agent import search_node
from agents.verifier import verifier_node
from agents.responder import responder_node


def route_decision(state: AgentState) -> str:
    """Router'in kararina gore hangi node'a gidilecegini belirler."""
    if state["needs_search"]:
        return "search"
    else:
        return "responder"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "search": "search",
            "responder": "responder",
        },
    )

    graph.add_edge("search", "verifier")
    graph.add_edge("verifier", "responder")
    graph.add_edge("responder", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state: AgentState = {
        "user_query": "2026 yılında Türkiye enflasyon oranı ne kadar?",
        "needs_search": False,
        "sub_queries": [],
        "raw_sources": [],
        "verified_sources": [],
        "final_answer": "",
        "trace": [],
    }

    result = app.invoke(initial_state)

    print("=== TRACE ===")
    for t in result["trace"]:
        print("-", t)
    print("\n=== FINAL CEVAP ===")
    print(result["final_answer"])