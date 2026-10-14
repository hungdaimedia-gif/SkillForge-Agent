# Xuất Nhập Dữ liệu và Tích hợp Đa Phần mềm trong Cascadeur

Cascadeur hoạt động như một mắt xích trung tâm mạnh mẽ trong quy trình sản xuất hoạt hình công nghiệp, kết nối mượt mà với Blender, Unreal Engine 5 (hỗ trợ Live Link thời gian thực), Maya, Roblox, Mixamo, Daz 3D, AccuRIG và RenderHub. Tài liệu này hướng dẫn chuẩn hoá hệ trục toạ độ, xuất nhập file FBX tối ưu, thiết lập kết nối Live Link với UE5 và chuẩn bị mô hình thương mại.

## Khái niệm cốt lõi
- Xuất file FBX và mô hình: Cấu hình xuất file FBX tương thích từng nền tảng đích (Roblox, Blender, Maya, Unreal Engine), mở file đã xuất trong menu tương ứng của phần mềm [K26 0:32 "You can then open up the exported file in Roblox in the corresponding menu"].
- **Unreal Engine Live Link**: Plugin truyền dữ liệu chuyển động thời gian thực từ Cascadeur sang Unreal Engine 5, cho phép vừa điều khiển nhân vật trong Cascadeur vừa thấy ngay kết quả render ánh sáng trên Metahuman [K7 0:15 "stream your animation live using Cascadeur Live Link directly into Unreal Engine"] [K10 0:00 "up a live link between Cascadeur and Unreal Engine, which allows you"] [K44 0:00 "set up a live link between Cascogir and Unreal Engine 5"].
- Chuẩn bị chuyển động Locomotion cho UE5: Quy trình chỉnh sửa bộ hoạt cảnh di chuyển (Walk, Run, Sprint, Jump) để sử dụng trong Unreal Engine [K39 0:00 "show you how you can edit the locomotion animations to further use them in Unreal Engine"] [K39 0:28 "With all the animations we will need Walk, Run, Sprint, Jump, Start, Loop and End, and also the FBX"].
- Quy trình nhân vật Roblox R15: Quy trình rig và xuất chuyển động cho nhân vật R15 của nền tảng Roblox [K26 0:00 "recently several new sample models for characters from Roblox have been added to Cascadeur"] [K26 0:32 "You can then open up the exported file in Roblox in the corresponding menu"].
- **Maya Bridge Plugin**: Cầu nối tích hợp trực tiếp giữa Autodesk Maya và Cascadeur, cho phép đồng bộ scene qua lại chỉ với một cú nhấp chuột [K92 0:15 "can use The Cask to my bridge to speed up your workflow"] [K92 1:15 "send it either to the current scene or to create a new"].

## Quy trình: Cầu nối Blender và Cascadeur (Blender Roundtrip)
1. Trong Blender, hoàn thiện mô hình và weight painting trước khi chuyển sang Cascadeur để diễn hoạt [K15 0:25 "You only come to Cascadeur when your weight painting is finished and you're ready to animate"].
2. Xuất file FBX từ Blender sang Cascadeur và kiểm tra cấu trúc skeleton tương ứng [K15 2:45 "means if you import pretty much any humanoid skeleton into Cascadeur, it"].
3. Kéo thả file FBX vào Cascadeur hoặc nhập file để bắt đầu tạo rig [K10 1:15 "Now one thing that I noticed running both Unreal Engine and Cascadeur"] [K15 0:45 "first things you will notice about Cascadeur is you do not need"].
4. Tiến hành rig hoặc diễn hoạt chuyển động với công cụ vật lý AutoPhysics [K15 1:03 "The rig is automatically provided to you and it's extremely powerful out of the box"].
5. Sau khi hoàn thiện hoạt cảnh và nắn chỉnh với vật lý, xuất dữ liệu animation quay trở lại Blender [K15 12:40 "Now, sometimes when you import an the X animation, you will see the"].

## Quy trình: Thiết lập Unreal Engine 5 Live Link (Cascadeur 2026.1 / Metahuman)
1. Cài đặt plugin **Cascadeur Live Link** trong Unreal Engine 5 [K10 0:30 "up a live link between Cascadeur and Unreal Engine, which allows you"] [K44 0:45 "Now in Unreal Engine, go to Edit, Plugins and search for Live Link"].
2. Khởi động UE5, mở cửa sổ Live Link và thêm nguồn kết nối **Cascadeur live link** [K10 1:50 "Here we click add source and select Cascadeur live link"].
3. Trong Cascadeur, vào menu **Synchronization → Live Link** để kích hoạt truyền dữ liệu trực tiếp sang Unreal Engine [K10 1:50 "Now to link this animation, go to synchronization live link"].
4. Nạp mô hình Metahuman vào cả hai phần mềm và ánh xạ tên khớp tương ứng [K7 6:00 "going to be using MetaHuman base skeleton, and then select the animation"].
5. Bấm Play hoặc xoay controller trong Cascadeur: nhân vật Metahuman trong viewport UE5 sẽ chuyển động đồng thời theo thời gian thực [K10 0:00 "up a live link between Cascadeur and Unreal Engine, which allows you"] [K10 3:45 "And with Cascadeur in-betweening system, you can prototype, create, and edit animations in no time"].

