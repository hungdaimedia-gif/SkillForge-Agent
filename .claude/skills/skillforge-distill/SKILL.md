---
name: skillforge-distill
description: Use when someone wants to turn YouTube videos, playlists or channels, or books (PDF, EPUB, Markdown), into offline agent skills (SKILL.md) with SkillForge-Agent — "chưng cất skill từ video/playlist", "học hết list này thành skill", "biến cuốn sách thành skill", "để agent làm được mà không cần lên mạng học". Covers environment check, surveying the source, fetch, distill, reading the gate/quiz report, fixing draft skills, exporting to a skills folder, and troubleshooting yt-dlp/LLM errors.
---

# Chưng cất skill từ video YouTube / sách bằng SkillForge-Agent

Biến tài liệu hướng dẫn (video, playlist, sách) thành **skill dạng kiến thức** — `SKILL.md`
+ `references/` + ảnh giao diện + `SOURCES.md` có trích dẫn — để agent sau này **đọc offline
và làm được việc**, không phải lên mạng học lại.

Đầu ra của mỗi lần chạy: vài skill theo *năng lực* (không phải một skill mỗi video) và một
**skill trung tâm** (tổng quan, bảng phím tắt, thuật ngữ, bảng chỉ đường sang skill con).

## Khi nào dùng / không dùng

| Tình huống | Làm gì |
|---|---|
| Video/playlist/kênh YouTube, sách PDF/EPUB/Markdown dạy cách làm | Dùng skill này |
| Một hướng dẫn **code** muốn ra script chạy được | `skillforge ingest file.md` (đường executable cũ) |
| Trang web, khoá học sau đăng nhập, video không phải YouTube | Chưa hỗ trợ — lưu thành `.md` rồi chưng cất như sách |
| PDF scan (không có lớp chữ) | OCR trước, công cụ sẽ báo lỗi "no text layer" |

## Quy trình (làm đúng thứ tự, dừng ở mỗi ⛔ để báo người dùng)

**Tìm repo trước.** Mọi lệnh chạy từ thư mục gốc của SkillForge-Agent (thư mục có
`skillforge_cli.py`): biến `SKILLFORGE_HOME` nếu có, nếu không thì hỏi người dùng. Chưa có ⇒
đề xuất (chờ đồng ý) clone `https://github.com/hungdaimedia-gif/SkillForge-Agent` rồi
`uv venv .venv && uv pip install -e ".[llm,youtube,books,dev]"`.
Python của venv: `PY=.venv/Scripts/python.exe` (Windows) hoặc `.venv/bin/python`; CLI là
`$PY skillforge_cli.py`. Đường dẫn `scripts/…` bên dưới tính từ thư mục của skill này.

### Bước 0 — Kiểm tra môi trường
```bash
$PY <thư-mục-skill>/scripts/check_env.py --repo <SkillForge-Agent> --ping
```
Thiếu gì thì sửa theo dòng ❌ in ra. Hai lỗi hay gặp nhất: **không có quyền gọi mô hình**
(chưa đặt `ANTHROPIC_API_KEY` và `claude` CLI chưa đăng nhập) và **yt-dlp cũ** trên PATH.
Chi tiết: [references/troubleshooting.md](references/troubleshooting.md).

### Bước 1 — Khảo sát nguồn trước khi tốn tiền
- Video: liệt kê playlist (số video, tổng thời lượng, có phụ đề không, có chapter không):
  `$PY -m yt_dlp --flat-playlist --print "%(playlist_index)s|%(duration_string)s|%(title)s" "<URL>"`
- Đọc mô tả video: nếu có dòng kiểu "guide đã cập nhật" ⇒ phần mềm có thể **đã đổi phiên bản**;
  ghi chú để nói với người dùng.
- Sách: kiểm tra có lớp chữ, có mục lục; ghi nhận bản quyền (skill chỉ được **diễn giải**).
- ⛔ Báo người dùng: số nguồn, thời lượng/số trang, rủi ro phiên bản, ước lượng số lần gọi
  mô hình (≈ số video/chương + 1 + 3 × số skill).

### Bước 2 — Tải về cache (không gọi mô hình, chạy lại miễn phí)
```bash
$PY skillforge_cli.py fetch "<URL playlist | file.pdf>"          # --limit 3 để thử ít video
```
Đọc bảng in ra:
- `chars` rất thấp (< 300) ⇒ video gần như **không lời thoại**, kiến thức nằm trên màn hình;
  công cụ đã tự cắt khung dày hơn — kiểm tra `frames` > 0.
- `frames=0` ⇒ tải video lỗi (thường là 403) ⇒ chạy lại `fetch` (có thử nhiều client).
- Mở 1–2 ảnh trong `sources_cache/youtube/<id>/frames_720p/` xem chữ giao diện đọc được không.

