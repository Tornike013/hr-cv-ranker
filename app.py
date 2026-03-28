import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    max_tokens=1000,
    temperature=0
)

parser = StrOutputParser()

# Step 1 - Extract key info from each CV
step1_prompt = PromptTemplate(
    input_variables=["cv_text", "job_description"],
    template="""You are an HR analyst. Extract the most relevant information from this CV for the job below.

Job Description:
{job_description}

CV:
{cv_text}

Return ONLY:
Name: [candidate name or "Unknown"]
Experience: [years of relevant experience]
Key skills: [top 5 relevant skills as comma separated list]
Education: [highest relevant degree]
Match highlights: [2 sentences on why this person could fit the role]
Missing: [1 sentence on what's missing or weak]"""
)

# Step 2 - Score each candidate
step2_prompt = PromptTemplate(
    input_variables=["candidate_summary", "job_description"],
    template="""You are a strict HR evaluator. Score this candidate using this exact rubric:

Job Description:
{job_description}

Candidate Summary:
{candidate_summary}

Scoring rubric:
- Relevant experience (0-30 points): years and quality of directly relevant experience
- Required skills match (0-30 points): how many required skills they have
- Education fit (0-20 points): relevance of their degree/education
- Seniority fit (0-20 points): are they the right level for this role

Be strict. Penalize missing skills heavily. No two candidates should have the same total score unless they are genuinely identical profiles.

Return ONLY:
Experience score: X/30
Skills score: X/30
Education score: X/20
Seniority score: X/20
Total: X/100
Reasoning: One sentence explaining the total."""
)

# Step 3 - Rank and compare all candidates
step3_prompt = PromptTemplate(
    input_variables=["all_candidates", "job_description"],
    template="""You are a hiring manager making a final decision.

Job Description:
{job_description}

All candidates with scores:
{all_candidates}

Write a final hiring recommendation:

## Candidate Ranking

[Rank all candidates from best to worst fit, with their score]

## Top Candidate Recommendation
[Name and why they are the best fit in 3 sentences]

## Hiring Notes
[One key observation per candidate that the hiring manager should know]"""
)

chain1 = step1_prompt | llm | parser
chain2 = step2_prompt | llm | parser
chain3 = step3_prompt | llm | parser

def extract_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

st.set_page_config(page_title="HR CV Ranker", page_icon="👥", layout="wide")
st.title("👥 HR CV Ranker")
st.write("Upload multiple CVs and a job description to instantly rank and compare candidates.")

with st.sidebar:
    st.header("How it works")
    st.markdown("""
    For each CV the tool runs 3 AI steps:
    
    1. **Extraction** - pulls key info from each CV
    2. **Scoring** - scores each candidate against the role
    3. **Ranking** - compares all candidates and recommends the best fit
    """)
    st.divider()
    st.info("Upload 2-5 CVs for best results.")

st.subheader("Job Description")
job_description = st.text_area("Paste the job description here", height=200)

st.subheader("Upload CVs")
uploaded_files = st.file_uploader("Upload CV files (PDF)", type="pdf", accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} CV(s) uploaded")

if st.button("Rank Candidates", use_container_width=True):
    if not job_description:
        st.warning("Please paste a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one CV.")
    elif len(uploaded_files) < 2:
        st.warning("Please upload at least 2 CVs to compare.")
    else:
        st.divider()
        all_candidates = []

        for i, cv_file in enumerate(uploaded_files):
            st.markdown(f"**Processing: {cv_file.name}**")

            col1, col2, col3 = st.columns(3)

            with col1:
                status1 = st.empty()
            with col2:
                status2 = st.empty()
            with col3:
                status3 = st.empty()

            try:
                status1.info("📄 Extracting info...")
                cv_text = extract_pdf_text(cv_file)
                summary = chain1.invoke({
                    "cv_text": cv_text,
                    "job_description": job_description
                })
                status1.success("✅ Info extracted")

                status2.info("📊 Scoring candidate...")
                score = chain2.invoke({
                    "candidate_summary": summary,
                    "job_description": job_description
                })
                status2.success("✅ Score calculated")

                status3.success("✅ Done")

                all_candidates.append(f"CV: {cv_file.name}\n{summary}\n{score}")

            except Exception as e:
                st.error(f"Error processing {cv_file.name}: {str(e)}")

        if len(all_candidates) > 1:
            st.divider()
            st.subheader("Final Ranking")

            with st.spinner("Comparing all candidates..."):
                try:
                    final_report = chain3.invoke({
                        "all_candidates": "\n\n---\n\n".join(all_candidates),
                        "job_description": job_description
                    })
                    st.markdown(final_report)
                except Exception as e:
                    st.error(f"Error generating ranking: {str(e)}")