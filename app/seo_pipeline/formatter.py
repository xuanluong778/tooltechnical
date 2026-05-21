"""
Output formatter layer: checklist groups, remediation, suggested_fix for API / UI.
"""

from __future__ import annotations

from typing import Any

from app.seo_pipeline.constants import TECH_CHECKLIST_BY_TYPE
from app.services.technical_knowledge import enrich_issue_from_technical_knowledge

# Gợi ý sửa mặc định (tiếng Việt) khi upstream chưa gắn remediation — dùng cho /tool, /report, export.
_DEFAULT_REMEDIATION: dict[str, str] = {
    "missing_title": "Thêm thẻ <title> duy nhất trong <head> (khoảng 50–60 ký tự thường phù hợp hiển thị SERP).",
    "missing_meta_description": "Thêm <meta name=\"description\" content=\"…\"> hoặc og:description mô tả đúng intent trang.",
    "missing_h1": "Dùng một H1 mô tả chủ đề chính; tránh H1 rỗng hoặc thay bằng div khi cần heading thật.",
    "multiple_h1": "Giảm còn một H1 chính hoặc hạ các H1 phụ xuống H2 nếu chỉ là tiêu đề section.",
    "missing_canonical": "Thêm <link rel=\"canonical\" href=\"…\"> trỏ về URL ưu tiên (thường self sau chuẩn hóa).",
    "title_too_long": "Rút ngắn title để SERP hiển thị rõ; đặt từ khóa chính phía trước.",
    "thin_content": "Bổ sung nội dung có giá trị hoặc gộp URL mỏng; ưu tiên nội dung chính trong HTML tĩnh khi có thể.",
    "images_missing_alt": "Thêm alt mô tả cho ảnh mang ngữ nghĩa; dùng alt=\"\" cho ảnh trang trí.",
    "soft_404_heuristic": "Nếu trang không tồn tại, trả 404/410 thật; nếu cần index, bổ sung nội dung hữu ích và bỏ thông điệp 'not found'.",
    "http_status_error": "Sửa cấu hình máy chủ để URL trả 200 cho user và bot, hoặc noindex/redirect nếu cố ý không index.",
    "robots_noindex": "Gỡ noindex nếu trang cần index; giữ noindex cho staging, tham số trùng lặp hoặc URL không muốn index.",
    "broken_internal_link": "Cập nhật hoặc gỡ liên kết trỏ tới 404; thêm redirect 301 nếu URL đích đã chuyển.",
    "broken_internal_http_error": "Xử lý lỗi máy chủ (5xx) hoặc chặn quyền (403) trên URL được liên kết nội bộ.",
    "redirect_chain": "Trỏ link nội bộ thẳng tới URL cuối; rút ngắn chuỗi redirect còn một bước khi có thể.",
    "crawl_page_non_200": "Đảm bảo URL crawl trả 200 kèm HTML; sửa redirect hoặc rule chặn bot.",
    "https_not_used": "Ép HTTPS bằng 301 + HSTS; cập nhật link nội bộ sang https.",
    "missing_favicon": "Thêm <link rel=\"icon\" href=\"/favicon.ico\"> (hoặc PNG/SVG) trong <head>.",
    "missing_html_lang": "Đặt <html lang=\"…\"> đúng ngôn ngữ chính của trang.",
    "duplicate_title": "Khác biệt hóa title theo từng URL để mỗi trang có title duy nhất, mô tả rõ.",
    "pagination_missing_rel_next": "Với phân trang, triển khai rel=next/prev hoặc canonical về trang xem tất cả theo chiến lược của bạn.",
    "link_check_truncated": "Giảm max_pages khi quét hoặc tách audit theo section; tăng giới hạn kiểm tra link nếu cấu hình cho phép.",
    "robots_unreachable": "Phục vụ robots.txt HTTP 200 tại gốc host; kiểm tra DNS/hosting nếu thiếu nhầm.",
    "robots_missing_sitemap_line": "Khai báo sitemap chính bằng dòng Sitemap: trong robots.txt.",
    "robots_sitemap_wrong_host": "Đảm bảo URL Sitemap trong robots.txt cùng domain đăng ký với site.",
    "robots_sitemap_invalid_url": "Sửa URL Sitemap trong robots.txt (https tuyệt đối, đúng định dạng, mỗi dòng một URL).",
    "robots_sitemap_unreachable": "Sửa URL sitemap để trả 200 và XML hợp lệ cho bot.",
    "robots_disallow_broad_querystring": "Rà Coverage trong GSC; thu hẹp Disallow không chặn URL tham số có giá trị.",
    "robots_disallow_all": "Gỡ Disallow: / nhầm cho production (trừ khi site phải ẩn hoàn toàn).",
    "robots_wordpress_standard_blocks": "Thông tin: pattern WordPress chặn plugin/theme — kiểm tra không chặn asset render quan trọng.",
    "sitemap_unreachable": "Xuất bản sitemap XML ổn định, URL trả HTTP 200.",
    "sitemap_empty": "Bổ sung các mục <loc> trong sitemap hoặc sửa generator để bot nhận danh sách URL.",
    # Decision engine / rules bổ sung
    "indexability_blocked": "Sửa meta robots / X-Robots-Tag / HTTP để URL có thể index theo intent (staging vs production).",
    "indexability_signal_conflict": "Chuẩn hóa một nguồn sự thật: meta vs header vs raw/rendered; đồng bộ CDN/CMS.",
    "canonical_cross_host": "Nếu đây là bản chính, canonical về cùng host hoặc property GSC đúng; kiểm tra syndication.",
    "canonical_self_mismatch": "Chuẩn hóa canonical về URL ưu tiên sau redirect (thường self khớp URL hiệu dụng).",
    "canonical_missing_high_value": "Thêm canonical tuyệt đối cho trang quan trọng (article/homepage/landing).",
    "canonical_points_to_non_indexable": "Sửa canonical trỏ tới URL indexable thật; kiểm tra robots và HTTP đích.",
    "canonical_low_similarity_mismatch": "Canonical chỉ tới URL duplicate thật hoặc gần duplicate; so khớp nội dung chính.",
    "google_may_ignore_canonical": "Chuẩn hóa chuỗi canonical một chiều; đồng bộ nội dung duplicate hoặc bỏ canonical sai.",
    "page_unlikely_indexed": "Xác định URL primary; dùng self-canonical đúng hoặc 301 gộp duplicate.",
    "cloaking_risk_advanced": "SSR/hybrid cho phần quan trọng; đồng nhất raw vs rendered cho Googlebot và user.",
    "js_seo_risk_high": "SSR hoặc pre-render cho title/H1/canonical; giảm shell HTML trống.",
    "js_seo_risk_medium": "Đưa title, meta, H1 chính vào HTML server hoặc pre-render.",
    "js_shell_missing_critical": "Bổ sung title/meta/H1 trong HTML tĩnh ban đầu, không chỉ sau JS.",
    "cloaking_heuristic": "Đảm bảo Googlebot nhận cùng logic nội dung với user; rà A/B và inject sau render.",
    "robots_meta_noindex_contradiction": "Đồng bộ meta robots với X-Robots-Tag và HTTP; kiểm tra canonical chain.",
    "http_status_non_200": "Sửa HTTP hoặc logic indexability để không mâu thuẫn status vs index.",
    "weak_heading_structure": "Chia section bằng H2/H3 hợp lý cho nội dung dài.",
}

