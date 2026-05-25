import streamlit as st
import dashboard as dashboard
import base64

st.set_page_config(
    page_title="ORION",
    page_icon="📊",
    layout="wide"
)

# --------- PAGE STATE INIT ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to_dashboard():
    st.session_state.page = "dashboard"
    st.rerun()  # Only here, for navigation!

# --------- PAGE ROUTER ----------
if st.session_state.page == "dashboard":
    dashboard.show()
    st.stop()  # End further rendering

# --------- Custom CSS ----------
st.markdown(
    """
    <style>
    .main { background-color: #0f172a; color: white; }
    .hero { padding: 80px 20px; text-align: center; background: linear-gradient(135deg, #1e293b, #2563eb); border-radius: 20px; margin-bottom: 40px; }
    .hero h1 { font-size: 60px; color: white; margin-bottom: 10px; }
    .hero p { font-size: 22px; color: #e2e8f0; }
    .feature-card { background-color: #1e293b; padding: 25px; border-radius: 16px; text-align: center; box-shadow: 0px 4px 12px rgba(0,0,0,0.3); height: 100%; }
    .feature-card h3 { color: #60a5fa; }
    .cta { background: linear-gradient(135deg, #2563eb, #7c3aed); padding: 50px; border-radius: 20px; text-align: center; margin-top: 50px; }
    .footer { text-align: center; margin-top: 40px; color: #94a3b8; }
    .grid-font-color { color: #ffffff; }
    div.stButton > button { margin: 0px 0px !important; padding: 5px 10px !important;}
    div[data-testid="column"] { padding-left: 4px !important; padding-right: 4px !important; }
    </style>
    """, unsafe_allow_html=True
)
# --------- Navbar ----------
col1, col2 = st.columns([3, 1]) 
with col2:
    b1, b2 = st.columns([1, 1])
    with b1:
        st.button("Home", disabled=True)
    with b2:
        if st.button("Dashboard"):
            go_to_dashboard()

# --------- Hero Section ----------
st.markdown(
    """
    <div class='hero'>
        <h1>ORION: AI Driven Daily Production Assistant</h1>
        <p>Modern AI-powered part characteristics analytics platform.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- Hero CTA ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started", use_container_width=True):
        go_to_dashboard()

# --------- Features ----------
st.markdown("## ✨ Features")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div class='feature-card'>
            <h3>📊 Real-Time Analytics</h3>
            <p class='grid-font-color'>Track your part characteristics instantly with interactive dashboards.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        """
        <div class='feature-card'>
            <h3>🤖 AI Automation</h3>
            <p class='grid-font-color'>Automate reporting and predictive analysis for part characteristics using AI models.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        """
        <div class='feature-card'>
            <h3>☁️ SPC Integration</h3>
            <p class='grid-font-color'>Connect seamlessly with SPC systems and APIs for part characteristics data.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------- Statistics ----------
st.markdown("## 📈 Part Characteristics Statistics")
stats1, stats2, stats3, stats4 = st.columns(4)
stats1.metric("Users", "25K+")
stats2.metric("Reports Generated", "1.2M")
stats3.metric("Accuracy", "98%")
stats4.metric("Uptime", "99.9%")

# --------- Testimonials ----------
st.markdown("## 💬 What Our Clients Say")
review1, review2 = st.columns(2)
with review1:
    st.info('"This platform transformed our business analytics workflow completely."')
with review2:
    st.info('"Clean dashboards and powerful AI insights. Highly recommended!"')

# --------- CTA Section ----------
st.markdown(
    """
    <div class='cta grid-font-color'>
        <h2>Ready to scale your analytics?</h2>
        <p>Start your journey with our AI-powered platform today.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --------- Contact Form ----------
st.markdown("## 📩 Contact Us")
with st.form("contact_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")
    submitted = st.form_submit_button("Send Message")
    if submitted:
        st.success(f"Thank you {name}, we will contact you soon!")

# --------- Footer ----------
st.markdown(
    """
    <div class='footer'>
        © 2026 AI Analytics Platform | Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
