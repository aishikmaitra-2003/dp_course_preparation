"""
📝 Journal — Study Notes & Knowledge Base
Create, edit, search, and AI-summarize your notes per module.
"""

import streamlit as st
import requests
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assets.exam_data import get_all_modules
from backend.server import start_flask_server, get_api_url

start_flask_server()
API_URL = get_api_url()

# Load CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Theme support
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
is_light = st.session_state.theme == "light"
text_primary = "#1e293b" if is_light else "#e2e8f0"
text_secondary = "#475569" if is_light else "#94a3b8"
text_muted = "#94a3b8" if is_light else "#64748b"

if is_light:
    st.markdown("""<style>
    [data-testid="stAppViewContainer"] { background: #f8fafc !important; }
    [data-testid="stHeader"] { background: #f8fafc !important; }
    [data-testid="stBottomBlockContainer"], [data-testid="stBottom"] { background: #f8fafc !important; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%) !important; border-right: 1px solid rgba(0,0,0,0.08) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #1e293b !important; }
    .stMarkdown p, .stCaption p { color: #475569 !important; }
    [data-testid="stExpander"] { background: rgba(255,255,255,0.85) !important; border: 1px solid rgba(0,0,0,0.08) !important; }
    .stTextInput input, .stTextArea textarea { background: #f1f5f9 !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1e293b !important; }
    .stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; }
    .stTabs [data-baseweb="tab"] { color: #475569 !important; }
    </style>""", unsafe_allow_html=True)

if "current_module" not in st.session_state:
    st.session_state.current_module = 1

