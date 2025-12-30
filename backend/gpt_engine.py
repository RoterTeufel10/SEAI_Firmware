from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment FIRST
load_dotenv(dotenv_path="../.env")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are an embedded firmware expert.

STRICT RULES (MANDATORY):
- Output ONLY raw Arduino C/C++ code
- DO NOT use Markdown
- DO NOT use ``` fences
- DO NOT add explanations
- DO NOT add comments unless required by code
- First line MUST be valid C/C++ (e.g. #include or void setup)

Target:
- Arduino UNO (ATmega328P)
- Use Arduino HAL (SPI, Wire, pinMode) when available
- Otherwise use direct register access
- Code must compile with Arduino CLI
"""

def generate_code(user_prompt, datasheet_text, error_log=None):
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
{SYSTEM_PROMPT}

DATASHEET CONTEXT:
{datasheet_text}

USER REQUEST:
{user_prompt}
"""

    if error_log:
        prompt += f"""

COMPILER ERROR:
{error_log}

Fix the code.
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 2048
        }
    )

    return response.text.strip()

