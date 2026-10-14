# Tạo dáng và Công nghệ AutoPosing trong Cascadeur

Hệ thống tạo dáng trong Cascadeur kết hợp các điểm điều khiển vật lý (Point Controllers), hộp định hướng (Box Controllers) cùng mạng nơ-ron AI AutoPosing dự đoán tư thế tự nhiên của cơ thể theo giải phẫu [K20 1:55 "By default, it's the feet points that are always active"] [K20 4:46 "First of all, I can select all the AutoPosing controllers and activate them"]. Tài liệu này hướng dẫn phương pháp tạo dáng nhanh với điểm Active/Inactive, điều khiển từng ngón tay và tận dụng bảng Control Picker để tối ưu tốc độ diễn hoạt [K20 2:51 "The pose may change immediately since this controller is now following the active controlling point"] [K20 3:06 "The pose may change immediately since this controller is now following the active controlling point"] [K53 0:00 "select all the controllers using Control Picker"] [K72 0:36 "As a rule, fingers do not have point controllers assigned to them and instead are controlled using box"].

## Khái niệm cốt lõi
- **AutoPosing**: Hệ thống AI tự động điều chỉnh toàn bộ các khớp nối phụ thuộc khi animator di chuyển các điểm điều khiển chính [K20 1:34 "All the controllers are interconnected. No matter what type of controllers you choose to edit, it automatically changes the position of all other controllers"] [K20 1:55 "AutoPosing uses AI for faster pose setting. Blue points are the active points"].
- **Active & Inactive Points**: Điểm điều khiển khi được di chuyển sẽ kích hoạt (Active) và chuyển sang màu xanh lam để tham gia định hình tư thế; điểm Inactive (màu xám hoặc vàng) sẽ được AI tự động tính toán vị trí tự nhiên nhất [K20 2:51 "By default, it's the feet points that are always active"] [K20 4:46 "the principle of posing using active points"].
- **Deactivate** (`Shift + Z`): Bấm phím `Shift + Z` hoặc bấm nút deactivate trên giao diện để đưa một controller về trạng thái không kích hoạt, giúp bộ phận đó tự do uốn lượn theo các điểm kích hoạt khác [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] [K72 1:33 "To deactivate it, select the controller and press shift Z or click this button here"].
- **Box Controllers**: Các khối hộp bao quanh xương dùng để điều khiển hướng xoay góc cục bộ (FK rotation) của các chi như cổ tay, khuỷu tay, thân mình [K20 9:12 "And finally, the third type of the controllers, box controllers"] [K72 3:57 "To avoid that, it is best to use the rotation manipulator with the box controllers at all times"].
- **Control Picker**: Bảng giao diện 2D mô phỏng sơ đồ cơ thể giúp chọn nhanh các cụm controller phức tạp mà không cần quét chuột tìm kiếm trong Viewport [K53 0:00 "select all the controllers using Control Picker"] [K53 0:19 "Then right-click anywhere on the Control Picker for options to appear"].

