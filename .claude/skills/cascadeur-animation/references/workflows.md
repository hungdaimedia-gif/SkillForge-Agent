# Quy trình Hoạt hình Mẫu từ Đầu đến Cuối (Workflows) trong Cascadeur

Tài liệu này tổng hợp các quy trình làm việc mẫu (production pipelines) hoàn chỉnh từ khâu ý tưởng đến khi xuất file thành phẩm, được đúc kết từ các dự án thực tế, timelapse của chuyên gia và các buổi góp ý (critique) chuyên môn từ animator kỳ cựu của studio game Banzai.Games [K2 0:00 "For this, I'll be using a parkour reference from Nick Pro"] [K40 0:00 "is difficult enough to make your character walk naturally, let alone make it reflect their personality"] [K74 0:32 "here's the reference and our first pose"] [K93 0:00 "hey everyone so today we have this animation here by"]. Bao gồm quy trình tạo chu kỳ bước đi (Walk Cycle), diễn hoạt cảnh chiến đấu/parkour từ video tham chiếu, hoạt cảnh vũ khí hai tay và ném vũ khí, hoạt cảnh tương tác 2 nhân vật và hoạt cảnh hoạt hình hoạt hoạ cách điệu [K24 0:00 "we're going to be animating this fighting sequence here"] [K59 0:00 "In this video, I'm going to show a couple of life hacks"] [K81 0:00 "In this video, I'll walk you step by step through character and"] [K90 0:00 "As a reference, I'm going to be using this video here"].

## Khái niệm cốt lõi
- **Animation Pipeline**: Chuỗi các giai đoạn kế tiếp nhau trong sản xuất hoạt cảnh: Dựng ý tưởng/Video tham chiếu → Chặn dáng chính (Blocking) → Nội suy trung gian (Inbetweening) → Gia cố Vật lý (AutoPhysics) → Tinh chỉnh chi tiết (Polishing) → Xuất dữ liệu [K2 1:06 "video or in-betweening, in this tutorial, I'll do most of the animation"] [K81 0:09 "step by step through character and weapon preparation, scene blocking, inbetweening, and"].
- **Walk Cycle Poses** (kiến thức hoạt hình chung, không từ nguồn): Bốn tư thế cơ bản cấu thành một chu kỳ bước đi hoàn chỉnh:
  1. *Contact Pose*: Hai chân tiếp xúc sàn ở khoảng cách xa nhất, gót chân trước chạm sàn, mũi chân sau chuẩn bị nhấc.
  2. *Down Pose*: Trọng tâm hạ thấp nhất, bàn chân trước tiếp đất hoàn toàn để hấp thụ lực va chạm.
  3. *Passing Pose*: Một chân thẳng đứng làm trụ nâng đỡ toàn bộ cơ thể, chân kia gập cong nhấc qua chân trụ.
  4. *Up Pose*: Cơ thể nhổm cao nhất, chân sau đẩy mạnh chuẩn bị bước tới.
- Nạp video tham chiếu (Reference): Kỹ thuật nhập video tham chiếu đời thực vào khung nhìn nền của Viewport để khớp góc camera, nhịp điệu và tư thế then chốt [K2 1:14 "This way I can see both the reference and my character"] [K32 0:40 "Hi there, in this time lapse we're going to use a video reference to create this animation here"].
- Ném và bắt vũ khí: Kỹ thuật chuyển đổi vũ khí từ trạng thái gắn vào tay sang quỹ đạo bay tự do và bắt lại vào tay đối diện [K81 0:09 "Hi, the scene you just saw was assembled using a simple and efficient pipeline"] [K81 16:28 "Now let's select the frames in between these two and enable AutoPhysics. Make sure work on interval is enabled"].
- Góp ý chuyên môn từ Animator: Các bài học thực tế về chuyển dịch trọng tâm, đường cong chuyển động (Arcs), sự tinh tế trong nhịp điệu khi diễn hoạt [K74 6:30 "position of the whole body slightly so the center of mass would actually be fully on the right foot"] [K93 0:14 "Grigori it's a jump with a kick and rotation in the air"].

