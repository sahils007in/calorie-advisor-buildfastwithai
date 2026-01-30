import streamlit as st
from openai import OpenAI
from PIL import Image
import base64

# ---------------- Page Config ----------------
st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
st.title("🍽️ Calorie Advisor")
st.write("Upload a photo of your food to get calorie information!")

# ---------------- Session State ----------------
if "together_api_key" not in st.session_state:
    st.session_state.together_api_key = None
if "client" not in st.session_state:
    st.session_state.client = None
if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

# ---------------- API Key Validation ----------------
def validate_together_api_key(api_key: str) -> bool:
    try:
        test_client = OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        )

        test_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1
        )
        return True

    except Exception as e:
        msg = str(e).lower()
        if "quota" in msg or "rate limit" in msg:
            return True
        return False

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("🔑 Configuration")

    api_key_input = st.text_input(
        "Together API Key",
        type="password",
        help="Your API key is validated and used only for this session."
    )

    if api_key_input:
        if api_key_input.strip() != st.session_state.together_api_key:
            with st.spinner("Validating API key..."):
                is_valid = validate_together_api_key(api_key_input.strip())

            if is_valid:
                st.session_state.together_api_key = api_key_input.strip()
                st.session_state.client = OpenAI(
                    api_key=st.session_state.together_api_key,
                    base_url="https://api.together.xyz/v1"
                )
                st.session_state.api_key_valid = True
                st.success("✅ API key is valid")
            else:
                st.session_state.api_key_valid = False
                st.session_state.client = None
                st.error("❌ Invalid Together API key")

    st.markdown("---")
    st.markdown(
        "**Built by Sahil Jain** 🚀  \n"
        "[LinkedIn](https://www.linkedin.com/in/sahils007in/)"
    )

# ---------------- Block App ----------------
if not st.session_state.api_key_valid:
    st.info("👈 Enter a valid Together API key to start.")
    st.stop()

client = st.session_state.client

# ---------------- Helpers ----------------
def image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

def analyze_food(image_base64):
    prompt = """
    Analyze the food in this image and provide:
    1. List of food items with estimated calories
    2. Total estimated calories
    3. Simple health advice
    """

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ],
            }
        ],
        max_tokens=500,
        temperature=0.4,
    )

    return response.choices[0].message.content

# ---------------- UI ----------------
uploaded_file = st.file_uploader(
    "Upload your food image (jpg, jpeg, png)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Food Image", use_column_width=True)

    if st.button("Calculate Calories"):
        with st.spinner("Analyzing your food..."):
            result = analyze_food(image_to_base64(uploaded_file))
            st.success("Analysis Complete!")
            st.write(result)
