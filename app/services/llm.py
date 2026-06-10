import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_answer(question, context, chat_history=""):

    prompt = f"""
You are a helpful PDF assistant.

Use ONLY the provided PDF context to answer.
Use chat history only to understand follow-up questions.

If the answer is not present in the PDF context, say:
"I could not find this information in the uploaded PDF."

PDF Context:
{context}

Chat History:
{chat_history}

Current Question:
{question}

Answer:
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return completion.choices[0].message.content
