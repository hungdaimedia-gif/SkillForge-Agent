# Danh sách duyệt trước khi giao skill

Cổng kiểm và quiz bắt được lỗi máy móc; danh sách này bắt lỗi mà chỉ người đọc mới thấy.
Làm với **skill trung tâm** và **ít nhất một skill con** (chọn skill có nhiều unit nhất).

## 1. Kích hoạt đúng lúc
- [ ] `description` bắt đầu bằng "Use when", có tên phần mềm/chủ đề, tên tính năng, cách người
      dùng hay hỏi (cả tiếng Việt nếu người dùng nói tiếng Việt).
- [ ] Hai skill con không có description gần như trùng nhau (agent sẽ chọn nhầm).

## 2. Làm được mà không cần mạng
- [ ] Có ít nhất một quy trình đánh số với **đường dẫn menu / nút / phím tắt cụ thể** (`code`).
- [ ] Không có câu kiểu "xem video để biết thêm" — thông tin phải nằm trong skill.
- [ ] Skill trung tâm có bảng chỉ đường tới mọi skill con và bảng phím tắt đầy đủ.
- [ ] Link `references/...` mở được và thật sự có nội dung bổ sung.

## 3. Đúng với nguồn
- [ ] Mở `SOURCES.md`, bấm **3 link ngẫu nhiên**: đúng giây/trang có nói/hiện điều skill viết.
- [ ] Các ý ghi "(chưa chắc chắn)" là ít — nếu nhiều, transcript tự động sai nặng ⇒ cân nhắc whisper.
- [ ] Không có đoạn chép nguyên văn dài từ nguồn (đặc biệt với sách).

## 4. Phiên bản & phạm vi
- [ ] Nếu nguồn có dấu hiệu cũ (mô tả video báo "guide đã cập nhật", giao diện khác bản hiện tại),
      skill trung tâm có dòng cảnh báo phiên bản — nếu thiếu, báo người dùng.
- [ ] Ảnh nhúng (`assets/`) đúng chỗ, giúp nhận ra giao diện; không quá ~6 ảnh/skill.

## 5. Quiz
- [ ] Mở `eval.json`: câu "wrong"/"partial" là do skill thiếu (⇒ `--redo`) hay do đáp án mẫu
      quá khắt khe (⇒ chấp nhận, ghi chú).

## Kết luận cho người dùng
Ghi: skill đạt / cần làm lại / chấp nhận draft kèm lý do — trước khi `export`.
