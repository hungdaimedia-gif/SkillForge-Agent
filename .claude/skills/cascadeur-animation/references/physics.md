# Hệ thống Vật lý Tự động (AutoPhysics) và Mô phỏng trong Cascadeur

AutoPhysics là công nghệ đột phá cốt lõi của Cascadeur, phân tích chuyển động của nhân vật dựa trên các định luật vật lý cơ bản: điểm tựa (Fulcrum), quỹ đạo rơi tự do (Ballistics), bảo toàn mô-men động lượng (Angular Momentum) và vị trí khối tâm (Center of Mass). Tài liệu này hướng dẫn chi tiết quy trình ứng dụng AutoPhysics, tinh chỉnh thanh trượt lực, tách chuyển động, xử lý va chạm ragdoll và diễn hoạt tương tác va chạm giữa hai nhân vật.

## Khái niệm cốt lõi
- **AutoPhysics**: Công cụ tính toán chuyển động vật lý tự động, tạo ra một "bóng ma" màu xanh lá (Green ghost) mô phỏng chính xác đường bay và chuyển động quay thực tế của nhân vật [K2 14:44 "The fulcrum points are highlighted in a green circle"] [K67 0:13 "each of them does let's take this animation as an example so"].
- **Fulcrum Points (Điểm tựa)**: Các điểm tiếp xúc giữa nhân vật và môi trường (mặt đất, tường, chướng ngại vật) truyền tải phản lực lên cơ thể; nếu điểm tựa xác định sai, nhân vật sẽ bị trượt chân hoặc bay bổng thiếu thực tế [K3 0:00 "Hello everyone, Falkron points are an essential part of the physics character"] [K66 0:17 "move too much, they were considered to be fulcrum"].
- **Center of Mass**: Điểm trung tâm phân bố trọng lượng cơ thể, quyết định quỹ đạo parabol đạn đạo khi nhân vật nhảy trên không [K2 16:10 "In the frames without fulcrum points, the main physics filter creates a ballistic curve for center of mass"] [K3 2:47 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"].
- **Angular Momentum**: Định luật bảo toàn độ xoay của cơ thể; khi nhân vật co tay chân lại, tốc độ xoay tăng lên và ngược lại [K49 0:14 "So what we can see is that to preserve the angular momentum"].
- **Secondary Motion**: Chuyển động phụ quán tính mô phỏng độ nảy, rung giật tự nhiên của tóc, đuôi, giáp và da thịt sau mỗi cú tiếp đất hoặc đổi hướng [K48 0:00 "the secondary motion tool is my favorite all of the Auto physics"] [K67 2:38 "compensate and finally let's enable secondary motion the higher the value ears"].
- **Separation of Motion**: Bộ lọc vật lý nâng cao tách biệt thành phần tịnh tiến và thành phần xoay góc của AutoPhysics để tránh hiện tượng nhân vật bị xoay vặn quá mức khi lộn nhào [K49 0:00 "Hi there, in the new update we added a new physics filter which is called separation of motion"] [K2 22:09 "Separation motion filter can look similar to the smooth rotation filter"].
- **Ragdoll & Colliders**: Hệ thống khung xương vật lý thụ động kết hợp các hình khối va chạm (Kinematic / Convex Mesh) để mô phỏng ngã gục, va đập chướng ngại vật hoặc đu xà [K28 0:36 "Select your object, go to commands, collision, add kinematic mesh"] [K29 1:27 "and now we can proceed to setting up the ragdoll"] [K42 1:00 "I want the second character to be in the Ragdoll"] [K52 0:12 "autophysics feature that helps you animate characters hanging down from various objects"].

## Quy trình: Áp dụng AutoPhysics cho Cảnh Hành động (Parkour / Nhảy)
1. Hoàn thiện chuyển động thô (Blocking) bằng cách chọn các dáng chuyển động chính [K2 1:16 "I'm starting with blocking. Blocking is a step when we select the key movement poses"] [K2 8:49 "Here is the final result of the blocking process"].
2. Bật công cụ **AutoPhysics** (physical assistant) trên thanh công cụ chính để hiện bóng ma vật lý [K2 14:48 "I'm turning on the physical assistant display button"] [K30 16:42 "you want to copy what you see from the green physics projection, you can click here to snap to autophysics"].
3. Kiểm tra các mốc **Fulcrum Points** trên bàn chân: đảm bảo các khung hình chân chạm đất được nhận diện chính xác là điểm tựa cố định [K3 1:35 "As you can see, the green outline around the points has disappeared"] [K3 4:54 "Setting it to N4s will mean that the points will be considered"].
4. Bật **Snap the animation** để áp dụng dữ liệu chuyển động vật lý vào hoạt cảnh trước khi chuyển sang bộ lọc tiếp theo [K2 24:38 "snap the animation. Once you've snapped the animation, the next filter will be taking these changes into account"].
5. Tinh chỉnh các thanh trượt sửa sai (Physics Correctors) để cân bằng giữa ý đồ nghệ thuật và tính chân thực vật lý [K2 15:55 "In the frames without fulcrum points, the main physics filter creates a"] [K67 0:13 "this animation as an example so first let's turn on autop physics"].

## Quy trình: Tinh chỉnh Bộ thanh trượt AutoPhysics Sliders
1. Mở bảng điều khiển **AutoPhysics Sliders** (quy trình đơn giản hóa với 4 thanh trượt chính) [K67 0:13 "you can now control AO physics parameters with only four sliders here"]:
2. **Smooth trajectory**: Làm mịn đường parabol của trọng tâm khi bay trên không, loại bỏ các điểm gãy quỹ đạo do đặt keyframe lỗi [K67 0:35 "trajectory lower values make less changes to the initial animation the higher"] [K2 19:44 "The next filter is called smooth trajectory"].
3. **Smooth rotation**: Làm mượt chuyển động xoay quanh khối tâm, hạn chế giật lắc góc đầu và thân [K67 1:12 "sharply and then stops rather abruptly with smooth rotation appli the character"] [K2 20:20 "This filter is going to help you smooth out all the rotating movements"].
4. **Compensation motion**: Thanh trượt bù trừ chuyển động giúp cơ thể tự động hạ thấp trọng tâm khi tiếp đất để hấp thụ xung lực [K67 1:42 "compensation motion it also helps to smooth the trajectory of the center"] [K2 21:15 "The next filter is called compensation motion"].
5. **Secondary motion settings**: Tinh chỉnh biên độ nảy (stiffness) và lực cản (damping) cho các chuyển động phụ thứ cấp [K67 2:38 "compensate and finally let's enable secondary motion the higher the value ears"] [K48 0:12 "the secondary motion tool is my favorite all of the Auto physics"].

## Quy trình: Thiết lập Va chạm và Tương tác Ragdoll
1. Mở cảnh nhân vật, bật AutoPhysics và kích hoạt **Ragdoll** [K29 1:19 "and now we can proceed to setting up the ragdoll"].
2. Thiết lập trạng thái khung hình thứ hai (Frame 2) để xác định vận tốc ban đầu cho mô phỏng ragdoll [K29 1:54 "So basically the first two frames are super important for ragdoll, because"].
3. Tạo khối va chạm bao quanh các bộ phận: chọn giữa **Kinematic Mesh Colliders** (cho đối tượng chuyển động theo key) và **Convex Mesh Colliders** (cho mô phỏng vật lý va đập môi trường) [K28 0:36 "Select your object, go to commands, collision, add kinematic mesh"] [K28 2:03 "Select your object, go to commands, collision, generate convex mesh"].
4. Thiết lập độ cứng khớp toàn cục (**Global Stiffness**) để nhân vật không bị mềm nhũn như búp bê vải khi va chạm [K29 8:32 "to global stiffness, right, it does the same thing"].
5. Sử dụng tính năng **Pin Collision** để cố định bàn tay vào thanh xà khi thực hiện động tác đu quay người [K52 1:52 "in the collision material, we have to change the collision type from surface to pin"].

## Quy trình: Tương tác Va chạm Hai Nhân vật (Contact Pair Animation)
1. Đưa hai nhân vật vào cùng một scene (hoặc liên kết thông qua Scene Linking) [K51 0:17 "Let's use this animation with two characters and turn the Art of Physics on"].
2. Bật AutoPhysics; lúc này hệ thống sẽ hiển thị vùng tương tác tiếp xúc chung giữa hai cơ thể [K51 0:47 "When we have a single character, the Art of Physics will rely on their center of mass"].
3. Thiết lập các điểm tiếp xúc xác định bởi các collider đặc biệt trong chế độ chỉnh sửa rig [K51 1:25 "Art of Physics works with a point of contact"].
4. Bán kính va chạm (Collision radius) là khoảng cách điểm cần đạt tới collider để được tính là điểm tiếp xúc (point of contact) [K51 2:05 "Collision radius is the distance between the point and the collider that the point needs"].
5. Kết hợp ràng buộc vũ khí (Constraints with AutoPhysics trong 2026.1) để giữ chắc vũ khí khi bị đối phương gạt đòn [K84 0:00 "quickly generate decent animation for a character with a double-handed weapon"] [K84 2:25 "auto physics now recognizes constraints, which is huge, especially when animating double-handed weapons"].

## Quy tắc chọn
- Khi nhân vật nhảy trên không ⇒ Kích hoạt AutoPhysics để xây dựng quỹ đạo đạn đạo cho khối tâm [K3 2:47 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"].
- Khi nhân vật lộn nhào mà thân trên bị xoay lệch bất thường ⇒ Bật bộ lọc **Separation of Motion** để giữ hướng xoay độc lập với hướng tịnh tiến [K49 0:00 "Hi there, in the new update we added a new physics filter which is called separation of motion"] [K2 22:09 "Separation motion filter can look similar to the smooth rotation filter"].
- Mô phỏng nhân vật ngã hoặc va chạm với vật thể ⇒ Kết hợp Ragdoll và điều chỉnh tư thế keyframe để định hướng hoạt cảnh ngã theo ý muốn [K29 4:35 "For the more advanced approach, we'll set the ragdoll slider to a hundred"] [K46 1:28 "The poses however do affect the ragdoll, and by changing the poses you can change the ragdoll animation as well"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Nhân vật bị trượt chân trên sàn khi bật AutoPhysics | Điểm tựa Fulcrum không được nhận diện đúng khung hình | Vào Fulcrum settings mở rộng vùng nhận diện hoặc gán thủ công [K3 1:35 "Now I'm going to go to frame 10 and raise one of the character's feet"] [K3 3:04 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"] | [K3 3:04 "autophysics treats such intervals as jumps and builds a ballistic trajectory for the character's center of mass"] |
| Nhân vật nhảy có quỹ đạo đạn đạo chưa chuẩn | Khối tâm trên các khung hình không có điểm tựa chưa chuẩn | Kiểm tra lại quỹ đạo đạn đạo của khối tâm trên các khung hình không có điểm tựa [K2 16:10 "In the frames without fulcrum points, the main physics filter creates a ballistic curve for center of mass"] [K35 0:00 "One of them is setting the weight of each rigid body and it's quite difficult to find"] | [K2 16:10 "In the frames without fulcrum points, the main physics filter creates a ballistic curve for center of mass"] |
| Cơ thể bị nảy giật quá mức sau khi snap | Thanh trượt Secondary Motion đặt biên độ quá lớn | Giảm Secondary Motion Slider và tăng Damping [K48 0:12 "the secondary motion tool is my favorite all of the Auto physics"] [K67 2:38 "compensate and finally let's enable secondary motion the higher the value ears"] | [K67 2:38 "compensate and finally let's enable secondary motion the higher the value ears"] |
| Vũ khí bị rời khỏi tay khi AutoPhysics giải nghiệm | Chưa gán Constraint ràng buộc vũ khí với AutoPhysics | Sử dụng Constraints with AutoPhysics (bản 2026.1 trở lên) [K84 0:00 "quickly generate decent animation for a character with a double-handed weapon"] [K84 2:25 "auto physics now recognizes constraints, which is huge, especially when animating double-handed weapons"] | [K84 2:25 "auto physics now recognizes constraints, which is huge, especially when animating double-handed weapons"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Bật/Tắt AutoPhysics | Icon AutoPhysics trên thanh công cụ | Bật tính toán vật lý cho hoạt cảnh [K3 0:44 "Now let's turn on autophysics. As you can see"] |
| Snap chuyển động vật lý | Nút Snap Animation | Áp dữ liệu vật lý vào keyframe [K2 23:49 "Now, I'm going to apply them to my animation"] |
| Mở Fulcrum Settings | Object Properties → Fulcrum tab | Chỉnh khoảng cách tiếp xúc mặt đất [K3 3:00 "select the points of the feet and open up the Falkron tab in the object properties"] [K3 3:16 "collision radius is the max distance from the surface within which the point is considered as Falkron"] |
| Mở AutoPhysics Sliders | Bảng Physics Sliders | 4 thanh trượt tinh chỉnh nhanh [K67 0:13 "you can now control AO physics parameters with only four sliders here"] |
| Điểm tiếp xúc 2 nhân vật | Collider tiếp xúc | Tính toán va chạm tương tác [K51 1:25 "Art of Physics works with a point of contact"] |
| Tạo khối va chạm lồi | Physics → Create Convex Collider | Phục vụ va chạm môi trường [K28 2:03 "Select your object, go to commands, collision, generate convex mesh"] |
