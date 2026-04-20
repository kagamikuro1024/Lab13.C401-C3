"""
Unit tests for PII scrubbing logic in TA_Chatbot backend.
Run with: python -m pytest tests/test_pii.py -v
"""
import sys
from pathlib import Path

# Add app/backend to sys.path to allow importing the obs module
BACKEND_DIR = Path(__file__).parent.parent / "app" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from obs.pii import scrub_text, hash_user_id

def test_scrub_email():
    text = "My email is test@example.com"
    result = scrub_text(text)
    assert "[REDACTED_EMAIL]" in result
    assert "test@example.com" not in result

def test_scrub_phone():
    text = "Call me at 0912345678"
    result = scrub_text(text)
    assert "[REDACTED_PHONE/TAX_ID_VN]" in result
    assert "0912345678" not in result

def test_scrub_passport():
    text = "Passport number: B1234567"
    result = scrub_text(text)
    assert "[REDACTED_PASSPORT_VN]" in result
    assert "B1234567" not in result

def test_user_id_hashing():
    user_id = "trung_tech_lead"
    hashed = hash_user_id(user_id)
    assert len(hashed) == 12
    assert user_id not in hashed
    # Deterministic check
    assert hash_user_id(user_id) == hashed

def test_IID():
    text = "My IID is 024508096456"
    result = scrub_text(text)
    assert "[REDACTED_CCCD]" in result
    assert "024508096456" not in result