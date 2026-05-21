"""
Technical SEO analysis pipeline (production-oriented layers).

1. Crawler — :mod:`app.seo_pipeline.crawler_layer`
2. Parser — :mod:`app.seo_pipeline.parser_layer`
3. Normalization — :mod:`app.seo_pipeline.normalize_layer`
4. Page type — :mod:`app.seo_pipeline.page_type_layer`
5. Decision rule engine — :mod:`app.services.seo_rule_engine` (via :func:`app.seo_pipeline.pipeline.run_page_pipeline`)
6. Scoring — :mod:`app.seo_pipeline.scoring`
7. Formatter — :mod:`app.seo_pipeline.formatter`
"""

from app.seo_pipeline.crawler_layer import (
    run_technical_crawl,
    run_technical_crawl_from_job,
    schedule_technical_crawl,
)
from app.seo_pipeline.formatter import enrich_issue_for_output, format_issue_list
from app.seo_pipeline.pipeline import run_page_pipeline
from app.seo_pipeline.scoring import compute_audit_scores

__all__ = [
    "compute_audit_scores",
    "enrich_issue_for_output",
    "format_issue_list",
    "run_page_pipeline",
    "run_technical_crawl",
    "run_technical_crawl_from_job",
    "schedule_technical_crawl",
]
