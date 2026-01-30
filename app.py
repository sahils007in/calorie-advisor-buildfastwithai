import streamlit as st
import google.genai as genai
from google.genai import types
from PIL import Image

# ---------------- Page Config ----------------
st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
st.title("🍽️ Calorie Advisor")
st.write("Upload a photo of your food to get calorie information!")

# ---------------- API Key ----------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("GOOGLE_API_KEY not found. Please add it in Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------------- Gemini Call ----------------
def get_gemini_response(image_bytes, mime_type, prompt):
    try:
        response = client.models.generate_content(
            model="models/gemini-1.0-pro-vision-latest",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=image_bytes
                            )
                        )
                    ]
                )
            ]
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- UI ----------------
uploaded_file = st.file_uploader(
    "Upload your food image (jpg, jpeg, or png)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Food Image", use_column_width=True)

    if st.button("Calculate Calories"):
        with st.spinner("Analyzing your food..."):
            prompt = """
            Please analyze this food image and provide:
            1. List each food item and its estimated calories
            2. Total estimated calories
            3. Simple health advice

            Format like this:

            FOOD ITEMS:
            1. [Food Item] - [Calories]

            TOTAL CALORIES: [Number]

            HEALTH TIPS:
            • [Tip 1]
            • [Tip 2]
            """

            response = get_gemini_response(
                uploaded_file.getvalue(),
                uploaded_file.type,
                prompt
            )

            st.success("Analysis Complete!")
            st.write(response)

# ---------------- Footer ----------------
st.markdown("---")
st.markdown(
    "Built by **Sahil Jain** 🚀  \n"
    "[LinkedIn](https://www.linkedin.com/in/sahils007in/)"
)
