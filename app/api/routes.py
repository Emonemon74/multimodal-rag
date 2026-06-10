import os

from fastapi import APIRouter, UploadFile, File

from app.models.request_models import QuestionRequest
from app.services.pdf_parser import parse_pdf
from app.services.vector_store import create_vector_store, load_vector_store
from app.services.llm import generate_answer

router = APIRouter()

uploaded_files = []
uploaded_file_details = []
chat_history = []


@router.post("/parse-pdf")
async def parse_pdf_api(file: UploadFile = File(...)):

    os.makedirs("temp", exist_ok=True)

    file_location = f"temp/{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    parsed_data = parse_pdf(file_location)

    create_vector_store(parsed_data["documents"])

    if file.filename not in uploaded_files:
        uploaded_files.append(file.filename)

        uploaded_file_details.append(
            {
                "filename": file.filename,
                "documents": len(parsed_data["documents"]),
                "pages": parsed_data["pages"],
            }
        )

    return {
        "message": "PDF uploaded successfully",
        "filename": file.filename,
        "documents": len(parsed_data["documents"]),
    }


@router.post("/ask")
def ask_question(request: QuestionRequest):

    vector_store = load_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr", search_kwargs={"k": 6, "fetch_k": 20}
    )

    docs = retriever.invoke(request.question)

    context = "\n".join([doc.page_content for doc in docs])

    history_text = "\n".join(chat_history[-6:])

    answer = generate_answer(
        question=request.question, context=context, chat_history=history_text
    )

    chat_history.append(f"User: {request.question}")

    chat_history.append(f"Assistant: {answer}")

    sources = [
        {
            "source": doc.metadata.get("source", "Unknown"),
            "page": doc.metadata.get("page", "Unknown"),
            "content": doc.page_content[:300],
        }
        for doc in docs
    ]

    return {"answer": answer, "sources": sources}


@router.get("/uploaded-files")
def get_uploaded_files():

    return {"files": uploaded_file_details}


@router.delete("/chat-history")
def clear_chat_history():

    chat_history.clear()

    return {"message": "Chat history cleared successfully"}
