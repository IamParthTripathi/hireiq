"""
app.py — HireIQ
---------------
Multi-agent AI Resume Screener & Interview Planner.
Powered by CrewAI 1.x with 3 specialized agents.

Run locally: streamlit run app.py
"""

import streamlit as st
from agents import run_hireiq
from resume_parser import parse_resume

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HireIQ — AI Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2.4rem; font-weight: 800; color: #0f4c81; }
    .subtitle   { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .agent-badge {
        display: inline-block;
        background: #e8f4fd;
        color: #0f4c81;
        border: 1px solid #0f4c81;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    .verdict-yes    { background: #e6f4ea; border-left: 4px solid #34a853; padding: 12px; border-radius: 4px; }
    .verdict-maybe  { background: #fef7e0; border-left: 4px solid #fbbc04; padding: 12px; border-radius: 4px; }
    .verdict-no     { background: #fce8e6; border-left: 4px solid #ea4335; padding: 12px; border-radius: 4px; }
    .score-big      { font-size: 3rem; font-weight: 800; color: #0f4c81; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">🎯 HireIQ</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Multi-Agent AI System · Resume Screener · Interview Designer · Hiring Advisor</p>',
    unsafe_allow_html=True,
)

# Show agent badges
st.markdown("""
<span class="agent-badge">🤖 Agent 1: Tech Screener</span>
<span class="agent-badge">🤖 Agent 2: Interview Designer</span>
<span class="agent-badge">🤖 Agent 3: Hiring Advisor</span>
""", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────
# Input Section
# ─────────────────────────────────────────────
col_resume, col_jd = st.columns(2, gap="large")

with col_resume:
    st.subheader("📄 Candidate Resume")
    resume_file = st.file_uploader(
        "Upload resume (PDF or DOCX)",
        type=["pdf", "docx"],
        key="resume_uploader",
    )

    resume_text = ""
    if resume_file:
        try:
            resume_text = parse_resume(resume_file)
            char_count  = len(resume_text)
            st.success(f"✅ Resume loaded ({char_count:,} characters extracted)")
            with st.expander("Preview extracted text", expanded=False):
                st.text(resume_text[:1500] + ("..." if len(resume_text) > 1500 else ""))
        except Exception as e:
            st.error(f"❌ Could not parse resume: {str(e)}")

with col_jd:
    st.subheader("📋 Job Description")
    jd_text = st.text_area(
        "Paste the full job description here",
        height=320,
        placeholder=(
            "Paste the complete job description including:\n"
            "- Role title and company\n"
            "- Required skills and tools\n"
            "- Years of experience required\n"
            "- Key responsibilities\n"
            "- Nice-to-have skills"
        ),
        key="jd_input",
    )

    if jd_text:
        word_count = len(jd_text.split())
        st.caption(f"📝 {word_count} words detected")

# ─────────────────────────────────────────────
# Run Button
# ─────────────────────────────────────────────
st.divider()

col_btn, col_info = st.columns([1, 3])

with col_btn:
    can_run = bool(resume_text) and bool(jd_text.strip())
    run_btn = st.button(
        "🚀 Run AI Screening",
        type="primary",
        disabled=not can_run,
        use_container_width=True,
    )

with col_info:
    if not resume_text:
        st.warning("⬆️ Upload a resume to proceed")
    elif not jd_text.strip():
        st.warning("⬆️ Paste a job description to proceed")
    else:
        st.info("✅ Ready! Click **Run AI Screening** — analysis takes ~30–60 seconds.")

# ─────────────────────────────────────────────
# Results Section
# ─────────────────────────────────────────────
if run_btn and can_run:
    st.divider()
    st.subheader("🔄 Running 3-Agent Pipeline...")

    # Progress indicator with agent labels
    progress_bar = st.progress(0)
    status_text  = st.empty()

    status_text.markdown("🤖 **Agent 1: Tech Screener** — Analyzing resume vs JD...")
    progress_bar.progress(10)

    with st.spinner("Three AI agents are collaborating on your analysis (~30-60 seconds)..."):
        results = run_hireiq(resume_text, jd_text)

    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()

    # ── Error handling ──
    if results.get("error"):
        st.error(f"❌ Pipeline error: {results['error']}")
        st.stop()

    st.success("✅ Analysis complete!")
    st.divider()

    # ── Display results in tabs ──
    tab1, tab2, tab3 = st.tabs([
        "📊 Screening Report",
        "❓ Interview Questions",
        "✅ Final Recommendation",
    ])

    with tab1:
        st.subheader("📊 Screening Report — Agent 1: Tech Screener")
        st.caption("Skills match analysis, red/green flags, and overall score")
        st.markdown(results["screening"])

    with tab2:
        st.subheader("❓ Interview Plan — Agent 2: Interview Designer")
        st.caption("Technical questions, behavioral questions, and practical assessment")
        st.markdown(results["questions"])

    with tab3:
        st.subheader("✅ Final Report — Agent 3: Hiring Advisor")
        st.caption("Verdict, strengths, concerns, and recommended next steps")
        st.markdown(results["recommendation"])

        # Download button for the full report
        full_report = f"""
HIREIQ ANALYSIS REPORT
======================

SCREENING REPORT:
{results['screening']}

INTERVIEW QUESTIONS:
{results['questions']}

HIRING RECOMMENDATION:
{results['recommendation']}
        """
        st.download_button(
            label="⬇️ Download Full Report (.txt)",
            data=full_report,
            file_name="hireiq_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

# ─────────────────────────────────────────────
# How It Works (shown when no results yet)
# ─────────────────────────────────────────────
if not run_btn:
    st.divider()
    st.subheader("🧠 How HireIQ Works")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
**🤖 Agent 1: Tech Screener**

Reads both resume and JD simultaneously. Maps each required skill to evidence in the resume. Assigns a match score 0–100 with reasoning. Flags red flags and green flags.
        """)

    with col2:
        st.markdown("""
**🤖 Agent 2: Interview Designer**

Reads the screening report. Generates 10 technical questions tailored to *this specific candidate* — including questions to probe their gaps. Adds 5 behavioral questions + a take-home assessment idea.
        """)

    with col3:
        st.markdown("""
**🤖 Agent 3: Hiring Advisor**

Synthesizes both reports. Delivers a clear verdict (Strong Yes / Yes / Maybe / No), salary recommendation, and the single most important next step. Designed for busy hiring managers.
        """)
