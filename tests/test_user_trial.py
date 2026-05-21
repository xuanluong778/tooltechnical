"""Trial activation rules."""

from datetime import timedelta

from app.db import SessionLocal, Base, engine
from app.models import knowledge as knowledge_models  # noqa: F401
from app.models import seo  # noqa: F401
from app.models.user_trial import TrialKeyClaim, UserTrial
from app.services.api_key_fingerprint import api_key_fingerprint
from app.services.user_trial_service import TRIAL_DAYS, try_activate_trial, trial_status_snapshot


def test_trial_activates_once_per_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(TrialKeyClaim).delete()
        db.query(UserTrial).delete()
        db.commit()
        key = "sk-test-user-trial-abc123456789"
        r1 = try_activate_trial(db, user_id=1, plain_api_key=key)
        assert r1["activated"] is True
        snap = trial_status_snapshot(db, 1)
        assert snap["is_active"] is True
        assert snap["days_remaining"] >= 1

        r2 = try_activate_trial(db, user_id=1, plain_api_key="sk-another-key-987654321")
        assert r2["activated"] is False
        assert r2["reason"] == "already_used_trial"
    finally:
        db.close()


def test_same_key_cannot_activate_second_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        db.query(TrialKeyClaim).delete()
        db.query(UserTrial).delete()
        db.commit()
        key = "sk-shared-key-for-trial-test-only"
        try_activate_trial(db, user_id=10, plain_api_key=key)
        r = try_activate_trial(db, user_id=11, plain_api_key=key)
        assert r["activated"] is False
        assert r["reason"] == "key_used_elsewhere"
        assert trial_status_snapshot(db, 11)["is_active"] is False
    finally:
        db.close()
