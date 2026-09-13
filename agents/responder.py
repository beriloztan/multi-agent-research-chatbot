"""
Responder Agent - onaylanan kaynaklari kullanarak kullaniciya final cevabi yazar.
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", timeout=20)

RESPONDER_WITH_SOURCES_PROMPT = """Kullanicinin sorusunu asagidaki dogrulanmis kaynaklara dayanarak cevapla.
Sohbet diliyle, net ve anlasilir yaz. Kaynaklari ayrica listeleme veya link verme;
kaynaklar arayuzde otomatik olarak gosteriliyor, sen sadece cevaba odaklan.

Soru: {query}

Kaynaklar:
{sources}
"""

RESPONDER_DIRECT_PROMPT = """Kullanicinin sorusunu kendi bilgine dayanarak, sohbet diliyle cevapla.

Soru: {query}
"""


def _extract_text(response) -> str:
    if isinstance(response.content, list):
        return response.content[0]["text"].strip()
    return response.content.strip()


def responder_node(state: AgentState) -> AgentState:
    if state["needs_search"] and state["verified_sources"]:
        sources_text = "\n\n".join(
            f"- {s['title']}\n  {s['content']}\n  Link: {s['url']}"
            for s in state["verified_sources"]
        )
        prompt = RESPONDER_WITH_SOURCES_PROMPT.format(
            query=state["user_query"],
            sources=sources_text,
        )
    else:
        prompt = RESPONDER_DIRECT_PROMPT.format(query=state["user_query"])

    response = llm.invoke(prompt)
    answer = _extract_text(response)

    state["final_answer"] = answer
    state["trace"] = state.get("trace", []) + ["Responder: final cevap uretildi"]
    return state


if __name__ == "__main__":
    from agents.search_agent import search_node
    from agents.verifier import verifier_node

    test_state: AgentState = {
        "user_query": "2026 yılında Türkiye enflasyon oranı ne kadar?",
        "needs_search": True,
        "sub_queries": [],
        "raw_sources": [],
        "verified_sources": [],
        "final_answer": "",
        "trace": [],
    }
    state_after_search = search_node(test_state)
    state_after_verify = verifier_node(state_after_search)
    result = responder_node(state_after_verify)

    print("=== TRACE ===")
    for t in result["trace"]:
        print("-", t)
    print("\n=== FINAL CEVAP ===")
    print(result["final_answer"])