# NHẬT KÝ LÀM VIỆC VỚI AI - Lab 05

Bài thực hành: **Phân tích biến động dòng tiền và số dư ví Ethereum (`analyze_wallet.py`)**  
Tài liệu tham chiếu: Giáo trình ECO2432 (Trang 13) & Danh mục 6 điểm kiểm tra bắt buộc.

---

## Lần 1

**Prompt:**
```text
Chạy thử với địa chỉ ví mẫu 0xae4533189C7281501F04bA4b7c37e3ADeD402902
Kiểm tra 6 điểm sau — đây là danh mục kiểm tra bắt buộc:
1 Đơn vị tiền: Số dư hiển thị có hợp lý không? Quên chia 10^18, hiển thị số 19 chữ số
2 Khóa API: Tìm chuỗi khóa trong mã nguồn. Ghi thẳng khóa vào mã — lỗi bảo mật nghiêm trọng
3 Phân trang: Ví có nhiều giao dịch, có lấy đủ không? Chỉ lấy trang đầu, thiếu dữ liệu
4 Giao dịch thất bại: Có tính phí của giao dịch thất bại không? Bỏ qua, làm sai số dư
5 Xử lý lỗi: Thử dùng khóa API sai. Chương trình dừng đột ngột, không có thông báo
6 Phiên bản API: Đối chiếu với tài liệu Etherscan hiện hành. Dùng địa chỉ endpoint đã ngừng hỗ trợ
```

**AI trả về:**
- Mã nguồn ban đầu sử dụng endpoint mặc định của Etherscan API V1:
  `https://api.etherscan.io/api?module=account&action=txlist...`

**Đánh giá:** Sai, bỏ.

**Chỗ sai:**
- Điểm kiểm tra số 6 (Phiên bản API): Endpoint V1 đã bị Etherscan chính thức khai tử (deprecated). 
- Dữ liệu đối chiếu: Khi gửi yêu cầu tới endpoint V1, Etherscan trả về mã lỗi:
  ```json
  {"status":"0","message":"NOTOK","result":"You are using a deprecated V1 endpoint, switch to Etherscan API V2 using https://docs.etherscan.io/v2-migration"}
  ```
  Nếu giữ nguyên mã này, chương trình hoàn toàn không thể lấy được bất kỳ giao dịch nào từ mạng lưới.

**Cách sửa:**
- Sinh viên yêu cầu AI cập nhật mã nguồn sang chuẩn **Etherscan API V2**:
  - Đổi URL sang: `https://api.etherscan.io/v2/api`
  - Bổ sung tham số bắt buộc `chainid=1` (đối với Ethereum Mainnet).

**Ai phát hiện:** Sinh viên phát hiện.

---

## Lần 2

**Prompt:**
```text
Cập nhật endpoint sang Etherscan V2 và chạy thử nghiệm mã nguồn trên môi trường Windows.
```

**AI trả về:**
- AI sinh mã và thực thi kiểm thử trên terminal Windows PowerShell, nhưng chương trình bị crash ngay khi bắt đầu in tiêu đề báo cáo.

**Đánh giá:** Phải sửa.

**Chỗ sai:**
- Lỗi mã hóa ký tự dòng lệnh (Terminal Encoding Bug): Môi trường Windows mặc định sử dụng bảng mã `cp1252` thay vì UTF-8. Khi mã nguồn in các ký tự tiếng Việt có dấu (`BẮT ĐẦU...`, `ĐẠT`, `THẤT BẠI`), Python 3.14 ném ngoại lệ:
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode character '\u1eae' in position 1: character maps to <undefined>
  ```
  Làm gián đoạn toàn bộ quá trình chạy kiểm tra.

**Cách sửa:**
- Bổ sung đoạn mã cấu hình lại encoding cho luồng `sys.stdout` và `sys.stderr` bằng `io.TextIOWrapper(..., encoding="utf-8", errors="replace")` ngay ở đầu tệp `analyze_wallet.py`.

**Ai phát hiện:** AI tự nhận.

---

## Lần 3

**Prompt:**
```text
Chạy lại bộ kiểm tra tự động 6 điểm bắt buộc bằng lệnh: python analyze_wallet.py --test
```

**AI trả về:**
- Bộ tự kiểm tra hoàn thành nhưng tại mục `[1/6] Kiểm tra Khóa API (Security Check)`, hệ thống bất ngờ báo:
  ```text
  -> THẤT BẠI: Phát hiện có thể có khóa API được ghi cứng trong mã nguồn!
  ```

**Đánh giá:** Phải sửa.

**Chỗ sai:**
- Lỗi nhận diện sai (False Positive) trong logic kiểm tra an toàn: Hàm kiểm tra sử dụng so khớp chuỗi thô `if "api_key =" in line` trong mã nguồn. Dòng mã `api_key = get_api_key()` trong hàm `main()` đã bị nhận diện nhầm là hành vi hardcode khóa API, dù thực chất hàm `get_api_key()` đang lấy giá trị từ biến môi trường `os.getenv("ETHERSCAN_API_KEY")`.

**Cách sửa:**
- Sinh viên chỉ ra chỗ so khớp lỏng lẻo và yêu cầu sửa lại bằng biểu thức chính quy (Regex) chặt chẽ:
  ```python
  re.findall(r'(?:api_key|apikey|secret)\s*=\s*["\'][A-Za-z0-9]{15,}["\']', src, re.IGNORECASE)
  ```
  Chỉ cảnh báo khi có chuỗi literal chứa ký tự chữ/số độ dài lớn hơn 15 ký tự được gán trực tiếp.

**Ai phát hiện:** Sinh viên phát hiện.

---

## Lần 4

**Prompt:**
```text
Kiểm tra Điểm 5: Xử lý lỗi khi người dùng cung cấp khóa API sai (ví dụ: INVALID_TEST_KEY_123).
```

**AI trả về:**
- Khi chạy với khóa sai, Etherscan trả về JSON có `status="0"` và `result="Invalid API Key (#err2)"`.
- Ban đầu nếu mã cố truy cập `result` như một danh sách (`for tx in data["result"]`), Python sẽ duyệt từng ký tự của chuỗi hoặc ném `TypeError`.

**Đánh giá:** Dùng được.

**Chỗ sai:**
- Lỗi giả định cấu trúc dữ liệu luôn là danh sách giao dịch (List), không phòng thủ trường hợp lỗi API trả về `result` là chuỗi thông báo lỗi (String).

**Cách sửa:**
- Bổ sung cấu trúc kiểm tra `if status == "0"`: Trích xuất trực tiếp thông báo lỗi từ Etherscan (`message` và `result`), in thông báo hướng dẫn người dùng rõ ràng và kết thúc chương trình có kiểm soát (`sys.exit(1)`), đảm bảo không bao giờ làm bung màn hình lỗi Traceback.

**Ai phát hiện:** Sinh viên phát hiện.
