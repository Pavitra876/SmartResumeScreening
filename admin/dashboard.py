"""
admin/dashboard.py
Admin analytics dashboard - shows system-wide stats, charts, and user activity.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import database
import theme


def show_admin_dashboard():
    st.title("📊 Admin Analytics Dashboard")
    st.caption("System-wide overview of resume screenings and skill trends.")

    conn = database.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT ats_results.ats_score, ats_results.matched_skills,
               ats_results.missing_skills, ats_results.analysis_date,
               job_roles.role_name, users.name as user_name
        FROM ats_results
        JOIN job_roles ON ats_results.role_id = job_roles.role_id
        JOIN users ON ats_results.user_id = users.user_id
    """)
    results = cur.fetchall()

    cur.execute("SELECT COUNT(*) as c FROM users")
    total_users = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) as c FROM resume")
    total_resumes = cur.fetchone()["c"]

    conn.close()

    theme.card_open()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Users", total_users)
    col2.metric("📄 Resumes Uploaded", total_resumes)
    col3.metric("🔍 Analyses Run", len(results))
    avg_score = round(sum(r["ats_score"] for r in results) / len(results), 1) if results else 0
    col4.metric("⭐ Avg ATS Score", f"{avg_score}%")
    theme.card_close()

    if not results:
        st.info("No analysis data yet. Students need to run ATS analyses first.")
        return

    df = pd.DataFrame([dict(r) for r in results])

    theme.card_open(eyebrow="Analytics", title="ATS Score Distribution")
    col_chart, col_gauge = st.columns([2, 1])

    with col_chart:
        bins = [0, 20, 40, 60, 80, 100]
        labels = ["0–20", "21–40", "41–60", "61–80", "81–100"]
        df["score_band"] = pd.cut(df["ats_score"], bins=bins, labels=labels, include_lowest=True)
        band_counts = df["score_band"].value_counts().sort_index().reset_index()
        band_counts.columns = ["Score Range", "Count"]
        fig = px.bar(band_counts, x="Score Range", y="Count",
                     color="Count", color_continuous_scale=["#FEE2E2", "#10B981"])
        fig.update_layout(showlegend=False, plot_bgcolor="white",
                          paper_bgcolor="white", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_gauge:
        st.markdown(theme.render_score_gauge(avg_score, label="Avg Score"),
                    unsafe_allow_html=True)

    theme.card_close()

    theme.card_open(eyebrow="Skill Insights", title="Most Common Skill Gaps")
    all_missing = []
    for r in results:
        if r["missing_skills"]:
            all_missing.extend(r["missing_skills"].split(","))

    if all_missing:
        from collections import Counter
        skill_counts = Counter(all_missing).most_common(10)
        skill_df = pd.DataFrame(skill_counts, columns=["Skill", "Frequency"])
        fig2 = px.bar(skill_df, x="Frequency", y="Skill", orientation="h",
                      color="Frequency", color_continuous_scale=["#FEF3C7", "#F59E0B"])
        fig2.update_layout(showlegend=False, plot_bgcolor="white",
                           paper_bgcolor="white", coloraxis_showscale=False,
                           yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)
    theme.card_close()

    theme.card_open(eyebrow="Role Breakdown", title="Average ATS Score by Job Role")
    role_avg = df.groupby("role_name")["ats_score"].mean().reset_index()
    role_avg.columns = ["Role", "Avg Score"]
    role_avg["Avg Score"] = role_avg["Avg Score"].round(1)
    fig3 = px.bar(role_avg, x="Role", y="Avg Score",
                  color="Avg Score", color_continuous_scale=["#DBEAFE", "#10B981"], text="Avg Score")
    fig3.update_traces(texttemplate="%{text}%", textposition="outside")
    fig3.update_layout(showlegend=False, plot_bgcolor="white",
                       paper_bgcolor="white", coloraxis_showscale=False, yaxis_range=[0, 110])
    st.plotly_chart(fig3, use_container_width=True)
    theme.card_close()

    theme.card_open(eyebrow="Recent Activity", title="Latest Analyses")
    display_df = df[["user_name", "role_name", "ats_score", "analysis_date"]].copy()
    display_df.columns = ["User", "Role", "ATS Score (%)", "Date"]
    display_df = display_df.sort_values("Date", ascending=False).head(10)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    theme.card_close()