"""
Streamlit arayuzu - Multi-Agent Research Chatbot.
Pipeline'i (Router -> Search -> Verifier -> Responder) canli olarak gosterir.
Tema: "basilmis rapor" - katmanli koyu zeytin/komur, kirik beyaz, serif+sans
karisik tipografi, cevabin yaninda dikey zaman cizelgesi paneli.
"""
import html
import time

import streamlit as st
import streamlit.components.v1 as components

from agents.graph import build_graph

st.set_page_config(
    page_title="Research Agent",
    page_icon="🖋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

USER_AVATAR = "🧑‍💻"
ASSISTANT_AVATAR = "🔬"

# --------------------------------------------------------------------------
# Fontlar (ayri cagri - <link> blank-line'a duyarli bir HTML blok turu,
# <style> icindeki CSS'in okunabilirlik icin birakilan bos satirlari onunla
# ayni cagriya karisirsa blogu erken kesip CSS'i duz metin olarak sizdirir.
# Bu yuzden fontlar ve stil her zaman iki ayri st.markdown cagrisinda kalmali.)
# --------------------------------------------------------------------------
st.markdown(
    """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Stil
# --------------------------------------------------------------------------
st.markdown(
    """<style>
:root {
    --bg: #14130f;
    --bg-2: #191712;
    --panel: #1d1b15;
    --panel-2: #242118;
    --border: #362f1f;
    --text: #ece6d6;
    --dim: #a89f87;
    --accent: #8ea373;
    --accent-strong: #5c7a44;
    --danger: #c1786a;
    --warn: #c9a45c;
    --serif: 'Newsreader', Georgia, 'Times New Roman', serif;
    --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background-color: var(--bg);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
    color: var(--text);
}
.stApp, [class*="css"] { font-family: var(--sans); }
::selection { background: var(--accent-strong); color: var(--text); }

[data-testid="stSidebar"] { background: var(--bg-2); border-right: 1px solid var(--border); }
[data-testid="stSidebar"] *:not([data-testid="stIconMaterial"]) { color: var(--text) !important; font-family: var(--sans) !important; }
.sidebar-kicker { font-family: var(--serif); font-style: italic; font-size: 1.05rem; color: var(--text); margin-bottom: 2px; }
.sidebar-sub { color: var(--dim); font-size: 0.76rem; letter-spacing: 0.02em; margin-bottom: 16px; }
.sidebar-label { color: var(--dim); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; margin: 4px 0 6px 0; }
[data-testid="stSidebar"] hr { border-color: var(--border); margin: 14px 0; }
[data-testid="stSidebar"] .stButton button {
    background: transparent; border: none; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
    border-radius: 0; color: var(--dim); padding: 11px 2px; font-size: 0.82rem; letter-spacing: 0.02em;
    text-align: left; justify-content: flex-start; transition: color 0.15s ease, border-color 0.15s ease;
}
[data-testid="stSidebar"] .stButton button:hover { color: var(--accent); border-color: var(--accent-strong); }
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: transparent !important; border: none !important; border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] summary { padding: 9px 0 !important; font-size: 0.8rem !important; }
[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover { color: var(--accent) !important; }

.stChatMessage { background: transparent; animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(3px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulseSoft { 0%, 100% { box-shadow: 0 0 0 0 rgba(201,164,92,0.35); } 50% { box-shadow: 0 0 0 5px rgba(201,164,92,0); } }

h1, h2, h3, h4 { color: var(--text) !important; font-family: var(--serif) !important; font-weight: 500; letter-spacing: -0.01em; }
a { color: var(--accent); }
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] li {
    font-family: var(--serif); font-size: 1.04rem; line-height: 1.75; color: var(--text);
}
[data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"] p { margin-bottom: 0.9em; }

[data-testid="stChatInput"] {
    border: 1px solid var(--border) !important; border-radius: 16px !important;
    background: var(--panel) !important; box-shadow: 0 10px 30px rgba(0,0,0,0.35) !important;
}
[data-testid="stChatInputTextArea"] {
    background: transparent !important; color: var(--text) !important; font-family: var(--sans) !important;
    font-size: 0.95rem !important;
}
[data-testid="stChatInputSubmitButton"] {
    background: var(--accent-strong) !important; border-radius: 50% !important; border: none !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: var(--bg) !important; }

[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 10px !important; background: var(--panel) !important; }
[data-testid="stExpander"] summary { font-family: var(--sans) !important; font-size: 0.85rem !important; }
[data-testid="stAlert"] { border-radius: 10px !important; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--panel-2); border-radius: 8px; border: 2px solid var(--bg); }
::-webkit-scrollbar-thumb:hover { background: var(--border); }

/* Hero */
.hero { padding: 6px 0 22px 0; margin-bottom: 22px; }
.hero h1 { font-size: 2.1rem; margin: 0 0 8px 0; }
.hero-sub { font-family: var(--serif); font-style: italic; color: var(--dim); font-size: 1.02rem; margin-bottom: 14px; }
.hero-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.hero-divider { width: 100%; height: 10px; color: var(--dim); opacity: 0.55; margin-top: 16px; display: block; }

.tag {
    display: inline-block; font-family: var(--sans); font-size: 0.68rem; color: var(--dim);
    border: 1px solid var(--border); padding: 3px 9px; border-radius: 999px; background: var(--panel);
}

/* Mode rozeti */
.mode-badge {
    display: inline-flex; align-items: center; gap: 6px; font-family: var(--sans);
    font-size: 0.66rem; letter-spacing: 0.09em; text-transform: uppercase; font-weight: 600;
    color: var(--accent); background: rgba(142,163,115,0.12); border: 1px solid rgba(142,163,115,0.32);
    padding: 5px 11px; border-radius: 999px; margin-bottom: 16px;
}
.mode-badge.direct { color: var(--warn); background: rgba(201,164,92,0.1); border-color: rgba(201,164,92,0.32); }

/* Dikey zaman cizelgesi */
.timeline { position: relative; padding: 2px 0 2px 2px; }
.tl-item { position: relative; padding: 0 0 20px 24px; }
.tl-item:last-child { padding-bottom: 0; }
.tl-item::before {
    content: ""; position: absolute; left: 5px; top: 15px; bottom: -6px; width: 1px; background: var(--border);
}
.tl-item:last-child::before { display: none; }
.tl-marker {
    position: absolute; left: 0; top: 3px; width: 11px; height: 11px; border-radius: 50%;
    background: var(--panel-2); border: 2px solid var(--border);
}
.tl-item.done .tl-marker { background: var(--accent-strong); border-color: var(--accent); }
.tl-item.active .tl-marker { border-color: var(--warn); animation: pulseSoft 1.2s infinite ease-in-out; }
.tl-item.skipped { opacity: 0.4; }
.tl-item.error .tl-marker { background: var(--danger); border-color: var(--danger); }
.tl-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
.tl-title {
    font-family: var(--sans); font-size: 0.74rem; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; color: var(--dim);
}
.tl-item.done .tl-title { color: var(--text); }
.tl-dur { font-family: var(--sans); font-size: 0.66rem; color: var(--dim); font-variant-numeric: tabular-nums; }
.tl-detail { font-family: var(--sans); font-size: 0.78rem; color: var(--dim); margin-top: 3px; line-height: 1.45; }

/* Kaynaklar - footnote listesi */
.footnote { display: flex; align-items: flex-start; gap: 10px; padding: 11px 0; border-bottom: 1px solid var(--border); }
.footnote:last-child { border-bottom: none; }
.fn-num { font-family: var(--sans); font-size: 0.72rem; color: var(--dim); font-variant-numeric: tabular-nums; min-width: 18px; padding-top: 3px; }
.fn-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); margin-top: 7px; flex-shrink: 0; }
.footnote.rejected .fn-dot { background: var(--danger); }
.fn-ddg {
    font-family: var(--sans); font-size: 0.58rem; font-weight: 700; color: var(--bg); background: var(--accent);
    border-radius: 3px; padding: 2px 5px; letter-spacing: 0.02em; margin-top: 2px; flex-shrink: 0; white-space: nowrap;
}
.footnote.rejected .fn-ddg { background: var(--danger); }
.fn-title { font-family: var(--sans); color: var(--text); text-decoration: none; font-weight: 500; font-size: 0.88rem; }
.fn-title:hover { color: var(--accent); }
.fn-desc { font-family: var(--serif); color: var(--dim); font-size: 0.85rem; margin-top: 3px; line-height: 1.5; }
.fn-reason { font-family: var(--sans); color: var(--danger); font-size: 0.76rem; margin-top: 4px; font-style: italic; }

.chip {
    display: inline-block; font-family: var(--sans); padding: 2px 9px; margin: 2px 4px 2px 0;
    border-radius: 999px; background: var(--panel-2); border: 1px solid var(--border);
    font-size: 0.7rem; color: var(--dim);
}
</style>""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------
# Yardimcilar
# --------------------------------------------------------------------------
STEPS = [
    {"key": "router", "label": "Router"},
    {"key": "search", "label": "Search"},
    {"key": "verifier", "label": "Verifier"},
    {"key": "responder", "label": "Responder"},
]
NODE_ORDER = [s["key"] for s in STEPS]

HERO_DIVIDER_SVG = (
    '<svg class="hero-divider" viewBox="0 0 600 12" preserveAspectRatio="none">'
    '<path d="M0,6 C50,0 100,12 150,6 C200,0 250,12 300,6 C350,0 400,12 450,6 C500,0 550,12 600,6" '
    'fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
)


@st.cache_resource(show_spinner=False)
def get_graph():
    return build_graph()


def trace_entry_key(entry: str) -> str:
    lower = entry.lower()
    if lower.startswith("router"):
        return "router"
    if lower.startswith("search"):
        return "search"
    if lower.startswith("verifier"):
        return "verifier"
    return "responder"


def parse_trace_details(trace: list, needs_search: bool = None) -> dict:
    """Trace log'undaki 'Node: aciklama' satirlarini {key: aciklama} sozlugune cevirir.

    Router icin ham model ciktisini ('ARAMA_GEREKLI' gibi) gostermek yerine
    sade bir Turkce metin uretiyoruz; ham hali sidebar'daki tam trace log'unda
    zaten goruluyor.
    """
    details = {}
    for entry in trace:
        details[trace_entry_key(entry)] = entry.split(":", 1)[-1].strip()[:90]
    if needs_search is not None:
        details["router"] = "arama gerekli" if needs_search else "arama gerekli değil"
    return details


def final_statuses(needs_search: bool) -> dict:
    if needs_search:
        return {"router": "done", "search": "done", "verifier": "done", "responder": "done"}
    return {"router": "done", "search": "skipped", "verifier": "skipped", "responder": "done"}


def render_timeline(statuses: dict, details: dict, durations: dict = None) -> str:
    # NOTE: every fragment below is emitted on a single line with no leading
    # whitespace. st.markdown(..., unsafe_allow_html=True) runs content through
    # a CommonMark parser first: a line that is (or becomes, e.g. an empty
    # interpolated value) pure whitespace is treated as a blank line, which
    # terminates the HTML block early and makes everything after it render as
    # literal text/code. Keeping each element on one line avoids that trap.
    durations = durations or {}
    rows = ['<div class="timeline">']
    for step in STEPS:
        status = statuses.get(step["key"], "pending")
        detail = details.get(step["key"], "")
        dur = durations.get(step["key"])
        dur_html = f'<span class="tl-dur">{dur:.1f}sn</span>' if dur else ""
        detail_text = html.escape(detail) if detail else ("bekliyor" if status == "pending" else "")
        detail_html = f'<div class="tl-detail">{detail_text}</div>' if detail_text else ""
        rows.append(
            f'<div class="tl-item {status}"><div class="tl-marker"></div>'
            f'<div class="tl-head"><span class="tl-title">{step["label"]}</span>{dur_html}</div>'
            f'{detail_html}</div>'
        )
    rows.append("</div>")
    return "".join(rows)


def render_sources(sources, rejected=False, start=1) -> str:
    if not sources:
        return ""
    rows = []
    for i, s in enumerate(sources, start):
        cls = "footnote rejected" if rejected else "footnote"
        reason_html = (
            f'<div class="fn-reason">{html.escape(s.get("reason") or "")}</div>' if rejected else ""
        )
        title = html.escape(s.get("title") or s.get("url") or "kaynak")
        url = html.escape(s.get("url") or "#")
        body = html.escape((s.get("content") or "")[:150])
        idx = f"{i:02d}"
        rows.append(
            f'<div class="{cls}"><span class="fn-num">{idx}</span><span class="fn-dot"></span>'
            f'<span class="fn-ddg">DDG</span>'
            f'<div><a class="fn-title" href="{url}" target="_blank">{title}</a>'
            f'<div class="fn-desc">{body}…</div>{reason_html}</div></div>'
        )
    return "".join(rows)


def render_sources_block(sub_queries, verified, rejected):
    """Kaynak expander'inin icerigini (chip'ler + footnote listesi) render eder."""
    with st.expander(f"Kaynaklar · {len(verified)} onaylı, {len(rejected)} elenmiş"):
        if sub_queries:
            chips = "".join(f'<span class="chip">{html.escape(q)}</span>' for q in sub_queries)
            st.markdown(chips, unsafe_allow_html=True)
            st.write("")
        if verified:
            st.markdown(render_sources(verified), unsafe_allow_html=True)
        if rejected:
            st.markdown(render_sources(rejected, rejected=True, start=len(verified) + 1), unsafe_allow_html=True)


def scroll_to_bottom():
    components.html(
        """<script>
        var doc = window.parent.document;
        var container = doc.querySelector('section.main') || doc.querySelector('[data-testid="stAppViewContainer"]');
        if (container) { container.scrollTo({top: container.scrollHeight, behavior: "smooth"}); }
        </script>""",
        height=0,
    )


def run_query(user_query: str, timeline_slot, trace_log: list, durations: dict):
    """Grafigi stream ederek calistirir, timeline_slot'u canli gunceller.

    graph.stream(stream_mode="values") her node tamamlandiginda bir kez chunk
    verir; iki chunk arasi gecen sure o node'un gercek calisma suresine (artı
    kucuk bir stream overhead'i) yakin bir tahmindir - uydurma bir sayi degil.
    """
    graph = get_graph()
    statuses = {s["key"]: "pending" for s in STEPS}
    details = {s["key"]: "" for s in STEPS}
    statuses["router"] = "active"
    timeline_slot.markdown(render_timeline(statuses, details, durations), unsafe_allow_html=True)

    initial_state = {
        "user_query": user_query,
        "needs_search": False,
        "sub_queries": [],
        "raw_sources": [],
        "verified_sources": [],
        "final_answer": "",
        "trace": [],
    }

    final_state = initial_state
    seen_trace = 0
    last_ts = time.time()

    try:
        for chunk in graph.stream(initial_state, stream_mode="values"):
            now = time.time()
            elapsed = now - last_ts
            last_ts = now

            final_state = chunk
            trace = chunk.get("trace", [])
            new_entries = trace[seen_trace:]
            seen_trace = len(trace)

            for entry in new_entries:
                trace_log.append(entry)
                key = trace_entry_key(entry)
                statuses[key] = "done"
                details[key] = entry.split(":", 1)[-1].strip()[:90]
                durations[key] = elapsed

                # Router karar verince arama gerekmiyorsa search/verifier'i atla
                if key == "router" and not chunk.get("needs_search", True):
                    details["router"] = "arama gerekli değil"
                    statuses["search"] = "skipped"
                    statuses["verifier"] = "skipped"
                    statuses["responder"] = "active"
                else:
                    if key == "router":
                        details["router"] = "arama gerekli"
                    idx = NODE_ORDER.index(key)
                    if idx + 1 < len(NODE_ORDER):
                        nxt = NODE_ORDER[idx + 1]
                        if statuses[nxt] == "pending":
                            statuses[nxt] = "active"

            timeline_slot.markdown(render_timeline(statuses, details, durations), unsafe_allow_html=True)
    except Exception as e:
        for key, val in statuses.items():
            if val == "active":
                statuses[key] = "error"
        timeline_slot.markdown(render_timeline(statuses, details, durations), unsafe_allow_html=True)
        raise e

    for key in statuses:
        if statuses[key] == "active":
            statuses[key] = "done"
    timeline_slot.markdown(render_timeline(statuses, details, durations), unsafe_allow_html=True)

    return final_state


def render_turn(query, answer, needs_search, sub_queries, verified, rejected, statuses, details, durations):
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(query)
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        col_answer, col_timeline = st.columns([3, 1], gap="large")
        with col_timeline:
            st.markdown(render_timeline(statuses, details, durations), unsafe_allow_html=True)
        with col_answer:
            mode_badge = (
                '<span class="mode-badge">web arama</span>'
                if needs_search
                else '<span class="mode-badge direct">direkt cevap</span>'
            )
            st.markdown(mode_badge, unsafe_allow_html=True)
            st.markdown(answer)
            if verified or rejected:
                render_sources_block(sub_queries, verified, rejected)


# --------------------------------------------------------------------------
# Sidebar - gecmis
# --------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown('<div class="sidebar-kicker">Research Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">router · search · verifier · responder</div>', unsafe_allow_html=True)
    if st.button("+ Yeni sohbet", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.write("")
    st.markdown('<div class="sidebar-label">Geçmiş sorular</div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.caption("Henüz soru sorulmadı.")
    for turn in reversed(st.session_state.history):
        icon = "🔎" if turn["needs_search"] else "💬"
        label = turn["query"][:38] + ("…" if len(turn["query"]) > 38 else "")
        with st.expander(f"{icon}  {label}"):
            st.caption("trace")
            for t in turn["trace"]:
                st.markdown(f"- {t}")

# --------------------------------------------------------------------------
# Ana panel
# --------------------------------------------------------------------------
st.markdown(
    f"""<div class="hero">
<h1>Multi-Agent Research Chatbot</h1>
<div class="hero-sub">Gemini · LangGraph · DuckDuckGo ile derlenen, kaynaklı yanıtlar.</div>
<div class="hero-tags"><span class="tag">model: gemini-3.5-flash-lite</span><span class="tag">agents: 4</span><span class="tag">graph: langgraph</span></div>
{HERO_DIVIDER_SVG}
</div>""",
    unsafe_allow_html=True,
)

for turn in st.session_state.history:
    details = parse_trace_details(turn["trace"], turn["needs_search"])
    render_turn(
        turn["query"],
        turn["answer"],
        turn["needs_search"],
        turn["sub_queries"],
        turn["verified_sources"],
        turn["rejected_sources"],
        final_statuses(turn["needs_search"]),
        details,
        turn.get("durations", {}),
    )

query = st.chat_input("Bir soru sor...")

if query:
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(query)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        col_answer, col_timeline = st.columns([3, 1], gap="large")
        timeline_slot = col_timeline.empty()
        trace_log: list = []
        durations: dict = {}
        try:
            with st.spinner("Agent'lar çalışıyor..."):
                result = run_query(query, timeline_slot, trace_log, durations)
        except Exception as e:
            with col_answer:
                st.error(f"Bir hata oluştu: {e}")
            st.stop()

        with col_answer:
            mode_badge = (
                '<span class="mode-badge">web arama</span>'
                if result.get("needs_search")
                else '<span class="mode-badge direct">direkt cevap</span>'
            )
            st.markdown(mode_badge, unsafe_allow_html=True)
            st.markdown(result.get("final_answer", "_Cevap üretilemedi._"))

            verified = result.get("verified_sources", [])
            rejected = [s for s in result.get("raw_sources", []) if not s.get("verified")]

            if verified or rejected:
                render_sources_block(result.get("sub_queries", []), verified, rejected)

    st.session_state.history.append(
        {
            "query": query,
            "answer": result.get("final_answer", ""),
            "needs_search": result.get("needs_search", False),
            "sub_queries": result.get("sub_queries", []),
            "verified_sources": verified,
            "rejected_sources": rejected,
            "trace": trace_log,
            "durations": durations,
        }
    )
    scroll_to_bottom()
