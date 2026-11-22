import os
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


class State(TypedDict, total=False):
    application: str
    experience_level: str
    skill_match: str
    response: str


def get_llm():
    """Create the model client using the OPENAI_API_KEY environment variable."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to Streamlit Cloud > App settings > Secrets."
        )
    return ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0)


def categorize_experience(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Based on the following job application, categorize the candidate as "
        "exactly one of: 'Entry-level', 'Mid-level' or 'Senior-level'. "
        "Return only the category.\n\nApplication: {application}"
    )
    chain = prompt | get_llm()
    experience_level = chain.invoke(
        {"application": state["application"]}
    ).content.strip()
    return {"experience_level": experience_level}


def assess_skillset(state: State) -> State:
    prompt = ChatPromptTemplate.from_template(
        "Based on the job application for a Python Developer, assess the candidate's "
        "skillset. Respond with exactly 'Match' or 'No Match'. "
        "Return only one of these two labels.\n\nApplication: {application}"
    )
    chain = prompt | get_llm()
    skill_match = chain.invoke(
        {"application": state["application"]}
    ).content.strip()
    return {"skill_match": skill_match}


def schedule_hr_interview(state: State) -> State:
    return {"response": "Candidate has been shortlisted for an HR interview."}


def escalate_to_recruiter(state: State) -> State:
    return {
        "response": "Candidate has senior-level experience but doesn't match job skills."
    }


def reject_application(state: State) -> State:
    return {"response": "Candidate doesn't meet JD and has been rejected."}


def route_app(state: State) -> str:
    skill_match = state.get("skill_match", "").strip().lower()
    experience_level = state.get("experience_level", "").strip().lower()

    if skill_match == "match":
        return "schedule_hr_interview"
    elif "senior-level" in experience_level or "senior level" in experience_level:
        return "escalate_to_recruiter"
    else:
        return "reject_application"


def build_workflow():
    workflow = StateGraph(State)

    workflow.add_node("categorize_experience", categorize_experience)
    workflow.add_node("assess_skillset", assess_skillset)
    workflow.add_node("schedule_hr_interview", schedule_hr_interview)
    workflow.add_node("escalate_to_recruiter", escalate_to_recruiter)
    workflow.add_node("reject_application", reject_application)

    workflow.add_edge(START, "categorize_experience")
    workflow.add_edge("categorize_experience", "assess_skillset")

    workflow.add_conditional_edges(
        "assess_skillset",
        route_app,
        {
            "schedule_hr_interview": "schedule_hr_interview",
            "escalate_to_recruiter": "escalate_to_recruiter",
            "reject_application": "reject_application",
        },
    )

    workflow.add_edge("schedule_hr_interview", END)
    workflow.add_edge("escalate_to_recruiter", END)
    workflow.add_edge("reject_application", END)

    return workflow.compile()


def run_candidate_screening(application: str) -> dict:
    if not application or not application.strip():
        raise ValueError("Please enter the candidate's application or resume text.")

    app = build_workflow()
    results = app.invoke({"application": application.strip()})

    return {
        "experience_level": results.get("experience_level", "Not available"),
        "skill_match": results.get("skill_match", "Not available"),
        "response": results.get("response", "No decision returned."),
    }
