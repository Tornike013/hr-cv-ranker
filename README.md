# HR CV Ranker

An AI-powered tool that helps HR managers rank and compare multiple candidates against a job description instantly.

## The problem it solves

HR managers receive dozens of CVs per role. Reading and comparing them manually takes hours and is inconsistent. This tool automates the entire process in under a minute.

## How it works

Upload 2-5 CVs and paste a job description. The tool runs a 3-step AI pipeline:

1. **Extraction** - reads each CV and pulls out the most relevant information for the role
2. **Scoring** - scores each candidate independently against the job description (0-100)
3. **Ranking** - compares all candidates and generates a final hiring recommendation

Each step is a separate focused AI call. The output of each step feeds automatically into the next. This produces more accurate results than asking AI to do everything at once.

## Live demo

[your streamlit URL here]

## Tech stack

- Python
- Streamlit
- LangChain
- Anthropic Claude API
- PyPDF2

## Run locally

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Anthropic API key: `ANTHROPIC_API_KEY=your_key`
4. Run: `streamlit run app.py`

## Why LangChain

Instead of sending one giant prompt and hoping for the best, LangChain lets me chain focused steps where each output becomes the next input automatically — like a factory assembly line for AI analysis. This makes the pipeline more accurate, easier to debug, and easier to improve.