"""
Search Agent - soruyu alt sorulara boler ve web'de arama yapar.
"""
import time

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState
from agents.tools import web_search

SEARCH_DELAY_SECONDS = 1.5  # DDG rate-limit'ine takilma ihtimalini azaltmak icin

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", timeout=20)

PLANNER_PROMPT = """Kullanicinin sorusunu 2-3 tane arama sorgusuna bol.
Her satira bir sorgu yaz, baska hicbir sey yazma (numara, aciklama vs. YOK).

Soru: {query}
"""


def search_node(state: AgentState) -> AgentState:
    # 1. Soruyu alt sorgulara bol
    prompt = PLANNER_PROMPT.format(query=state["user_query"])
    response = llm.invoke(prompt)

    if isinstance(response.content, list):
        text = response.content[0]["text"]
    else:
        text = response.content

    sub_queries = [q.strip() for q in text.strip().split("\n") if q.strip()]
    state["sub_queries"] = sub_queries

    # 2. Her alt sorgu icin arama yap (biri basarisiz olursa digerleriyle devam et)
    raw_sources = []
    failed_queries = 0
    for i, sq in enumerate(sub_queries):
        if i > 0:
            time.sleep(SEARCH_DELAY_SECONDS)
        results = web_search(sq, max_results=2)
        if not results:
            failed_queries += 1
        for r in results:
            raw_sources.append({
                "url": r["url"],
                "title": r["title"],
                "content": r["content"],
                "verified": False,
                "reason": None,
            })

    state["raw_sources"] = raw_sources
    summary = f"Search: {len(sub_queries)} alt sorgu -> {len(raw_sources)} kaynak bulundu"
    if failed_queries:
        summary += f" ({failed_queries} sorgu sonuc vermedi)"
    state["trace"] = state.get("trace", []) + [summary]
    return state


if __name__ == "__main__":
    test_state: AgentState = {
        "user_query": "2026 yılında Türkiye enflasyon oranı ne kadar?",
        "needs_search": True,
        "sub_queries": [],
        "raw_sources": [],
        "verified_sources": [],
        "final_answer": "",
        "trace": [],
    }
    result = search_node(test_state)
    print(result["trace"])
    print(result["sub_queries"])
    for s in result["raw_sources"]:
        print("-", s["title"], "|", s["url"])