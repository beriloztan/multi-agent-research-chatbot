"""
Tum agent'larin paylastigi ortak state.
LangGraph'ta her node bu dict'i okuyup guncelleyerek calisir.
"""
from typing import TypedDict, List, Optional


class Source(TypedDict):
    url: str
    title: str
    content: str
    verified: bool
    reason: Optional[str]  # elenme sebebi varsa


class AgentState(TypedDict):
    user_query: str          # kullanicinin sorusu
    needs_search: bool        # Router karari: arama gerekli mi
    sub_queries: List[str]    # Planner'in bolduugu alt sorular
    raw_sources: List[Source] # Search agent'in topladigi kaynaklar
    verified_sources: List[Source]  # Verifier'dan gecen kaynaklar
    final_answer: str         # Responder'in urettigi cevap
    trace: List[str]          # UI'da gosterecegimiz adim adim log