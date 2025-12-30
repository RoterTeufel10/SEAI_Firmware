import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import PlainTextResponse
from pdf_parser import extract_pdf_text
from gpt_engine import generate_code
from compiler import compile_sketch

app = FastAPI()

PDF_PATH = "workspace/datasheet.pdf"
SKETCH_PATH = "workspace/sketch/sketch.ino"


def strip_markdown(code: str) -> str:
    """
    Removes Markdown code fences if the LLM accidentally adds them.
    """
    lines = code.strip().splitlines()

    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


@app.post("/generate")
async def generate(
    pdf: UploadFile,
    prompt: str = Form(...)
):
    try:
        # Ensure workspace exists
        os.makedirs("workspace/sketch", exist_ok=True)

        # Save PDF
        with open(PDF_PATH, "wb") as f:
            shutil.copyfileobj(pdf.file, f)

        datasheet_text = extract_pdf_text(PDF_PATH)
        error_log = None

        # Self-correction loop
        for _ in range(3):
            raw_code = generate_code(prompt, datasheet_text, error_log)
            code = strip_markdown(raw_code)

            with open(SKETCH_PATH, "w") as f:
                f.write(code)

            rc, output = compile_sketch()

            if rc == 0:
                return PlainTextResponse(code)

            error_log = output

        return {
            "status": "failed",
            "error": error_log
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "status": "crashed",
            "error": str(e)
        }

