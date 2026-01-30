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

# ---------------- Sidebar: API Key + Branding ----------------
with st.sidebar:
    st.header("🔑 Configuration")

    api_key_input = st.text_input(
        "Together API Key",
        type="password",
        help="Your API key is used only for this session and is not stored."
    )

    if api_key_input:
        st.session_state.together_api_key = api_key_input.strip()
        st.session_state.client = OpenAI(
            api_key=st.session_state.together_api_key,
            base_url="https://api.together.xyz/v1"
        )
        st.success("API key added")

    st.markdown("---")
    st.markdown(
        "**Built by Sahil Jain** 🚀  \n"
        "[LinkedIn](https://www.linkedin.com/in/sahils007in/)"
    )

# ---------------- Block App if No API Key ----------------
if not st.session_state.client:
    st.info("👈 Please enter your Together API key in the sidebar to start.")
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

    Format:
    FOOD ITEMS:
    1. Item - Calories

    TOTAL CALORIES: Number

    HEALTH TIPS:
    • Tip 1
    • Tip 2
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
            try:
                image_base64 = image_to_base64(uploaded_file)
                result = analyze_food(image_base64)
                st.success("Analysis Complete!")
                st.write(result)
            except Exception as e:
                st.error(f"Error analyzing image: {str(e)}")