### Bước 3 — Chưng cất
```bash
$PY skillforge_cli.py distill "<URL hoặc file>" --domain <ten-mien> --lang vi
```
- `--domain`: tiền tố tên skill, chữ thường không dấu (vd `cascadeur`, `blender`, `nguyen-ly-hoat-hinh`).
- Nhiều nguồn cùng chủ đề ⇒ đưa **chung một lệnh** để được gộp thành một bộ skill.
- `--limit N` để chạy thử N video đầu trước khi chạy cả list.
- Bị ngắt giữa chừng ⇒ chạy lại đúng lệnh cũ: mọi bước đã xong được lấy từ `work/<domain>/`.

### Bước 4 — Đọc báo cáo, xử lý skill `draft`
Mở `work/<domain>/report.md`. Mỗi skill là `validated` (qua cổng kiểm + quiz ≥ 70%) hoặc `draft`.

| Thấy trong báo cáo | Nguyên nhân | Cách xử lý |
|---|---|---|
| `invalid anchor [S3 9:59]` | Mô hình bịa mốc trích dẫn | `--redo <tên-skill>` |
| `image assets/... is not an available asset`, `link to missing references/...` | Link hỏng | `--redo <tên-skill>` |
| `offline quiz score 50% < 70%` | Skill thiếu thông tin so với nguồn | Mở `eval.json` trong thư mục skill xem câu sai; `--redo <tên-skill>`; nếu nguồn thật sự thiếu ⇒ chấp nhận draft và ghi chú |
| Skill quá ít/quá nhiều, gộp sai chủ đề | Kế hoạch chưa hợp lý | `--redo plan` (lập lại danh sách skill) |

**Không bao giờ** tự sửa tay mốc trích dẫn cho qua cổng, không hạ `--min-eval` để ép validated
mà không báo người dùng.

### Bước 5 — Duyệt bằng mắt (bắt buộc trước khi giao)
Làm theo [references/review-checklist.md](references/review-checklist.md): đọc skill trung tâm +
ít nhất một skill con, bấm thử 3 link trong `SOURCES.md` để đối chiếu đúng giây/trang.

### Bước 6 — Cài vào thư viện skill của agent
```bash
$PY skillforge_cli.py export <domain> --to <thư-mục-skills>     # vd ~/.claude/skills
```
Chỉ xuất skill `validated` (thêm `--include-drafts` nếu người dùng đồng ý). Thư mục đích đã có
skill cùng tên ⇒ **bỏ qua, không ghi đè**; báo người dùng tự quyết.

### Bước 7 — Bàn giao
Báo: danh sách skill + trạng thái + điểm quiz, skill draft và lý do, rủi ro phiên bản phần mềm,
nơi đã export, và các file cache người dùng có thể tự xoá (kèm đường dẫn đầy đủ).

## Luật bắt buộc

1. **Không xoá gì.** Cache (`sources_cache/`), kết quả trung gian (`work/`), skill cũ trong thư
   mục đích: chỉ *liệt kê kèm đường dẫn* để người dùng tự xoá. Muốn làm lại một phần ⇒ `--redo`,
   không xoá file cache.
2. **Bản quyền.** Video tải về và transcript thô chỉ nằm trong `sources_cache/` (đã git-ignore),
   không đưa lên repo. Skill chỉ chứa nội dung diễn giải; sách ⇒ `license: book_paraphrase_only`.
3. **Không bịa.** Mọi ý trong skill phải có trích dẫn `[S<n> <mốc>]` kiểm chứng được; nguồn không
   nói thì skill ghi "nguồn không đề cập".
4. **Tiết kiệm.** Không dùng `--force` (chạy lại toàn bộ, tốn tiền) khi `--redo` đủ.
5. **Không đổi dữ liệu người dùng ngoài repo** ngoài thao tác `export` họ đã đồng ý.

## Tra nhanh

| Việc | Lệnh |
|---|---|
| Kiểm tra môi trường | `$PY <thư-mục-skill>/scripts/check_env.py --repo <SkillForge-Agent> [--ping]` |
| Tải nguồn | `$PY skillforge_cli.py fetch "<URL\|file>" [--limit N] [--no-frames]` |
| Chưng cất | `$PY skillforge_cli.py distill "<URL\|file>"... --domain X --lang vi` |
| Viết lại 1 skill / lập lại kế hoạch | `... distill ... --redo <tên-skill>` / `--redo plan` |
| Bỏ quiz (nhanh, rẻ, chỉ còn cổng kiểm) | `... distill ... --no-eval` |
| Chọn backend mô hình | `--llm api` (cần `ANTHROPIC_API_KEY`) / `--llm claude-cli` (dùng đăng nhập Claude) |
| Tìm skill đã có | `$PY skillforge_cli.py search "từ khoá" --domain X` |
| Xuất skill | `$PY skillforge_cli.py export X --to <dir> [--include-drafts]` |
| Phục vụ qua MCP | `$PY skillforge_cli.py serve` (tool `get_skill_details`, `read_skill_file`) |

Cơ chế bên trong (5 giai đoạn, định dạng đầu ra, biến môi trường, chi phí):
[references/how-it-works.md](references/how-it-works.md).
