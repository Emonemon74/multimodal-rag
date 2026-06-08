import os

from groq import Groq

from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def generate_answer(question, context):

    prompt = f"""
    You are an assistant for answering questions based on the provided context.
    The context is extracted from a PDF document and may contain relevant information to answer the question.
    You have the freedom to use the information in the context to generate a comprehensive and accurate answer to the question.
    
    Context:
    {context}

    Question:
    {question}
    """
    
    print("Prompt for LLM:")
    print(prompt)

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return completion.choices[0].message.content