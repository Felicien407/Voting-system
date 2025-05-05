from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, validator
from typing import List
import json
from pathlib import Path

app = FastAPI(title="WMHS Voting System")

DATA_DIR = Path("data")
candidates_FILE = DATA_DIR / "candidates.json"
VOTES_FILE = DATA_DIR / "votes.json"

if not VOTES_FILE.exists():
    VOTES_FILE.write_text("[]")


# Data models
class VoteRequest(BaseModel):
    email: EmailStr
    name: str
    vote_for: str

    @validator("email")
    def must_be_worldms_email(cls, v):
        if not v.endswith("@worldms.edu"):
            raise ValueError("Only @worldms.edu emails are allowed")
        return v

    @validator("vote_for")
    def must_be_valid_candidate(cls, v):
        candidates = load_candidates()
        if v not in candidates:
            raise ValueError("Invalid candidate. Must be from the list.")
        return v

# utility funcs
def load_candidates() -> List[str]:
    with open(candidates_FILE, "r") as f:
        return json.load(f)


def load_votes() -> List[dict]:
    with open(VOTES_FILE, "r") as f:
        return json.load(f)


def save_votes(votes: List[dict]):
    with open(VOTES_FILE, "w") as f:
        json.dump(votes, f, indent=2)

# Routes

@app.get("/candidates", response_model=List[str])
def get_candidates():
    return load_candidates()


@app.post("/vote")
def submit_vote(vote: VoteRequest):
    votes = load_votes()

    # Prevent duplicate vote from same email
    if any(v["email"] == vote.email for v in votes):
        raise HTTPException(status_code=400, detail="User has already voted.")

    votes.append(vote.dict())
    save_votes(votes)

    return {"message": f"Vote cast successfully for {vote.vote_for}"}


@app.get("/votes")
def get_vote_counts():
    votes = load_votes()
    candidates = load_candidates()

    results = {name: 0 for name in candidates}
    for vote in votes:
        if vote["vote_for"] in results:
            results[vote["vote_for"]] += 1

    return results
