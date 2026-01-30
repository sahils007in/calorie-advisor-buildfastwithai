import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import re

# ---------------- Page Config ----------------
st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
st.title("🍽️ Calorie Advisor")
st.write("Upload a photo of your food to get calorie information!")

# ---------------- Session State ----------------
for key in ["openai_api_key", "client", "api_key_valid", "vision_failed"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "api_key_valid" else False

# ---------------- API Key Validation ----------------
def validate_openai_api_key(api_key: str) -> bool:
    try:
        OpenAI(api_key=api_key).models.list()
        return True
    except Exception:
        return False

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("🔑 Configuration")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Used only for this session."
    )

    if api_key and api_key != st.session_state.openai_api_key:
        with st.spinner("Validating API key..."):
            if validate_openai_api_key(api_key):
                st.session_state.openai_api_key = api_key
                st.session_state.client = OpenAI(api_key=api_key)
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
    st.info("👈 Enter a valid OpenAI API key to continue.")
    st.stop()

client = st.session_state.client

# ---------------- Helpers ----------------
def image_to_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

# ---------------- Output Formatting ----------------
def prettify_output(text: str) -> str:
    # Remove stray markdown symbols
    text = text.replace("**", "").strip()

    # -------- FOOD ITEMS (dedupe + number) --------
    if "FOOD ITEMS:" in text:
        _, rest = text.split("FOOD ITEMS:", 1)
        lines = rest.splitlines()

        items = []
        seen = set()
        remainder = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "TOTAL CALORIES" in line.upper():
                remainder.append(line)
                break

            clean = line.lstrip("•-0123456789. ").strip()
            key = clean.lower()

            if clean and key not in seen:
                seen.add(key)
                items.append(clean)

        food_block = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
        text = f"FOOD ITEMS:\n{food_block}\n\n" + "\n".join(remainder)

    # -------- TOTAL CALORIES (highlight) --------
    text = re.sub(
        r"TOTAL CALORIES:\s*([~]?\d+[,\d]*)",
        r"### 🔥 TOTAL CALORIES: \1 calories",
        text,
        flags=re.IGNORECASE
    )

    # -------- HEALTH TIPS (clean bullets) --------
    if "HEALTH TIPS" in text:
        before, tips = text.split("HEALTH TIPS", 1)
        tips = tips.replace(":", "").strip()

        raw = re.split(r"(?:🥗|•|Tip\s*\d+)", tips, flags=re.IGNORECASE)
        clean = [t.strip() for t in raw if len(t.strip()) > 10]

        tips_block = "\n".join(f"🥗 {tip}" for tip in clean)
        text = f"{before.strip()}\n\nHEALTH TIPS:\n{tips_block}"

    return text.strip()

# ---------------- Vision Analysis ----------------
def analyze_food_with_vision(image_base64):
    system_prompt = """
You are a nutrition assistant.
If the image shows food, make a best-effort calorie estimate.
Do not refuse. Use common portion sizes.
"""

    user_prompt = """
Analyze the food in this image and return:

FOOD ITEMS:
1. Item - Calories

TOTAL CALORIES: Number

HEALTH TIPS:
• Tip 1
• Tip 2
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception:
        st.session_state.vision_failed = True
        return None

# ---------------- Text Fallback ----------------
def analyze_food_from_text(description):
    prompt = f"""
Estimate calories based on this food description:

{description}

Return:

FOOD ITEMS:
1. Item - Calories

TOTAL CALORIES: Number

HEALTH TIPS:
• Tip 1
• Tip 2
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
            image_b64 = image_to_base64(uploaded_file)
            result = analyze_food_with_vision(image_b64)

            if result:
                st.success("Analysis Complete!")
                st.markdown(prettify_output(result))
            else:
                st.warning("I couldn’t confidently identify the food.")

# ---------------- User Confirmation ----------------
if st.session_state.vision_failed:
    st.markdown("### Help me out 👇")
    description = st.text_input(
        "What food is this? (e.g., pizza, dal + rice, salad)"
    )

    if description and st.button("Estimate Calories from Description"):
        with st.spinner("Estimating calories..."):
            result = analyze_food_from_text(description)
            st.success("Estimated from your input!")
            st.markdown(prettify_output(result))
