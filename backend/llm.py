import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLM:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in .env file"
            )

        self.client = genai.Client(api_key=api_key)

    def generate_answer(self, question, context):

        prompt = f"""
You are an AUTOSAR High-Level Design document analysis assistant.

Answer the user's question using ONLY the information provided
in the HLD document context below.

If the answer cannot be found in the provided context,
say:

"I could not find this information in the provided HLD document."

Do not make up information.
Do not use external knowledge.

HLD DOCUMENT CONTEXT:
---------------------
{context}
---------------------

USER QUESTION:
{question}

Provide a clear and concise answer.
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text