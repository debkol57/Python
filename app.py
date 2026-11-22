import os
import streamlit as st

st.set_page_config(
    page_title="AI HR Recruitment Agent",
    page_icon="🧑‍💼",
    layout="wide",
)

# Load the API key from Streamlit Secrets (deployed) or environment variables (local).
try:
    secret_key = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    secret_key = ""

if secret_key:
    os.environ["OPENAI_API_KEY"] = secret_key

from workflow import run_candidate_screening


st.title("🧑‍💼 AI HR Recruitment Agent")
st.caption("Resume screening powered by LangGraph and OpenAI")

with st.sidebar:
    st.header("About this app")
    st.write(
        "This demo classifies a candidate's experience, checks skill fit for a "
        "Python Developer role, and routes the result to one of three outcomes."
    )
    st.warning(
        "Demo only: AI-generated screening results should be reviewed by a human. "
        "Do not enter sensitive personal information."
    )

st.subheader("Candidate application")
with st.form("candidate_form"):
    candidate_name = st.text_input("Candidate name (optional)")
    application_text = st.text_area(
        "Paste candidate application / resume text",
        height=230,
        placeholder=(
            "Example: I have 5 years of experience in software development, "
            "including Python, APIs, and databases..."
        ),
    )
    submitted = st.form_submit_button(
        "Run AI Screening",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not application_text.strip():
        st.error("Please paste the candidate's application or resume text.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error(
            "OpenAI API key not configured. Add OPENAI_API_KEY in "
            "Streamlit Cloud → App settings → Secrets."
        )
    else:
        with st.spinner("LangGraph is assessing the candidate..."):
            try:
                result = run_candidate_screening(application_text)

                st.divider()
                st.subheader("Screening results")
                if candidate_name.strip():
                    st.write(f"**Candidate:** {candidate_name.strip()}")

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Experience level", result["experience_level"])
                with col2:
                    st.metric("Skill match", result["skill_match"])

                response = result["response"]
                if "shortlisted" in response.lower():
                    st.success("Recommended next step: HR interview")
                elif "escalating" in response.lower() or "senior-level" in response.lower():
                    st.warning("Recommended next step: Recruiter review")
                else:
                    st.error("Workflow outcome: Application not shortlisted")

                st.info(response)
                with st.expander("View technical result"):
                    st.json(result)

            except Exception as exc:
                st.error(f"Screening failed: {exc}")
                st.exception(exc)

st.divider()
st.caption("Prototype application • Human review is required for all hiring decisions.")
