import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field

from meal_mentor.rag import rag
from meal_mentor import db

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request and response bodies
class QuestionRequest(BaseModel):
    question: str = Field(..., example="What is a nice healthy Italian recipe?")


class QuestionResponse(BaseModel):
    conversation_id: str
    question: str
    answer: str


class FeedbackRequest(BaseModel):
    conversation_id: str = Field(
        ..., example="123e4567-e89b-12d3-a456-426614174000"
    )
    feedback: int = Field(
        ..., example=1, description="1 for positive feedback, -1 for negative feedback"
    )


class FeedbackResponse(BaseModel):
    message: str

# Create API router with a prefix to avoid conflicts
api_router = APIRouter(prefix="/api")

# Define API endpoints
@api_router.post("/question", response_model=QuestionResponse)
def handle_question(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="No question provided")

    conversation_id = str(uuid.uuid4())

    try:
        answer_data = rag(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    result = QuestionResponse(
        conversation_id=conversation_id,
        question=question,
        answer=answer_data.get("answer", "No answer available"),
    )

    try:
        db.save_conversation(
            conversation_id=conversation_id,
            question=question,
            answer_data=answer_data,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save conversation: {str(e)}"
        )

    return result


@api_router.post("/feedback", response_model=FeedbackResponse)
def handle_feedback(request: FeedbackRequest):
    conversation_id = request.conversation_id.strip()
    feedback = request.feedback

    if not conversation_id or feedback not in {1, -1}:
        raise HTTPException(status_code=400, detail="Invalid input")

    try:
        db.save_feedback(
            conversation_id=conversation_id,
            feedback=feedback,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save feedback: {str(e)}"
        )

    message = f"Feedback received for conversation {conversation_id}: {feedback}"
    return FeedbackResponse(message=message)

# Include the API router in the main app
app.include_router(api_router)

# Mount the static directory at "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at "/"
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