## Quy trình 1: Dựng Chu kỳ Bước đi Chuẩn (Walk Cycle Workflow)
1. Nạp nhân vật Cascy từ Samples, chia hai viewport để nhìn chính diện và bên cạnh; bật chế độ isometric bằng cách bấm vào giữa view cube [K40 1:57 "selecting the isometric mode by clicking on the center of the"].
2. Tư thế tiếp đất: một chân trước, một chân sau. Trước khi kéo chân, khoá điểm hướng của đầu và thân bằng `Shift + Z` để thân không xoay theo [K40 2:39 "lock this point in place by pressing Shift Z"].
3. Tay đánh ngược chiều chân; có thể xoay nhẹ thân về phía chân trước [K40 3:05 "Arms and legs will be moving in the opposite directions"]. Giữ `Ctrl` để giảm lực công cụ khi chỉnh nhỏ [K40 3:32 "holding down Ctrl to reduce the force of the tool"]. Tránh gối duỗi thẳng 180°, để khoảng 175° [K40 3:57 "A little adjustment of 175 degrees instead will make a big difference"].
4. Sang khung 12, thêm key và tạo tư thế đối xứng: chọn mọi điểm (bấm đúp điểm chính ở pelvis), mở Mirror tool, chọn mặt YZ, bấm mirror trên khung hiện tại [K40 4:27 "we're going to mirror tool and I'm selecting planes YZ in this situation"]. Chọn nội suy Bezier Clamped [K40 4:43 "add interpolation by choosing Bezier Clamped"]; nhảy giữa các key bằng `Shift + A` / `Shift + D` [K40 4:43 "by holding Shift and using A and D buttons"].
5. Khuỷu tay bị gập do nội suy IK: mở danh sách track, chọn track tay, đổi kiểu nội suy sang FK để tay đi theo đường cung [K40 5:42 "Select FK or forward kinematic. Now the characters arms are moving in an arc trajectory"].
6. Thêm key trung gian ở khung 6: tắt các điểm của bàn chân bằng `Shift + Z` để chân tự bám đất, giữ gối hơi cong, nâng nhẹ chân kia [K40 6:27 "I'll first deactivate the field points by selecting them and clicking shift and Z"]. Thêm key ở khung 3 và dùng chế độ Ghost để so với vị trí ở key trước [K40 7:35 "To better adjust the positioning, I'm going to be using the ghost mode"].
7. Ghim hiển thị quỹ đạo bàn chân và chỉnh ở nhiều khung cho quỹ đạo gần hình giọt nước [K40 8:51 "It looks so much better if your foot is following a trajectory over a raindrop"].
8. Bước thứ hai: chọn đoạn khung đã làm, giữ `Shift` và lăn chuột để nhân bản sao cho key đầu trùng key cuối [K40 9:22 "scroll my mouse while holding shift"]; chọn mọi điểm và mirror cả đoạn. Nếu ra nội suy Fixed thì hoàn tác, bỏ chọn nút pin rồi mirror lại [K40 9:51 "It happened because we had a little pin button pressed"].
9. Tạo cycle: chọn mọi khung trừ khung cuối rồi bấm nút tạo cycle (các khung cycle viền hồng) [K40 10:23 "select all the frames, except for the very last one"]. Cho AutoPhysics, kéo dài thành 3 chu kỳ: từ 32 lên 96 khung, để chỉ dùng chu kỳ giữa [K40 11:05 "I'll increase the number of frames to 96"].
10. Nhân vật bị nhảy khi bật AutoPhysics vì chân trượt tại chỗ không được nhận là fulcrum: chọn mọi điểm bàn chân và đoạn khung, vào Object properties → Fulcrum point, tăng Max speed (thử 10) [K40 12:18 "go to object properties, falcrum point, and increase the max speed. Let's try 10"]. Khung hai chân chạm đất tô xanh, một chân tô vàng [K40 12:48 "frames where only one foot is touching the ground are highlighted in yellow"].
11. Bật thêm filter Smooth trajectory (làm mượt quỹ đạo trọng tâm) và Secondary motion (làm tay đung đưa) [K40 13:30 "Now let's add the smooth trajectory filter"] [K40 13:45 "The secondary motion filter will make the arms swing"].
12. Gỡ cycle thành khung thường rồi bấm Snap to AutoPhysics để nhân vật theo kết quả vật lý; sau đó lấy chu kỳ giữa đưa về đầu animation [K40 14:35 "Select the snap to art of physics button"] [K40 15:07 "I will select this middle cycle, and I will also move it to the beginning"].