## Quy trình: Tạo dáng nhanh với AutoPosing
1. Chuyển sang chế độ **AutoPosing Mode** trên thanh công cụ chính [K20 1:55 "AutoPosing uses AI for faster pose setting"].
2. Chọn điểm bàn chân hoặc trọng tâm và di chuyển đến vị trí mong muốn; toàn bộ cơ thể sẽ tự động uốn theo [K20 2:20 "You can move the controllers along the axes or along the plane"] [K20 2:37 "the request for the pose. Now the entire body is following the feet"].
3. Di chuyển các bộ điều khiển hướng (Direction Controllers) để định hướng mặt và thân; bộ điều khiển kích hoạt sẽ đổi sang màu xanh lam [K20 2:51 "the direction controller, it activates and becomes part of the request and the color changes to blue"].
4. Để thả lỏng một bộ phận cho AI tự uốn nắn, chọn controller đó và bấm `Shift + Z` để huỷ kích hoạt (deactivate) [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"].
5. Chọn nhanh toàn bộ phân cấp xương bên dưới bằng cách nhấp đúp chuột (Double-click) vào điểm điều khiển cha [K20 3:54 "Double clicking on any points will select all the points down below in the hierarchy"].
6. Thay đổi điểm trọng tâm xoay (Pivot Point) bằng cách nhấp chuột phải vào vị trí mong muốn (ví dụ: điểm gót chân) [K20 4:16 "you set it as a pivot point"].
7. Chọn nhanh nhóm controller bằng phím tắt Ctrl + số [K45 0:41 "select the group of controllers. You can do this by pressing CTRL plus the number"].

## Quy trình: Điều khiển Bàn tay với AutoPosing for Fingers
1. Bật tính năng **AutoPosing for Fingers** bằng cách bấm vào biểu tượng bàn tay trên thanh AutoPosing [K72 0:36 "controllers or an auto posing tool for fingers"].
2. Khi thao tác, luôn chọn và di chuyển controller ở ngay đầu ngón tay (tip of the finger) để AI tự động uốn cong toàn bộ các khớp ngón [K72 1:03 "Make sure you move the controller at the very tip of the finger"].
3. Khi ngón tay đã đạt dáng nắm hoặc xoè mong muốn, có thể huỷ kích hoạt bằng phím `Shift + Z` để bàn tay thả lỏng [K72 1:33 "To deactivate it, select the controller and press shift Z or click this button here"] [K72 2:45 "the controllers by pressing shift Z so that the fingers will keep their positions"].
4. Khi làm việc với ngón tay, nên chuyển sang chế độ thao tác cục bộ (Local Manipulator Mode) để dễ căn góc uốn [K72 1:48 "When working with fingers, it is best to use the local manipulator mode"].
5. Bắt đầu từ dáng nắm đấm (Fist) làm điểm xuất phát thuận lợi để biến đổi sang các cử chỉ phức tạp khác [K72 2:17 "A fist can be a good starting point for a lot of other gestures"].

## Quy trình: Thiết lập và Sử dụng Control Picker
1. Mở cửa sổ **Control Picker** từ menu Window hoặc thanh bên [K53 0:00 "Go to Window, then select Control Picker"].
2. Neo cửa sổ thành một bảng điều khiển cố định trong giao diện hoặc để dưới dạng pop-up [K53 0:19 "this window as a pop-up or you can integrate it into your interface"].
3. Quét chọn các bộ điều khiển cần thiết trên nhân vật trong Viewport [K53 0:25 "Now select the controllers you need. Then right-click anywhere on the Control Picker for options to appear"].
4. Bấm nút **Add 1 button** trong Control Picker để gộp nhóm các controller đã chọn [K53 0:33 "To easily manipulate all the selected controllers together, click Add 1 button"].
5. Bấm vào nút trên Control Picker để chọn và làm nổi bật các controller tương ứng [K53 0:54 "When I now select the button, you can see the relevant controllers being highlighted"].

## Quy tắc chọn
- Khi phác thảo dáng chính (Key pose / Extreme pose) ⇒ Ưu tiên dùng AutoPosing để nhanh chóng đạt được dáng giải phẫu cân bằng tự nhiên [K20 1:55 "AutoPosing uses AI for faster pose setting"] [K20 4:46 "not that important to be able to set up a pose from"].
- Khi muốn bộ phận cơ thể tự do uốn nắn theo dáng chuyển động mà không bị gượng ép ⇒ Chọn controller đó và bấm `Shift + Z` để đưa về trạng thái Inactive [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] [K36 2:51 "Deactivating these points makes this pose look so much more natural"].
- Khi điều chỉnh ngón tay chi tiết ⇒ Bật AutoPosing for fingers và kéo controller ở đầu ngón tay [K72 0:36 "controllers or an auto posing tool for fingers"] [K72 1:03 "Make sure you move the controller at the very tip of the finger"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Dáng cơ thể bị gượng ép cứng nhắc khi kéo chân tay | Quá nhiều controller đang ở trạng thái kích hoạt (Active) | Chọn các controller không cần thiết và bấm `Shift + Z` để chuyển về Inactive [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] [K36 2:51 "Deactivating these points makes this pose look so much more natural"] | [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] |
| Kéo ngón tay nhưng cả bàn tay không uốn cong tự nhiên | Di chuyển khớp giữa thay vì đầu ngón | Luôn di chuyển controller ở ngay đầu ngón tay (tip of the finger) [K72 1:03 "Make sure you move the controller at the very tip of the finger"] | [K72 1:03 "Make sure you move the controller at the very tip of the finger"] |
| Thao tác xoay bị lệch tâm điểm nhìn | Điểm neo xoay (Pivot point) đang đặt sai vị trí | Nhấp chuột phải vào controller mong muốn (như gót chân) để đặt lại pivot [K20 4:16 "you set it as a pivot point"] | [K20 4:16 "you set it as a pivot point"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Huỷ kích hoạt controller | `Shift + Z` (hoặc nút deactivate) | Đưa controller về Inactive để AI tự uốn [K20 3:06 "deactivate the controller using this button or by using the hotkeys shift + Z"] [K72 1:33 "To deactivate it, select the controller and press shift Z or click this button here"] |
| Chuyển đổi manipulator Translate / Rotate | `W` (dịch chuyển) / `E` (xoay) | Chuyển nhanh giữa công cụ di chuyển và xoay [K1 3:08 "Now, let's rotate our character using the rotation manipulator"] |
| Bật AutoPosing ngón tay | Icon bàn tay trên thanh AutoPosing | Tự động uốn cụp ngón tay [K72 0:36 "To enable this tool, click this button here"] |
| Chọn phân cấp bên dưới | Nhấp đúp chuột (Double click) | Chọn mọi điểm con trong nhánh [K20 3:54 "Double clicking on any points will select all the points down below in the hierarchy"] |
| Đặt điểm neo xoay (Pivot) | Nhấp chuột phải (RMB) | Đặt pivot tại khớp mong muốn [K20 4:16 "it is easy to use if you set it as a pivot"] |
