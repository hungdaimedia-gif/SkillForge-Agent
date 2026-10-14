# Giao diện và Điều hướng Viewport trong Cascadeur

Giao diện Cascadeur được thiết kế chuyên biệt cho diễn hoạt vật lý và điều khiển khớp nối 3D, kết hợp khung nhìn tương tác trực quan cùng hệ thống timeline đa tầng. Tài liệu này hướng dẫn chi tiết cách làm chủ các công cụ quan sát, phím tắt điều hướng camera, tuỳ biến giao diện làm việc, ẩn/hiện bộ điều khiển, rãnh âm thanh và cơ chế liên kết đa scene trong các phiên bản Cascadeur.

## Khái niệm cốt lõi
- **Start Window**: Cửa sổ khởi động xuất hiện khi mở phần mềm hoặc bấm nút Home, quản lý các scene gần đây, tệp tự động lưu (Auto saves) và các mô hình mẫu như Cassie [K1 0:00 "You are currently looking at the start window"] [K1 0:16 "You are currently looking at the start window"].
- Điều hướng Viewport: Hệ thống điều khiển camera trong không gian 3 chiều qua phím `Alt` kết hợp chuột, ViewCube định hướng và các góc nhìn trực giao [K1 0:34 "Let's rotate the viewport camera to take a closer look"] [K25 0:56 "to master is the skills of navigating the viewport window"].
- Khối ViewCube và Đa khung nhìn: Khối lập phương góc trên phải hiển thị hướng các trục toạ độ; bấm vào mặt hoặc trục để snap camera vào trục toạ độ, bấm vào giữa khối để chuyển giữa perspective và isometric [K22 5:19 "In the right top corner of the viewport, you can see the view cube. It will be rotating along with the scene"] [K22 5:35 "the middle of the cube, you can switch between perspective and isometric modes"]. Bấm `Shift + Space` để chia đôi màn hình Viewport [K25 2:09 "Press Shift and Space to divide the viewport into two"].
- **Scene Linking**: Công cụ liên kết nhiều scene độc lập vào một cảnh tổng thể, cho phép làm việc song song nhiều nhân vật với hệ toạ độ và lưới riêng biệt [K50 0:00 "In the recent Cascager update, the Scene Linking tool had been significantly"] [K50 0:49 "In the recent Cascager update, the Scene Linking tool had been significantly"].
- **Audio Track**: Rãnh nạp file âm thanh dạng sóng trực tiếp trên Timeline để căn chuyển động theo âm thanh [K62 0:14 "file import audio once uploaded it will automatically be added to the timeline"] [K62 0:30 "file import audio once uploaded it will automatically be added to the timeline"].
- Mặt nạ chọn (Selection Mask): Thanh công cụ trên cùng cho phép bật/tắt khả năng chọn riêng biệt từng loại đối tượng (như Points, Box, Meshes, Joints), giúp tránh bấm nhầm khi diễn hoạt chi tiết [K25 2:44 "The down arrow pointer allows us to add a camera into the scene"].

## Quy trình: Thao tác Viewport và Điều khiển Camera
1. Mở một cảnh nhân vật (như Cassie) từ Start Window [K1 0:16 "You are currently looking at the start window"].
2. Xoay khung nhìn: Giữ phím `Alt` và chuột trái để xoay camera quan sát xung quanh đối tượng [K1 0:34 "Alt plus the left mouse key is rotation"] [K25 0:56 "The combination of Alt with a left mouse button performs rotation"].
3. Thu phóng: Giữ phím `Alt` và chuột phải (hoặc lăn bánh xe chuột) để phóng to/thu nhỏ khung nhìn mượt mà [K1 0:34 "the right mouse key controls zooming. You can also zoom by scrolling the mouse wheel"] [K25 0:56 "Now, for all my next actions, I'm holding out the Alt key and using corresponding mouse buttons"].
4. Trượt khung nhìn: Giữ phím `Alt` và nhấn giữ chuột giữa để di chuyển mặt phẳng quan sát [K25 1:11 "And with a scroll wheel pressed, you can move the camera in space, normally in one plane"].
5. Căn tâm vào đối tượng: Bấm phím `T` để camera tự động căn giữa vào đối tượng đang được kích hoạt trong cảnh [K25 3:01 "The second is switching to the display mode from the camera itself"].
6. **Đổi góc camera trực diện**: Bấm vào các mặt hoặc trục trên khối ViewCube để snap camera trực diện vào trục toạ độ [K22 5:19 "In the right top corner of the viewport, you can see the view cube. It will be rotating along with the scene"] [K1 0:51 "axes arrows next to the view cube to snap the camera view"].

