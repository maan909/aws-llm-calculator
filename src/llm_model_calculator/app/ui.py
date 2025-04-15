import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
from fuzzywuzzy import fuzz

# Load DistilGPT-2
model_name_gpt = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name_gpt)
model = AutoModelForCausalLM.from_pretrained(model_name_gpt)

# Load pricing data
json_path = r"C:\\Users\\AdheeshShankar\\OneDrive - CloudThat\\llm_projects\\src\\llm_model_calculator\\data\\latest_prices.json"
with open(json_path, "r") as file:
    model_data = json.load(file)

# Extract dropdown options
valid_providers = sorted(set(entry["provider"] for entry in model_data.values() if entry["provider"]))
valid_regions = sorted(set(entry["region"] for entry in model_data.values() if entry["region"]))
valid_models = sorted(model_data.keys())

# Cost calculation
def calculate_cost(model_name, input_tokens, output_tokens, num_requests, model_data):
    matched_model = None
    highest_score = 0
    for candidate in model_data:
        score = fuzz.partial_ratio(model_name.lower(), candidate.lower())
        if score > highest_score and score > 70:
            highest_score = score
            matched_model = candidate

    if matched_model:
        details = model_data[matched_model]
        input_cost = details["input_price"] * input_tokens / 1000
        output_cost = details["output_price"] * output_tokens / 1000
        total_cost = (input_cost + output_cost) * num_requests

        return {
            "matched_model": matched_model,
            "input_cost": input_cost * num_requests,
            "output_cost": output_cost * num_requests,
            "total_cost": total_cost,
            "details": details
        }

    return None

# GPT fallback
def generate_response(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            top_p=0.92,
            temperature=0.75,
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

# UI
st.title("🤖 LLM Cost Estimation Chatbot")

# Session state
if "step" not in st.session_state:
    st.session_state.step = 0
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "done" not in st.session_state:
    st.session_state.done = False

# Keys and Questions
keys = ["model_provider", "region", "model_name", "input_tokens", "output_tokens", "num_requests"]
questions = {
    "model_provider": "Choose your model provider:",
    "region": "Choose the deployment region:",
    "model_name": "Choose the specific model name:",
    "input_tokens": "How many input tokens per request?",
    "output_tokens": "How many output tokens per request?",
    "num_requests": "Total number of requests expected?"
}

# Chat logic
if st.session_state.step < len(keys):
    current_key = keys[st.session_state.step]
    question = questions[current_key]

    st.markdown(f"**Q{st.session_state.step + 1}: {question}**")

    user_input = None

    if current_key == "model_provider":
        user_input = st.selectbox("", valid_providers, key="model_provider_input")
    elif current_key == "region":
        user_input = st.selectbox("", valid_regions, key="region_input")
    elif current_key == "model_name":
        selected_provider = st.session_state.responses.get("model_provider", "")
        selected_region = st.session_state.responses.get("region", "")
        filtered_models = [
            model_name for model_name, details in model_data.items()
            if details["provider"] == selected_provider and details["region"] == selected_region
        ]
        if not filtered_models:
            st.warning("⚠️ No models available for selected provider and region. Please go back and change.")
        else:
            user_input = st.selectbox("", sorted(filtered_models), key="model_name_input")
    else:
        user_input = st.text_input("", key=current_key + "_input")

    # Confirm with button
    if st.button("Next"):
        if user_input:
            st.session_state.responses[current_key] = user_input
            st.session_state.step += 1
            st.rerun()
        else:
            st.warning("Please provide a valid input before continuing.")

# Show cost after all questions
elif not st.session_state.done:
    try:
        input_tokens = int(st.session_state.responses.get("input_tokens", 0))
        output_tokens = int(st.session_state.responses.get("output_tokens", 0))
        num_requests = int(st.session_state.responses.get("num_requests", 1))
        model_name = st.session_state.responses.get("model_name", "")

        result = calculate_cost(model_name, input_tokens, output_tokens, num_requests, model_data)

        if result:
            st.markdown(f"### ✅ Pricing Summary for **{result['matched_model']}**:")
            st.markdown(f"- Input Price: ${result['details']['input_price']} per 1,000 tokens")
            st.markdown(f"- Output Price: ${result['details']['output_price']} per 1,000 tokens")
            st.markdown(f"- 🔢 Input Tokens × Requests: {input_tokens} × {num_requests} = {input_tokens * num_requests}")
            st.markdown(f"- 🔢 Output Tokens × Requests: {output_tokens} × {num_requests} = {output_tokens * num_requests}")
            st.markdown(f"- 💰 Input Cost: ${result['input_cost']:.6f}")
            st.markdown(f"- 💰 Output Cost: ${result['output_cost']:.6f}")
            st.markdown(f"### 💸 Total Cost: **${result['total_cost']:.6f}**")
        else:
            st.error("❌ Model not found or not priced. Please try again with a different option.")

    except ValueError:
        st.error("❌ Please enter valid numbers for tokens and request counts.")

    st.session_state.done = True

# Reset button
if st.session_state.step > 0:
    if st.button("🔄 Start Over"):
        st.session_state.step = 0
        st.session_state.responses = {}
        st.session_state.done = False
        st.rerun()
