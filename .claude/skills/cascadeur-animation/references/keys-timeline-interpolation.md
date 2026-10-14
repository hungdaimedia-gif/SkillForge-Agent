# Quản lý Keyframe, Timeline và Nội suy Chuyển động trong Cascadeur

Timeline trong Cascadeur đóng vai trò là trục xương sống của toàn bộ quy trình hoạt hình, hỗ trợ các chế độ nội suy cổ điển, công nghệ Inbetweening hiện đại, công cụ Easing đường cong và hệ thống Animation Layers mới được giới thiệu trong bản 2026.2. Tài liệu này hướng dẫn cách tổ chức rãnh (tracks), tinh chỉnh đường cong chuyển động (trajectories/tangents), và kết hợp linh hoạt giữa các phương pháp nội suy.

## Khái niệm cốt lõi
- **Key**: Khung hình lưu trữ dữ liệu vị trí của đối tượng [K18 0:48 "The key is the frame in which the position data of objects is stored"]; tạo hoặc xoá keyframe bằng phím `F` hoặc nút chìa khoá xanh trên thanh công cụ [K41 4:40 "going to show you how to create, delete, and edit the frames"].
- **Interpolation Frames**: Các khung hình trung gian nằm giữa hai keyframe, được phần mềm tính toán tự động dựa theo thuật toán nội suy đã chọn [K18 1:53 "Interpolation is a way of calculating the type of movement between the key frames"].
- **Interpolation Types**:
  - *Step*: Giữ nguyên vị trí và tư thế của keyframe trước trên toàn bộ khoảng thời gian cho đến khi gặp keyframe kế tiếp [K18 2:16 "When using the STEP interpolation in each frame of the interval between the key frames the position of the previous key will be preserved"].
  - *Linear*: Các đối tượng di chuyển theo các đường thẳng đều giữa hai keyframe [K18 2:25 "Also there are other interpolation types such as Linear"].
  - *Bezier & Bezier Clamped*: Đường cong chuyển động mượt mà có gia tốc tăng tốc và giảm tốc [K18 2:44 "Here you can see a smooth curved trajectory line with accelerations and decelerations"]; kiểu nội suy Bézier clamped là lựa chọn mềm hơn giúp triệt tiêu văng lố [K18 6:55 "clamped interpolation. It's a type of Bézier interpolation which I could characterize as a softer option"].
- **Inbetweening**: Phương thức nội suy thông minh sinh chuyển động chuyển tiếp giữa các keyframe theo thời gian thực [K16 0:17 "it can now update in real time and can be used with other interpolation methods"]; tốc độ chuyển động phụ thuộc trực tiếp vào khoảng cách thời gian (timing) giữa hai key [K31 2:24 "Timing refers to the time in between the keys in which the movement is happening"].
- **Easing**: Bộ công cụ kiểm soát gia tốc chuyển động trong bản 2026.2, cho phép nắn chỉnh khoảng cách giữa các khung hình (spacing) bằng tay cầm tangents [K82 0:14 "In the latest version, we've added a new tool called easing"] [K82 0:12 "In the latest version, we've added a new tool called easing"] [K83 0:53 "turn on easing, and by moving the black handles on the"].
- **Animation Layers**: Hệ thống lớp diễn hoạt trong bản 2026.2 cho phép thêm layer cộng dồn (Additive) tạo ra một timeline riêng biệt để chỉnh sửa hoạt cảnh phi phá huỷ mà không làm biến dạng dữ liệu gốc [K83 0:00 "In the second update of 2026, we finally introduced animation layers"] [K83 0:13 "In the second update of 2026, we finally introduced animation layers"].

## Quy trình: Tạo và Quản lý Keyframe trên Timeline
1. Di chuyển con trỏ thời gian đến khung hình mong muốn và tạo keyframe bằng phím `F` [K41 4:40 "To create the key frames, you can either press the blue key button or press F on your keyboard"].
2. Chỉnh sửa tư thế nhân vật, sau đó bấm phím `F` (hoặc bấm nút chìa khoá xanh) để tạo keyframe; bấm `F` lần nữa tại keyframe đó để xoá keyframe [K41 4:40 "going to show you how to create, delete, and edit the frames"].
3. Để biến toàn bộ các khung hình trong khoảng thời gian đã chọn thành keyframe, bấm tổ hợp phím `Alt + F` [K41 5:46 "When dealing with key frame groups, you can drag them or copy"].
4. Di chuyển keyframe bằng cách lăn chuột giữa trên timeline; sao chép keyframe bằng cách giữ `Shift` và lăn chuột giữa [K41 4:53 "To move the key frames within the timeline, use the scroll button on your mouse"] [K41 4:53 "You can copy the key frames if you do the same thing while also pressing shift"].
5. Thêm khung hình trung gian bằng phím `+` hoặc xoá bớt khung hình bằng phím `-` trên bàn phím [K41 5:05 "Another option for moving the key frames would be pressing shift and"] [K36 4:13 "For instance, these moments can benefit from being re-timed"].
6. Mở rộng vùng chọn khung hình bằng cách giữ phím `Control` và bấm phím mũi tên trái hoặc phải [K41 5:20 "Press control and either the right or the left arrow on your keyboard to add"].