## Quy trình: Tùy biến Viewport và Màu sắc hiển thị
1. Mở menu **Settings → Settings Window** trên thanh menu chính [K57 0:15 "customize the viewport to your liking go to settings settings window and"].
2. Chọn mục **Visualizers** để chỉnh các tham số hiển thị giao diện [K57 0:20 "go to settings settings window and under visualizers you can find the"].
3. Điều chỉnh **Sky color** (màu nền trời) phù hợp với chủ đề sáng (Light theme) hoặc tối (Dark theme) để tăng độ tương phản với nhân vật [K57 0:27 "color in the viewport for the light and for the Dark theme"] [K57 0:40 "color in the viewport for the light and for the Dark theme"].
4. Đặt góc nhìn mặc định (Field of View): bấm `Alt + 0` để trả lại góc mở mặc định là 30 độ [K25 3:57 "The default value is 30 when pressing Alt plus 0"].

## Quy trình: Ẩn/Hiện đối tượng và Bộ điều khiển
1. Chọn một hoặc nhiều controller, bộ phận cơ thể hoặc mesh trong viewport [K25 3:57 "Shift plus S switches between Point Controller and Box Mode"].
2. Bấm phím `V` để ẩn nhanh các đối tượng đã chọn khỏi màn hình [K25 3:57 "The V key hides the selected scene object"].
3. Bấm `Shift + V` để ẩn mọi thứ ngoại trừ đối tượng đang được chọn [K25 3:57 "And Shift plus V hides everything except the selected scene object"].
4. Bấm `Alt + V` để hiện lại toàn bộ tất cả các đối tượng đã bị ẩn trong cảnh [K25 4:12 "Alt plus V returns a display of everything previously hidden in the scene"].
5. Sử dụng biểu tượng con mắt trên từng rãnh track trong Timeline để ẩn toàn bộ các đối tượng thuộc rãnh đó [K63 0:43 "You can check the box under the eye icon for any track which will effectively hide all"].

## Quy trình: Liên kết nhiều Scene (Scene Linking)
1. Mở đồng thời các dự án cần liên kết trong Cascadeur [K50 0:13 "multiple projects open at the same time"].
2. Trong scene chính, mở công cụ **Scene Linking** từ menu Commands/Scene [K50 0:20 "In the recent Cascager update, the Scene Linking tool had been significantly"].
3. Chọn các file scene con cần đưa vào và thiết lập giá trị dịch khung hình **Frame Shift** để đồng bộ mốc thời gian [K50 0:31 "the frame shift. Now let's move the drummer to that place over there"].
4. Nhập toạ độ offset XYZ hoặc di chuyển vị trí nhân vật con trong không gian tổng [K50 0:35 "You can change its color, the position and rotation offset and"].
5. Lưới toạ độ (Grid) của từng scene con tự động xoay theo nhân vật, cho phép chỉnh sửa song song trong cùng một cửa sổ mà không làm hỏng toạ độ cục bộ [K50 0:49 "You can see how the grid is rotated which means you can"].

## Quy trình: Tải và Sử dụng File Âm thanh
1. Vào menu **File → Import → Audio** và chọn file âm thanh; file được tự thêm vào timeline [K62 0:14 "file import audio once uploaded it will automatically be added to the timeline"].
2. Rãnh âm thanh tự động xuất hiện trên thanh Timeline cùng dạng sóng trực quan [K62 0:14 "file import audio once uploaded it will automatically be added to the timeline"] [K62 0:30 "Cog icon in the top right corner of the timeline you can"].
3. Quản lý hoặc thay đổi file âm thanh thông qua bảng Outliner [K62 0:30 "you import can be accessed through outliner you can access some of"].
4. Bấm vào biểu tượng bánh răng **Cog icon** ở góc trên bên phải Timeline để tắt/bật tiếng trong lúc playback hoặc khi rê trượt timeline (Scrubbing) [K62 0:44 "Cog icon in the top right corner of the timeline you can"].

