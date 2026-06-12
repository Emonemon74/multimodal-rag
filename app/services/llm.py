import json
import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from app.services.vector_store import search_pdf_chunks


load_dotenv()

MAX_TOOL_ITERATIONS = 3

SYSTEM_PROMPT = """
You are a helpful PDF assistant.

You answer questions about uploaded PDFs by using the available retrieval tool.
Use the tool when you need evidence from the PDFs, and you may call it multiple
times with refined search queries before answering.

Use prior chat history only to understand follow-up questions.
Answer only from the retrieved PDF chunks. If the answer is not present in the
retrieved chunks, say: "I could not find this information in the uploaded PDFs."
"""

chat_model = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="openai/gpt-oss-120b",
    temperature=0,
)


@tool
def retrieve_pdf_chunks(query: str, k: int = 6) -> str:
    """Search the uploaded PDFs for relevant text chunks using a natural-language query."""

    chunks = search_pdf_chunks(query=query, k=k)

    return json.dumps(chunks, ensure_ascii=True)


tool_enabled_model = chat_model.bind_tools([retrieve_pdf_chunks])


def _as_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []

        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))

        return "\n".join(part for part in text_parts if part).strip()

    return str(content)


def _build_history_messages(chat_history):

    messages = []

    for message in chat_history:
        if message.role == "user":
            messages.append(HumanMessage(content=message.content))
        else:
            messages.append(AIMessage(content=message.content))

    return messages


def generate_answer(question, chat_history=None):

    history = chat_history or []

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(_build_history_messages(history))
    messages.append(HumanMessage(content=question))

    for _ in range(MAX_TOOL_ITERATIONS):
        response = tool_enabled_model.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return _as_text(response.content)

        for tool_call in response.tool_calls:
            tool_result = retrieve_pdf_chunks.invoke(tool_call["args"])
            messages.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"],
                    name=retrieve_pdf_chunks.name,
                )
            )

    final_response = chat_model.invoke(
        messages
        + [
            HumanMessage(
                content=(
                    "Provide the final answer using the retrieved PDF chunks above. "
                    "Do not call any tools. If the answer is not present, say "
                    '"I could not find this information in the uploaded PDFs."'
                )
            )
        ]
    )

    return _as_text(final_response.content)
