---
name: cascadeur-mcp
description: Use when an agent must control or inspect Cascadeur (3D physics-based character animation software) on this machine — run Python inside Cascadeur through its built-in MCP script server, open .casc scenes, read objects/frames/joint positions, take viewport screenshots to check an animation, export, or write Cascadeur scripts. Covers starting the server, the csc/pycsc API, verified recipes, safety rules, and known gaps. Not for learning animation theory from tutorials (use the distilled cascadeur skills for that).
---

# Điều khiển Cascadeur qua MCP

Cascadeur (từ bản 2026.2) có sẵn **MCP script server**: chạy code Python *bên trong*
phần mềm, với toàn bộ API `csc` / `pycsc`. Agent dùng nó làm "đôi tay" (mở scene, đọc và
sửa animation, xuất file) và "con mắt" (chụp khung nhìn để tự kiểm tra kết quả).

Mọi điều trong skill này được kiểm chứng trên **Cascadeur 2026.2.3** tại `G:\cascadeur`
ngày 2026-10-14, trừ chỗ ghi rõ *(chưa chạy thử)*.

## 1. Bật kết nối (người dùng làm)

1. Mở Cascadeur.
2. Menu **Scripts → MCP → Start script server**. Server nghe `127.0.0.1:8765`.
3. Kiểm tra: `python <thư-mục-skill>/scripts/casc.py health` → `{"ok": true, ...}`.
   Mã thoát 2 ⇒ server chưa bật: nhờ người dùng làm bước 2, **không** tự mở/khởi động hộ.
4. Xong việc: **Scripts → MCP → Stop script server** (server không có mật khẩu).

## 2. Hai cách gọi

| Cách | Khi nào | Gọi thế nào |
|---|---|---|
| MCP | Agent đã nạp server `cascadeur` (vd `.mcp.json`: `{"type": "http", "url": "http://127.0.0.1:8765/mcp"}`) | tool `run_script` với `{"code": "..."}` |
| HTTP / script | Agent không có MCP, hoặc MCP chưa được duyệt | `python scripts/casc.py run "<code>"`, `run --file x.py`, `shot out.png --frame N` |

Code chạy ở lần `scene_idle` kế tiếp, trong namespace có sẵn `csc`, `scene` (scene hiện
tại, `csc.domain.Scene`) và `app`. Biểu thức đơn ⇒ trả về `value`; câu lệnh ⇒ dùng `print`
(trả về trong `messages`). Mỗi lệnh chờ tối đa 30 s phía server.

## 3. Luật an toàn (bắt buộc)

1. **Không sửa scene người dùng đang làm.** Thử nghiệm trên scene mới
   (`create_application_scene`, xem công thức) và **không** `save` đè file `.casc` có sẵn —
   lưu bản mới với tên mới khi người dùng yêu cầu.
2. **Không xoá/đóng scene, không chạy `Scene.Undo`, không xoá object** khi chưa được yêu cầu rõ.
3. Hàm sửa (`scene.modify*`, `pyscene.edit`) **trả về `False` khi callback lỗi** trong khi
   HTTP vẫn báo `ok: true` ⇒ luôn kiểm tra giá trị trả về, rồi xem cuối log
   `%LOCALAPPDATA%\Nekki Limited\Cascadeur\logs\cascadeur_log.log`.
4. Đơn vị độ dài là **cm** (nhân vật cao ~180).
5. Chỉ gọi API của chính Cascadeur. **Không** dịch ngược `cascadeur.exe`/DLL (giấy phép Nekki
   cấm sửa đổi chương trình).

## 4. Công thức đã kiểm chứng

Chi tiết + code đầy đủ: [references/recipes.md](references/recipes.md).

| Việc | Cốt lõi |
|---|---|
| Khung hiện tại / nhảy khung | `scene.get_current_frame()` · `scene.set_current_frame(30)` |
| Số khung animation | `scene.layers_viewer().frames_count()` |
| Danh sách object | `scene.model_viewer().get_objects()` |
| Mở `.casc` vào scene mới | `sm = app.get_scene_manager(); a = sm.create_application_scene(); sm.set_current_scene(a); csc.app.ProjectLoader.load_from(path, a.domain_scene())` |
| Vị trí toàn cục (cm) | `import pycsc; o.get_behaviour("Transform").global_position.get()` với `o in pycsc.get_scene_objects()` |
| Chụp khung nhìn | `casc.py shot out.png --frame N` (dùng `screen().grabWindow(winId)`) |

## 5. Vòng "làm → xem → sửa"

1. Làm thay đổi trên scene thử nghiệm (kiểm tra giá trị trả về của `modify`).
2. Chụp vài khung đại diện: `casc.py shot f030.png --frame 30` … rồi **mở ảnh ra xem**.
3. So với mục tiêu (tư thế, quỹ đạo, chân chạm đất…), sửa, chụp lại. Đừng báo xong khi chưa
   nhìn ảnh của chính lần sửa cuối.

## 6. Tra API

- [references/api-index.md](references/api-index.md): mục lục 332 module, ~1.070 lớp/hàm
  sinh từ phần mềm đang chạy.
- Chi tiết một hàm: `casc.py run "help(csc.view.Camera.zoom_to_points)"`.
- Tài liệu kèm ví dụ của Nekki: `G:\cascadeur\resources\scripts\python\samples\api_document.py`
  (~6.000 dòng). Script chính hãng để học cách dùng thật: `resources\scripts\python\commands\`,
  `scripts\`, `samples\`. Web: `https://cascadeur.com/python-api/`.

## 7. Điều chưa giải được (đừng đoán)

- **Đưa camera về nhân vật:** `Camera.zoom_to_points([...])` chạy không lỗi nhưng khung nhìn
  hầu như không đổi trong thử nghiệm; hộp bao lấy từ mọi object bị lệch vì có object phụ trợ.
  Hướng chưa thử: lọc khớp theo tên rồi dùng `ViewportDomain.set_camera_struct`.
- **Danh sách action:** `ActionManager` chỉ có `call_action(name)`, không liệt kê được tên;
  tên đã biết từ script chính hãng: `Scene.Undo`.
- `QWindow.grabWindow()` không tồn tại trong bản PySide6 của Cascadeur — dùng `screen().grabWindow`.