## Quy trình 2: Diễn hoạt Cảnh Chiến đấu và Parkour từ Video Tham chiếu
1. Nạp video tham chiếu: Nhập đoạn video quay cảnh võ thuật hoặc nhào lộn parkour vào khung nhìn nền [K2 1:16 "This way I can see both the reference and my character"] [K32 0:00 "in this time lapse we're going to use a video reference to create this animation here"].
2. Dựng hoạt cảnh từ đầu theo video tham chiếu parkour [K33 0:00 "take this reference here to create a keyframe animation from scratch"].
3. **Chặn dáng chính (Blocking)**: Đặt chế độ nội suy Step; dừng tại các khung hình then chốt (cú bật nhảy, chạm tay vào tường, lộn nhào, tiếp đất) để tạo các keyframe chính xác [K2 1:47 "Blocking is a step when we select the"] [K2 7:15 "After the small step that we've just talked about, we can see"].
4. Kiểm tra nhịp điệu (Timing): số khung hình giữa hai key càng nhiều thì chuyển động càng chậm, giảm số khung hình thì nhân vật tăng tốc [K31 2:24 "Timing refers to the time in between the keys in which the movement is happening"] [K31 2:39 "the more frames you have in between the keys, the slower your character is going to move"].
5. Chuyển sang nội suy Bezier hoặc Inbetweening để tạo chuyển động trung gian [K2 9:35 "After selecting all the frames on the timeline, I click on the busy clamp interpolation button"].
6. Kích hoạt AutoPhysics, xác định các điểm Fulcrum trên tay và chân khi tiếp xúc chướng ngại vật để tạo phản lực chuẩn xác [K2 14:44 "Before moving on to the editing, I'm making sure that all the fulcrum points are correct"] [K66 1:49 "You can now see that autophysics does recognize this cube as a"].
7. Sử dụng thanh trượt Snap Animation để hợp nhất vật lý và nắn lại đường cong chuyển động [K2 23:49 "Now, I'm going to apply them to my animation"].

## Quy trình 3: Hoạt cảnh Vũ khí Hai tay (Two-Handed Sword) và Ném Vũ khí
1. Hoạt cảnh vũ khí hai tay: Nhập nhân vật và mô hình kiếm vào cảnh [K59 0:04 "In this video, I'm going to show a couple of life hacks on how to work with a double-handed sword in Cascadeur"] [K91 1:15 "While in the rig mode, go to file, import FBX model"].
2. Gắn chuôi kiếm vào bàn tay thuận (tay phải) bằng Parent Constraint [K59 12:38 "enabled, you will see red outlines around the points. And now the hand will move along with the sword"].
3. Bàn tay phụ (tay trái) sử dụng hệ thống Inverse Kinematics (IK) nhắm vào chuôi kiếm để cả hai tay cùng xoay kiếm mượt mà mà không bị trượt khớp tay [K59 7:56 "To select all the points of the sword, just double-click the main point"].
4. **Ném vũ khí (Throwing Weapons Pipeline)**: Khi nhân vật vung tay ném, tại khung hình nhả kiếm, ngắt liên kết Constraint khỏi bàn tay [K81 2:15 "My scene has two characters, a protagonist with a small throwing ax"] [K81 5:30 "recommend saving characters and their weapons as separate scenes"].
5. Gán thuộc tính vật lý Ballistics cho vũ khí: thanh kiếm sẽ tự động bay theo một quỹ đạo parabol đạn đạo và tự xoay quanh khối tâm của nó [K81 9:45 "And just like that, we get a running animation"] [K81 14:21 "AutoPhysics for realistic weight and of course rag doll"].
6. Tại khung hình tiếp đất hoặc cắm vào mục tiêu, ghim cố định mũi kiếm bằng Pin Collision hoặc ràng buộc vào đối tượng bị trúng đòn [K81 17:01 "Now we need to make sure the ax stays in the head"].

## Quy trình 4: Diễn hoạt Hoạt hình Cách điệu (Stylized Cartoon Animation)
1. Diễn hoạt nhân vật có các chi tiết phụ (tai, đuôi) hoặc động tác nhảy [K38 0:29 "when animating characters which have additional elements to them such as the tail or scrolls or ears"] [K38 1:11 "The next step was using auto-physics. It helped quickly achieve a more accurate ballistic trajectory for the jump"].
2. Tận dụng bộ điều khiển Box Controllers để kéo giãn các đoạn chân tay ở khung hình đỉnh vận tốc [K38 2:06 "For the facial animation a separate scene was prepared featuring some of the basic emotions. So we could easily copy them using box controllers"] [K54 5:40 "Box controllers location can be changed pretty easily. I will also create a box controller for this lower part of"].
3. Giảm bớt số khung hình nội suy để tạo chuyển động giật nhanh dứt khoát (Snappy timing) [K38 1:38 "on adding secondary motion. Then we used compensation motion for the tail specifically to give us an idea of what poses the tail could take"].
4. Sử dụng Secondary Motion để các chi tiết phụ như đuôi hoặc tai nảy tự nhiên [K38 1:51 "Then we used secondary motion on top of that"] [K48 2:10 "is dumping which controls how quickly the motion Fades out a lower"].

