# SPEC - Phân Tích Biến Động Dòng Tiền & Số Dư Ví Ethereum (Lab 05)

> **Tài liệu tham chiếu:** Giáo trình ECO2432 · Trang 13  
> **So sánh mẫu đặc tả:**
> - *Đặc tả sai:* “Viết chương trình phân tích ví.” → Không nói rõ phân tích ví nào, phân tích cái gì, tiêu chí tính toán ra sao và định dạng kết quả thế nào.
> - *Đặc tả đúng:* Được chuẩn hóa rõ ràng thành 6 mục kiểm thử được bên dưới.

---

## 1. Mục đích

Chương trình tự động thu thập lịch sử giao dịch từ Etherscan API của một địa chỉ ví Ethereum chỉ định, tính toán biến động dòng tiền (vào/ra), phí gas và số dư lũy kế theo thời gian thực để phục vụ kiểm toán và điều tra dòng tiền on-chain.

---

## 2. Đầu vào

- **Địa chỉ ví mục tiêu:** Dạng chuỗi 42 ký tự (hexadecimal), bắt đầu bằng tiền tố `0x` (ví dụ: `0x...`).
- **Khóa API Etherscan:** Đọc từ biến môi trường `ETHERSCAN_API_KEY` (tuân thủ nghiêm ngặt quy tắc bảo mật của `AGENTS.md`, tuyệt đối không hardcode trong mã nguồn).
- **Khoảng thời gian phân tích:** Số ngày cần lấy dữ liệu tính ngược từ thời điểm hiện tại, mặc định là **90 ngày**.

---

## 3. Quy tắc nghiệp vụ

- **R1 (Dòng tiền vào):** Giao dịch có trường `to` trùng khớp với địa chỉ ví đang xét và thực thi thành công (`isError == "0"`) được ghi nhận là **dòng tiền vào (+)**. Giá trị cộng = `value`.
- **R2 (Dòng tiền ra):** Giao dịch có trường `from` trùng khớp với địa chỉ ví đang xét được ghi nhận là **dòng tiền ra (-)**.
- **R3 (Số tiền thực trừ khi gửi đi):** Với giao dịch đi ra thành công, số tiền thực trừ khỏi ví:
  $$\text{Số tiền thực trừ} = \text{Giá trị chuyển } (\text{value}) + \text{Phí giao dịch } (\text{gasUsed} \times \text{gasPrice})$$
- **R4 (Xử lý giao dịch thất bại):** Giao dịch do ví gửi đi (`from` trùng địa chỉ ví) nhưng có trạng thái thất bại (`isError == "1"`): Giá trị chuyển không bị trừ, nhưng ví **vẫn bị trừ phí giao dịch**. Do đó, phí này vẫn phải tính vào dòng tiền ra (-). Đối với giao dịch chuyển đến bị thất bại, ví không chịu phí và không nhận tiền (bỏ qua).
- **R5 (Chuẩn hóa đơn vị tiền tệ):** Mọi số tiền lấy từ Etherscan API đều ở đơn vị `wei`. Toàn bộ giá trị `value` và phí gas phải được chia cho $10^{18}$ để quy đổi sang `ETH` trước khi tính toán số dư và hiển thị.
- **R6 (Thứ tự thời gian):** Dữ liệu giao dịch phải được sắp xếp theo thời gian (`timeStamp`) tăng dần (từ cũ nhất đến mới nhất) trước khi tính toán số dư lũy kế.

---

## 4. Đầu ra

- **Bảng dữ liệu chi tiết:** Hiển thị danh sách giao dịch gồm các cột:
  1. Thời gian (định dạng `YYYY-MM-DD HH:MM:SS` UTC hoặc giờ địa phương).
  2. Loại giao dịch (`Vào` / `Ra`).
  3. Số tiền chuyển (`ETH`).
  4. Phí giao dịch thực trả (`ETH`).
  5. Số dư ròng lũy kế trong kỳ (`ETH`).
- **Biểu đồ trực quan:** Một biểu đồ đường (line chart):
  - *Trục ngang (X):* Mốc thời gian.
  - *Trục dọc (Y):* Số dư ròng lũy kế (`ETH`).
- **3 chỉ số tổng hợp toàn kỳ:**
  1. **Tổng tiền vào:** Tổng lượng ETH thực nhận.
  2. **Tổng tiền ra:** Tổng lượng ETH chuyển đi + toàn bộ phí gas đã trả.
  3. **Biến động ròng / Số dư lũy kế cuối kỳ:** $\text{Tổng vào} - \text{Tổng ra}$.

---

## 5. Trường hợp ngoại lệ

- **E1 (Ví không có giao dịch):** Nếu API trả về danh sách rỗng (không có giao dịch nào trong khoảng thời gian đã chọn): In thông báo chuẩn `"Vi khong co giao dich trong ky"`, kết thúc bình thường, không báo lỗi runtime hay crash chương trình.
- **E2 (Lỗi kết nối / API trả mã lỗi):** Nếu API trả về mã lỗi (ví dụ sai API key, rate limit `MAX_RATE_LIMIT_EXCEEDED`): In rõ mã lỗi nhận được và dừng chương trình, không tiếp tục xử lý tính toán.
- **E3 (Phân trang khi giao dịch lớn):** Nếu ví có hơn 10.000 giao dịch (giới hạn tối đa một lần gọi của Etherscan): Chương trình phải tự động xử lý phân trang (`page`, `offset`) để thu thập đầy đủ toàn bộ các trang giao dịch trước khi phân tích.
- **E4 (Giao dịch tự chuyển cho chính mình - Self-transfer):** Nếu `from == to == wallet_address`: Giá trị chuyển `value` không đổi, nhưng số dư ví vẫn bị trừ một khoản bằng đúng phí gas thực trả.

---

## 6. Ngoài phạm vi

- Không phân tích các giao dịch token ERC-20, NFT ERC-721/1155 (chỉ tập trung vào dòng tiền native `ETH`).
- Không hỗ trợ quy đổi giá trị sang tiền pháp định (VND, USD).
- Không phân tích các lệnh gọi nội bộ phức tạp (Internal Transactions) ngoài phạm vi API get normal transactions cơ bản.