## Quy trình: Sử dụng Inbetweening kết hợp Nội suy
1. Tạo hai dáng chính (Key A và Key B) cách nhau một khoảng khung hình [K41 4:40 "To create the key frames, you can either press the blue key button or press F on your keyboard"].
2. Chọn khoảng khung hình giữa hai key và chuyển kiểu nội suy sang **Inbetweening** [K16 2:40 "Now, for the rest of the body tracks I want to use inbetweening"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
3. Điều chỉnh khoảng cách thời gian (Timing): khoảng cách càng nhiều khung hình thì chuyển động càng chậm; thu ngắn khoảng cách khung hình thì nhân vật di chuyển càng nhanh [K31 2:24 "Timing refers to the time in between the keys in which the movement is happening"] [K31 2:39 "Timing refers to the time in between the keys in which the movement is happening"].
4. Bổ sung thêm các keyframe trung gian ngay trong dải Inbetweening để nắn lại các tư thế mong muốn (ví dụ: tránh bàn tay đâm xuyên mặt bàn) [K16 4:22 "we can create additional key frames within inbetweening interpolation to specify certain"] [K31 2:06 "If I want to have a more uninterrupted walk, I'll have to edit the keyframe in the middle"].
5. Có thể kết hợp song song Inbetweening cho một số track cơ thể và nội suy FK/Bezier cho các track khác (như đầu hoặc cánh tay) [K16 2:39 "Now, for the rest of the body tracks I want to use inbetweening"].

## Quy trình: Điều chỉnh Quỹ đạo (Trajectories) và Tiếp tuyến (Tangents)
1. Chọn một điểm điều khiển quan trọng (như đầu bàn tay, bàn chân hoặc chóp đuôi) [K27 0:14 "Let's say I want to see a trajectory of the tail's end"].
2. Bật chế độ hiển thị quỹ đạo chuyển động trong 3D Viewport [K27 0:42 "This immediately shows the trajectory of the selected point in the viewport"].
3. Xem đường cong không gian nối giữa các keyframe; tại mỗi điểm mốc trên đường cong xuất hiện các tay đòn tiếp tuyến (Tangents) [K27 4:33 "Here you can see small controllers around the key points of the trajectory. These are your tangent handles"].
4. Bấm chọn đầu tay đòn và kéo xoay hoặc kéo dài để nắn lại độ cong và quỹ đạo chuyển động; có thể huỷ chỉnh sửa để quay về tiếp tuyến gốc [K27 5:21 "If you would like to cancel your edits and get back to the original tangents, use this button"].
5. Mặc định các tay đòn tiếp tuyến cùng tác động đồng thời; có thể tắt chức năng này để điều chỉnh từng tiếp tuyến độc lập khi đổi hướng đột ngột [K27 5:34 "By default, tangent handles act together"].

## Quy trình: Sử dụng Easing và Animation Layers (Cascadeur 2026.2)
1. **Áp dụng Easing**: Chọn khoảng khung hình giữa hai key, bật tính năng Easing và di chuyển các tay nắm màu đen trên timeline để thay đổi khoảng cách bước chuyển động [K82 0:12 "In the latest version, we've added a new tool called easing"] [K83 0:53 "Then we can turn on easing, and by moving the black handles on the"].
2. **Tạo Animation Layer**: Trên bảng quản lý layer, bấm **Add Layer** để tạo rãnh additive layer mới [K83 0:13 "You can now create additive layers and make non-destructive changes to your animation"].
3. Đặt keyframe trên timeline riêng của layer mới để thêm cử động phụ chồng lên hoạt cảnh nền [K83 0:13 "separate timeline where you can add keyframes, make changes in them, and choose between different interpolation types"] [K83 0:25 "You can turn each layer on and off, and when you're happy"].
4. Chuyển đổi linh hoạt giữa IK, FK và nội suy toàn cục trên layer mới, hoặc bật/tắt từng layer độc lập [K83 0:26 "You can turn each layer on and off, and when you're happy"].
5. Khi hoàn thiện, có thể gộp (merge) các layer lại với nhau thành một hoạt cảnh thống nhất [K83 0:26 "You can turn each layer on and off, and when you're happy"].

## Quy tắc chọn
- Cần giữ nguyên tư thế của keyframe trước cho đến keyframe tiếp theo ⇒ Dùng nội suy **Step** [K18 2:16 "When using the STEP interpolation in each frame of the interval between the key frames the position of the previous key will be preserved"].
- Diễn hoạt vòng lặp hoặc chuyển động mềm hơn cần triệt tiêu quán tính văng lố ⇒ Dùng kiểu nội suy **Bézier clamped** [K18 6:55 "clamped interpolation. It's a type of Bézier interpolation which I could characterize as a softer option"].
- Cần sinh chuyển động chuyển tiếp tự nhiên giữa hai dáng chính có thể cập nhật thời gian thực ⇒ Dùng **Inbetweening** [K31 0:00 "the in-betweening generates animations, and what's important for us animators is to have enough control over the animation"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
- Cần chỉnh sửa thêm chuyển động phụ hoặc dọn dẹp mocap mà không muốn làm hỏng track gốc ⇒ Dùng **Animation Layers** (Additive) [K83 0:13 "You can now create additive layers and make non-destructive changes to your animation"] [K83 0:40 "You can now create additive layers and make non-destructive changes to your animation"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Chân tay bị văng quá đà giữa hai keyframe | Tiếp tuyến Bezier tự do bị kéo quá dài gây văng lố | Chuyển sang Bezier Clamped là lựa chọn mềm hơn [K18 6:55 "clamped interpolation. It's a type of Bézier interpolation which I could characterize as a softer option"] | [K18 6:55 "clamped interpolation. It's a type of Bézier interpolation which I could characterize as a softer option"] |
| Đổi dáng ở key này làm sai lệch toàn bộ dáng sau | Các controller bị thiếu keyframe lưu vị trí ở các khung hình lân cận | Đặt keyframe bổ sung bằng phím `F` trước khi sửa tư thế [K18 0:48 "The key is the frame in which the position data of objects is stored"] [K41 4:40 "To create the key frames, you can either press the blue key button or press F on your keyboard"] | [K41 4:40 "To create the key frames, you can either press the blue key button or press F on your keyboard"] |
| Chuyển động bị giật cục khi đổi hướng | Tay đòn Tangent bị gãy góc không mượt | Chỉnh lại các tay đòn tiếp tuyến trên đường quỹ đạo [K27 5:34 "By default, tangent handles act together"] | [K27 5:34 "By default, tangent handles act together"] |
| Nhân vật di chuyển quá nhanh hoặc quá chậm khi dùng Inbetweening | Khoảng cách khung hình (Timing) giữa hai key chưa phù hợp | Thêm khung hình bằng phím `+` để làm chậm, hoặc bấm `-` để tăng tốc [K31 2:39 "Timing refers to the time in between the keys in which the movement is happening"] [K41 5:05 "You can add frames in between the key frames by pressing plus or delete them by pressing minus"] | [K31 2:39 "Timing refers to the time in between the keys in which the movement is happening"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Tạo hoặc xoá keyframe | `F` (hoặc nút chìa khoá xanh) | Đặt hoặc gỡ keyframe tại con trỏ [K41 4:40 "To create the key frames, you can either press the blue key button or press F on your keyboard"] |
| Biến toàn bộ khoảng thành keyframe | `Alt + F` | Đặt key cho toàn bộ interval [K41 5:46 "If you want all the frames on the selected interval to be key frames, press Alt + F"] |
| Thêm / bớt khung hình | `+` / `-` | Tăng giảm khoảng cách timing [K41 5:05 "You can add frames in between the key frames by pressing plus or delete them by pressing minus"] [K36 4:13 "For instance, these moments can benefit from being re-timed"] |
| Sao chép keyframe | Giữ `Shift` và cuộn nút chuột | Copy keyframe trên timeline [K41 4:53 "You can copy the key frames if you do the same thing while also pressing shift"] |
| Mở rộng vùng chọn khung hình | Giữ phím `Control` và mũi tên trái / phải | Mở rộng interval chọn [K41 5:20 "can select an interval by left clicking on your mouse and dragging"] |
| Chuyển nội suy Step | Menu Interpolation → Step | Giữ nguyên tư thế của key trước [K18 2:16 "When using the STEP interpolation in each"] |
| Chuyển nội suy Bezier | Menu Interpolation → Bezier | Nội suy đường cong mượt [K18 2:41 "A few more details for the Bézier type of interpolation"] |
| Thêm Animation Layer | Bảng Layers → Add Layer | Diễn hoạt phi phá huỷ (2026.2) [K83 0:13 "In the second update of 2026, we finally introduced animation layers"] |