## Bài học Góp ý Chuyên môn từ Animator (Senior Animator Feedback)
1. Chuyển dịch trọng tâm: Trong các bài quyền võ thuật (như Thái Cực Quyền), trọng tâm cơ thể cần chuyển hoàn toàn sang chân trụ đối diện trước khi nhấc chân lăng [K74 6:30 "position of the whole body slightly so the center of mass would actually be fully on the right foot"].
2. Đường cong chuyển động: Tránh dùng nội suy thẳng trên khoảng di chuyển, dùng Bezier Clamped để tạo gia tốc slow-in/slow-out tự nhiên [K74 15:39 "really use bezier clamps instead in this interval I believe busier interpolation is the best"] [K93 5:40 "to this later but for now let's snap the trajectory that we"]. Bật hiển thị Trajectory để kiểm tra quỹ đạo [K27 0:42 "If I select a different point, I will see its trajectory on the selected frames"].
3. Cú đá nhảy (Jump Kick): Cần kiểm tra kỹ các tư thế chuẩn bị, nâng hông và quỹ đạo chân khi chân tiếp đất và duỗi thẳng để tạo lực thị giác rõ ràng [K93 7:20 "into spline when we set up the jump we make this preparation"] [K93 7:00 "so if we had chosen to instead fix the poses first I mean to get this um the highest pose"].
- Diễn hoạt xoay súng góc nhìn thứ nhất (FPV) từ video tham chiếu [K79 0:03 "we are going to animate gun spinning using a visual reference specifically so it would work for the first person's view"].
- Diễn hoạt game hành động độc lập (Eternity's Echo) kết hợp Cascadeur và Unreal Engine 5 [K88 1:19 "I'm the 3D animator and I use mainly Casketeer and Unreal Engine 5"].
- Diễn hoạt game parkour (Rooftops and Alleys) [K87 0:20 "What does it take to build a parkour game from scratch? Especially if you're just one person. Today we dive into a solo journey"].

## Quy tắc chọn
- Diễn hoạt hành động thực tế (Realism) ⇒ Bắt buộc tìm video tham chiếu chất lượng cao và tuân thủ chặt chẽ AutoPhysics [K2 1:14 "This way I can see both the reference and my character"] [K74 0:32 "here's the reference and our first pose"].
- Hoạt cảnh game đối kháng nhịp độ nhanh ⇒ Ưu tiên sửa dáng then chốt trước khi kiểm tra quỹ đạo [K93 7:00 "so if we had chosen to instead fix the poses first I mean to get this um the highest pose"].
- Hoạt cảnh ném đạo cụ bay trên không ⇒ Chọn các frame giữa và bật AutoPhysics trên interval để tính toán quỹ đạo đạn đạo (ballistic trajectory) [K81 16:28 "Now let's select the frames in between these two and enable AutoPhysics. Make sure work on interval is enabled"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Động tác võ thuật cảm giác nhẹ bẫng thiếu lực | Cần phân bố trọng lượng cơ thể lên chân trụ | Dịch chuyển vị trí cơ thể để khối tâm nằm trọn trên bàn chân trụ [K74 6:30 "position of the whole body slightly so the center of mass would actually be fully on the right foot"] | [K74 6:30 "position of the whole body slightly so the center of mass would actually be fully on the right foot"] |
| Chọn toàn bộ kiếm | Nhấp đúp vào điểm chính (main point) | Di chuyển toàn bộ kiếm như một đối tượng thống nhất [K59 7:56 "To select all the points of the sword, just double-click the main point"] | [K59 7:56 "To select all the points of the sword, just double-click the main point"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Nhập video tham chiếu | Import Reference | Chèn video nền vào Viewport [K2 1:14 "This way I can see both the reference and my character"] |
| Dựng dáng đối xứng bước đi | Mirroring | Tạo bước chân đối xứng cho chu kỳ đi [K40 10:30 "Now we're mirroring the entire interval. In this case, we ended up with fixed interpolation"] |
| Kiểm tra cung tròn chuyển động | Bật Trajectory trên Viewport | Nắn cung tròn cú đấm/đá [K27 0:42 "This immediately shows the trajectory of the selected point in the viewport"] [K93 5:40 "to this later but for now let's snap the trajectory that we"] |
