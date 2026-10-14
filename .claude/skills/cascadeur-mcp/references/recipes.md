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

## ✅ Rig một con vật bốn chân từ đầu (Blender Rigify → Cascadeur), 2026-10-14

Đã chạy trọn trên Cascadeur 2026.2.3 + Blender 4.5.14 LTS (bản Microsoft Store). Script đầy đủ trong
`scripts/examples/`.

1. **Blender (nền):** `build_horse.py` — khung xương ngựa Rigify (`armature_horse_metarig_add`,
   70 xương) → mesh thô bằng Skin modifier → gắn xương tự động → xuất `horse_crude.fbx`.
   - Blender bản Store chỉ chạy được qua `%LOCALAPPDATA%\Microsoft\WindowsApps\blender-launcher.exe`
     (gọi thẳng exe trong `WindowsApps` bị "Access is denied"); launcher không trả stdout ⇒ script tự ghi
     kết quả/lỗi ra file.
   - Xương Rigify (chân, đuôi) tách rời thân: nối mỗi xương với xương cha trước khi tạo khối.
2. **Nhập FBX vào scene mới:**
   ```python
   a = app.get_scene_manager().create_application_scene(); app.get_scene_manager().set_current_scene(a)
   app.get_tools_manager().get_tool("FbxSceneLoader").get_fbx_loader(a).import_model(r"...\horse_crude.fbx")
   ```
3. **Bật Rig mode:** `import rig_mode.on as rm_on; rm_on.run_raw(scene, [0.0, 0.5, 0.0])`
   (`RiggingModeTool` editor `get_joints_data()` → 70 xương).
4. **Quick Rigging bốn chân bằng code** (`step2_quadruped_qrt.py`):
   - `csc.rig.QrtData().quadruped = [csc.rig.QuadrupedBoneProperty()]`; 5 nhóm `trunk`, `left_fore_paw`,
     `right_fore_paw`, `left_hind_paw`, `right_hind_paw`, **mỗi nhóm là `list[list[csc.rig.BoneProperty]]`**.
   - `BoneProperty.bone_name` = tên điểm chuẩn trong `resources/autorig_templates/Quadruped.qrigcasc`
     (`pelvis, spine_1..3, neck_1, neck_2, head, head_end, tail_1..4, tail_end, scapula_l, humerus_l,
     radius_l, carpals_l, paw_f_l, femur_l, tibia_l, tarsals_l, paw_h_l` + bản `_r`); `object_id` = xương;
     `joint_path_name = csc.model.PathName.get_path_name(obj_id, scene.model_viewer())`.
   - Gọi `prototypes.qrt_prototypes.create.create_quadruped_rig(scene, q, 15.0, 30.0, [0.0, 0.5, 0.0], "")`
     (độ dài cm). Kết quả: +209 object.
5. **Thoát Rig mode để dựng rig:** `import rig_mode.off as rm_off; rm_off.run(scene, True)` → RigInfo 1,
   64 Point, 29 RigidBody, CenterOfMass, 4 FulcrumGroup (4 móng), Ragdoll.
   - ⚠️ **AutoPosing cho động vật bốn chân cần giấy phép Pro**: bản Basic/Indie hiện hộp thoại "AutoPosing for
     Quadruped is not available…" (người dùng bấm Close — agent không bấm Upgrade).
6. **Tạo key và di chuyển điểm điều khiển** (`step4_lift_hoof.py`, callback 3 tham số của `modify_update`):
   - Scene mới chỉ có 1 khung ⇒ **đặt key trên mọi layer trước** (`layers_editor().set_fixed_interpolation_or_key_if_need(layer, f, True)`),
     rồi `model.fit_animation_size_by_layers()`, sau đó mới `node_deep("Position").set_value(v, f)` +
     `normalize_sections(scene)` + `scene_updater.run_update({pos.data_id()}, f)`.
   - Kiểm chứng bằng số: nâng `f_toe.L_MainPoint` 40 cm ở khung 10 ⇒ xương `f_toe.L` y 22,1→62,1,
     `forearm.L` tự gập (IK), móng phải không đổi.

7. **Animation bước tại chỗ** (`step5_walk_in_place.py`): key ở các khung 0,5,…,40 trên mọi layer →
   `fit_animation_size_by_layers()` → đặt vị trí 4 điểm móng (`f_toe.L/R_MainPoint`, `toe.L/R_MainPoint_r`)
   lần lượt nhấc 25 cm ở khung 5/15/25/35, `head_MainPoint` gật, `tail.004_MainPoint` phe phẩy →
   `run_update` mọi khung. Kiểm chứng: xương móng y 20–22 → 45–47 đúng thứ tự chân. Quay video:
   `casc.screenshot(path, frame=f)` từng khung rồi ffmpeg ghép MP4/GIF.
   Giới hạn: chỉ di chuyển điểm điều khiển (không AutoPosing, không AutoPhysics) nên thân đứng yên, cử động cứng.
