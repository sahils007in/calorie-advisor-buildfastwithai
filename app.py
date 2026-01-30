# Import required libraries
import streamlit as st  # for creating the web app
from dotenv import load_dotenv  # for loading API key from .env file
import os
import google.generativeai as genai  # Google's AI model
from PIL import Image  # for handling images

# Load the API key from .env file
load_dotenv()

# Set up the Google Gemini AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get AI response about the food image
def get_gemini_response(image, prompt):
    """Send image to Google's AI and get calorie information"""
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content([image[0], prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to prepare the uploaded image for AI processing
def prepare_image(uploaded_file):
    """Convert uploaded image to format required by Google's AI"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        return None

# Main web app
def main():
    # Set up the webpage
    st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
    
    # Add title and description
    st.title("🍽️ Calorie Advisor")
    st.write("Upload a photo of your food to get calorie information!")

    # Create file uploader
    uploaded_file = st.file_uploader(
        "Upload your food image (jpg, jpeg, or png)",
        type=["jpg", "jpeg", "png"]
    )

    # Display uploaded image
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Food Image", use_column_width=True)

        # Create Analyze button
        if st.button("Calculate Calories"):
            with st.spinner("Analyzing your food..."):
                # Prepare the prompt for AI
                prompt = """
                Please analyze this food image and provide:
                1. List each food item and its calories
                2. Total calories
                3. Simple health advice

                Format like this:
                FOOD ITEMS:
                1. [Food Item] - [Calories]
                2. [Food Item] - [Calories]

                TOTAL CALORIES: [Number]

                HEALTH TIPS:
                • [Tip 1]
                • [Tip 2]
                """

                # Get and display AI response
                image_data = prepare_image(uploaded_file)
                if image_data is not None:
                    response = get_gemini_response(image_data, prompt)
                    st.success("Analysis Complete!")
                    st.write(response)
                else:
                    st.error("Please upload an image first!")

# Run the app
if __name__ == "__main__":
    main()