## Quy trình: Chuẩn bị Chuyển động Locomotion cho UE5
1. Chuẩn bị bộ hoạt cảnh locomotion gồm Walk, Run, Sprint, Jump và file FBX nhân vật ở tư thế T-pose [K39 0:28 "With all the animations we will need Walk, Run, Sprint, Jump, Start, Loop and End, and also the FBX"].
2. Sử dụng công cụ copy để tạo hoạt cảnh in-place cho locomotion đơn giản [K39 5:41 "for a simple locomotion we will need an in-place animation instead. To quickly make this animation in place we're going to use"].
3. Triệt tiêu độ dời trên trục di chuyển bằng paste interval để giữ nhân vật tại chỗ [K39 6:42 "Because in our animation the character is moving along the Z axis. Now make sure you're still on the very first frame"].
4. Xuất file FBX với tuỳ chọn Bake Animation và nạp vào Blend Space hoặc State Machine của UE5 [K39 9:20 "By first turn it into an in-place animation then copy the weapon placement from the previous animation"] [K39 11:15 "Then once we feel the animation is ready we save the scene"].

## Quy trình: Xuất Diễn hoạt sang Roblox, Daz 3D và Mixamo
1. **Roblox R15**: Mở trực tiếp các mẫu nhân vật Roblox có sẵn trong Cascadeur hoặc nạp mô hình R15, diễn hoạt và xuất FBX sang Roblox [K26 0:00 "recently several new sample models for characters from Roblox have been added to Cascadeur"] [K26 0:32 "You can then open up the exported file in Roblox in the corresponding menu"].
2. **Daz 3D**: Sử dụng bảng chuyển đổi Daz Genesis để khớp trục toạ độ xương Genesis 8/9, xuất ngược animation vào Daz Studio qua FBX [K69 1:20 "crucial to correctly set the export settings. In figures, enable merge followers into target. This will prevent it having additional joint hierarchies"].
3. **Mixamo & AccuRIG**: Nhập mô hình tự rig từ AccuRIG (template tự nhận diện) [K77 1:30 "the character's template for accurate will be loaded automatically"]; lấy animation từ Mixamo xuất dạng without skin và dán qua Ctrl+Shift+V [K78 2:13 "we need to export it without skin because we already have the mash in Cascada"] [K78 4:17 "edit copy interval or press Ctrl shift C and in our character scene we go edit paste the interval or Ctrl shift V"].
4. **Cải thiện animation Mixamo**: Sử dụng Cascadeur để biên tập, dọn dẹp hoặc thay đổi hoạt cảnh tải về từ Mixamo [K64 0:00 "show you how you can use Cascader to edit any animation you can find in Mixamo"].
4. **RenderHub Models**: Chuẩn hoá kiểm tra lưới và bản quyền rig trước khi đóng gói bán trên sàn thương mại RenderHub [K71 0:45 "Here are the three steps on how to upload your models to Render Hub in the CASC format"].

## Quy tắc chọn
- Làm game chất lượng cao trên Unreal Engine ⇒ Bắt buộc kích hoạt **Live Link** để preview trực tiếp ánh sáng và tương tác vật lý trước khi xuất file [K7 0:15 "stream your animation live using Cascadeur Live Link directly into Unreal Engine"] [K10 0:00 "up a live link between Cascadeur and Unreal Engine, which allows you"].
- Xuất hoạt cảnh cho Roblox ⇒ Chọn khối tâm và các khung hình rồi dùng lệnh Export to Roblox [K26 0:33 "Select the character's center of mass, the frames on the timeline, then go to commands, export to Roblox"].
- Chuyển đổi dữ liệu giữa Maya và Cascadeur ⇒ Dùng **Maya Bridge Plugin** thay vì lưu xuất file FBX thủ công nhằm giảm thiểu lỗi mất mát thuộc tính [K92 1:15 "now to send it to me go to commands Maya export"] [K92 3:20 "we have a readymade character in Maya with human ey care rig"].

## Lỗi hay gặp
| Triệu chứng | Nguyên nhân | Cách sửa | Nguồn |
|---|---|---|---|
| Live Link không nhận nguồn trong Unreal | Nguồn kết nối chưa được thêm trong Live Link | Vào Virtual Production Live Link, chọn Add Source và chọn Cascadeur Live Link [K10 2:10 "Here we click add source and select Cascadeur live link. Here in a pop-up window, we have to select"] [K44 1:30 "Now in this asset, we also need to enable Live Link controller, same as we did before"] | [K10 2:10 "Here we click add source and select Cascadeur live link. Here in a pop-up window, we have to select"] |

## Tra nhanh
| Việc | Phím / menu | Ghi chú |
|---|---|---|
| Xuất animation và mesh | Commands → Export | Xuất animation hoặc kèm mesh ra file [K26 0:32 "You can either export the animation only or include the character's mesh into the export"] |
| Kết nối Unreal Live Link | `Synchronization → Live Link` | Đồng bộ hoạt cảnh sang UE5 thời gian thực [K10 1:50 "Now to link this animation, go to synchronization live link"] |
| Xuất chuẩn Roblox R15 | Commands → Export to Roblox | Xuất animation hoặc kèm mesh sang Roblox [K26 0:33 "Select the character's center of mass, the frames on the timeline, then go to commands, export to Roblox"] |
| Đồng bộ sang Maya | Maya Bridge Plugin | Cầu nối trực tiếp hai chiều [K92 1:15 "now to send it to me go to commands Maya export"] |
| Rigging mô hình AccuRIG | Drag and drop mesh vào AccuRIG | Gán xương và xuất FBX sang Cascadeur [K77 0:13 "position the center line correctly and click rig body then you need to place all the points"] [K77 1:00 "now we can export it to Cascada click export export fbx"] |
