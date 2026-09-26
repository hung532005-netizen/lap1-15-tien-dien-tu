# NHẬT KÝ LÀM VIỆC VỚI AI - Lab 04

Bài thực hành: **Thẩm định rủi ro hợp đồng token (`ClubTokens.sol`)**

---

## Lần 1

**Prompt:**
```text
Bạn là chuyên viên thẩm định rủi ro tài sản số.
Dưới đây là mã nguồn một hợp đồng token. Hãy liệt kê mọi quyền đặc biệt mà chủ sở hữu hợp đồng có thể thực hiện, và với mỗi quyền, nêu rõ:
- Tên hàm và số dòng
- Người nắm giữ token chịu rủi ro gì
Chỉ trả lời dựa trên mã nguồn tôi cung cấp. Nếu không tìm thấy, nói là không tìm thấy.
```

**AI trả về:**
- AI thông báo người dùng chưa đính kèm mã nguồn trực tiếp trong nội dung câu lệnh, đúng theo điều kiện *"Chỉ kết luận từ mã được cung cấp; nếu không đủ dữ liệu, nói rõ phần còn thiếu"*.
- Sau đó AI chủ động quét mã nguồn tệp [`contracts/lab04/ClubTokens.sol`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol) có sẵn trong dự án để liệt kê đặc quyền và rủi ro của 3 hợp đồng `ClubTokenA`, `ClubTokenB`, `ClubTokenC`.

**Đánh giá:** Phải sửa.

**Chỗ sai:**
- AI trả lời dạng báo cáo chung, chưa kẻ bảng tổng kết ngắn gọn theo đúng biểu mẫu yêu cầu của sổ tay `lab04.md` (các cột: Hợp đồng, Kết luận, Tên hàm, Số dòng, Rủi ro cho người nắm giữ).

**Cách sửa:**
- Sinh viên gửi câu lệnh tinh chỉnh (prompt lần 2), yêu cầu AI kết luận trực tiếp vào bảng mẫu của `lab04.md` với đầy đủ tên hàm, số dòng chính xác, từ chối câu trả lời định tính chung chung.

**Ai phát hiện:** Sinh viên phát hiện.

---

## Lần 2

**Prompt:**
```text
kết luận trong lab04.md :
Hợp đồng | Kết luận | Tên hàm | Số dòng | Rủi ro cho người nắm giữ
A
B
C
Không chấp nhận kết luận không có số dòng. Câu trả lời kiểu “AI nói hợp đồng B có rủi ro” bị tính là chưa làm
```

**AI trả về:**
- Bảng tổng hợp đối chiếu mã nguồn chuẩn xác với đầy đủ số dòng:
  + Token A: Không có quyền đặc biệt (constructor dòng 8–10).
  + Token B: Hàm `mint` (dòng 18–20), rủi ro lạm phát không giới hạn và Rug-pull.
  + Token C: Hàm `setRestricted` (dòng 30–32) tác động qua `_update` (dòng 34–37), rủi ro Honeypot/đóng băng tài sản tùy tiện.

**Đánh giá:** Dùng được.

**Chỗ sai:** Không có. Số dòng và tên hàm khớp hoàn toàn với tệp `ClubTokens.sol`.

**Cách sửa:** Không cần sửa mã nguồn, tích hợp trực tiếp bảng kết luận vào tệp báo cáo `lab04.md`.

**Ai phát hiện:** Sinh viên kiểm tra và xác nhận.

---

## So sánh: Đọc thủ công vs AI hỗ trợ

### 1. Đọc thủ công tìm ra gì?
- **ClubTokenA:** Đọc thấy chỉ là token ERC-20 cơ bản, không có `Ownable`, đúc 1,000,000 token cố định trong constructor. Không thấy có hàm admin hay backdoor.
- **ClubTokenB:** Thấy hàm `mint` có modifier `onlyOwner` (dòng 18–20), nhận biết được chủ sở hữu có thể in thêm token theo ý muốn.
- **ClubTokenC:** Thấy mapping `restricted` (dòng 24), hàm `setRestricted` có `onlyOwner` (dòng 30–32) và điều kiện kiểm tra trong `_update` (dòng 35). Nhận biết được chủ sở hữu có thể cấm ví của người khác không cho giao dịch.

### 2. AI tìm thêm được gì?
- **Phân tích chiều sâu về rủi ro tài chính và kịch bản khai thác:**
  - Với **Token B:** AI chỉ rõ hợp đồng thiếu biến trần tổng cung (`cap`) và thiếu khóa thời gian (`Timelock`). AI làm rõ kịch bản tấn công: Owner tự đúc lượng lớn token rồi bán tháo cạn thanh khoản bể DEX (Rug-pull), làm token của người nắm giữ bị pha loãng về 0.
  - Với **Token C:** AI phát hiện đây là bẫy **Honeypot**: cơ chế `_update` chỉ chặn chiều chuyển đi (`from`) chứ không chặn chiều nhận vào (`to`), nghĩa là nạn nhân vẫn mua được token nhưng không thể bán ra.
- **Nhận diện hàm kế thừa từ thư viện OpenZeppelin:**
  - AI chỉ ra Token B và C còn thừa hưởng hàm `renounceOwnership()` và `transferOwnership()`. Nếu chủ sở hữu từ bỏ quyền, các rủi ro trên sẽ được triệt tiêu hoàn toàn.
- **Đánh giá rủi ro ngoài luồng của Token A:**
  - AI lưu ý thêm về rủi ro tập trung lượng cung ban đầu (100% thuộc về deployer), nhắc nhở không nhầm lẫn giữa "code an toàn" và "không có rủi ro thị trường".

### 3. AI có nói sai chỗ nào không?
- **Khả năng ảo giác (Hallucination):** Ở lần 2, AI không bị sai lệch số dòng hay bịa hàm không tồn tại; tất cả các dòng (8–10, 18–20, 24, 30–32, 34–37) đều khớp chính xác với mã nguồn thực tế.
- **Tuân thủ nguyên tắc thẩm định:** AI không vội vàng kết luận mã an toàn tuyệt đối mà phân định rõ rủi ro logic on-chain và rủi ro phân bổ ban đầu, tuân thủ đúng yêu cầu của môn học ECO2432 và `AGENTS.md`.