## Quy tắc chọn
- Khi làm việc với chi tiết phức tạp (như ngón tay, mắt) ⇒ Dùng `V` ẩn tạm thời các controller xung quanh hoặc dùng `Shift + V` để cô lập đối tượng cần làm việc [K25 3:57 "Shift plus S switches between Point Controller and Box Mode"].
- Muốn quan sát chuyển động từ nhiều góc đồng thời ⇒ Bấm `Shift + Space` (2 khung) hoặc `Shift + Alt + Space` (4 khung) [K25 2:09 "Press Shift and Space to divide the viewport into two"].
- Khi diễn hoạt vũ đạo hoặc cảnh hội thoại ⇒ Bắt buộc import file audio vào timeline trước khi đặt keyframe để căn theo nhịp [K62 0:14 "file import audio once uploaded it will automatically be added to the timeline"].
- Khi diễn hoạt cảnh nhiều nhân vật tương tác độc lập ⇒ Dùng Scene Linking thay vì gom chung vào một file nặng, giúp giảm giật lag và dễ quản lý [K50 0:13 "In the recent Cascager update, the Scene Linking tool had been significantly"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Viewport bị cắt vụn hoặc đối tượng bị khuất khi zoom gần | Góc nhìn camera (FOV) hoặc khoảng cách hiển thị bị sai lệch | Bấm `Alt + 0` để trả lại góc mở mặc định 30 độ [K25 3:57 "Set default field of view. The default value is 30 when pressing Alt plus 0"] | [K25 3:57 "Set default field of view. The default value is 30 when pressing Alt plus 0"] |
| Không bấm chọn được controller trên nhân vật | Selection Mask đang tắt loại đối tượng tương ứng | Bật lại icon Point Controller hoặc Box Controller trên thanh công cụ Selection Mask [K25 2:44 "The down arrow pointer allows us to add a camera into the scene"] | [K25 2:44 "The down arrow pointer allows us to add a camera into the scene"] |
| Âm thanh không phát khi bấm Play | Tùy chọn Mute đang bật trong cài đặt timeline | Bấm vào biểu tượng Cog trên Timeline và kiểm tra checkbox Audio playback [K62 0:44 "corner of the timeline you can disable audio during playback or when"] | [K62 0:44 "corner of the timeline you can disable audio during playback or when"] |
| Quên vị trí các đối tượng vừa bị ẩn | Không nhớ phím tắt hiện lại | Bấm `Alt + V` để hiện lại toàn bộ đối tượng đã ẩn trong scene [K25 4:12 "Alt plus V returns a display of everything previously hidden in the scene"] | [K25 4:12 "Alt plus V returns a display of everything previously hidden in the scene"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Xoay khung nhìn camera | Giữ `Alt` + chuột trái | Xoay quanh tâm điểm nhìn [K1 0:34 "Alt plus the left mouse key is rotation"] [K25 0:56 "The combination of Alt with a left mouse button performs rotation"] |
| Thu phóng camera | Giữ `Alt` + chuột phải | Phóng to thu nhỏ khung nhìn [K1 0:34 "Alt plus the right mouse key controls zooming"] [K25 0:56 "And with the right mouse button, you can zoom in and out"] |
| Trượt ngang camera (Pan) | Giữ `Alt` + chuột giữa | Dời mặt phẳng quan sát [K1 0:34 "Alt plus held down mouse wheel will move you around"] [K25 1:11 "And with a scroll wheel pressed, you can move the camera in space, normally in one plane"] |
| Căn tâm camera vào vật thể | `T` | Căn giữa khung hình vào đối tượng [K25 3:01 "pressing the hotkey T, performs centering on a particular active object in the scene"] |
| Chia 2 khung nhìn | `Shift + Space` | Chia đôi màn hình Viewport [K25 2:09 "Press Shift and Space to divide the viewport into two"] |
| Chia 4 khung nhìn | `Shift + Alt + Space` | 4 góc nhìn đồng thời [K25 2:09 "Or Shift, Alt and Space for four viewports, respectively"] |
| Ẩn đối tượng được chọn | `V` | Ẩn nhanh controller hoặc mesh [K25 3:57 "The V key hides the selected scene object"] |
| Ẩn mọi thứ trừ đối tượng chọn | `Shift + V` | Cô lập đối tượng quan sát [K25 3:57 "And Shift plus V hides everything except the selected scene object"] |
| Hiện lại toàn bộ đối tượng ẩn | `Alt + V` | Phục hồi hiển thị tất cả [K25 4:12 "Alt plus V returns a display of everything previously hidden in the scene"] |
| Chuyển Viewing / Editing mode | `S` | Chuyển đổi chế độ xem và sửa [K25 3:15 "The hotkey S activates switching between Viewing Mode and Editing Mode"] |
| Cố định đường quỹ đạo | `Y` | Hiển thị cố định trajectory [K25 4:12 "hotkey Y fixes the display of trajectories for all currently selected objects in the scene"] |
| Trả về FOV mặc định 30 độ | `Alt + 0` | Khôi phục trường nhìn chuẩn [K25 3:57 "The default value is 30 when pressing Alt plus 0"] |
| Nhập âm thanh | `File → Import → Audio` | Tự thêm vào timeline [K62 0:14 "file import audio once uploaded it will automatically be added to the timeline"] |
