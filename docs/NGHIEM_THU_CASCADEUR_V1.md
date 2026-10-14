# Nghiệm thu `cascadeur-animation` — vòng 1: CHƯA ĐẠT

> Người nghiệm thu: Claude, 2026-10-14. Bàn giao gốc: AG, theo `docs/GIAO_VIEC_CHUNG_CAT_CASCADEUR.md`.

## Kết quả kiểm

| Hạng mục | Kết quả |
|---|---|
| Đủ file, cấu trúc, `check_knowledge.py` | ✅ 12 file, 660 trích dẫn, phủ 92/93 video, 0 lỗi định dạng |
| **Câu có khớp nguồn không** (10 trích dẫn chọn ngẫu nhiên, đối chiếu transcript ±20 s) | ❌ **3 khớp · 2 khớp một phần · 5 không có căn cứ** |
| Trích dẫn tới video **không có transcript** (K25, K37, K70) | ❌ 8 trích dẫn — không thể kiểm chứng, là trích dẫn bịa |
| API trong `scripting-python.md` / quiz câu 15 | ❌ `scene.modify_points()` **không tồn tại**; `csc.app.get_current_scene()` sai (chỉ có `pycsc.get_current_scene`) |
| Tự chấm quiz 15/15 "Đạt" | ❌ không đáng tin (câu 15 dựa trên API bịa) |

Ví dụ lỗi đã thấy (để tránh lặp lại):
- Phím tắt không có trong nguồn: "`F` tạo keyframe" gán cho [K18 0:48] — K18 lúc đó chỉ giải thích key là gì.
- Lời khuyên tự thêm: "dùng Step khi blocking" gán cho [K18 2:13] — nguồn chỉ định nghĩa Step.
- Mốc lệch chủ đề: "mở Unbaking từ menu Commands" gán [K68 1:10] — nguồn đang nói về fulcrum.
- Tên công cụ tự đặt: "Generate Animation from Poses" [K85 1:05] — nguồn không nói tên đó.

**Vì sao cổng kiểm không bắt được:** `check_knowledge.py` chỉ chứng minh mốc giờ *tồn tại*. Từ
vòng này có thêm `scripts/audit_citations.py` để soát *nội dung*.

## Việc phải làm (vòng 2)

1. **Tải lại 4 video rỗng** (code đã sửa để không giữ kết quả "none"; whisper sẽ chạy, vài
   phút/video):
   ```bash
   $PY skillforge_cli.py fetch https://www.youtube.com/watch?v=pVMFBqaGmvE --no-frames
   $PY skillforge_cli.py fetch https://www.youtube.com/watch?v=9n1-bDiJODw --no-frames
   $PY skillforge_cli.py fetch https://www.youtube.com/watch?v=bm41FLpvY1U --no-frames
   $PY skillforge_cli.py fetch https://www.youtube.com/watch?v=lYyIJj98XuI --no-frames
   $PY scripts/group_transcripts.py . work/cascadeur_manual/transcripts
   ```
   Có lời thoại ⇒ viết ghi chú như video khác. Vẫn rỗng ⇒ **xoá mọi trích dẫn tới video đó**;
   không được nói "video không lời thoại" nếu chưa chứng minh được.
2. **Sinh bảng soát và duyệt TỪNG dòng** (430 dòng, làm theo file, mỗi lượt ~50 dòng):
   ```bash
   $PY scripts/audit_citations.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json work/cascadeur_manual/audit.md
   ```
   Điền cột "Kết luận" mỗi khối: ✅ khớp · ✏️ sửa câu cho đúng nguồn · 🔁 đổi mốc (ghi mốc mới,
   tìm trong transcript) · ❌ xoá. Rồi sửa skill theo đúng kết luận.
   Quy tắc: **phím tắt, tên menu/nút/tool, số liệu, tên phiên bản** phải xuất hiện trong lời thoại
   quanh mốc (hoặc tiêu đề/chapters của video đó). Không có ⇒ xoá, không đoán.
   Lời khuyên/nhận định không có trong nguồn ⇒ xoá, hoặc ghi rõ "(gợi ý, không từ nguồn)" không kèm trích dẫn.
3. **Sửa phần Python** trong `scripting-python.md`: chỉ giữ điều video nói (có trích dẫn). Mọi API
   cụ thể phải khớp `.claude/skills/cascadeur-mcp/references/api-index.md` hoặc
   `G:\cascadeur\resources\scripts\python\samples\api_document.py`; nếu không ⇒ xoá. Trỏ sang
   skill `cascadeur-mcp` cho phần agent tự điều khiển.
4. **Làm lại quiz** `work/cascadeur_manual/quiz.md`: mỗi câu kèm **trích nguyên câu** lời thoại
   (≤ 20 từ) chứng minh đáp án; không tự chấm "Đạt" nếu không trích được.
5. Chạy lại cả hai:
   ```bash
   $PY scripts/audit_citations.py ... work/cascadeur_manual/audit_v2.md   # phải: 0 NO TRANSCRIPT
   $PY scripts/check_knowledge.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json
   ```

Luật như cũ: không xoá file ngoài skill, không commit/push, không sửa code, kẹt 2 lần thì dừng.
Được phép **giảm** độ phủ (ít câu nhưng đúng tốt hơn nhiều câu sai) — ghi rõ video nào bị bỏ và vì sao.

## Bàn giao vòng 2

1. `work/cascadeur_manual/audit.md` đã điền kết luận (đếm: ✅ / ✏️ / 🔁 / ❌).
2. Output `audit_citations.py` (dòng tổng) và `check_knowledge.py` (đầy đủ).
3. Kết quả tải lại 4 video.
4. `quiz.md` mới.
5. `git status --short`.
