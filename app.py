import streamlit as st
import re
from PIL import Image
import pytesseract
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import requests
import yfinance as yf
import datetime
from sklearn.cluster import KMeans
from streamlit.components.v1 import html

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="BFSI OCR", layout="wide")

# -------------------- CUSTOM CSS --------------------
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    h1, h2, h3, h4 {
        color: #2c3e50;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border-radius: 8px;
        height: 3em;
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    .stNumberInput>div>div>input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- AUTHENTICATION --------------------

# Initialize session state for users and authentication
if "users" not in st.session_state:
    st.session_state["users"] = {}  # store user credentials
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def password_valid(password):
    # Password must have 1 upper, 1 lower, 1 digit, 1 special, min 8 characters
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$'
    return bool(re.match(pattern, password))

def sign_up():
    st.subheader("🔐 Sign Up")
    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    signup_btn = st.button("Sign Up")

    if signup_btn:
        if not username or not password:
            st.warning("⚠️ Username and password cannot be empty.")
            return
        if username in st.session_state["users"]:
            st.error("❌ Username already exists.")
            return
        if password != confirm_password:
            st.error("❌ Passwords do not match.")
            return
        if not password_valid(password):
            st.error("❌ Password must have:\n- 1 uppercase\n- 1 lowercase\n- 1 number\n- 1 special character\n- Minimum 8 characters.")
            return

        st.session_state["users"][username] = password
        st.success("✅ Sign up successful! Please sign in.")

def sign_in():
    st.subheader("🔒 Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    signin_btn = st.button("Sign In")

    if signin_btn:
        if username in st.session_state["users"] and st.session_state["users"][username] == password:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = username
            st.success(f"✅ Welcome, {username}!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

# -------------------- LOAD LOTTIE FUNCTION --------------------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def display_lottie_animation(url, height=300):
    lottie_json = load_lottieurl(url)
    if lottie_json:
        html(f"""
            <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
            <lottie-player src="{url}" background="transparent" speed="1"
             style="width: 100%; height: {height}px;" loop autoplay></lottie-player>
        """, height=height)

# -------------------- AUTHENTICATION FLOW --------------------
if not st.session_state["authenticated"]:
    st.title("🏦 BFSI OCR Authentication")
    auth_mode = st.radio("Select", ["Sign In", "Sign Up"])

    if auth_mode == "Sign In":
        sign_in()
    else:
        sign_up()

else:
    # -------------------- SIDEBAR NAV --------------------
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2344/2344128.png", width=100)
    st.sidebar.title(f"🏦 BFSI OCR - {st.session_state['current_user']}")
    navigation = st.sidebar.radio("📂 Navigate to", ("🏠 Home", "📄 Document Analysis", "🎓 Student Loan", "🔓 Logout"))

    # Logout Button
    if navigation == "🔓 Logout":
        st.session_state["authenticated"] = False
        st.rerun()

    # ----------- HOME SECTION -----------
    if navigation == "🏠 Home":
        st.markdown("<h1 style='text-align: center; color: #0066cc;'>🏦 BFSI OCR & Financial Insights</h1>", unsafe_allow_html=True)
        display_lottie_animation("https://assets4.lottiefiles.com/packages/lf20_touohxv0.json", height=300)

        st.markdown("""
            ### 🚀 AI-Powered Features
            - ✅ OCR-based Document Analysis  
            - ✅ Student Loan Eligibility  
            - ✅ EMI Calculator  
            - ✅ Stock Market Visualizations  
            - ✅ Clustering & Visualization from CSV  
        """)

    # ----------- DOCUMENT ANALYSIS SECTION -----------
    elif navigation == "📄 Document Analysis":
        st.markdown("## 📄 Document Analysis")

        analysis_type = st.selectbox("Select Analysis Type", ["Supervised", "Semi-Supervised", "Unsupervised"])

        # --------- SUPERVISED ---------
        if analysis_type == "Supervised":
            st.markdown("### 📄 OCR Text Extraction & Visualization (Supervised)")
            doc_type = st.selectbox("Choose Document Type", ["Bank Statement", "Invoice", "Payslip", "Profit and Loss"])
            uploaded_file = st.file_uploader("Upload Document Image", type=["png", "jpg", "jpeg"])

            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)

                if st.button("Run OCR Extraction & Analysis"):
                    with st.spinner("Processing OCR..."):
                        img = Image.open(uploaded_file).convert("RGB")
                        extracted_text = pytesseract.image_to_string(img, lang='eng')

                    st.success("✅ Extraction complete!")

                    with st.expander("📝 Extracted Text"):
                        st.text_area("Extracted Text", extracted_text, height=300)

                    words = re.findall(r'\b\w+\b', extracted_text.lower())
                    word_freq = Counter(words)
                    freq_df = pd.DataFrame(word_freq.items(), columns=["Word", "Frequency"]).sort_values(by="Frequency", ascending=False)

                    with st.expander("📊 Word Frequency Table"):
                        st.dataframe(freq_df)

                    # Visualization - Bar Chart
                    st.markdown("#### 📈 Word Frequency - Bar Chart")
                    top_n = 10
                    top_words = freq_df.head(top_n)

                    fig_bar, ax_bar = plt.subplots(figsize=(8, 5))
                    ax_bar.barh(top_words["Word"], top_words["Frequency"], color=plt.cm.Pastel1.colors)
                    ax_bar.invert_yaxis()
                    ax_bar.set_xlabel("Frequency")
                    ax_bar.set_title(f"Top {top_n} Words Frequency (Bar Chart)")
                    st.pyplot(fig_bar)

                    # Visualization - Pie Chart
                    st.markdown("#### 🟢 Word Frequency - Pie Chart")
                    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
                    ax_pie.pie(top_words["Frequency"], labels=top_words["Word"], autopct='%1.1f%%',
                               colors=plt.cm.Pastel2.colors, startangle=140)
                    ax_pie.set_title(f"Top {top_n} Words Distribution (Pie Chart)")
                    st.pyplot(fig_pie)

        # --------- SEMI-SUPERVISED ---------
        elif analysis_type == "Semi-Supervised":
            st.header("📈 Live & Past Week Stock Market Analysis (Semi-Supervised)")

            stock_map = {
                "Apple": "AAPL",
                "Google": "GOOG",
                "Microsoft": "MSFT",
                "Amazon": "AMZN",
                "Tesla": "TSLA"
            }

            stock_choice = st.selectbox("Select Stock", list(stock_map.keys()))
            ticker_symbol = stock_map[stock_choice]

            st.info(f"Fetching data for {stock_choice} ({ticker_symbol})...")

            today = datetime.date.today()
            one_week_ago = today - datetime.timedelta(days=7)

            try:
                ticker = yf.Ticker(ticker_symbol)

                todays_data = ticker.history(period="1d", interval="1m")
                if not todays_data.empty:
                    latest_price = todays_data['Close'].iloc[-1]
                    st.metric(label=f"💰 Live {stock_choice} Price", value=f"${latest_price:.2f}")
                else:
                    st.warning("Live data not available right now.")

                stock_data_week = yf.download(ticker_symbol, start=one_week_ago, end=today)

                if not stock_data_week.empty:
                    st.subheader(f"📊 {stock_choice} Stock Prices - Past 7 Days")
                    st.dataframe(stock_data_week[['Open', 'High', 'Low', 'Close', 'Volume']])

                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.plot(stock_data_week.index, stock_data_week['Close'], marker='o', linestyle='-', color='blue')
                    ax.set_title(f"{stock_choice} Closing Price (Last 7 Days)", fontsize=14)
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Price ($)")
                    ax.grid(True)
                    st.pyplot(fig)

                else:
                    st.warning(f"No historical data available for {stock_choice} ({ticker_symbol}).")

            except Exception as e:
                st.error(f"Error fetching stock data: {e}")

        # --------- UNSUPERVISED ---------
        elif analysis_type == "Unsupervised":
            st.header("📊 CSV Clustering & Visualization (Unsupervised)")

            uploaded_csv = st.file_uploader("Upload CSV file", type=["csv"])

            if uploaded_csv:
                df = pd.read_csv(uploaded_csv)
                st.subheader("Uploaded CSV Data")
                st.dataframe(df)

                numeric_df = df.select_dtypes(include=[np.number])

                if numeric_df.shape[1] < 2:
                    st.warning("⚠️ The CSV must have at least 2 numeric columns for clustering.")
                else:
                    st.success(f"✅ Found {numeric_df.shape[1]} numeric columns for clustering.")

                    k = st.slider("Select number of clusters (K)", min_value=2, max_value=10, value=3)

                    kmeans = KMeans(n_clusters=k, random_state=42)
                    cluster_labels = kmeans.fit_predict(numeric_df)

                    numeric_df["Cluster"] = cluster_labels
                    st.subheader("📋 Data with Cluster Labels")
                    st.dataframe(numeric_df)

                    st.subheader("📊 Cluster Visualization (Scatter Plot)")
                    fig, ax = plt.subplots(figsize=(8, 6))
                    scatter = ax.scatter(
                        numeric_df.iloc[:, 0],
                        numeric_df.iloc[:, 1],
                        c=cluster_labels,
                        cmap='viridis'
                    )
                    ax.set_xlabel(numeric_df.columns[0])
                    ax.set_ylabel(numeric_df.columns[1])
                    ax.set_title(f"KMeans Clustering (K={k})")
                    plt.colorbar(scatter, label='Cluster')
                    st.pyplot(fig)

                    st.subheader("🟢 Cluster Distribution (Pie Chart)")
                    cluster_counts = pd.Series(cluster_labels).value_counts().sort_index()

                    fig_pie, ax_pie = plt.subplots()
                    ax_pie.pie(cluster_counts, labels=[f'Cluster {i}' for i in cluster_counts.index],
                               autopct='%1.1f%%', colors=plt.cm.Paired.colors)
                    ax_pie.set_title("Cluster Distribution")
                    st.pyplot(fig_pie)

    # ----------- STUDENT LOAN ELIGIBILITY SECTION -----------
    elif navigation == "🎓 Student Loan":
        st.markdown("<h1 style='text-align: center; color: #FF5733;'>🎓 Student Loan Recommendation</h1>", unsafe_allow_html=True)
        display_lottie_animation("https://assets10.lottiefiles.com/packages/lf20_4dwjpruo.json", height=250)

        with st.form("loan_form"):
            st.markdown("### 📝 Fill Your Details Below")
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Name")
                age = st.number_input("Age", min_value=16, max_value=60)
                tenth_score = st.number_input("10th Grade Score (%)", min_value=0.0, max_value=100.0)

            with col2:
                twelfth_score = st.number_input("12th Grade Score (%)", min_value=0.0, max_value=100.0)
                family_income = st.number_input("Family Income (INR)", min_value=0)
                category = st.selectbox("Category", ["Undergraduate", "Postgraduate", "Abroad Studies"])

            loan_amount = st.number_input("Requested Loan Amount (INR)", min_value=0)
            submit_button = st.form_submit_button("Check Eligibility")

        if submit_button:
            st.markdown("### Eligibility Result")

            if tenth_score >= 60 and twelfth_score >= 60 and age <= 35:
                st.success(f"🎉 Congratulations {name}, you are eligible for an education loan!")

                st.markdown("### 📜 Bank Offers")
                sample_bank_offers = [
                    {"Bank": "SBI Bank", "Interest Rate": "8.5%", "Max Loan": "10 Lakh", "Tenure": "5 Years"},
                    {"Bank": "ICICI Bank", "Interest Rate": "9%", "Max Loan": "7 Lakh", "Tenure": "7 Years"},
                    {"Bank": "HDFC Bank", "Interest Rate": "7.5%", "Max Loan": "12 Lakh", "Tenure": "10 Years"},
                ]

                for offer in sample_bank_offers:
                    st.markdown(f"**🏦 Bank**: {offer['Bank']}")
                    st.markdown(f"**💰 Interest Rate**: {offer['Interest Rate']}")
                    st.markdown(f"**📈 Max Loan**: {offer['Max Loan']}")
                    st.markdown(f"**🕒 Tenure**: {offer['Tenure']}")
                    st.markdown("---")
            else:
                st.error(f"Sorry {name}, you are not eligible based on the provided information.")

        st.markdown("### 🧮 EMI Calculator")
        col1, col2, col3 = st.columns(3)

        with col1:
            principal = st.number_input("Loan Amount (₹)", min_value=0)

        with col2:
            rate_of_interest = st.number_input("Annual Interest Rate (%)", min_value=0.0)

        with col3:
            tenure_years = st.number_input("Tenure (Years)", min_value=0)

        if st.button("Calculate EMI"):
            if principal > 0 and rate_of_interest > 0 and tenure_years > 0:
                monthly_interest = rate_of_interest / (12 * 100)
                tenure_months = tenure_years * 12
                emi = (principal * monthly_interest * (1 + monthly_interest) ** tenure_months) / \
                      ((1 + monthly_interest) ** tenure_months - 1)
                st.success(f"✅ Your EMI is ₹ {emi:.2f} per month")
            else:
                st.warning("⚠️ Please enter valid values to calculate EMI.")
