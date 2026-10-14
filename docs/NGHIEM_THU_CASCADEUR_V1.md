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

---

# Vòng 2: CHƯA ĐẠT (2026-10-14)

| Hạng mục | Kết quả |
|---|---|
| Tải lại 4 video "rỗng" | ✅ cả 4 **có lời thoại** (whisper 4–12 nghìn ký tự) — nhận định "không lời thoại" ở vòng 1 là sai |
| `check_knowledge.py`, `audit_citations.py` | ✅ 93/93 video, 0 trích dẫn tới video rỗng |
| Mẫu ngẫu nhiên mới 12 trích dẫn | ❌ **0 khớp hẳn · 6 một phần · 6 sai**. Vẫn còn đúng lỗi đã chỉ ở vòng 1 (phím `F` [K18 0:48]); menu bịa "Physics → Character Contacts" [K51 1:25], "Commands → Live Link → Connect 127.0.0.1" [K7 1:30]; [K74 0:00] chỉ có tiếng nhạc; tên hàm sai `layer_viewer().layer_id_by_object_id` (thật: `layers_viewer().layer_id_by_obj_id`) |
| Bảng soát `audit.md` | ❌ 301 ✅ / 128 ✏️ / 26 🔁 / **0 ❌** — đánh dấu cho qua, không phải soát thật |
| `audit_citations.py --strict` (mới) | ❌ **92/455 dòng** có thuật ngữ `code`/**in đậm** không xuất hiện trong lời thoại quanh mốc |

## Việc vòng 3 — cổng máy, không tự chấm

Cổng bắt buộc (phải thoát mã 0):

```bash
$PY scripts/audit_citations.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json work/cascadeur_manual/audit_v3.md --strict
```

`--strict`: mọi thuật ngữ viết trong `code` hoặc **in đậm** (phím tắt, nút, menu, tool, tên hàm)
phải có **đủ các từ tiếng Anh** của nó trong lời thoại quanh mốc trích (hoặc tiêu đề video đó).

Với mỗi dòng ⛔ trong output:
1. Tìm thuật ngữ trong transcript của video đó (`work/cascadeur_manual/transcripts/*.txt`, tìm theo
   chữ). Thấy ⇒ **đổi mốc** cho đúng chỗ được nói. Không thấy ở video nào ⇒ **xoá thuật ngữ / cả câu**.
2. **Không** được lách bằng cách bỏ định dạng `code`/in đậm mà giữ nguyên nội dung bịa.
   Claude sẽ kiểm mẫu ngẫu nhiên phần chữ thường; lách = trượt nghiệm thu.
3. Câu không có thuật ngữ nhưng nói điều nguồn không nói (lời khuyên, "lỗi phổ biến nhất"…) ⇒ xoá
   hoặc ghi "(gợi ý, không từ nguồn)" không kèm trích dẫn.
4. Code/API: chỉ giữ tên hàm có trong `.claude/skills/cascadeur-mcp/references/api-index.md`
   hoặc `api_document.py`.

Bàn giao: output đầy đủ của lệnh `--strict` (phải `STRICT: 0/...`), `check_knowledge.py`, số câu đã
xoá / đổi mốc, `git status --short`. Tiêu chí PASS của Claude: cổng máy xanh **và** ≥ 9/10 mẫu ngẫu
nhiên khớp nguồn.

---

# Vòng 3: CHƯA ĐẠT (2026-10-14)

| Hạng mục | Kết quả |
|---|---|
| `--strict` | ✅ 0/452 — nhưng thuật ngữ `code`/in đậm giảm 338 → 262 trong khi chỉ bớt 3 dòng ⇒ nhiều chỗ **bỏ định dạng, giữ nội dung** (vd "Physics → Character Contacts" [K51 1:25] vẫn còn ở dạng chữ thường) |
| Sửa đúng | ✅ phím `F` nay trích đúng [K41 4:40] ("press F on your keyboard"); Bezier Clamped [K18 6:55] |
| Lỗi đã chỉ đích danh còn nguyên | ❌ `scene.layer_viewer().layer_id_by_object_id` (thật: `layers_viewer().layer_id_by_obj_id`); [K74 0:00] (chỉ có nhạc) |
| Mẫu ngẫu nhiên 10 | ❌ **3 khớp · 4 một phần · 3 sai** (K35 2:00 nói về cài add-on; K39 3:15 nói về khuỷu tay; K38 2:30 nói về blend shape/camera) |

**Gốc rễ:** câu được viết từ kiến thức chung rồi mới gắn mốc. Từ vòng 4, cổng máy bắt buộc **trích nguyên văn**.

## Việc vòng 4 — trích nguyên văn cho MỌI trích dẫn

Định dạng mới (bắt buộc cho mọi trích dẫn):

```
[K41 4:40 "press F on your keyboard"]
```

- Trong ngoặc kép: **3–25 từ chép đúng** từ lời thoại (tiếng Anh, như trong transcript) nằm quanh mốc.
- Máy kiểm câu trích có thật gần mốc (chuẩn hoá chữ hoa/dấu câu). Không tìm thấy = trượt.
- Câu tiếng Việt chỉ được nói **đúng điều câu trích nói** (có thể gộp nhiều trích dẫn). Câu nói thêm
  điều không có trong câu trích ⇒ sửa lại hoặc xoá.

Cách làm hiệu quả: **đi từ transcript ra**, không đi từ câu đã viết. Với mỗi file reference, mở
transcript các video liên quan, chọn câu lời thoại chứa thông tin, rồi viết câu tiếng Việt dựa trên nó.
Câu nào không tìm được lời thoại chứng minh ⇒ xoá (được phép giảm độ phủ, ít mà đúng).

Cổng bắt buộc (phải thoát mã 0):

```bash
$PY scripts/audit_citations.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json work/cascadeur_manual/audit_v4.md --strict --quotes
$PY scripts/check_knowledge.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json
```

Hiện tại: `GATE: 702 lỗi` (toàn bộ trích dẫn chưa có câu trích). Sửa thêm 2 lỗi đích danh ở bảng trên.
Bàn giao: output đầy đủ 2 lệnh trên, số dòng trước/sau mỗi file, `git status --short`.
