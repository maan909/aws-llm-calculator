# Python module
import streamlit as st
import re  # To help parse the number of tokens from the query

# Sample data for Jurassic-2 Ultra
pricing_data = {
    "Jurassic-2 Ultra": {
        "input_tokens": 0.0188,
        "output_tokens": 0.0188
    }
}

# Set page configuration
st.set_page_config(page_title="LLM Cost Estimator Chatbot", layout="centered")

# App title
st.title("🤖 LLM Cost Estimator Chatbot")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input box for user query
user_query = st.text_input("💬 Ask me about LLM pricing (e.g., 'How much does it cost for 100 input tokens for Jurassic-2 Ultra?')")

def calculate_cost(query, model_name):
    # Extract token amount from the query (either "100 input tokens" or "1000 input tokens")
    match = re.search(r"(\d+)\s*(input|output)\s*tokens", query, re.IGNORECASE)
    
    if match:
        token_count = int(match.group(1))
        token_type = match.group(2).lower()

        # Retrieve pricing data for the model
        if model_name in pricing_data:
            price_per_1000_tokens = pricing_data[model_name]["input_tokens"] if token_type == "input" else pricing_data[model_name]["output_tokens"]
            cost = (token_count / 1000) * price_per_1000_tokens
            return f"The cost for {token_count} {token_type} tokens for {model_name} is: ${cost:.4f}"

    return "❓ Sorry, I couldn't process your query correctly."

# If user submits a query
if user_query:
    # Add user message to chat history
    st.session_state.chat_history.append(("user", user_query))

    # Check if the query contains model name and the type of tokens
    if "Jurassic-2 Ultra" in user_query:
        bot_reply = calculate_cost(user_query, "Jurassic-2 Ultra")
    else:
        bot_reply = "❓ Sorry, I couldn't find any pricing info related to your query."

    # Add bot reply to chat history
    st.session_state.chat_history.append(("bot", bot_reply))

# Display the chat history
st.markdown("---")
for sender, message in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"🧑‍💻 **You:** {message}")
    else:
        st.markdown(f"🤖 **Bot:** {message}")