st.markdown(
    """<h1 style='background: linear-gradient(135deg, #2563eb, #06b6d4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-weight: 800;'>📝 Study Journal</h1>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="header-line"></div>', unsafe_allow_html=True)
st.caption("Your personal knowledge base. Take notes, summarize with AI, and never forget a concept! 🧠")

# Sidebar
with st.sidebar:
    st.markdown("### 📚 Filter by Module")
    modules = get_all_modules()
    filter_options = {"All Modules": None}
    for m in modules:
        filter_options[f"Day {m['day']}: {m['icon']} {m['title']}"] = m["id"]

    selected_filter = st.selectbox(
        "Module",
        options=list(filter_options.keys()),
        index=0,
        key="journal_filter",
    )
    filter_module = filter_options[selected_filter]

    st.divider()
    st.markdown("### 🔍 Search Notes")
    search_query = st.text_input("Search...", key="journal_search", placeholder="Type to search notes")

# Tabs: View notes vs Create new
tab_view, tab_create = st.tabs(["📖 My Notes", "✏️ New Note"])

# ---------------------------------------------------------------------------
# CREATE TAB
# ---------------------------------------------------------------------------
with tab_create:
    st.markdown("### ✏️ Create New Note")

    module_options = {f"Day {m['day']}: {m['icon']} {m['title']}": m["id"] for m in modules}
    default_idx = st.session_state.current_module - 1
    selected_module = st.selectbox(
        "Module",
        options=list(module_options.keys()),
        index=min(default_idx, len(module_options) - 1),
        key="new_note_module",
    )
    new_module_id = module_options[selected_module]

    note_title = st.text_input("📌 Title", placeholder="e.g., Delta Lake MERGE syntax", key="new_note_title")
    note_content = st.text_area(
        "📝 Content (Markdown supported)",
        height=300,
        placeholder="Write your notes here...\n\n## Key Points\n- Point 1\n- Point 2\n\n```python\n# Code example\ndf.write.format('delta').save('/path')\n```",
        key="new_note_content",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Note", use_container_width=True, type="primary"):
            if note_title and note_content:
                try:
                    resp = requests.post(
                        f"{API_URL}/api/journal",
                        json={
                            "module_id": new_module_id,
                            "title": note_title,
                            "content": note_content,
                        },
                        timeout=10,
                    ).json()
                    st.success(f"✅ Note saved! (ID: {resp.get('id')})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save: {e}")
            else:
                st.warning("Please fill in both title and content!")

    with col2:
        if st.button("🤖 AI Summarize", use_container_width=True):
            if note_content:
                with st.spinner("DP_Bot is summarizing... 🧑‍🍳"):
                    try:
                        resp = requests.post(
                            f"{API_URL}/api/journal/summarize",
                            json={"content": note_content},
                            timeout=30,
                        ).json()
                        st.markdown("### 📋 AI Summary")
                        st.markdown(resp.get("summary", "No summary generated"))
                    except Exception as e:
                        st.error(f"Summary failed: {e}")
            else:
                st.warning("Write some content first!")

# ---------------------------------------------------------------------------
# VIEW TAB
# ---------------------------------------------------------------------------
with tab_view:
    # Fetch entries
    try:
        params = {}
        if filter_module is not None:
            params["module_id"] = filter_module
        resp = requests.get(f"{API_URL}/api/journal", params=params, timeout=10).json()
        entries = resp.get("entries", [])
    except Exception:
        entries = []

    # Apply search filter
    if search_query:
        entries = [
            e for e in entries
            if search_query.lower() in e.get("title", "").lower()
            or search_query.lower() in e.get("content", "").lower()
        ]

    if not entries:
        st.markdown(
            f"""<div style='text-align: center; padding: 3rem; color: {text_muted};'>
            <div style='font-size: 3rem;'>📝</div>
            <div style='font-size: 1.2rem; margin-top: 1rem;'>No notes yet!</div>
            <div>Switch to the <strong>✏️ New Note</strong> tab to start writing.</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"Showing {len(entries)} note(s)")
        for entry in entries:
            module = None
            for m in modules:
                if m["id"] == entry.get("module_id"):
                    module = m
                    break

            module_label = f"{module['icon']} Day {module['day']}" if module else "📝"

            with st.expander(
                f"{module_label} — **{entry.get('title', 'Untitled')}** | "
                f"🕐 {entry.get('updated_at', 'unknown')[:16]}",
            ):
                st.markdown(entry.get("content", ""))

                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    if st.button("🤖 Summarize", key=f"sum_{entry['id']}", use_container_width=True):
                        with st.spinner("Summarizing..."):
                            try:
                                resp = requests.post(
                                    f"{API_URL}/api/journal/summarize",
                                    json={"content": entry.get("content", "")},
                                    timeout=30,
                                ).json()
                                st.markdown("---")
                                st.markdown("### 📋 AI Summary")
                                st.markdown(resp.get("summary", ""))
                            except Exception as e:
                                st.error(f"Error: {e}")

                with col2:
                    # Edit functionality
                    if st.button("✏️ Edit", key=f"edit_{entry['id']}", use_container_width=True):
                        st.session_state[f"editing_{entry['id']}"] = True
                        st.rerun()

                with col3:
                    if st.button("🗑️", key=f"del_{entry['id']}", use_container_width=True):
                        try:
                            requests.delete(f"{API_URL}/api/journal/{entry['id']}", timeout=5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

                # Edit form
                if st.session_state.get(f"editing_{entry['id']}"):
                    st.markdown("---")
                    new_title = st.text_input("Title", value=entry.get("title", ""), key=f"et_{entry['id']}")
                    new_content = st.text_area("Content", value=entry.get("content", ""), height=200, key=f"ec_{entry['id']}")
                    if st.button("💾 Save Changes", key=f"save_{entry['id']}"):
                        try:
                            requests.post(
                                f"{API_URL}/api/journal",
                                json={
                                    "entry_id": entry["id"],
                                    "module_id": entry.get("module_id", 0),
                                    "title": new_title,
                                    "content": new_content,
                                },
                                timeout=10,
                            )
                            del st.session_state[f"editing_{entry['id']}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

# Export all notes
st.markdown("---")
if entries:
    all_notes = ""
    for e in entries:
        all_notes += f"# {e.get('title', 'Untitled')}\n\n"
        all_notes += f"Module: {e.get('module_id', '?')}\n"
        all_notes += f"Updated: {e.get('updated_at', '')}\n\n"
        all_notes += f"{e.get('content', '')}\n\n---\n\n"

    st.download_button(
        "📥 Export All Notes (Markdown)",
        data=all_notes,
        file_name="dp700_study_notes.md",
        mime="text/markdown",
        use_container_width=True,
    )
