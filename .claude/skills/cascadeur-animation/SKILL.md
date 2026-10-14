---
name: cascadeur-animation
description: Kỹ năng chuyên sâu về hoạt hình 3D dựa trên vật lý (physics-based 3D character animation) trong Cascadeur (tập trung phiên bản 2026.2.3, bao gồm cả 2026.1, 2025 và 2024). Hướng dẫn toàn diện từ điều hướng giao diện, phím tắt, tạo dáng AI AutoPosing, quản lý Timeline & Keyframe, giải thuật vật lý AutoPhysics, dọn dẹp dữ liệu mocap, Quick Rigging nhân vật, tích hợp bộ công cụ AI đến xuất nhập khẩu đa nền tảng (Unreal Engine 5, Blender, Roblox). Cung cấp bảng tra cứu nhanh, cảnh báo lỗi thực chiến và 10 file tài liệu chuyên đề chi tiết.
---

# Kỹ năng Hoạt hình 3D Chuyên sâu với Cascadeur

Cascadeur là phần mềm làm diễn hoạt 3D độc đáo kết hợp giữa hoạt hình truyền thống, trí tuệ nhân tạo (AutoPosing) và mô phỏng vật lý tự động (AutoPhysics). Kỹ năng này cung cấp hệ thống tri thức thực chiến được tinh gọn và chưng cất từ hơn 90 video hướng dẫn chuyên sâu, giúp người dùng nắm vững toàn bộ quy trình từ khâu chuẩn bị mô hình, tạo dáng, mô phỏng chuyển động cơ học đến xuất file sang các engine trò chơi hiện đại.

## 1. Quy trình Hoạt hình Chuẩn 6 Bước (End-to-End Workflow)