# Ví dụ thực tế gắn thêm (khi remediation chưa chứa chữ «Ví dụ» — tránh lặp).
_TYPE_EXAMPLE_SUFFIX: dict[str, str] = {
    "https_not_used": "",  # analyzer đã gắn remediation chi tiết
    "missing_title": "\n\nVí dụ: <title>Máy phát điện 10kVA công nghiệp — Bảo hành 24 tháng | Hyundai</title> (một thẻ duy nhất, từ khóa chính gần đầu).",
    "missing_meta_description": "\n\nVí dụ: <meta name=\"description\" content=\"Phân phối máy phát điện 10–500kVA, lắp đặt tận nơi, hotline 09xx — xem bảng giá và catalog PDF.\">",
    "missing_h1": "\n\nVí dụ: <h1>Máy phát điện công nghiệp Hyundai</h1> ngay dưới header, một H1 cho trang danh mục.",
    "missing_canonical": "\n\nVí dụ: <link rel=\"canonical\" href=\"https://www.shop.com/may-phat-dien/\" /> (URL tuyệt đối, khớp bản https sau redirect).",
    "broken_internal_link": "\n\nVí dụ: link nội bộ đang trỏ /san-pham-cu — sửa href thành URL 200 hiện tại hoặc thêm redirect 301 /san-pham-cu → /may-phat-dien/.",
    "broken_internal_http_error": "\n\nVí dụ: URL đích trả 502 — xem log PHP-FPM/nginx; tạm thời gỡ rule WAF chặn IP; kiểm tra plugin bảo mật Wordfence «Learning mode».",
    "redirect_chain": "\n\nVí dụ: /a →302→ /b →301→ /c — sửa link nội bộ trỏ thẳng /c; giữ tối đa một bước redirect công khai.",
    "robots_disallow_all": "\n\nVí dụ: xóa dòng «Disallow: /» trong robots.txt production (giữ chỉ cho staging có Basic Auth).",
    "sitemap_unreachable": "\n\nVí dụ: sitemap khai báo https://shop.com/sitemap.xml nhưng trả 404 — tạo file hoặc chỉnh Yoast/RankMath sinh đúng đường dẫn.",
    "missing_html_lang": "\n\nVí dụ: <html lang=\"vi\"> cho site tiếng Việt; nếu song ngữ theo path dùng lang trên thẻ gốc từng template.",
    "images_missing_alt": "\n\nVí dụ: <img src=\"/upload/may-phat.jpg\" alt=\"Máy phát điện Hyundai DHY-12KSEm 12kVA ba pha\" width=\"800\" height=\"600\" />",
}


