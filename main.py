from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
import json

with open("./data/audio_recordings_metadata.json", "r") as j:
    data = json.load(j)

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:mqn0JchBZX5o@ep-falling-haze-a5xbzqwj.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transcription(Base):
    __tablename__ = "transcriptions"

    audio_id = Column(String, primary_key=True)
    chunk_id = Column(String, primary_key=True)
    transcript = Column(Text)
    original_transcript = Column(Text)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptionUpdate(BaseModel):
    transcript: str
    original_transcript: str

@app.get("/api/transcriptions/{audio_id}", response_model=List[dict])
def get_transcriptions(audio_id: str):
    db = SessionLocal()
    try:
        transcriptions = db.query(Transcription).filter(Transcription.audio_id == audio_id).all()
        return [{"chunk_id": t.chunk_id, "transcript": t.transcript, "original_transcript": t.original_transcript} for t in transcriptions]
    finally:
        db.close()

@app.put("/api/transcriptions/{audio_id}/{chunk_id}")
def update_transcription(audio_id: str, chunk_id: str, transcription: TranscriptionUpdate):
    db = SessionLocal()
    try:
        db_transcription = db.query(Transcription).filter(
            Transcription.audio_id == audio_id,
            Transcription.chunk_id == chunk_id
        ).first()
        if db_transcription is None:
            raise HTTPException(status_code=404, detail="Transcription not found")
        db_transcription.transcript = transcription.transcript
        if not db_transcription.original_transcript:
            db_transcription.original_transcript = transcription.original_transcript
        db.commit()
        return {"message": "Transcription updated successfully"}
    finally:
        db.close()

def setup_database():
    db = SessionLocal()
    try:
        existing = db.query(Transcription).first()
        if existing is None:
            sample_data = [
                Transcription(audio_id=d['audio_id'], chunk_id=d['chunk_id'], transcript=d['transcript'], original_transcript=d['transcript']) for d in data
            ]
            db.add_all(sample_data)
            db.commit()
            print("Sample data inserted successfully")
        else:
            print("Database already contains data")
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)