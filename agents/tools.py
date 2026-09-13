"""
Web search tool - DuckDuckGo uzerinden ucretsiz arama.
"""
from ddgs import DDGS
from ddgs.exceptions import DDGSException


def web_search(query: str, max_results: int = 3) -> list[dict]:
    """
    Verilen sorgu icin DuckDuckGo'da arama yapar.
    Her sonuc icin: title, href (url), body (icerik ozeti) doner.

    DDG'nin ucretsiz html backend'i art arda gelen isteklerde sikca
    rate-limit'e takilip "No results found" firlatiyor. Bu durumda tum
    pipeline'i cokertmek yerine bos liste donuyoruz; cagiran taraf
    (search_node) eldeki diger sonuclarla devam edebiliyor.
    """
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results, backend="html"):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "content": r.get("body", ""),
                })
    except DDGSException:
        return []
    return results


if __name__ == "__main__":
    # Hizli test: python agents/tools.py
    test_results = web_search("2026 Türkiye enflasyon oranı")
    for r in test_results:
        print(r["title"], "-", r["url"])
        print(r["content"][:150])
        print("---")