def attach_checklist_group(issue: dict[str, Any]) -> dict[str, Any]:
    out = dict(issue)
    if not out.get("checklist_group"):
        out["checklist_group"] = TECH_CHECKLIST_BY_TYPE.get(str(out.get("type") or ""), "General")
    return out


def enrich_issue_for_output(issue: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure each issue has checklist_group, remediation (if missing), and suggested_fix.
    """
    out = attach_checklist_group(issue)
    t = str(out.get("type") or "")
    if not (out.get("remediation") or "").strip():
        fix = _DEFAULT_REMEDIATION.get(t)
        if fix:
            out["remediation"] = fix
    rem = (out.get("remediation") or "").strip()
    ex_suf = _TYPE_EXAMPLE_SUFFIX.get(t, "")
    if ex_suf and "Ví dụ" not in rem:
        rem = (rem + ex_suf).strip()
        out["remediation"] = rem
    u = str(out.get("url") or "").strip()
    if u and t in ("broken_internal_link", "broken_internal_http_error", "crawl_page_non_200"):
        if u not in rem:
            rem = (rem + f"\n\nURL liên quan trong báo cáo: {u}").strip()
            out["remediation"] = rem
    rem = (out.get("remediation") or "").strip()
    out["suggested_fix"] = rem or (out.get("explanation") or "").strip()
    return enrich_issue_from_technical_knowledge(out)


def format_issue_list(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply formatter to a full audit issue list (immutable input)."""
    return [enrich_issue_for_output(dict(i)) for i in issues]
