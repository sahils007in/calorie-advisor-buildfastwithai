import streamlit as st
from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from PIL import Image

# Load env variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(image_bytes, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/jpeg",
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

def main():
    st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
    st.title("🍽️ Calorie Advisor")
    st.write("Upload a photo of your food to get calorie information!")

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
                1. List each food item and its calories
                2. Total calories
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
                    prompt
                )

                st.success("Analysis Complete!")
                st.write(response)

if __name__ == "__main__":
    main()
