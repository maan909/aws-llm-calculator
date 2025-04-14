# Python module
import streamlit as st
import re  # To help parse the number of tokens from the query
import json

# Load updated pricing data from JSON file
file_path = "C:\\Users\\MaanPatel\\OneDrive - CloudThat\\projects\\llm_cal_project\\src\\llm_model_calculator\\data\\latest_prices.json"
with open("C:\\Users\\MaanPatel\\OneDrive - CloudThat\\projects\\llm_cal_project\\src\\llm_model_calculator\\data\\latest_prices.json", "r") as file:
    pricing_data = json.load(file)

# Set page configuration
st.set_page_config(page_title="LLM Cost Estimator Chatbot", layout="centered")

# App title
st.title("🤖 LLM Cost Estimator Chatbot")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box for user query
user_query = st.text_input("💬 Ask me about LLM pricing (e.g., 'How much does it cost for 100 input tokens for Jurassic-2 Ultra?')")

def calculate_cost(query):
    # Match tokens and type
    match = re.search(r"(\d+)\s*(input|output)\s*tokens", query, re.IGNORECASE)
    if not match:
        return "❓ Sorry, I couldn't extract token info from your query."

    token_count = int(match.group(1))
    token_type = match.group(2).lower()

    # Check for model names in the query
    for model_name in pricing_data:
        if model_name.lower() in query.lower():
            price_key = "input_price" if token_type == "input" else "output_price"
            price = pricing_data[model_name].get(price_key)

            if price is not None:
                cost = (token_count / 1000) * price
                return f"The cost for {token_count} {token_type} tokens for **{model_name}** is: **${cost:.4f}**"
            else:
                return f"⚠️ Pricing for {token_type} tokens for {model_name} is not available."

    return "❓ Sorry, I couldn't find any model name in your query."

# If user submits a query
if user_query:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", user_query))

    # Get bot reply
    bot_reply = calculate_cost(user_query)

    # Add bot reply to chat history
    st.session_state.chat_history.append(("bot", bot_reply))

# Display the chat history
st.markdown("---")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"🧑‍💻 **You:** {message}")
    else:
        st.markdown(f"🤖 **Bot:** {message}")
