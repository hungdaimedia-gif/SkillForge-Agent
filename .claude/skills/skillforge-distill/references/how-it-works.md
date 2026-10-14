# Cơ chế bên trong SkillForge distill

## Luồng dữ liệu

```
URL/file ─► fetch ─► SourceDoc (cache) ─► map ─► units ─► plan ─► write ─► gate ─► quiz ─► skills_wiki
            (không LLM)                  (LLM, xem ảnh)  (LLM)    (LLM)   (code)  (LLM ×2)
```

| Giai đoạn | Mã nguồn | Đầu vào → đầu ra | Gọi mô hình |
|---|---|---|---|
| fetch YouTube | `core/sources/youtube.py` | URL → `sources_cache/youtube/<id>/doc.json` (transcript theo mốc giờ + keyframe 720p) | 0 |
| fetch sách | `core/sources/book.py` | PDF/EPUB/MD → SourceDoc, mốc `p.87` / `§3¶4` | 0 |
| map | `core/distill.py: map_section` | 1 phần (video ngắn = cả video; video > 15 phút chia theo chapter; sách theo chương) → các *đơn vị kiến thức* | 1 / phần |
| plan | `plan_skills` | toàn bộ đơn vị → danh sách skill + skill trung tâm | 1 |
| write | `write_skill` | 1 skill + các đơn vị của nó → body, references, quiz | 1 / skill |
| gate | `lint_skill` | kiểm tra tất định, không tốn tiền | 0 |
| quiz | `evaluate_skill` | "học sinh" chỉ đọc skill trả lời → "giám khảo" chấm | 2 / skill |

## Đơn vị kiến thức (unit)

Loại: `procedure` (các bước), `shortcut` (phím tắt), `setting` (tham số), `concept`,
`heuristic` (quy tắc chọn), `pitfall` (lỗi + cách sửa), `example`.
Mỗi unit có `anchors` (mốc thời gian/trang) — mốc nằm ngoài độ dài video hoặc không có trong
sách bị **loại bỏ**; unit không còn mốc nào bị hạ `confidence: low`.

Keyframe được gửi **như ảnh thật** (API: khối image base64; claude-cli: tool Read mở file),
nên phím tắt hiện trên màn hình mà lời thoại không nói vẫn được ghi lại.

## Cách chọn keyframe

- Đầu mỗi chapter (+2 s) được ưu tiên, sau đó rải đều.
- Mật độ: ~1 khung / 15 s; video ít lời (< 400 ký tự transcript) ~1 khung / 6 s; tối thiểu 6,
  tối đa `--max-frames` (mặc định 24). Các khung cách nhau ≥ 4 s.
- Tải luồng hình 720p (không tiếng). 360p quá nhỏ để đọc chữ giao diện.

## Định dạng đầu ra

```
skills_wiki/<domain>/<category>/<ten_skill>/
├── SKILL.md        frontmatter name + description ("Use when ..."), thân bài có trích dẫn
├── references/     chi tiết dài, link từ SKILL.md
├── assets/         keyframe được nhúng (s<n>_f<mốc>.jpg)
├── SOURCES.md      bảng nguồn + mọi mốc trích dẫn thành link (YouTube &t=<giây>s)
├── quiz.json       câu hỏi + đáp án + mốc
├── eval.json       kết quả quiz offline từng câu
└── skill.json      metadata (kind=knowledge, status, eval_score, gate_issues, license)
```

Trích dẫn trong bài: `[S3 1:23]`, `[S3 1:23, 2:05]`, `[S5 p.87]`, `[S2 §3¶4]`.
`S<n>` = thứ tự nguồn trong lệnh `distill` (xem `work/<domain>/sources.json`).

`export` chỉ chép `SKILL.md`, `references/`, `assets/`, `SOURCES.md` (bỏ file nội bộ).

## Kết quả trung gian (resume)

```
work/<domain>/
├── sources.json        S<n> → video/sách
├── units/<phần>.json   kết quả map từng phần (cache)
├── units.json          toàn bộ unit đã đánh số S<n>.u<k>
├── plan.json           kế hoạch skill (dùng lại nếu tập unit không đổi)
├── skills/<tên>.json   bản viết + điểm quiz (dùng lại nếu kế hoạch của skill không đổi)
└── report.md           báo cáo cuối
```

Chạy lại cùng lệnh ⇒ không gọi mô hình cho phần đã có. `--redo <tên>` bỏ qua cache của đúng
skill đó; `--redo plan` lập lại kế hoạch; `--force` bỏ qua mọi cache.

**Chú ý:** mỗi lần `distill` ghi lại thư mục skill trong `skills_wiki/` từ cache. Sửa tay thì
sửa ở thư mục đích **sau khi export**, không sửa trong `skills_wiki/`.

## Cổng kiểm (gate)

Lỗi (giữ `draft`): tên không phải kebab-case ≤ 64 ký tự · description rỗng/ > 1024 ·
thân bài > 800 dòng · trích dẫn tới nguồn không tồn tại hoặc mốc sai · ảnh không có trong
assets · link tới references không tồn tại · không có trích dẫn nào.
Cảnh báo: thiếu "Use when", > 500 dòng, ít trích dẫn, reference không được link, < 3 câu quiz,
điểm quiz < `--min-eval`.

## Biến môi trường

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `SKILLFORGE_LLM` | `auto` / `api` / `claude-cli` | `auto` (có API key ⇒ api) |
| `ANTHROPIC_API_KEY` | khoá API cho backend `api` | — |
| `SKILLFORGE_MODEL` | model cho backend `api` | `claude-sonnet-5-5` |
| `SKILLFORGE_MAX_TOKENS` | trần token đầu ra | 32000 |
| `SKILLFORGE_CLI_MODEL` | model/alias cho `claude -p` | mặc định của CLI |
| `SKILLFORGE_CLAUDE_BIN` | đường dẫn `claude` | tìm trên PATH |
| `SKILLFORGE_YTDLP` / `SKILLFORGE_FFMPEG` / `SKILLFORGE_WHISPER` | đường dẫn công cụ | yt-dlp trong venv, rồi PATH |
| `SKILLFORGE_WHISPER_MODEL` | model whisper khi không có phụ đề | `small` |
| `SKILLFORGE_VIDEO_HEIGHT` | độ phân giải tải để cắt khung | 720 |
| `SKILLFORGE_CACHE` / `SKILLFORGE_WORK` / `SKILLFORGE_WIKI` | thư mục | `sources_cache` / `work` / `skills_wiki` |

## Ước lượng chi phí

Số lần gọi ≈ (số phần nguồn) + 1 + 3 × (số skill). Ví dụ playlist 17 video ngắn ⇒ ~17 + 1 +
3 × 9 ≈ 45 lần. Mỗi keyframe 720p ≈ 1.200 token đầu vào; 160 khung ≈ 200 nghìn token.
`--no-eval` bỏ 2 lần/skill; `--max-frames` nhỏ hơn giảm token ảnh (đổi lấy rủi ro sót chữ trên màn hình).

## Nguồn gốc ý tưởng

Kiến trúc lấy cảm hứng từ Microsoft Resource2Skill (MIT, github.com/microsoft/Resource2Skill):
tách modality, cổng chất lượng trước khi skill được dùng, gắn nhãn giấy phép theo nguồn.
Khác biệt: Resource2Skill đưa URL thẳng cho Gemini và sinh code; SkillForge tự lấy transcript +
khung hình cho Claude và sinh skill dạng kiến thức, hỗ trợ sách.
