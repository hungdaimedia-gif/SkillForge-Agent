# Bộ Công cụ Trí tuệ Nhân tạo và Sinh Diễn hoạt trong Cascadeur

Cascadeur tích hợp các công cụ hỗ trợ AI và thuật toán sinh chuyển động tự động, bao gồm công cụ tạo chu kỳ di chuyển lặp (Animation Cycles), mô hình khuếch tán sinh hoạt cảnh sáng tạo Root Motion, kỹ thuật sinh diễn hoạt từ các tư thế chính bằng Inbetweening, và nhân vật mẫu OpenPose phục vụ cho quy trình AI tạo sinh (ControlNet / ComfyUI).

## Khái niệm cốt lõi
- **Generate Animation Cycles**: Công cụ tạo vòng lặp chuyển động tuần hoàn (chu kỳ bước đi, chạy) từ các đoạn diễn hoạt được tạo bằng hệ thống Inbetweening [K6 0:00 "you can create animation cycles from the animation you can generate using"].
- **Mô hình Root Motion**: Mô hình sinh chuyển động dạng khuếch tán (diffusion model) tạo ra diễn hoạt sáng tạo giữa các keyframe; mỗi lần chạy sinh ra một kết quả khác nhau và có thể tự động tạo cử động nghỉ (idle animation) ngay cả giữa hai tư thế tương đồng [K9 0:00 "to show you how Root Motion, a new animation generation model, works"] [K9 0:13 "to show you how Root Motion, a new animation generation model, works"].
- **Inbetweening**: Phương pháp đặt các tư thế then chốt ở đầu và cuối khoảng thời gian, sau đó sử dụng nội suy inbetweening để hệ thống tự động tính toán cử động chuyển tiếp theo thời gian thực [K85 0:54 "So in this example here, we have an action pose in the start and then some idle"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
- **Nhân vật mẫu OpenPose**: Nhân vật khung xương que (Stickman) có sẵn trong mục Sample Scenes của Cascadeur với bảng màu chuẩn OpenPose, được rig sẵn để người dùng tạo dáng, diễn hoạt và xuất video đưa vào ControlNet / Stable Diffusion / ComfyUI [K86 0:00 "to create generative animations and stable diffusion add-on models such as control"] [K86 0:27 "You can find the open pose preset in our sample scenes"].

## Quy trình: Tạo Chu kỳ Hoạt cảnh (Animation Cycles)
1. Xây dựng một đoạn diễn hoạt bước chân bằng hệ thống Inbetweening của Cascadeur [K6 0:00 "the animation you can generate using Cascadeur in-betweening system"].
2. Chọn khoảng khung hình chứa chu kỳ bước chân trên timeline [K6 0:15 "we'll set up two key frames and then use AI interpolation to generate the motion between them"].
3. Sử dụng tính năng Cycles để tự động biến đoạn bước chân thành một chu kỳ lặp mượt mà [K6 0:00 "Today we're going to learn how you can create animation cycles from"] [K6 1:00 "Now, let's find two similar frames within this interval that going to be"].

## Quy trình: Sinh Hoạt cảnh Sáng tạo bằng Mô hình Root Motion
1. Thiết lập các keyframe với tư thế ban đầu và tư thế kết thúc trên timeline [K9 0:00 "Root Motion, a new animation generation model, works in Cascadeur. Same as In-betweening, it generates animations between the key frames"].
2. Chọn khoảng khung hình và kích hoạt mô hình sinh **Root Motion** dựa trên diffusion để sinh các biến thể chuyển động khác nhau [K9 0:13 "However, unlike In-betweening, it's a diffusion model, and it will generate a different animation every time you use it"].
3. Xem xét kết quả được nướng (baked) vào khung hình; nếu muốn thử nghiệm biến thể khác, hoàn tác (Undo) và cho mô hình sinh lại [K9 0:51 "in the key frames, it's a good idea to undo before generating"] [K9 1:04 "in the key frames, it's a good idea to undo before generating"].
4. Do mô hình khuếch tán không tính toán vật lý chuẩn xác tuyệt đối, khuyến nghị chạy thêm một lượt **auto physics** để nắn lại đường đạn đạo CoM, thêm quán tính và làm mượt quỹ đạo khối tâm [K9 0:39 "highly advise to do an auto physics pass on them"].

## Quy trình: Tạo Hoạt cảnh Tự động từ các Dáng Then chốt (Inbetweening)
1. Đặt tư thế hành động ban đầu ở keyframe thứ nhất bằng AutoPosing [K85 0:41 "Using auto posing will help you create natural poses in no time"] [K85 0:54 "The generated animation will heavily depend on the poses that you set"].
2. Đặt tư thế kết thúc (hoặc tư thế nghỉ) ở keyframe tiếp theo [K85 0:54 "The generated animation will heavily depend on the poses that you set"] [K85 1:08 "pose at the end which will tell in betweening that we want"].
3. Áp dụng kiểu nội suy **Inbetweening** cho khoảng giữa hai keyframe để phần mềm tự động tính toán chuyển động liên tục cập nhật theo thời gian thực [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
4. Bổ sung thêm các keyframe trung gian hoặc điều chỉnh khoảng cách thời gian nếu cần nắn chỉnh nhịp điệu [K85 1:38 "you can add and remove key frames, change the timing, poses, and"] [K85 2:11 "Use autophysics to make it better fit the character that you have"].
5. Bật AutoPhysics để bổ sung chuyển động phụ (secondary motion) và gia cố quán tính chân thực [K85 2:11 "Use autophysics to make it better fit the character that you have. Add secondary motion and so on"].

## Quy trình: Diễn hoạt Nhân vật OpenPose cho Generative AI
1. Mở cảnh mẫu nhân vật OpenPose Stickman có sẵn trong thư mục Sample Scenes [K86 0:27 "You can find the open pose preset in our sample scenes"].
2. Sử dụng AutoPosing tạo dáng hoặc nạp mocap từ Mixamo qua `Edit → Retargeting → Copy/Paste` [K86 1:42 "timeline, go to edit, retargeting, copy. And in the other scene, make sure you select enough frames on the timeline. Go to edit, retarget"].
3. Ẩn lưới hiển thị (Mesh) và ẩn sàn lưới (Grid) trước khi kết xuất để khung hình chỉ chứa khung xương màu OpenPose [K86 1:54 "Now, before we render the video, make sure you hide the grip first here or in the settings window"].
4. Xuất video hoạt cảnh qua menu **File → Export → Export Video** và nạp vào ComfyUI để sinh nhân vật bám sát tư thế [K86 2:09 "Go to file, export, export video. Once the file is ready, start config UI and upload it into your build"].
5. Nạp file video vào ComfyUI để tạo hình nhân vật bám theo các tư thế trong animation [K86 2:15 "Once the file is ready, start config UI and upload it into your build"].

## Quy tắc chọn
- Cần tạo vòng lặp chạy/bước đi đồng đều ⇒ Sử dụng công cụ Cycles từ chuyển động inbetweening [K6 0:00 "Today we're going to learn how you can create animation cycles from"].
- Cần ý tưởng động tác mới lạ, động tác nghỉ ngẫu nhiên từ hai dáng tĩnh ⇒ Dùng mô hình Root Motion rồi chạy tiếp AutoPhysics [K9 0:26 "Overall, this tool allows you to get more variations and more creative results"] [K9 0:39 "auto physics fixed the ballistic trajectory, added inertia, and overall smoothed the trajectory of the center of mass"].
- Muốn kiểm soát chính xác nhịp điệu và quỹ đạo có thể chỉnh sửa thời gian thực ⇒ Dùng Inbetweening giữa các keyframe [K9 0:51 "Okay, so let's quickly compare it to In-betweening"] [K9 1:20 "Root Motion does not update results in real time"] [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"].
- Muốn tạo dữ liệu hướng dẫn dáng cho Stable Diffusion / ControlNet ⇒ Sử dụng cảnh mẫu OpenPose Stickman và xuất video [K86 0:00 "to create generative animations and stable diffusion add-on models such as control"] [K86 0:27 "to create generative animations and stable diffusion add-on models such as control"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Kết quả sinh từ mô hình Root Motion bị thiếu chính xác vật lý | Mô hình khuếch tán chú trọng tính sáng tạo hơn độ chuẩn xác cơ học | Chạy thêm một lượt AutoPhysics để sửa quỹ đạo và bổ sung quán tính [K9 0:30 "However, the results you will get will not be physically accurate. So, we highly advise to do an auto physics pass on them"] [K9 0:39 "auto physics fixed the ballistic trajectory, added inertia, and overall smoothed the trajectory of the center of mass"] | [K9 0:30 "However, the results you will get will not be physically accurate. So, we highly advise to do an auto physics pass on them"] [K9 0:39 "auto physics fixed the ballistic trajectory, added inertia, and overall smoothed the trajectory of the center of mass"] |
| Inbetweening không sinh ra cử động giữa hai dáng | Hai keyframe có tư thế quá giống nhau khiến nội suy không có khoảng trượt | Dùng mô hình Root Motion để sinh cử động nghỉ (idle) tự nhiên [K9 1:47 "Also, unlike In-betweening, Root Motion can generate idle animations"] | [K9 1:47 "Also, unlike In-betweening, Root Motion can generate idle animations"] |
| Khung que OpenPose bị lẫn lưới sàn khi xuất video | Chưa ẩn đường lưới sàn trong Viewport | Ẩn lưới trước khi kết xuất video [K86 1:55 "Now, before we render the video, make sure you hide the grip first here or in the settings window"] | [K86 1:55 "Now, before we render the video, make sure you hide the grip first here or in the settings window"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Sinh chu kỳ chuyển động | Menu Animation Cycles | Tạo vòng lặp bước đi từ inbetweening [K6 0:00 "Today we're going to learn how you can create animation cycles from"] |
| Sinh hoạt cảnh bằng diffusion | Mô hình Root Motion | Sinh biến thể sáng tạo và động tác idle [K9 0:13 "unlike In-betweening, it's a diffusion model, and it will generate a different animation every time you use it"] [K9 1:47 "Also, unlike In-betweening, Root Motion can generate idle animations"] |
| Nội suy giữa hai dáng | Interpolation → Inbetweening | Sinh chuyển động trung gian thời gian thực [K85 1:23 "set, we're going to use inbetweening as a type of interpolation between the two key frames"] [K86 0:57 "To quickly create animation, you can use our inbetweening feature which generates animation between the key frames"] |
| Xuất video OpenPose | `File → Export → Export Video` | Xuất video đưa vào ControlNet / ComfyUI [K86 2:09 "Go to file, export, export video. Once the file is ready, start config UI and upload it into your build"] |
| Sao chép Retargeting | `Edit → Retargeting → Copy / Paste` | Chuyển hoạt cảnh sang nhân vật OpenPose [K86 1:42 "timeline, go to edit, retargeting, copy. And in the other scene, make sure you select enough frames"] |
