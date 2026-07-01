import streamlit as st
import database
from auth import login
from resume_processing.pdf_reader import extract_text_from_pdf, get_basic_stats
from resume_processing.skill_extractor import extract_skills_from_text
from resume_processing.ats_calculator import analyze_resume_for_role
from recommendation.career_advisor import build_recommendation, suggest_alternative_roles
from reports.pdf_report import generate_report
from admin.dashboard import show_admin_dashboard
import theme

st.set_page_config(page_title="Smart Resume Screening", page_icon="📄", layout="wide")
theme.inject_custom_css()

database.init_db()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def show_dashboard():
    st.title("📄 Smart Resume Screening & Career Improvement")
    st.caption(f"Signed in as **{st.session_state['user_name']}** · `{st.session_state['user_role']}`")

    st.sidebar.markdown("### 📄 SmartResume")
    st.sidebar.markdown(f"**{st.session_state['user_name']}**")
    st.sidebar.caption(st.session_state['user_role'].capitalize())
    st.sidebar.markdown("---")

    page = "Resume Analysis"
    if st.session_state["user_role"] == "admin":
        page = st.sidebar.radio("Navigate", ["Resume Analysis", "Admin Dashboard"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        login.logout()

    if page == "Admin Dashboard":
        show_admin_dashboard()
        return

    theme.card_open(eyebrow="Step 1", title="📤 Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"], label_visibility="collapsed")
    theme.card_close()

    if uploaded_file is not None:
        extracted_text = extract_text_from_pdf(uploaded_file)

        if not extracted_text:
            st.warning("We couldn't find any text in this PDF. It might be a scanned image.")
            return

        stats = get_basic_stats(extracted_text)

        theme.card_open(eyebrow="Resume processed")
        st.markdown(f"**{uploaded_file.name}**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Words", stats["word_count"])
        col2.metric("Characters", stats["character_count"])
        col3.metric("Lines", stats["line_count"])
        with st.expander("View extracted text"):
            st.text(extracted_text)
        theme.card_close()

        resume_id = database.save_resume(
            user_id=st.session_state["user_id"],
            file_name=uploaded_file.name,
            extracted_text=extracted_text,
        )
        st.session_state["current_resume_id"] = resume_id
        st.session_state["current_resume_text"] = extracted_text

        theme.card_open(eyebrow="Step 2", title="🎯 Choose a Target Role")
        job_roles = database.get_all_job_roles()
        role_names = [role["role_name"] for role in job_roles]
        role_lookup = {role["role_name"]: role["role_id"] for role in job_roles}
        selected_role_name = st.selectbox("Job Role", role_names, label_visibility="collapsed")
        run_clicked = st.button("Run ATS Analysis", type="primary")
        theme.card_close()

        if run_clicked:
            role_id = role_lookup[selected_role_name]
            required_skills = database.get_skills_for_role(role_id)
            resume_skills_found = extract_skills_from_text(extracted_text, required_skills)
            analysis = analyze_resume_for_role(resume_skills_found, required_skills)

            database.save_ats_result(
                user_id=st.session_state["user_id"],
                role_id=role_id,
                resume_id=resume_id,
                ats_score=analysis["ats_score"],
                matched_skills=analysis["matched_skills"],
                missing_skills=analysis["missing_skills"],
            )

            score = analysis["ats_score"]

            theme.card_open(eyebrow="Result", title=f"📊 {selected_role_name}")
            gauge_col, summary_col = st.columns([1, 2])
            with gauge_col:
                st.markdown(theme.render_score_gauge(score), unsafe_allow_html=True)
            with summary_col:
                st.markdown(
                    f"<span class='src-pill src-pill-match'>{analysis['total_matched']} matched</span> "
                    f"<span class='src-pill src-pill-gap'>{len(analysis['missing_skills'])} missing</span>",
                    unsafe_allow_html=True,
                )
                st.write("")
                if score >= 60:
                    st.markdown("✅ **Strong match** — your resume covers most of what this role needs.")
                elif score >= 35:
                    st.markdown("⚠️ **Partial match** — a few key skills would strengthen your fit.")
                else:
                    st.markdown("🔴 **Low match** — this role needs several skills not yet on your resume.")

            st.markdown("<br>", unsafe_allow_html=True)
            col_match, col_gap = st.columns(2)
            with col_match:
                st.markdown("**✅ Matched Skills**")
                theme.render_skill_chips(analysis["matched_skills"], kind="match")
            with col_gap:
                st.markdown("**⚠️ Skill Gap**")
                theme.render_skill_chips(analysis["missing_skills"], kind="gap")
            theme.card_close()

            recommendation = build_recommendation(score, analysis["missing_skills"])

            theme.card_open(eyebrow="Step 3", title="🧭 Your Career Roadmap")
            st.write(recommendation["verdict"])
            if recommendation["roadmap"]:
                st.markdown("##### Priority skills to learn next")
                for item in recommendation["roadmap"]:
                    st.markdown(f"**{item['skill']}**")
                    if item["resources"]:
                        for title, url in item["resources"]:
                            st.markdown(f"- [{title}]({url})")
                    else:
                        st.caption("No curated resource yet for this skill.")
            else:
                st.success("No priority gaps — you're well prepared for this role!")

            if score < 50:
                all_role_scores = []
                for role in job_roles:
                    r_skills = database.get_skills_for_role(role["role_id"])
                    r_found = extract_skills_from_text(extracted_text, r_skills)
                    r_analysis = analyze_resume_for_role(r_found, r_skills)
                    all_role_scores.append({"role_name": role["role_name"], "score": r_analysis["ats_score"]})
                alternatives = suggest_alternative_roles(all_role_scores, current_role=selected_role_name)
                if alternatives:
                    st.markdown("##### 💡 You may be a stronger fit for")
                    for alt in alternatives:
                        st.markdown(f"- **{alt['role_name']}** — {alt['score']}% match")
            theme.card_close()

            theme.card_open(eyebrow="Step 4", title="📥 Download Your Report")
            st.write("Get a full PDF summary of your ATS analysis and career roadmap.")
            pdf_bytes = generate_report(
                user_name=st.session_state["user_name"],
                resume_name=uploaded_file.name,
                role_name=selected_role_name,
                ats_score=score,
                matched_skills=analysis["matched_skills"],
                missing_skills=analysis["missing_skills"],
                verdict=recommendation["verdict"],
                roadmap=recommendation["roadmap"],
            )
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=f"ATS_Report_{selected_role_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
            theme.card_close()


if st.session_state["logged_in"]:
    show_dashboard()
else:
    login.show_auth_page()