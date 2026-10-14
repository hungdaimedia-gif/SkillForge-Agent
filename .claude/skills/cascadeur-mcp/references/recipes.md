# Công thức Cascadeur MCP

Đánh dấu: ✅ đã chạy thật trên Cascadeur 2026.2.3 (2026-10-14) · 📄 lấy từ script chính hãng
của Nekki, *chưa chạy thử* trong phiên kiểm chứng.

Chạy mỗi khối bằng `python scripts/casc.py run --file khoi.py` hoặc tool MCP `run_script`.
Namespace có sẵn: `csc`, `scene`, `app`.

## ✅ Đọc trạng thái scene hiện tại

```python
print("frame:", scene.get_current_frame())
print("frames:", scene.layers_viewer().frames_count())
print("objects:", len(scene.model_viewer().get_objects()))
```

## ✅ Mở một file .casc vào scene MỚI (không đụng scene đang mở)

```python
sm = app.get_scene_manager()
a = sm.create_application_scene()          # mở tab mới "untitled (n).casc"
sm.set_current_scene(a)
csc.app.ProjectLoader.load_from(r"G:\cascadeur\samples\Backflip_animation.casc", a.domain_scene())
ds = a.domain_scene()
print(len(ds.model_viewer().get_objects()), ds.layers_viewer().frames_count())   # 280, 124
```

Sau lệnh này `scene` trong các lần gọi kế tiếp là scene mới. Nhân vật mẫu có sẵn trong
`G:\cascadeur\samples\` (Cascy, UE5_Manny, Roblox, Dracorex_walk_cycle, Backflip_animation…;
mô tả trong `samples.json`). **Chỉ mở**, không lưu đè.

## ✅ Vị trí toàn cục của các object (cm)

```python
import numpy as np, pycsc
pts = {}
for o in pycsc.get_scene_objects():
    try:
        pts[o] = np.array(o.get_behaviour("Transform").global_position.get(), dtype=float).reshape(3)
    except Exception:
        pass                                  # object không có Transform
print(len(pts))                               # Backflip: 230 / 280 object có Transform
```

Hộp bao của *mọi* object gồm cả điểm phụ trợ (Backflip: x từ -200 tới 835) — muốn khung nhân
vật thì lọc theo tên/loại object trước.

## ✅ Nhảy khung và chụp khung nhìn

```bash
python scripts/casc.py shot f055.png --frame 55 --width 960
```

Bên trong: `scene.set_current_frame(55)`, chờ ~0,8 s cho Cascadeur vẽ lại, rồi
`w.screen().grabWindow(w.winId()).toImage()` và cắt vùng viewport của bố cục mặc định
(bỏ thanh công cụ, Outliner bên phải, timeline bên dưới). Bố cục khác ⇒ chỉnh tỉ lệ cắt trong
`SHOT_CODE` của `casc.py`.

## ✅ Tra tài liệu một hàm

```python
help(csc.view.Camera.zoom_to_points)
```

## 📄 Sửa scene có kiểm tra kết quả

```python
def mod(model, update, sc, session):          # chữ ký như commands/add/add_joint.py
    ...                                       # thay đổi dữ liệu ở đây
ok = scene.modify_with_session("Tên thao tác", mod)   # → bool (api_document.py:3590)
print("modify ok:", ok)                       # False ⇒ đọc cuối cascadeur_log.log
```

`scene.modify(name, fn)` dùng callback **3 tham số** `fn(model, update, sc)`
(add_function/add_dynamic.py); các bản `_with_session` thêm `session`. Biến thể khác:
`scene.modify_update(...)`, `scene.modify_update_with_session(...)`. Xem cách dùng thật trong
`resources/scripts/python/commands/` và `scripts/animation_scripts/`.

## 📄 Lưu scene thử nghiệm ra file MỚI và xuất FBX

```python
a = app.get_scene_manager().current_scene()
a.save(r"G:\path\ket_qua_moi.casc")           # tên mới, không đè file có sẵn
loader = app.get_tools_manager().get_tool("FbxSceneLoader").get_fbx_loader(a)
loader.export_model(r"G:\path\ket_qua_moi.fbx")
```

Nguồn: `samples/casc_import_export.py` (chính hãng). Chỉ làm khi người dùng yêu cầu lưu/xuất.

## ❓ Chưa giải: camera bám nhân vật

```python
import numpy as np
a = app.get_scene_manager().current_scene()
cam = a.active_viewport().domain_viewport().camera()
cam.zoom_to_points([np.array([x, y, z], dtype=np.float32) for ...])   # chạy được, hiệu quả chưa rõ
```

Còn có `cam.set_target(np.array([...], dtype=np.float32))`,
`ViewportDomain.camera_struct()` / `set_camera_struct(SphericalCameraStruct)` (target,
position, type) — chưa thử.
