# Giao việc: chưng cất khoá học Cascadeur thành skill `cascadeur-animation`

> Dành cho agent thi công (AG1/AG2/agent bất kỳ). Đọc **hết** file này trước khi làm.
> Người lập: Claude (lập kế hoạch + nghiệm thu), 2026-10-14. Repo: `G:\SkillForge-Agent`,
> nhánh `feat/knowledge-distill`. `$PY` = `G:\SkillForge-Agent\.venv\Scripts\python.exe`.

## 1. Mục tiêu

Đọc transcript của **93 video** hướng dẫn Cascadeur (78 bài cascadeur.com/tutor +
15 bài mới trên kênh) và viết thành **một skill tổng hợp** để agent khác học xong là
hiểu mọi chức năng làm animation/video trong Cascadeur — **không cần lên mạng**.

Lệnh `skillforge distill` tự động đang không dùng được (thiếu đăng nhập mô hình), nên
việc đọc–tóm–viết do chính agent làm, theo đúng tinh thần pipeline: bóc ý → gom theo năng
lực → viết có trích dẫn → kiểm bằng script.

## 2. Đầu ra (đúng đường dẫn này)

```
G:\SkillForge-Agent\.claude\skills\cascadeur-animation\
├── SKILL.md                         ← skill tổng hợp (hub), ≤ 300 dòng
├── SOURCES.md                       ← bảng K1…K93 → tiêu đề + link YouTube
└── references\
    ├── interface-navigation.md      ← giao diện, viewport, camera, chọn, ẩn/hiện, scene linking, audio
    ├── posing-autoposing.md         ← kiểu controller, tạo dáng, AutoPosing (cả ngón tay), Control Picker
    ├── keys-timeline-interpolation.md ← key, track, layer, nội suy, tangent/trajectory, Inbetweening, Easing, Animation Layers
    ├── physics.md                   ← AutoPhysics (+ sliders), Fulcrum, trọng tâm, ballistics, angular momentum,
    │                                  chuyển động thứ cấp, separation of motion, ragdoll, collision, contact 2 nhân vật, constraints
    ├── mocap-cleanup.md             ← nhập mocap, retarget, dọn (công cụ tốt nhất, twist, limb direction, penetration),
    │                                  tách đoạn, unbaking, sửa animation có sẵn (Mixamo…)
    ├── rigging.md                   ← Quick Rigging / rig đầy đủ, rig tuỳ biến (động vật, cartoon, non-humanoid),
    │                                  rigid body mass, node editor (mắt, root controller), rig đạo cụ/vũ khí
    ├── ai-tools.md                  ← tạo chu kỳ, root motion, tạo từ 2 tư thế, các công cụ AI khác
    ├── import-export.md             ← Blender, UE5 (Live Link, locomotion, Metahuman), Roblox, Mixamo, Maya, Daz, AccuRIG, RenderHub
    ├── scripting-python.md          ← giới thiệu scripting, modify methods, add-on, animation scripts, vibe coding
    └── workflows.md                 ← quy trình mẫu từ đầu đến cuối: walk cycle, đánh nhau/parkour từ video tham
                                       chiếu, vũ khí 2 tay & ném vũ khí, 2 nhân vật, cartoon, góp ý của animator
```

Một ý thuộc hai file ⇒ viết đầy đủ ở file chính, file kia chỉ một dòng + link.

## 3. Các bước

### Bước 0 — Kiểm tra transcript đã tải đủ

```bash
cd G:\SkillForge-Agent
$PY skillforge_cli.py fetch manifests/cascadeur_tutor.urls --no-frames
$PY skillforge_cli.py fetch manifests/cascadeur_channel_extra.urls --no-frames
```

Chạy lại không tốn gì (lấy từ cache). Video không có phụ đề sẽ được whisper nghe trên máy
(vài phút/video). Bảng in ra cột `chars` = độ dài lời thoại; ghi lại video nào `chars=0`.

### Bước 1 — Gom transcript theo chuyên mục

```bash
$PY scripts/group_transcripts.py . work/cascadeur_manual/transcripts
```

Tạo `work/cascadeur_manual/transcripts/<chuyên-mục>.txt` (mỗi video: dòng tiêu đề có **mã K**,
chapters, rồi từng dòng `[m:ss] lời`) và `sources.json`. **Mã K là cố định** — dùng nó để trích dẫn.

### Bước 2 — Đọc từng nhóm, ghi chú ý (tiết kiệm token)

- Mở **một** file nhóm một lúc. File `mocap_editing.txt` lớn (~95 nghìn ký tự) ⇒ đọc làm 2–3 lượt.
- Với mỗi video, ghi ra (nháp trong `work/cascadeur_manual/notes/<K>.md`, không cần đẹp):
  quy trình từng bước · phím tắt/nút/menu · tham số & tác dụng · mẹo/quy tắc chọn · lỗi hay gặp
  & cách sửa · phiên bản Cascadeur được nhắc tới. Mỗi ý kèm mốc `[K12 3:45]`.
- **Sửa lỗi nghe nhầm** của phụ đề tự động/whisper dựa vào tiêu đề, chapters và ngữ cảnh
  (ví dụ đã gặp: "Falkron" ⇒ **Fulcrum**). Không chắc ⇒ ghi "(nghe không rõ)".
- Bỏ qua lời chào, quảng cáo, kêu gọi subscribe.

### Bước 3 — Viết `references/*.md`

