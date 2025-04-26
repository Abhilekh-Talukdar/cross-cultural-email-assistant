import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Configuration ---
# Allow requests from your React frontend (adjust origin if needed)
origins = [
    "http://localhost:3000", # Default React dev server port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Request and Response Models (using Pydantic) ---
class EmailInput(BaseModel):
    subject: str
    body: str
    target_culture: str
    tone_emphasis: str | None = None # Optional tone

class RewriteOutput(BaseModel):
    rewritten_subject: str
    rewritten_body: str
    cultural_notes: str

# --- Cultural Guidance Data (Expand this!) ---
CULTURAL_GUIDANCE = {
    "Japan": "Adopt an indirect and highly polite tone. Use appropriate honorifics if possible (though difficult without context). Emphasize harmony and avoid strong negatives or direct demands. Use formal openings and closings (e.g., 'Sincerely yours,'). Structure may be less direct than Western styles.",
    "U.S.": "Be direct, clear, and concise. Focus on the main point or action needed early on. Use a friendly but professional tone. Explicitly state deadlines or requests. Standard professional closings (e.g., 'Best regards,', 'Sincerely,').",
    "U.K.": "Maintain politeness and a degree of formality, often using understatement. Avoid overly strong or enthusiastic language. Suggestions or criticisms may be phrased indirectly (e.g., 'Perhaps we could consider...'). Standard polite closings (e.g., 'Kind regards,', 'Best regards,').",
    "France": "A degree of formality is expected. Logic and intellectual reasoning can be appreciated. Tone can sometimes be more direct or critical than U.K. style, but maintain professional courtesy. Standard formal closings (e.g., 'Cordialement,').",
    "India": "Show respect, especially if addressing someone senior. Deference to hierarchy is common. Use polite and courteous language. Opening pleasantries might be slightly longer. Closing should be respectful (e.g., 'Warm regards,', 'Respectfully,').",
    "Germany": "Be direct, factual, and precise. Focus on information and avoid excessive small talk. Formality is generally preferred in initial contact (using 'Sie' form conceptually). Structure emails logically. Formal closings (e.g., 'Mit freundlichen Grüßen')."
    # Add more cultures as needed
}

# --- API Endpoint ---
@app.post("/rewrite", response_model=RewriteOutput)
async def rewrite_email(email_input: EmailInput):
    """
    Rewrites an email based on the target culture and optional tone emphasis.
    """
    culture_guidance = CULTURAL_GUIDANCE.get(email_input.target_culture)
    if not culture_guidance:
        raise HTTPException(status_code=400, detail=f"Cultural guidance for '{email_input.target_culture}' not found.")

    tone_instruction = f" Additionally, emphasize {email_input.tone_emphasis}." if email_input.tone_emphasis else ""

    # --- Prompt Engineering ---
    # This is the core part. Craft a detailed prompt for the LLM.
    prompt = f"""
    You are an expert cross-cultural communication assistant. Your task is to rewrite an email to be appropriate for a recipient from {email_input.target_culture}.

    Cultural Guidance for {email_input.target_culture}: {culture_guidance}{tone_instruction}

    Original Email Subject: {email_input.subject}
    Original Email Body:
    {email_input.body}

    Instructions:
    1. Rewrite the email subject and body strictly following the cultural guidance provided above.
    2. Maintain the core message and intent of the original email.
    3. Do NOT invent new information unless necessary for cultural adaptation (e.g., slightly adjusting phrasing for politeness).
    4. Provide brief "Cultural Notes" explaining the key changes you made and why they align with the target culture's communication style. Format these notes clearly.

    Output the result in the following format ONLY:
    ### Rewritten Subject ###
    [Your rewritten subject here]

    ### Rewritten Body ###
    [Your rewritten email body here]

    ### Cultural Notes ###
    [Your concise explanation of changes here]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Or your preferred GPT model
            messages=[
                {"role": "system", "content": "You are a cross-cultural communication assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, # Adjust creativity vs. predictability
            max_tokens=1000 # Adjust based on expected output length
        )

        content = response.choices[0].message.content

        # --- Parse the LLM Output ---
        # This parsing relies on the specific format requested in the prompt.
        subject_start = content.find("### Rewritten Subject ###") + len("### Rewritten Subject ###")
        body_start = content.find("### Rewritten Body ###")
        notes_start = content.find("### Cultural Notes ###")

        if subject_start == -1 or body_start == -1 or notes_start == -1:
             raise ValueError("LLM response did not follow the expected format.")

        rewritten_subject = content[subject_start:body_start].strip()
        rewritten_body = content[body_start + len("### Rewritten Body ###"):notes_start].strip()
        cultural_notes = content[notes_start + len("### Cultural Notes ###"):].strip()

        return RewriteOutput(
            rewritten_subject=rewritten_subject,
            rewritten_body=rewritten_body,
            cultural_notes=cultural_notes
        )

    except Exception as e:
        print(f"Error interacting with OpenAI or parsing response: {e}") # Log error server-side
        raise HTTPException(status_code=500, detail=f"Failed to rewrite email: {str(e)}")

# --- Root Endpoint (Optional - for testing) ---
@app.get("/")
def read_root():
    return {"message": "Cross-Cultural Email Assistant Backend is running!"}