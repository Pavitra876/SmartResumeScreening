import streamlit as st
import database
from auth import login
from resume_processing.pdf_reader import extract_text_from_pdf, get_basic_stats

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

    st.info("Next: we'll add ATS scoring and skill gap analysis here.")


# Main routing: show login/register page, or the dashboard, based on session state.
if st.session_state["logged_in"]:
    show_dashboard()
else:
    login.show_auth_page()