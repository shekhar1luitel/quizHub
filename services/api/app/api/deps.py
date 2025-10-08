from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db

# Placeholder for auth dependency (parse JWT in a real app)
def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db
