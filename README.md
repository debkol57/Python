# AI HR Recruitment Agent

A Streamlit interface for the LangGraph resume-screening workflow.

## Files
- `app.py`: Streamlit user interface
- `workflow.py`: LangGraph workflow
- `requirements.txt`: Python dependencies

## Run locally
1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key as an environment variable named `OPENAI_API_KEY`.
3. Run: `streamlit run app.py`

## Deploy to Streamlit Community Cloud
1. Push these files to a GitHub repository.
2. In Streamlit Community Cloud, choose the repository and branch.
3. Set **Main file path** to `app.py`.
4. In App settings > Secrets, add:
   `OPENAI_API_KEY = "your_api_key"`

Never commit API keys or real candidate data to GitHub.

## Important
This is a teaching/demo prototype. The workflow uses a fixed Python Developer skill assessment prompt from the supplied notebook. AI output must not be used as the sole basis for hiring decisions. Review results with a human and avoid entering sensitive personal information.
