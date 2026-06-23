"""
agents.py — HireIQ
------------------
Defines the 3 CrewAI agents and their tasks.

Agent Architecture:
  Agent 1: TechScreener   — Scores resume vs JD, extracts matched/missing skills
  Agent 2: InterviewDesigner — Generates targeted technical + behavioral questions
  Agent 3: HiringAdvisor  — Synthesizes a final structured recommendation report

Uses CrewAI 1.x API (stable, released Oct 2025).
All agents are powered by Llama 3.1 via Groq.
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

# ─────────────────────────────────────────────
# LLM Configuration
# ─────────────────────────────────────────────
# CrewAI 1.x uses LiteLLM internally.
# You can swap to Groq for free inference:
#   model="groq/llama-3.1-70b-versatile"
# Or to Anthropic:
#   model="anthropic/claude-sonnet-4-20250514"

llm = LLM(
    model="groq/llama-3.1-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,  # Low temp for consistent structured outputs
)


# ─────────────────────────────────────────────
# Agent Definitions
# ─────────────────────────────────────────────

tech_screener = Agent(
    role="Senior Technical Recruiter",
    goal=(
        "Analyze a candidate's resume against a job description and produce a "
        "precise skill-match report with a numerical score and clear reasoning."
    ),
    backstory=(
        "You have 10+ years screening AI/ML/Software candidates at top tech firms. "
        "You can instantly identify whether a resume matches a JD's requirements, "
        "flag gaps, and distinguish genuine experience from keyword stuffing. "
        "You are direct, data-driven, and specific — never vague."
    ),
    llm=llm,
    verbose=False,   # Set True to see agent's thinking process during dev
    allow_delegation=False,
)

interview_designer = Agent(
    role="Technical Interview Specialist",
    goal=(
        "Design a personalized, role-specific interview plan based on the candidate's "
        "profile — including technical depth questions, gap-probing questions, and "
        "behavioral questions aligned to the role requirements."
    ),
    backstory=(
        "You have designed interview loops for hundreds of AI/ML roles at startups and "
        "enterprises. You craft questions that reveal genuine technical depth — not "
        "questions candidates can answer by memorizing LeetCode. You tailor every "
        "question to the specific candidate's background and the JD requirements."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

hiring_advisor = Agent(
    role="Hiring Decision Analyst",
    goal=(
        "Synthesize the screener's report and the interview plan into a final, "
        "structured hiring recommendation that a hiring manager can act on immediately."
    ),
    backstory=(
        "You are a data-driven hiring consultant who synthesizes technical assessments "
        "into clear go/no-go recommendations. Your reports are used by CTOs and "
        "Engineering Managers to make final hiring decisions. You are fair, thorough, "
        "and always back your verdict with specific evidence from the candidate's profile."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,
)


# ─────────────────────────────────────────────
# Task Definitions
# ─────────────────────────────────────────────

def create_screening_task(resume_text: str, jd_text: str) -> Task:
    """Task 1: Screen the resume against the JD."""
    return Task(
        description=f"""
Carefully analyze the following resume against the job description.

=== JOB DESCRIPTION ===
{jd_text[:3000]}

=== CANDIDATE RESUME ===
{resume_text[:3000]}

Produce a structured screening report with exactly these sections:

1. OVERALL MATCH SCORE: [0-100] with one-line justification
2. MATCHED SKILLS: List every required skill the candidate clearly demonstrates (with evidence from resume)
3. MISSING SKILLS: List every required skill the candidate does NOT demonstrate
4. EXPERIENCE RELEVANCE: 2-3 sentences on how relevant the candidate's work history is to this role
5. EDUCATION FIT: Does their educational background meet the role's requirements?
6. RED FLAGS: List any concerns (gaps, mismatch, vague claims)
7. GREEN FLAGS: List any standout positives (rare skills, impressive projects, strong metrics)