Mẫu cho mỗi file:

```markdown
# <Chủ đề>

Tóm tắt 2–3 câu: chủ đề này giải quyết việc gì trong làm animation.

## Khái niệm cốt lõi
- **<Thuật ngữ>**: định nghĩa ngắn. [K2 1:05]

## Quy trình: <tên việc>
1. Bước cụ thể, tên nút/menu/phím giữ nguyên tiếng Anh như trên giao diện: `Ctrl + Shift + K`. [K18 2:10]
2. ...

## Quy tắc chọn
- Khi <tình huống> ⇒ dùng <công cụ/chế độ>, vì ... [K27 4:00]

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
```

Luật viết:
1. **Mọi câu nêu sự thật đều có trích dẫn** `[K<số> m:ss]` (nhiều mốc: `[K18 2:10, 5:40]`).
   Không có trong transcript ⇒ không viết, hoặc ghi rõ "nguồn không đề cập".
2. **Diễn giải bằng tiếng Việt**, không chép nguyên văn quá 1 câu ngắn. Tên nút, menu, tham số,
   phím tắt giữ nguyên tiếng Anh trong `code`.
3. Nội dung **phiên bản cũ** (video ghi 2024.x mà bài 2025–2026 làm khác) ⇒ ghi cả hai, đánh
   dấu bản mới. Bản đang cài trên máy là **2026.2.3**.
4. Mỗi file reference ≤ ~400 dòng; dài hơn thì tách thêm file và link.

### Bước 4 — Viết `SKILL.md` (hub)

```markdown
---
name: cascadeur-animation
description: Use when ... (tiếng Anh, ≤ 600 ký tự, nêu Cascadeur, các tính năng chính:
  AutoPosing, AutoPhysics, fulcrum, keyframe/inbetweening, mocap cleanup, rigging, export UE5/Blender/Roblox,
  và các câu người dùng hay hỏi)
---
```

Thân bài gồm:
1. **Quy trình tổng** làm một animation từ đầu tới khi xuất (dựng/nhập nhân vật → rig → tạo dáng
   key → nội suy/inbetween → vật lý → tinh chỉnh → xuất), mỗi bước trỏ tới file reference.
2. **Bảng chỉ đường**: | Việc người dùng muốn | Đọc file nào |.
3. **Bảng phím tắt** quan trọng nhất (gom từ các file, có trích dẫn).
4. **Thuật ngữ** (Fulcrum, AutoPhysics, Ballistic, Center of Mass, Angular Momentum, Inbetweening,
   Tween Machine, Interval, Layer, Unbaking, Retargeting…).
5. **Agent tự thao tác Cascadeur**: một đoạn ngắn trỏ sang skill `cascadeur-mcp`
   (`.claude/skills/cascadeur-mcp/SKILL.md`). Không chép lại nội dung skill đó.
6. **Cảnh báo phiên bản** + giới hạn: "chưng cất từ lời thoại; thứ chỉ hiện trên màn hình có thể thiếu".

### Bước 5 — `SOURCES.md`

Bảng từ `sources.json`: | K | Tiêu đề | Chuyên mục | Cấp độ | Thời lượng | Link YouTube |.
Ghi thêm: nguồn = transcript (phụ đề YouTube hoặc whisper), giấy phép `youtube_review_pending`,
nội dung đã diễn giải, ngày chưng cất.

### Bước 6 — Cổng kiểm (bắt buộc xanh)

```bash
$PY scripts/check_knowledge.py .claude/skills/cascadeur-animation work/cascadeur_manual/transcripts/sources.json
```

- `❌` ⇒ sửa đúng chỗ báo (mã K sai, mốc vượt độ dài video, link hỏng, file không có trích dẫn).
- Dòng `never cited` = video chưa dùng. Mục tiêu: **≥ 85/93**. Video bị bỏ ⇒ ghi lý do trong báo cáo
  (trùng nội dung, chỉ là timelapse không lời…).

### Bước 7 — Tự kiểm bằng câu hỏi (không cần công cụ)

Viết 15 câu hỏi thực hành (ví dụ "Nhân vật trượt chân khi AutoPhysics bật thì kiểm tra gì?"),
tự trả lời **chỉ** bằng nội dung skill, đối chiếu transcript. Câu nào skill không trả lời được ⇒
bổ sung. Ghi bảng kết quả vào `work/cascadeur_manual/quiz.md`.

## 4. Luật chung

- **Không xoá file nào** (cache, work, skill khác). Không `--force`. Không sửa code SkillForge.
- **Không commit, không push, không mở PR.** Dừng ở Bước 7 và bàn giao.
- Không mở Cascadeur, không gọi MCP Cascadeur — việc này chỉ đọc transcript.
- Kẹt quá 2 lần cùng một chỗ ⇒ dừng, báo.

## 5. Bàn giao (dán đủ)

1. Danh sách file đã tạo + số dòng (`wc -l`).
2. Toàn bộ output của `check_knowledge.py` (phải `✅ OK`).
3. Danh sách video `chars=0` / bị bỏ + lý do.
4. `work/cascadeur_manual/quiz.md` (15 câu, đạt/không đạt).
5. `git status --short`.

Claude sẽ nghiệm thu: chạy lại cổng kiểm, đối chiếu ngẫu nhiên 10 trích dẫn với transcript,
đọc hub + 2 reference, rồi trả PASS hoặc danh sách sửa.
