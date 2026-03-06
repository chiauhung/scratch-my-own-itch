import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Google Banana Costume Generator", page_icon="🍌", layout="wide"
)


# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    # Check if API key exists in environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Please set GEMINI_API_KEY environment variable")
        st.stop()
    # Client automatically reads GEMINI_API_KEY from environment
    return genai.Client()


client = get_gemini_client()

# Title
st.title("🍌 Google Banana Costume Generator")
st.markdown("Generate custom banana costume images using AI")

# Sidebar for user inputs
st.sidebar.header("Customize Your Banana Costume")

# Gender selection
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Non-binary", "Any"])

# Age group
age_group = st.sidebar.selectbox(
    "Age Group",
    [
        "Child (5-12)",
        "Teen (13-19)",
        "Young Adult (20-35)",
        "Adult (36-55)",
        "Senior (55+)",
    ],
)

# Height
height = st.sidebar.selectbox("Height", ["Short", "Average", "Tall"])

# Weight/Build
build = st.sidebar.selectbox("Build", ["Slim", "Average", "Athletic", "Heavyset"])

# Expression
expression = st.sidebar.selectbox(
    "Expression",
    ["Happy", "Excited", "Silly", "Cool", "Surprised", "Confident", "Playful"],
)

# Skin tone
skin_tone = st.sidebar.selectbox(
    "Skin Tone", ["Light", "Fair", "Medium", "Olive", "Tan", "Brown", "Dark"]
)

# Pose/Style
pose = st.sidebar.selectbox(
    "Pose/Style",
    [
        "Standing",
        "Dancing",
        "Jumping",
        "Arms spread",
        "Thumbs up",
        "Peace sign",
        "Action pose",
    ],
)

# Background
background = st.sidebar.selectbox(
    "Background",
    [
        "White studio",
        "Colorful",
        "Party scene",
        "Outdoor",
        "Cyberpunk city",
        "Tropical beach",
        "Space",
    ],
)

# Additional details
additional_details = st.sidebar.text_area(
    "Additional Details (optional)",
    placeholder="e.g., wearing sunglasses, holding a prop, specific accessories...",
)

# Generate button
if st.sidebar.button("🎨 Generate Image", type="primary", use_container_width=True):
    # Build the prompt
    prompt_parts = [
        f"Create a realistic photo of a {gender.lower()} person wearing a full banana costume.",
        f"Age group: {age_group}.",
        f"Height: {height}, Build: {build}.",
        f"Facial expression: {expression}.",
        f"Skin tone: {skin_tone}.",
        f"Pose: {pose}.",
        f"Background: {background}.",
    ]

    if additional_details:
        prompt_parts.append(f"Additional details: {additional_details}.")

    prompt = " ".join(prompt_parts)

    # Display the prompt
    with st.expander("View Generated Prompt"):
        st.code(prompt)

    # Generate image
    with st.spinner("Generating your banana costume image..."):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt,
            )

            # Display the generated image
            image_found = False

            # Check if response has parts and iterate through them
            if hasattr(response, "parts") and response.parts is not None:
                for part in response.parts:
                    if part.inline_data is not None:
                        # Get the image object from Gemini
                        gemini_image = part.as_image()
                        gemini_image.save("generated_image.png")

                        # Load the saved image as a standard PIL Image for Streamlit display
                        pil_image = Image.open("generated_image.png")

                        # Display the image
                        st.image(
                            pil_image,
                            caption="Generated Banana Costume",
                            width="stretch",
                        )
                        image_found = True

                        # Download button
                        with open("generated_image.png", "rb") as file:
                            st.download_button(
                                label="Download Image",
                                data=file,
                                file_name="banana_costume.png",
                                mime="image/png",
                            )

            else:
                # Response might be text instead of image
                st.warning("The model returned a text response instead of an image.")
                if hasattr(response, "text"):
                    st.write("Response text:", response.text)
                st.info(
                    "Note: Image generation may require a different model. Try 'imagen-3.0-generate-001' or check the Gemini API documentation for available image generation models."
                )

            if not image_found:
                st.warning(
                    "No image was generated. The response did not contain image data."
                )

        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            st.info("Please check your GEMINI_API_KEY and model availability.")
            import traceback

            with st.expander("Show error details"):
                st.code(traceback.format_exc())

# Main content area - show instructions when no image is generated
else:
    st.info(
        "👈 Use the sidebar to customize your banana costume and click 'Generate Image'"
    )

    # Show example
    st.subheader("Example")
    st.markdown("""
    This app uses Google's Gemini AI to generate realistic images of people wearing banana costumes
    based on your specifications. Simply:

    1. Select your preferences in the sidebar
    2. Add any additional details (optional)
    3. Click the 'Generate Image' button
    4. Wait for your custom banana costume image to appear
    5. Download it if you like it!
    """)

    st.markdown("---")
    st.caption("Powered by Google Gemini API")
