from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / "env.local")

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from sqlalchemy import inspect, text

from app.db import Base, engine, get_db
from app.models import seo  # noqa: F401
from app.models.crawl_job import DistributedCrawlJob, DistributedCrawlResult  # noqa: F401
from app.models.keyword_intel import (  # noqa: F401
    SEOKeywordClusterEntity,
    SEOKeywordEntity,
    SEOKeywordUrlMapping,
)
from app.models.keyword_research_project import KeywordResearchProject  # noqa: F401
from app.models.keyword_cluster_job import KeywordClusterJob  # noqa: F401
from app.models.keyword_cluster_project import KeywordClusterProject  # noqa: F401
from app.models.keyword_volume_cache import KeywordVolumeCache  # noqa: F401
from app.models.otp_login import OtpLogin  # noqa: F401
from app.models.credit_ledger import CreditLedger  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.security_audit_log import SecurityAuditLog  # noqa: F401
from app.models.user_api_key import UserApiKey  # noqa: F401
from app.models.user_trial import TrialKeyClaim, UserTrial  # noqa: F401
from app.models.plan import Plan  # noqa: F401 — SaaS Phase 1
from app.models.subscription import Subscription  # noqa: F401
from app.models.usage_limit import UsageLimit  # noqa: F401
from app.models.usage_event import UsageEvent  # noqa: F401
from app.models.monthly_usage import MonthlyUsage  # noqa: F401
from app.models.payment_transaction import PaymentTransaction  # noqa: F401
from app.models import knowledge as knowledge_models  # noqa: F401
from app.routers.analyze import router as analyze_router
from app.routers.internal_links import router as internal_links_router
from app.routers.pages import pricing_page as saas_pricing_page
from app.routers.pages import router as pages_router
from app.routers.report import router as report_router
from app.routers.settings_api import router as settings_api_router
from app.routers.integrations_google import router as integrations_router
from app.routers.serp_intel import router as serp_intel_router
from app.routers.keyword_intelligence import router as keyword_intel_router
from app.routers.keywords import router as keywords_router
from app.routers.wp_bulk_update import router as wp_bulk_router
from app.routers.user_files import router as user_files_router
from app.routers.admin import api_router as admin_api_router
from app.routers.admin import router as admin_router
from app.routers.saas_admin import router as saas_admin_router
from app.routers.saas import router as saas_router
from app.routers.chatbot import router as chatbot_router
from app.services.internal_linking import models as il_models  # noqa: F401


@asynccontextmanager
async def _app_lifespan(_app: FastAPI):
    from app.services.content_ai_bulk_worker_loop import start_content_ai_bulk_worker_background

    start_content_ai_bulk_worker_background()
    yield


app = FastAPI(title="URL Analyzer API", version="1.0.0", lifespan=_app_lifespan)


@app.middleware("http")
async def bind_request_user_context(request: Request, call_next):
    """Attach logged-in user id so LLM/API-key resolution is per-user."""
    from app.core.user_context import bind_request_user_id, unbind_request_user_id
    from app.db import SessionLocal
    from app.services.auth import user_from_token

    uid: int | None = None
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            db = SessionLocal()
            try:
                uid = user_from_token(db, token).id
            except Exception:
                uid = None
            finally:
                db.close()

    ctx_token = bind_request_user_id(uid)
    try:
        return await call_next(request)
    finally:
        unbind_request_user_id(ctx_token)


app.include_router(settings_api_router)
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
app.include_router(analyze_router)
app.include_router(pages_router)
app.include_router(report_router)
app.include_router(integrations_router)
app.include_router(serp_intel_router)
app.include_router(keyword_intel_router)
app.include_router(keywords_router)
app.include_router(wp_bulk_router)
app.include_router(user_files_router)
app.include_router(internal_links_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(admin_router)
app.include_router(admin_api_router, prefix="/admin/api")
app.include_router(admin_api_router, prefix="/api/admin")  # legacy alias
app.include_router(saas_admin_router, prefix="/admin/api")
app.include_router(saas_admin_router, prefix="/api/admin")
app.include_router(saas_router, prefix="/api")
app.include_router(chatbot_router, prefix="/chatbot")
app.include_router(chatbot_router, prefix="/api/chatbot")
Base.metadata.create_all(bind=engine)

_templates = Jinja2Templates(directory="templates")


def _ensure_users_has_password_column() -> None:
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "has_password" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN has_password BOOLEAN NOT NULL DEFAULT 1"))


_ensure_users_has_password_column()


def _ensure_user_credit_balance_column() -> None:
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "credit_balance" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN credit_balance INTEGER NOT NULL DEFAULT 0"))


_ensure_user_credit_balance_column()


def _ensure_knowledge_base_tables() -> None:
    """Additive KB tables only; legacy data/ai_knowledge_bases.json is not modified."""
    from app.knowledge_tables import ensure_knowledge_tables

    ensure_knowledge_tables()


_ensure_knowledge_base_tables()


def _ensure_keyword_history_user_id() -> None:
    insp = inspect(engine)
    for table in ("keyword_research_projects", "keyword_cluster_projects"):
        if table not in insp.get_table_names():
            continue
        cols = {c["name"] for c in insp.get_columns(table)}
        if "user_id" not in cols:
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER"))


_ensure_keyword_history_user_id()


def _ensure_user_role_column() -> None:
    import os

    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "role" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT 'user'"))
    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    if admin_email:
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE users SET role = 'admin' WHERE lower(email) = :email"),
                {"email": admin_email},
            )


_ensure_user_role_column()


def _ensure_user_status_column() -> None:
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    if "status" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'active'"))


_ensure_user_status_column()


def _ensure_user_api_access_columns() -> None:
    insp = inspect(engine)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    with engine.begin() as conn:
        if "api_access_enabled" not in cols:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN api_access_enabled BOOLEAN NOT NULL DEFAULT 1")
            )
            conn.execute(text("UPDATE users SET api_access_enabled = 1"))
        if "use_admin_api_pool" not in cols:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN use_admin_api_pool BOOLEAN NOT NULL DEFAULT 0")
            )


_ensure_user_api_access_columns()


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return _templates.TemplateResponse(request=request, name="home.html", context={})


@app.get("/pricing", response_class=HTMLResponse, tags=["pages"])
def pricing_page_route(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Bảng giá SaaS (đăng ký tại app để luôn có route sau khi deploy/restart)."""
    return saas_pricing_page(request, db)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
