"""
Verifier Agent - toplanan kaynaklari alaka/guvenilirlik acisindan degerlendirir.
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", timeout=20)

VERIFIER_PROMPT = """Asagida bir soru ve o soru icin bulunmus bir web kaynagi var.
Bu kaynagin soruyla alakali ve guvenilir olup olmadigina karar ver.

Soru: {query}

Kaynak basligi: {title}
Kaynak icerigi: {content}

Eger bu kaynak soruyu cevaplamaya yardimci oluyorsa "GECERLI" yaz.
Eger alakasizsa, cok zayifsa veya guvenilmez gorunuyorsa "GECERSIZ: <kisa sebep>" yaz.
SADECE bu formatta cevap ver, baska aciklama ekleme.
"""


def verifier_node(state: AgentState) -> AgentState:
    verified = []
    eliminated_count = 0

    for source in state["raw_sources"]:
        prompt = VERIFIER_PROMPT.format(
            query=state["user_query"],
            title=source["title"],
            content=source["content"],
        )
        response = llm.invoke(prompt)

        if isinstance(response.content, list):
            text = response.content[0]["text"].strip()
        else:
            text = response.content.strip()

        if text.startswith("GECERLI"):
            source["verified"] = True
            verified.append(source)
        else:
            source["verified"] = False
            source["reason"] = text.replace("GECERSIZ:", "").strip()
            eliminated_count += 1

    state["verified_sources"] = verified
    state["trace"] = state.get("trace", []) + [
        f"Verifier: {len(verified)} kaynak onaylandi, {eliminated_count} kaynak elendi"
    ]
    return state


if __name__ == "__main__":
    from agents.search_agent import search_node

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
    result = verifier_node(state_after_search)

    print(result["trace"])
    print("\n--- Onaylanan kaynaklar ---")
    for s in result["verified_sources"]:
        print("-", s["title"])
    print("\n--- Elenen kaynaklar ---")
    for s in state_after_search["raw_sources"]:
        if not s["verified"]:
            print("-", s["title"], "| Sebep:", s["reason"])