# BÁO CÁO NỘP BÀI - LAB 05 (ECO2432)

**Đề bài:** Viết chương trình Python phân tích biến động dòng tiền và số dư ví Ethereum từ Etherscan API.  
**Địa chỉ ví mẫu kiểm tra:** `0xae4533189C7281501F04bA4b7c37e3ADeD402902`

---

## 1. Danh mục các sản phẩm nộp

Toàn bộ sản phẩm được lưu trữ đầy đủ trong thư mục `lap5/`:

1. **Chương trình chạy được:** [`analyze_wallet.py`](file:///d:/BAITAPLAP/LAP1/lap5/analyze_wallet.py)
   - Viết bằng Python 3.10+ tuân thủ nghiêm ngặt [`AGENTS.md`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/AGENTS.md).
   - Tích hợp chuẩn **Etherscan API V2**, hỗ trợ phân trang tự động, xử lý giao dịch lỗi, chia chuẩn $10^{18}$ Wei $\rightarrow$ ETH, bắt lỗi toàn diện không để crash.
   - Tích hợp sẵn cờ `--test` để chạy kiểm tra tự động toàn bộ 6 điểm bắt buộc.
2. **Biểu đồ số dư lũy kế trực quan:** [`balance_chart.png`](file:///d:/BAITAPLAP/LAP1/lap5/balance_chart.png)
   - Biểu đồ đường trục ngang thời gian, trục dọc số dư ròng lũy kế (ETH) được xuất tự động bằng thư viện `matplotlib`.
3. **Nhật ký AI đầy đủ lỗi:** [`AI_JOURNAL.md`](file:///d:/BAITAPLAP/LAP1/lap5/AI_JOURNAL.md)
   - Ghi nhận chi tiết **4 lỗi** (vượt yêu cầu tối thiểu 2 lỗi) theo đúng mẫu chuẩn Phần B.3.
   - Trường **"Ai phát hiện"** được ghi nhận rõ ràng (3 lỗi do sinh viên phát hiện, 1 lỗi do AI tự nhận).
4. **Tài liệu đặc tả kiểm thử được:** [`SPEC.md`](file:///d:/BAITAPLAP/LAP1/lap5/SPEC.md)
   - Đặc tả chuẩn hóa 6 mục (Mục đích, Đầu vào, Quy tắc R1–R6, Đầu ra, Trường hợp ngoại lệ E1–E4, Ngoài phạm vi).

---

## 2. Kết quả nghiệm thu 6 điểm bắt buộc

| STT | Điểm kiểm tra | Yêu cầu | Kết quả thực tế | Trạng thái |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Đơn vị tiền** | Chia $10^{18}$, hiển thị số dư hợp lý | Quy đổi toàn bộ Wei sang ETH dạng số thực với 6 chữ số thập phân (`1.500000 ETH`). | **ĐẠT** |
| 2 | **Khóa API** | Không hardcode trong mã nguồn | Đọc an toàn từ biến môi trường `ETHERSCAN_API_KEY`. | **ĐẠT** |
| 3 | **Phân trang** | Lấy đủ giao dịch khi ví có $> 10.000$ tx | Vòng lặp `while True` với `offset=10000`, liên tục tăng `page` đến trang cuối. | **ĐẠT** |
| 4 | **Giao dịch thất bại** | Có tính phí gas của giao dịch fail | Giao dịch gửi đi thất bại (`isError == "1"`) không trừ `value` nhưng vẫn trừ phí gas vào dòng tiền ra. | **ĐẠT** |
| 5 | **Xử lý lỗi** | Không dừng đột ngột khi API Key sai | Nhận diện mã lỗi Etherscan `status == "0"`, in thông báo thân thiện và thoát có kiểm soát (`exit code 1`). | **ĐẠT** |
| 6 | **Phiên bản API** | Dùng endpoint hiện hành | Sử dụng đúng **Etherscan API V2** (`https://api.etherscan.io/v2/api` + `chainid=1`). | **ĐẠT** |

---

## 3. Tóm tắt các lỗi ghi nhận trong `AI_JOURNAL.md`

- **Lỗi 1 (Sinh viên phát hiện):** AI ban đầu gọi endpoint V1 cũ đã bị Etherscan ngừng hỗ trợ $\rightarrow$ Đổi sang API V2.
- **Lỗi 2 (AI tự nhận):** Lỗi mã hóa bảng mã `cp1252` trên console Windows $\rightarrow$ Bọc lại `sys.stdout` với UTF-8.
- **Lỗi 3 (Sinh viên phát hiện):** Nhận diện sai (False Positive) hardcode key khi quét chuỗi thô $\rightarrow$ Viết lại bằng Regex chuẩn.
- **Lỗi 4 (Sinh viên phát hiện):** Unhandled exception khi Etherscan trả về chuỗi thông báo lỗi thay vì mảng $\rightarrow$ Phòng thủ bằng `if status == "0"`.

---

## 4. Lệnh chạy thực nghiệm

```powershell
# Chạy bộ kiểm thử tự động 6 điểm:
python lap5/analyze_wallet.py --test

# Chạy thực tế với ví mẫu:
$env:ETHERSCAN_API_KEY="Khoa_API_Cua_Ban"
python lap5/analyze_wallet.py 0xae4533189C7281501F04bA4b7c37e3ADeD402902
```
