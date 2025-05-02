import streamlit as st
import os
import smtplib
from email.mime.text import MIMEText
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Initialize LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

# Prompt Template
prompt_template = PromptTemplate.from_template("""
### CUSTOMER ISSUE:
{customer_issue}

### INSTRUCTION:
You are a Financial Support Agent. A customer has described a financial problem. Your job is to:
1. Identify the issue category.
2. Ask for account number if not collected.
3. Confirm the details with the customer.
4. Summarize the issue for sending to the bank.

Provide a clear, formal summary after confirmation that can be emailed to the bank.
""")

# App layout
st.set_page_config(layout="wide")
st.title("Human-like Financial Support Chatbot")
st.caption("Handles transaction failure, complaint summary, and email to bank support.")

# Initialize session
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.account_number = ""
    st.session_state.issue = ""
    st.session_state.summary = ""

# Step 0: Ask for account number
if st.session_state.step == 0:
    st.subheader("🔐 Step 1: Account Verification")
    acc = st.text_input("Please enter your account number to begin:")
    if acc:
        st.session_state.account_number = acc
        st.session_state.step = 1
        st.rerun()

# Step 1: Ask for issue
elif st.session_state.step == 1:
    st.subheader("💬 Step 2: Describe Your Issue")
    issue = st.text_area("Tell us your issue in detail:")
    if issue:
        st.session_state.issue = issue
        st.session_state.step = 2
        st.rerun()

# Step 2: Generate and show summary
elif st.session_state.step == 2:
    st.subheader("📄 Step 3: Review the Summary")

    prompt_input = f"Account Number: {st.session_state.account_number}\nIssue: {st.session_state.issue}"
    response = llm.invoke(prompt_template.format(customer_issue=prompt_input))
    summary = response.content.strip()

    st.session_state.summary = summary
    st.markdown(f"**Summary Generated:**\n\n{summary}")
    
    if st.button("✅ Confirm and Send to Bank"):
        st.session_state.step = 3
        st.rerun()

# Step 3: Send email
# Step 3: Send email
elif st.session_state.step == 3:
    st.subheader("📤 Step 4: Complaint Submitted")

    # Extract only the confirmation summary part
    if "### CONFIRMATION SUMMARY FOR BANK:" in st.session_state.summary:
        summary_clean = st.session_state.summary.split("### CONFIRMATION SUMMARY FOR BANK:")[-1].strip()
    else:
        summary_clean = st.session_state.summary  # fallback in case format changes

    # Email config
    sender_email = "sanhulk73@gmail.com"
    sender_password = "lqdh rosa cdcz xlyr"  # App password
    receiver_email = "sanjayshankar91@gmail.com"
    subject = "Customer Complaint - Transaction Issue"
    message = summary_clean

    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        st.success("Complaint summary sent to the bank successfully! ✅")
        st.code(message)

    except Exception as e:
        st.error("Failed to send email.")
        st.exception(e)

    if st.button("🔁 Start New Conversation"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

