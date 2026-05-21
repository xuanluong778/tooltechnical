# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
text = p.read_text(encoding="utf-8")

old = """                        </motion>

                        <motion class="apik-modal-err" id="aikbModalErr"></motion>""".replace("motion", "div")

new = """                        </motion>

                        <motion class="aikb-grid2">
                            <motion>
                                <label for="aikbTone">Giọng văn</label>
                                <select id="aikbTone" name="tone"></select>
                            </motion>
                            <motion>
                                <label for="aikbLang">Ngôn ngữ</label>
                                <select id="aikbLang" name="language">
                                    <option value="vi">Tiếng Việt</option>
                                    <option value="en">English</option>
                                </select>
                            </motion>
                        </motion>

                        <label for="aikbProducts">Sản phẩm / dịch vụ <span class="req">*</span></label>
                        <textarea id="aikbProducts" name="products_services" placeholder="Mô tả ngắn sản phẩm, dịch vụ chính…" required></textarea>

                        <label for="aikbAudience">Đối tượng khách hàng <span class="req">*</span></label>
                        <textarea id="aikbAudience" name="target_audience" placeholder="Ai là khách hàng mục tiêu?" required></textarea>

                        <label for="aikbFacts">USP / điểm nổi bật / chính sách <span class="req">*</span></label>
                        <textarea id="aikbFacts" name="key_facts" placeholder="Cam kết, chứng chỉ, ưu đãi, điểm khác biệt…" required></textarea>

                        <label for="aikbAvoid">Tránh đề cập</label>
                        <textarea id="aikbAvoid" name="avoid_topics" placeholder="Chủ đề, từ ngữ, claim không được dùng…"></textarea>

                        <label for="aikbCustom">Hướng dẫn bổ sung cho AI</label>
                        <textarea id="aikbCustom" name="custom_instructions" placeholder="Quy tắc viết, CTA, format, tone chi tiết…"></textarea>

                        <motion class="apik-enable-row">
                            <motion>
                                <motion class="label">Bật</motion>
                                <motion class="hint">Tắt = không dùng trong pipeline</motion>
                            </motion>
                            <label class="apik-toggle">
                                <input type="checkbox" id="aikbEnabled" checked>
                                <span class="track"></span>
                            </label>
                        </motion>
                        <motion class="apik-enable-row">
                            <motion>
                                <motion class="label">Mặc định</motion>
                                <motion class="hint">Ưu tiên khi Content AI cần ngữ cảnh thương hiệu</motion>
                            </motion>
                            <label class="apik-toggle">
                                <input type="checkbox" id="aikbDefault">
                                <span class="track"></span>
                            </label>
                        </motion>

                        <motion class="apik-modal-err" id="aikbModalErr"></motion>""".replace("motion", "motion").replace("<motion", "<div").replace("</motion>", "</div>")

form_start = text.find('id="aikbForm"')
form_end = text.find('id="aikbImportModal"')
segment = text[form_start:form_end]
if "aikbTone" in segment:
    print("form already restored")
else:
    if old not in segment:
        raise SystemExit("old block not found in form")
    segment = segment.replace(old, new, 1)
    segment = segment.replace('placeholder="VD: Book, FAQ sản phẩm…"', 'placeholder="VD: Thương hiệu chính"')
    text = text[:form_start] + segment + text[form_end:]
    p.write_text(text, encoding="utf-8")
    print("ok")
