from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .controllers import users, quests, awards, db_status, pipeline, leaderboard, notifications, user_state, badge_awards, whatif, activity

app = FastAPI(title="Game+ Quest League API (backend)")

# CORS — allow frontend on any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (dashboard)
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(quests.router, prefix="/quests", tags=["quests"])
app.include_router(awards.router, prefix="/awards", tags=["awards"])
app.include_router(activity.router, prefix="/activity", tags=["activity"])
app.include_router(db_status.router, prefix="/db", tags=["db"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(user_state.router, prefix="/user_state", tags=["user_state"])
app.include_router(badge_awards.router, prefix="/badge_awards", tags=["badge_awards"])
app.include_router(whatif.router, prefix="/whatif", tags=["whatif"])

@app.get("/")
def root():
    return {"message": "Game+ Quest League API. Visit /static/dashboard.html for dashboard or /docs for API docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

