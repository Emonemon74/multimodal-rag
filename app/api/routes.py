import os

from fastapi import APIRouter, UploadFile, File

from app.models.request_models import QuestionRequest
from app.services.pdf_parser import parse_pdf
from app.services.vector_store import create_vector_store
from app.services.llm import generate_answer

router = APIRouter()

uploaded_files = []
uploaded_file_details = []


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

    answer = generate_answer(
        question=request.question,
        chat_history=request.chat_history,
    )

    return {"answer": answer}


@router.get("/uploaded-files")
def get_uploaded_files():

    return {"files": uploaded_file_details}


@router.delete("/chat-history")
def clear_chat_history():

    return {"message": "Chat history cleared successfully"}
