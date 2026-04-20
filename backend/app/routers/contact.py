import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Senator import Senator
from app.schemas.contact import ContactRequest, ContactResponse
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

router = APIRouter(prefix="/api/contact", tags=["contact"])

# Basic In-Memory Rate Limiter (IP -> list of message timestamps)
# Note: For production with multiple workers, a Redis store is better, 
# but this perfectly handles our core deliverable!
ip_logs: Dict[str, List[datetime]] = {}

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = datetime.now()
    cutoff_time = now - timedelta(hours=1)
    
    # Clean up old timestamps for this IP
    if client_ip in ip_logs:
        ip_logs[client_ip] = [t for t in ip_logs[client_ip] if t > cutoff_time]
    else:
        ip_logs[client_ip] = []
        
    # Block if they have 5 or more messages in the last hour
    if len(ip_logs[client_ip]) >= 5:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
        
    ip_logs[client_ip].append(now)

def send_email(to_email: str, reply_to: str, subject: str, body: str):
    # Graceful degradation if SMTP isn't configured for local dev
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASSWORD:
        print("----------------------------------------")
        print(f"MOCK EMAIL WOULD SEND TO: {to_email}")
        print(f"REPLY-TO: {reply_to}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{body}")
        print("----------------------------------------")
        return
        
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.add_header('reply-to', reply_to)

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        # Log error but don't crash user submission
        print(f"Failed to send email: {e}")

@router.post("", response_model=ContactResponse)
def submit_contact_form(
    payload: ContactRequest, 
    request: Request,
    db: Session = Depends(get_db)
):
    # 1. Enforce Rate Limit
    check_rate_limit(request)
    
    # 2. Determine target email
    target_email = "speaker@unc.edu"
    if payload.senator_id:
        senator = db.query(Senator).filter(Senator.id == payload.senator_id).first()
        if not senator:
            raise HTTPException(status_code=404, detail="Senator not found")
        target_email = senator.email

    # 3. Dispatch Email
    subject_line = f"New Message via Senate Portal from {payload.name}"
    body_text = f"Name: {payload.name}\nEmail: {payload.email}\n\nMessage:\n{payload.message}"
    
    send_email(
        to_email=target_email,
        reply_to=payload.email,
        subject=subject_line,
        body=body_text
    )

    return ContactResponse(success=True)