1. Khởi tạo và chuẩn bị dự án: Nhập mô hình nhân vật (FBX/DAE), kiểm tra bộ xương hoặc thực hiện Quick Rigging, đặt góc quan sát camera và thiết lập FPS phù hợp [K1 0:16 "Let's rotate the viewport camera to take a closer look"] [K73 5:24 "rig controllers will be to use the quick rigging tool"]. Xem chi tiết: [Điều hướng Giao diện](references/interface-navigation.md) và [Hệ thống Rigging](references/rigging.md).
2. Chặn dáng then chốt (Blocking): Sử dụng công cụ AutoPosing để tạo các tư thế chính trên nội suy Step [K18 2:16 "If you hover the mouse over the timeline, you will see the type of interpolation"] [K20 1:55 "You can also use the hot keys here"]. Xem chi tiết: [Tạo dáng & AutoPosing](references/posing-autoposing.md) và [Timeline & Nội suy](references/keys-timeline-interpolation.md).
3. Nội suy và đệm dáng (Inbetweening): Chuyển sang nội suy Bezier hoặc sử dụng thanh trượt Inbetweening/Easing để tạo nhịp điệu và độ mượt chuyển tiếp [K31 0:45 "So here I made two keys. Now I'm selecting the frames on the timeline, and I click on the in-betweening"] [K82 0:12 "In the latest version, we've added a new tool called easing"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"]. Xem chi tiết: [Quản lý Keyframe & Timeline](references/keys-timeline-interpolation.md).
4. **Áp dụng Vật lý Tự động (AutoPhysics)**: Kích hoạt AutoPhysics để bóng ma xanh tính toán đường bay đạn đạo CoM, điều chỉnh điểm tựa Fulcrum và snap chuyển động vật lý vào keyframe [K3 0:44 "Now let's turn on autophysics. As you can see, the character stands still in all the frames"] [K3 0:00 "Hello everyone, Falkron points are an essential part of the physics character"] [K36 7:09 "To fix this, use Art of Physics feature"]. Xem chi tiết: [Vật lý AutoPhysics](references/physics.md).
5. Dọn dẹp mocap và tinh chỉnh chi tiết: Nếu dùng dữ liệu mocap, unbake keyframe thưa trong Scene Settings, khử trượt chân bằng Fulcrum Cleaning, sửa lật khớp và thêm Animation Layers cho chuyển động phụ [K8 0:00 "You can find it in the scene settings tab over here"] [K36 1:45 "The Fulcrum Motion Cleaning Tool is designed to automatically edit feed orientation, height differences and unwanted glides"] [K36 2:12 "Now go to Scene Settings. Click on Animation Unbaking and here you have Interpolation Difference"] [K83 0:00 "In the second update of 2026, we finally introduced animation layers"]. Xem chi tiết: [Dọn dẹp Mocap](references/mocap-cleanup.md) và [Quy trình Mẫu](references/workflows.md).
6. Tự động hoá và xuất file: Sử dụng kịch bản Python hoặc xuất file sang Unreal Engine 5, Blender hoặc Roblox [K15 12:40 "Now, sometimes when you import an the X animation, you will see the"] [K65 0:00 "cascader has a really powerful python API which you can use to"]. Xem chi tiết: [Bộ Công cụ AI](references/ai-tools.md), [Xuất Nhập Đa phần mềm](references/import-export.md) và [Lập trình Python](references/scripting-python.md).

## 2. Bảng Chỉ đường Tra cứu Tài liệu Chuyên sâu

| Mục tiêu hoặc Vấn đề Cần giải quyết | Đọc File Tài liệu |
|---|---|
| Làm quen giao diện, phím tắt camera, ẩn/hiện đối tượng, rãnh âm thanh, scene linking | [Giao diện & Điều hướng](references/interface-navigation.md) |
| Kỹ thuật tạo dáng, AutoPosing toàn thân và ngón tay, điểm Active/Inactive | [Tạo dáng & AutoPosing](references/posing-autoposing.md) |
| Đặt keyframe, các kiểu nội suy (Bezier, Step), Inbetweening, Easing, Animation Layers | [Timeline & Nội suy](references/keys-timeline-interpolation.md) |
| Khắc phục trượt chân, AutoPhysics, điểm tựa Fulcrum, trọng tâm CoM, ném vũ khí | [Vật lý AutoPhysics](references/physics.md) |
| Nhập mocap (Rokoko/Move.ai/Mixamo), retarget, unbaking, sửa lật gối/khuỷu, dọn xuyên thấu | [Dọn dẹp Mocap](references/mocap-cleanup.md) |
| Quick Rigging cho người, rig động vật 4 chân, rig non-humanoid, Rigid Body Mass, Node Editor | [Hệ thống Rigging](references/rigging.md) |
| Tạo chu kỳ di chuyển Cycles, mô hình diffusion Root Motion, nhân vật mẫu OpenPose | [Bộ Công cụ AI](references/ai-tools.md) |
| Cầu nối Blender, xuất nhập Unreal Engine 5 (Live Link / Metahuman), Roblox, Maya, Daz 3D | [Xuất Nhập Đa phần mềm](references/import-export.md) |
| Lập trình Python với module `csc`, Modify Methods, thêm rung nhiễu, viết Add-on, Vibe Coding | [Lập trình Python & Add-on](references/scripting-python.md) |
| Quy trình mẫu: Walk Cycle, Parkour võ thuật từ video mẫu, vũ khí 2 tay, ném kiếm | [Quy trình Mẫu Hoàn chỉnh](references/workflows.md) |

## 3. Bảng Phím tắt Thiết yếu Nhất (Essential Hotkeys)

| Phím tắt | Chức năng chính | Trích dẫn nguồn |
|---|---|---|
| Giữ `Alt` + chuột trái | Xoay khung nhìn camera 3D quanh tâm điểm nhìn | [K1 0:34 "Alt plus the left mouse key is rotation"] [K25 0:56 "The combination of Alt with a left mouse button performs rotation"] |
| Giữ `Alt` + chuột phải | Thu phóng (Zoom) khung nhìn mượt mà | [K1 0:34 "You can also zoom by scrolling the mouse wheel"] [K25 0:56 "And with the right mouse button, you can zoom in and out"] |
| Giữ `Alt` + chuột giữa | Trượt ngang khung nhìn camera (Pan) | [K25 1:11 "And with a scroll wheel pressed, you can move the camera in space, normally in one plane"] |
| `T` | Căn giữa camera vào đối tượng đang chọn trong Viewport | [K25 3:01 "The second is switching to the display mode from the camera itself"] |
| `F` | Tạo hoặc xoá keyframe trên timeline (tương đương nút chìa khoá xanh) | [K41 4:40 "To move the key frames within the timeline, use the scroll button on your mouse"] |
| `Alt + F` | Biến toàn bộ khung hình trong khoảng chọn thành keyframe hoặc xoá toàn bộ | [K41 5:46 "When dealing with key frame groups, you can drag them or copy"] |
| `V` | Ẩn nhanh đối tượng đang chọn trong Viewport | [K25 3:57 "The V key hides the selected scene object"] |
| `Shift + V` | Ẩn mọi thứ ngoại trừ đối tượng đang được chọn | [K25 3:57 "And Shift plus V hides everything except the selected scene object"] |
| `Alt + V` | Hiện lại toàn bộ tất cả các đối tượng đã bị ẩn trong scene | [K25 4:12 "Alt plus V returns a display of everything previously hidden in the scene"] |
| `Shift + Z` | Huỷ kích hoạt controller trong AutoPosing để AI tự uốn nắn | [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] [K72 1:33 "To deactivate it, select the controller and press shift Z or click this button here"] |
| `Shift + Space` | Chia đôi khung nhìn Viewport thành 2 màn hình | [K25 2:09 "Press Shift and Space to divide the viewport into two"] |
| Phím `W` / `E` | Chuyển đổi qua lại giữa công cụ di chuyển và xoay | [K1 3:08 "Another way to select multiple points is to hold down the shift key"] |
| Phím `Control` + Z / Shift + Z | Hoàn tác (Undo) và Làm lại (Redo) thao tác | [K15 4:18 "Control Z will undo and Control Shift Z will redo"] |

## 4. Bảng Tra cứu Thuật ngữ Cốt lõi (Glossary)

- **Fulcrum (Điểm tựa)**: Điểm tiếp xúc vật lý giữa nhân vật và bề mặt môi trường (chân chạm sàn, tay chống tường) chịu phản lực trọng trường [K3 0:00 "Hello everyone, Falkron points are an essential part of the physics character"] [K36 1:28 "Let's start by checking our fulcrum points"].
- **AutoPhysics**: Công cụ tính toán vật lý tự động dựng quỹ đạo đạn đạo cho khối tâm nhân vật trên các khoảng nhảy không có điểm tựa [K3 2:47 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"].
- **Ballistics (Đạn đạo)**: Quỹ đạo parabol rơi tự do của khối tâm khi nhân vật rời khỏi mặt đất trong các cú nhảy [K2 16:10 "In the frames without fulcrum points, the main physics filter creates a ballistic curve for center of mass"] [K3 2:47 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"].
- **Center of Mass**: Vị trí trung bình phân bố khối lượng cơ thể, điểm mấu chốt quyết định sự cân bằng [K2 16:10 "In the frames without fulcrum points, the main physics filter creates a ballistic curve for center of mass"] [K35 4:50 "The most important to check is that your center of mass is in the right position"].
- **Angular Momentum**: Đại lượng đo mức độ xoay quán tính của nhân vật trong không trung [K49 0:00 "This tool helps you to smooth out the angular momentum"] [K49 0:14 "So what we can see is that to preserve the angular momentum"].
- **Inbetweening**: Kỹ thuật tạo dáng chuyển tiếp trung gian dựa trên thuật toán nội suy cập nhật thời gian thực [K16 0:17 "it can now update in real time and can be used with other interpolation methods"] [K31 0:00 "the in-betweening generates animations, and what's important for us animators is to have enough control over the animation"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
- **Interval**: Khoảng thời gian giữa hai khung hình trên timeline được bảo vệ hoặc chỉnh sửa đồng loạt [K13 2:15 "This green line also appears above the timeline"] [K36 3:06 "Let's keep going and refine this animation along the timeline"].
- **Animation Layer**: Lớp diễn hoạt phụ (Additive) cho phép sửa chi tiết mà không làm biến dạng track mocap gốc [K83 0:00 "You can now create additive layers and make non-destructive changes to your animation"] [K83 0:13 "You can now create additive layers and make non-destructive changes to your animation"].
- **Unbaking**: Thuật toán nén dữ liệu mocap dày đặc từng frame thành hệ thống keyframe thưa có thể chỉnh sửa dễ dàng [K18 10:49 "And I want to tell you more about the unbaking tool"] [K36 2:12 "Click on Animation Unbaking and here you have Interpolation Difference"] [K68 0:00 "This animation is baked which means every frame is a keyframe"].
- **Retargeting**: Quy trình ánh xạ dữ liệu chuyển động từ bộ xương này sang bộ xương khác có tỷ lệ và cấu trúc khác nhau [K56 0:00 "In this video we're going to talk about animation retargeting, which allows"] [K86 1:42 "timeline, go to edit, retargeting, copy. And in the other scene, make sure you select enough frames"].

## 5. Agent Tự Động Thao Tác Cascadeur qua MCP

Khi agent cần trực tiếp điều khiển phần mềm Cascadeur trên máy cục bộ (mở scene, đọc khớp, chạy script Python hoặc chụp ảnh viewport kiểm tra kết quả), **không dùng kỹ năng này** mà hãy chuyển sang kỹ năng chuyên biệt:
👉 [Kỹ năng Điều khiển Cascadeur MCP](../../.claude/skills/cascadeur-mcp/SKILL.md)

Skill đó cung cấp toàn bộ tài liệu về server `127.0.0.1:8765`, công cụ `run_script`, API `csc` và bộ kịch bản dòng lệnh `scripts/casc.py`.

## 6. Cảnh báo Phiên bản và Giới hạn Tri thức

- Các tính năng phiên bản mới: Cập nhật và kiểm chứng các tính năng mới như Animation Layers [K83 0:00 "In the second update of 2026, we finally introduced animation layers"], Easing [K82 0:14 "In the latest version, we've added a new tool called easing"], Collision Penetration Cleaning [K8 0:00 "Today, let's highlight our brand new feature called collision penetration cleaning"] và Live Link với Unreal Engine 5 [K10 0:00 "up a live link between Cascadeur and Unreal Engine, which allows you"].
- **Giới hạn tri thức**: Toàn bộ dữ liệu được chưng cất từ lời thoại và transcript của các video hướng dẫn; những thao tác thuần thị giác chỉ xuất hiện trên màn hình mà không được người hướng dẫn thuyết minh bằng lời có thể bị khuyết thiếu. Hãy đối chiếu thêm mã K tương ứng trong [Danh mục Nguồn](SOURCES.md) khi cần.
