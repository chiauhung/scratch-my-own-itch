# 🍌 Google Banana Costume Generator

A fun Streamlit app that generates custom banana costume images using Google's Gemini AI API. Users can customize various features like gender, age, height, expression, and more to create unique banana costume photos.

## Features

- **Interactive Sidebar**: Easy-to-use dropdown menus for customization
- **Multiple Customization Options**:
  - Gender (Male, Female, Non-binary, Any)
  - Age Group (Child, Teen, Young Adult, Adult, Senior)
  - Height (Short, Average, Tall)
  - Build (Slim, Average, Athletic, Heavyset)
  - Expression (Happy, Excited, Silly, Cool, etc.)
  - Skin Tone (Light, Fair, Medium, Olive, Tan, Brown, Dark)
  - Pose/Style (Standing, Dancing, Jumping, etc.)
  - Background (Studio, Colorful, Party, Outdoor, etc.)
- **Additional Details**: Optional text field for custom additions
- **Image Download**: Download generated images as PNG files
- **Prompt Preview**: View the generated AI prompt before image creation

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

## Setup Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd google-banana-costume
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```

3. **Set up your environment variables**:
   - Copy the example environment file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. **Run the Streamlit app**:
   ```bash
   uv run streamlit run app.py
   ```

5. **Open your browser**:
   - The app should automatically open at `http://localhost:8501`
   - If not, navigate to the URL shown in your terminal

## Usage

1. Use the sidebar on the left to select your preferences:
   - Choose gender, age group, height, build
   - Select expression, skin tone, and pose
   - Pick a background setting
   - Optionally add custom details

2. Click the "🎨 Generate Image" button

3. Wait for the AI to generate your custom banana costume image

4. Download the image if you like it!

## Project Structure

```
google-banana-costume/
├── app.py              # Main Streamlit application
├── pyproject.toml      # Project dependencies (managed by uv)
├── .env.example        # Example environment variables
├── .env                # Your actual API key (git-ignored)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Technologies Used

- **Streamlit**: Web app framework
- **Google Gemini API**: AI image generation
- **PIL (Pillow)**: Image processing
- **python-dotenv**: Environment variable management
- **uv**: Fast Python package manager

## Troubleshooting

- **API Key Error**: Make sure your `GEMINI_API_KEY` is correctly set in the `.env` file
- **Module Not Found**: Run `uv sync` to install all dependencies
- **Image Not Generating**: Check your internet connection and API key validity

## Notes

- The app uses the `gemini-2.0-flash-exp` model for image generation
- Generated images are based on AI interpretation and may vary
- Each image generation consumes API credits

## License

This is a prototype project for demonstration purposes.

---

**Powered by Google Gemini API** 🚀
