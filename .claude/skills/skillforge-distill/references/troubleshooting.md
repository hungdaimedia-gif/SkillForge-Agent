# Xử lý sự cố

## Mô hình (LLM)

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `claude CLI error: Failed to authenticate: OAuth session expired` | Phiên đăng nhập Claude Code hết hạn | Người dùng mở `claude` trong terminal, gõ `/login`. Agent **không** tự đăng nhập hộ |
| `claude CLI not found on PATH` | Chưa cài Claude Code hoặc không có trên PATH | Đặt `SKILLFORGE_CLAUDE_BIN` hoặc dùng `--llm api` |
| `AuthenticationError` / thiếu key với `--llm api` | Chưa đặt `ANTHROPIC_API_KEY` | Người dùng tự đặt biến môi trường; agent không nhập khoá hộ |
| `Output truncated at max_tokens` | Skill quá dài trong một lần viết | Tăng `SKILLFORGE_MAX_TOKENS` (vd 64000) rồi `--redo <tên>` |
| `Model refused the request` | Nội dung nguồn bị bộ lọc an toàn chặn | Bỏ nguồn đó khỏi lệnh, báo người dùng |
| `Model did not return JSON` (claude-cli) | CLI cũ không hỗ trợ `--json-schema` | Cập nhật Claude Code, hoặc dùng `--llm api` |
| Rate limit / 429 | Gọi song song quá nhiều | `--workers 2` (hoặc 1) rồi chạy lại — phần đã xong lấy từ cache |

## Tải video (yt-dlp)

| Triệu chứng | Nguyên nhân | Cách sửa |
|---|---|---|
| `HTTP Error 403: Forbidden` khi tải video | yt-dlp cũ hoặc YouTube chặn tạm một client | `$PY -m pip install -U yt-dlp` (cài vào **venv dự án**, không sửa bản của công cụ khác); chạy lại `fetch` — code đã tự thử `web_safari,tv` rồi `ios,mweb` |
| Cảnh báo "yt-dlp version is older than 90 days" | Bản trên PATH cũ | Như trên; code ưu tiên bản `yt_dlp` trong venv |
| `frames=0` cho một video | Tải video thất bại cả 3 lần | Chạy lại `fetch` sau vài phút; vẫn lỗi ⇒ chưng cất chỉ với transcript và ghi chú cho người dùng |
| Video chỉ có 360p/720p, không có 480p | Bình thường | Mặc định đã là 720p (`SKILLFORGE_VIDEO_HEIGHT`) |
| `chars` rất thấp, transcript chỉ một câu | Video nhạc nền + chữ trên màn hình; "phụ đề thủ công" chỉ là chú thích | Code tự thử phụ đề tự động và cắt khung dày hơn; kiểm tra ảnh |
| Không có phụ đề nào | Video không bật phụ đề | Cài whisper (`pip install openai-whisper`) — tự chạy khi thiếu phụ đề; hoặc `SKILLFORGE_WHISPER` |
| Video riêng tư / giới hạn tuổi / cần đăng nhập | yt-dlp không truy cập được | Bỏ video đó; **không** dùng cookie trình duyệt của người dùng nếu họ chưa cho phép rõ ràng |
| `ffmpeg not found` | Chưa cài ffmpeg | Cài ffmpeg, thêm vào PATH hoặc đặt `SKILLFORGE_FFMPEG` |

## Sách

| Triệu chứng | Cách sửa |
|---|---|
| `Reading PDF needs pip install pymupdf` | `$PY -m pip install pymupdf` (hoặc `pypdf`) |
| `no text layer (scanned PDF?)` | OCR trước (vd `ocrmypdf in.pdf out.pdf`), rồi chưng cất file mới |
| Chương bị chia `(part 2)` | Chương > 60.000 ký tự được cắt để vừa một lần gọi — bình thường |
| EPUB ra ít chương | Trang < 200 ký tự (bìa, mục lục) bị bỏ qua — bình thường |

## Kết quả

| Triệu chứng | Cách sửa |
|---|---|
| Nhiều skill `draft` vì `invalid anchor` | `--redo <tên>` từng skill; nếu lặp lại ⇒ nguồn có mốc lạ, báo người dùng |
| Quiz thấp ở mọi skill | Nguồn quá mỏng so với câu hỏi, hoặc transcript tự động sai nhiều ⇒ xem `eval.json`, cân nhắc whisper |
| Chạy lại không thấy thay đổi | Đang lấy từ cache — dùng `--redo` cho phần muốn làm lại |
| Sửa tay trong `skills_wiki/` bị mất | `distill` ghi lại từ cache; sửa ở thư mục đích sau `export` |
| `export` báo `exists ... not overwritten` | Thư mục đích đã có skill cùng tên — người dùng tự đổi tên/xoá rồi export lại |

## Dọn dẹp (chỉ người dùng làm)

Agent chỉ **liệt kê**, không xoá: video đã tải `sources_cache/youtube/<id>/video_720p.*` (lớn
nhất), file cũ của các bản trước (`video.mp4`, `frames/`, `subs.*.json3`), và `work/<domain>/`
khi đã chắc không cần chạy lại.
