import streamlit as st
from openai import OpenAI
from PIL import Image
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
st.title("🍽️ Calorie Advisor")
st.write("Upload a photo of your food to get calorie information!")

# ---------------- Session State ----------------
for key in ["together_api_key", "client", "api_key_valid", "vision_failed"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "api_key_valid" else False

# ---------------- API Key Validation ----------------
def validate_together_api_key(api_key: str) -> bool:
    try:
        OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        ).chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        return True
    except Exception as e:
        return "quota" in str(e).lower() or "rate limit" in str(e).lower()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("🔑 Configuration")

    api_key = st.text_input(
        "Together API Key",
        type="password",
        help="Validated and used only for this session."
    )

    if api_key and api_key != st.session_state.together_api_key:
        with st.spinner("Validating API key..."):
            if validate_together_api_key(api_key):
                st.session_state.together_api_key = api_key
                st.session_state.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.together.xyz/v1"
                )
                st.session_state.api_key_valid = True
                st.success("✅ API key is valid")
            else:
                st.session_state.api_key_valid = False
                st.error("❌ Invalid API key")

    st.markdown("---")
    st.markdown(
        "**Built by Sahil Jain** 🚀  \n"
        "[LinkedIn](https://www.linkedin.com/in/sahils007in/)"
    )

# ---------------- Guard ----------------
if not st.session_state.api_key_valid:
    st.info("👈 Enter a valid Together API key to continue.")
    st.stop()

client = st.session_state.client

# ---------------- Helpers ----------------
def image_to_base64(uploaded_file):
    return (
        base64.b64encode(uploaded_file.getvalue()).decode("utf-8"),
        uploaded_file.type
    )

# ---------------- Vision Analysis ----------------
def analyze_food_with_vision(image_b64, mime):
    prompt = """
You are a nutrition assistant.

If the image shows food, make a BEST-EFFORT calorie estimate even if details are unclear.
Do NOT refuse. Do NOT say you cannot analyze the image.

If unsure, estimate using common portion sizes.

Return in this format:

FOOD ITEMS:
1. Item - Calories

TOTAL CALORIES: Number

HEALTH TIPS:
• Tip 1
• Tip 2
"""

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{image_b64}"
                        }
                    }
                ]
            }],
            max_tokens=500,
            temperature=0.4,
        )
        return response.choices[0].message.content

    except Exception:
        st.session_state.vision_failed = True
        return None

# ---------------- Text Fallback (Option 2) ----------------
def analyze_food_from_text(description):
    prompt = f"""
Estimate calories based on this food description:

{description}

Format:

FOOD ITEMS:
1. Item - Calories

TOTAL CALORIES: Number

HEALTH TIPS:
• Tip 1
• Tip 2
"""
    response = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
    )
    return response.choices[0].message.content

# ---------------- UI ----------------
uploaded_file = st.file_uploader(
    "Upload your food image (jpg, jpeg, png)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    st.image(Image.open(uploaded_file), caption="Your Food Image", use_column_width=True)

    if st.button("Calculate Calories"):
        with st.spinner("Analyzing your food..."):
            image_b64, mime = image_to_base64(uploaded_file)
            result = analyze_food_with_vision(image_b64, mime)

            if result:
                st.success("Analysis Complete!")
                st.write(result)
            else:
                st.warning("I couldn’t confidently identify the food.")

# ---------------- Option 2: User Confirmation ----------------
if st.session_state.vision_failed:
    st.markdown("### Help me out 👇")
    description = st.text_input(
        "What food is this? (e.g., bowl of rice, dal + roti, grilled chicken)"
    )

    if description and st.button("Estimate Calories from Description"):
        with st.spinner("Estimating calories..."):
            result = analyze_food_from_text(description)
            st.success("Estimated from your input!")
            st.write(result)
