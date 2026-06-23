import streamlit as st
import database
from auth import login
from resume_processing.pdf_reader import extract_text_from_pdf, get_basic_stats
from resume_processing.skill_extractor import extract_skills_from_text
from resume_processing.ats_calculator import analyze_resume_for_role

st.set_page_config(page_title="Smart Resume Screening", page_icon="📄", layout="wide")

# Make sure the database and tables exist every time the app starts.
database.init_db()

# Initialize session_state keys if they don't exist yet.
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def show_dashboard():
    """Shown once a user is logged in."""
    st.title("📄 Smart Resume Screening and Career Improvement System")
    st.write(f"Welcome, **{st.session_state['user_name']}**! 👋")
    st.write(f"Account type: `{st.session_state['user_role']}`")

    if st.sidebar.button("Logout"):
        login.logout()

    st.divider()
    st.subheader("📤 Upload Your Resume")

    uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])

    if uploaded_file is not None:
        # Extract text using our pdf_reader module
        extracted_text = extract_text_from_pdf(uploaded_file)

        if not extracted_text:
            st.warning(
                "We couldn't find any text in this PDF. "
                "It might be a scanned image rather than a text-based PDF."
            )
        else:
            st.success(f"Resume '{uploaded_file.name}' processed successfully!")

            stats = get_basic_stats(extracted_text)
            col1, col2, col3 = st.columns(3)
            col1.metric("Words", stats["word_count"])
            col2.metric("Characters", stats["character_count"])
            col3.metric("Lines", stats["line_count"])

            with st.expander("View extracted text"):
                st.text(extracted_text)

            # Save to database, linked to the logged-in user
            resume_id = database.save_resume(
                user_id=st.session_state["user_id"],
                file_name=uploaded_file.name,
                extracted_text=extracted_text,
            )
            st.session_state["current_resume_id"] = resume_id
            st.session_state["current_resume_text"] = extracted_text

            # ---- Job role selection + ATS scoring ----
            st.divider()
            st.subheader("🎯 Select a Job Role to Analyze Against")

            job_roles = database.get_all_job_roles()
            role_names = [role["role_name"] for role in job_roles]
            role_lookup = {role["role_name"]: role["role_id"] for role in job_roles}

            selected_role_name = st.selectbox("Job Role", role_names)

            if st.button("Run ATS Analysis"):
                role_id = role_lookup[selected_role_name]
                required_skills = database.get_skills_for_role(role_id)

                # Detect which required skills appear in the resume text
                resume_skills_found = extract_skills_from_text(extracted_text, required_skills)

                analysis = analyze_resume_for_role(resume_skills_found, required_skills)

                # Save the result to the database
                database.save_ats_result(
                    user_id=st.session_state["user_id"],
                    role_id=role_id,
                    resume_id=resume_id,
                    ats_score=analysis["ats_score"],
                    matched_skills=analysis["matched_skills"],
                    missing_skills=analysis["missing_skills"],
                )

                st.divider()
                st.subheader(f"📊 ATS Results for {selected_role_name}")

                score = analysis["ats_score"]
                st.metric("ATS Score", f"{score}%")
                st.progress(min(int(score), 100) / 100)

                col_match, col_gap = st.columns(2)
                with col_match:
                    st.success("✅ Matched Skills")
                    for skill in analysis["matched_skills"]:
                        st.write(f"- {skill}")
                    if not analysis["matched_skills"]:
                        st.write("_No matching skills found._")

                with col_gap:
                    st.warning("⚠️ Skill Gap (Missing Skills)")
                    for skill in analysis["missing_skills"]:
                        st.write(f"- {skill}")
                    if not analysis["missing_skills"]:
                        st.write("_No skill gaps — great fit!_")


# Main routing: show login/register page, or the dashboard, based on session state.
if st.session_state["logged_in"]:
    show_dashboard()
else:
    login.show_auth_page()