Be specific and evidence-based. Never be vague.
        """,
        expected_output=(
            "A structured screening report with all 7 sections filled with "
            "specific, evidence-based observations. Match score must be numeric."
        ),
        agent=tech_screener,
    )


def create_interview_task(screening_context) -> Task:
    """Task 2: Design the interview plan based on screening results."""
    return Task(
        description="""
Using the screening report from the previous task, design a complete interview plan.

Generate:

SECTION A — TECHNICAL QUESTIONS (10 questions):
- 3 questions testing core skills the candidate claims to have (verify depth)
- 3 questions probing the candidate's missing skills (see if they have hidden knowledge)
- 2 scenario-based system design questions relevant to the role
- 2 questions about their specific projects mentioned in the resume

SECTION B — BEHAVIORAL QUESTIONS (5 questions):
- Use the STAR format (Situation, Task, Action, Result)
- Tailor to the specific role requirements and seniority level

SECTION C — PRACTICAL ASSESSMENT SUGGESTION:
- Suggest one take-home or live coding/design task (2-4 hours max)
- Describe what you'd evaluate and what "good" looks like

Format as a numbered list under each section header.
        """,
        expected_output=(
            "15 interview questions organized in 3 sections (A, B, C) with "
            "a practical assessment suggestion. All questions tailored to this "
            "specific candidate and role."
        ),
        agent=interview_designer,
        context=screening_context,  # Has access to screening task output
    )


def create_recommendation_task(screening_context, interview_context) -> Task:
    """Task 3: Write the final hiring recommendation."""
    return Task(
        description="""
Using the screening report and interview plan from the previous tasks, write a
final structured hiring recommendation report.

Format the report with these exact sections:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIREIQ CANDIDATE ASSESSMENT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

VERDICT: [STRONG YES / YES / MAYBE / NO]
Match Score: [X/100]

TOP 3 STRENGTHS:
1. [Specific strength with evidence]
2. [Specific strength with evidence]
3. [Specific strength with evidence]

TOP 3 CONCERNS:
1. [Specific concern with reasoning]
2. [Specific concern with reasoning]
3. [Specific concern with reasoning]

INTERVIEW PRIORITY AREAS:
- [What to probe first and why]
- [Technical areas to verify]

SALARY RECOMMENDATION:
[Suggest a realistic salary range based on experience level and skills demonstrated]

NEXT STEP RECOMMENDATION:
[One clear action — e.g., "Proceed to technical phone screen" / "Reject" / "Request portfolio"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Be direct. Hiring managers need actionable decisions, not ambiguous language.
        """,
        expected_output=(
            "A complete, formatted hiring recommendation report with all sections "
            "filled in. Must include a clear verdict and a salary range."
        ),
        agent=hiring_advisor,
        context=screening_context + interview_context,
    )


# ─────────────────────────────────────────────
# Main Pipeline Function
# ─────────────────────────────────────────────

def run_hireiq(resume_text: str, jd_text: str) -> dict:
    """
    Run the full 3-agent HireIQ pipeline.

    Returns a dict with:
      - screening: str (screening report)
      - questions: str (interview questions)
      - recommendation: str (final report)
      - error: str or None
    """
    try:
        # Create tasks
        task1 = create_screening_task(resume_text, jd_text)
        task2 = create_interview_task([task1])
        task3 = create_recommendation_task([task1], [task2])

        # Assemble crew
        crew = Crew(
            agents=[tech_screener, interview_designer, hiring_advisor],
            tasks=[task1, task2, task3],
            process=Process.sequential,  # Tasks run in order; each can see previous outputs
            verbose=False,
        )

        # Execute
        result = crew.kickoff()

        return {
            "screening":       task1.output.raw if task1.output else "No output",
            "questions":       task2.output.raw if task2.output else "No output",
            "recommendation":  str(result),
            "error":           None,
        }

    except Exception as e:
        return {
            "screening":      "",
            "questions":      "",
            "recommendation": "",
            "error":          str(e),
        }
