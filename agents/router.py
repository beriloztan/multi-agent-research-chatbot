"""
Router Agent - kullanicinin sorusuna bakip arama gerekip gerekmedigine karar verir.
"""
from dotenv import load_dotenv
load_dotenv()



from langchain_google_genai import ChatGoogleGenerativeAI
from agents.state import AgentState

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", timeout=20)

ROUTER_PROMPT = """Sen bir router agent'sin. Kullanicinin sorusuna bak ve karar ver:
Eger soru guncel bilgi, veri, haber veya arastirma gerektiriyorsa "ARAMA_GEREKLI" yaz.
Eger soru genel bilgi/sohbet ise ve arama gerektirmiyorsa "ARAMA_GEREKSIZ" yaz.
SADECE bu iki kelimeden birini yaz, baska hicbir sey yazma.

Soru: {query}
"""


def router_node(state: AgentState) -> AgentState:
    prompt = ROUTER_PROMPT.format(query=state["user_query"])
    response = llm.invoke(prompt)
    if isinstance(response.content, list):
        decision = response.content[0]["text"].strip()
    else:
        decision = response.content.strip()

    needs_search = "ARAMA_GEREKLI" in decision
    state["needs_search"] = needs_search
    state["trace"] = state.get("trace", []) + [
        f"Router: '{decision}' -> arama {'gerekli' if needs_search else 'gerekli degil'}"
    ]
    return state


if __name__ == "__main__":
    test_state: AgentState = {
        "user_query": "2026 yılında Türkiye enflasyon oranı ne kadar?",
        "needs_search": False,
        "sub_queries": [],
        "raw_sources": [],
        "verified_sources": [],
        "final_answer": "",
        "trace": [],
    }
    result = router_node(test_state)
    print(result["trace"])