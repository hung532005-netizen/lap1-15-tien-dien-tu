# Báo Cáo Điều Tra & Phân Tích Blockchain (Forensics Report)

## Bước 1: Bảng 10 trường thông tin giao dịch và ý nghĩa nghiệp vụ

Giao dịch mẫu phân tích: `0xaad397fe12c5762a20f43cdb445e91b054318f6741e6c8e5988ad66cb86502dd`

| STT | Trường | Ý nghĩa | Vì sao người làm nghiệp vụ cần | Giá trị thực tế từ giao dịch |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **Status** | Thành công hay thất bại | Giao dịch thất bại vẫn mất phí — ảnh hưởng hạch toán | `Success` |
| 2 | **Block** | Số thứ tự khối chứa giao dịch | Xác định thời điểm ghi nhận và số xác nhận (confirmations) | `11770417` |
| 3 | **Timestamp** | Thời gian tạo khối / khớp lệnh | Mốc ghi nhận doanh thu / chi phí kế toán theo chuẩn thời gian thực | `Sep-24-2026 07:05:36 AM +UTC` |
| 4 | **From / To** | Ví gửi / ví nhận | Đối tượng cần xác minh danh tính (KYC/AML), đối soát công nợ | **From:** `0xB22A4B327EdB0774Dbe3dad0B4e9780f8BaB322E`<br>**To:** `0x8321641822DA45762adAd0229Fc685369C9F319c` |
| 5 | **Value** | Số tiền chuyển | Giá trị thanh toán/giao dịch thực tế | `0.01 ETH` |
| 6 | **Transaction Fee** | Phí thực trả | Chi phí giao dịch mạng lưới, cần hạch toán chi phí tài chính riêng | `0.000051818698806 ETH` |
| 7 | **Gas Price** | Đơn giá phí gas (theo Gwei/ETH) | Giải thích vì sao cùng một loại giao dịch mà các thời điểm khác nhau phí lại khác nhau (tùy thuộc vào mức độ tắc nghẽn mạng) | `2.467557086 Gwei` *(0.000000002467557086 ETH)* |
| 8 | **Gas Limit** | Mức gas tối đa ví gửi cho phép dùng | Đặt quá thấp → giao dịch thất bại vì hết gas (*Out of Gas*) nhưng vẫn mất phí | `21,000` *(mức chuẩn cho giao dịch chuyển native ETH)* |
| 9 | **Gas Used** | Lượng gas thực tế đã tiêu thụ | Cùng Gas Price với Gas Used tính ra phí:<br>$$\text{Transaction Fee} = \text{Gas Used} \times \text{Gas Price}$$<br>Nếu $\text{Gas Used} = \text{Gas Limit}$ là dấu hiệu cảnh báo giao dịch bị cạn gas | `21,000 (100%)` |
| 10 | **Nonce** | Số thứ tự giao dịch của ví gửi | Phát hiện giao dịch bị bỏ sót, trùng lặp hoặc bị ghi đè/thay thế (*Speed Up / Cancel*) | Thứ tự giao dịch từ ví gửi |

---

## Bước 2: Phân tích hợp đồng thông minh `0xdAC17F958D2ee523a2206206994597C13D831ec7` (Tether USD - USDT)

### 1. Hợp đồng bạn xem có công bố mã nguồn đã xác thực không?
- **Trả lời:** **Có.**
- **Chi tiết:** Trên Etherscan, hợp đồng `0xdAC17F958D2ee523a2206206994597C13D831ec7` đã được xác thực mã nguồn (hiển thị tích xanh **Contract Source Code Verified - Exact Match**). Người dùng có thể vào tab **Contract -> Code** để đọc toàn bộ mã nguồn Solidity công khai và ABI của hợp đồng.

### 2. Tổng cung của đồng đó là bao nhiêu? Đọc ra từ hàm nào?
- **Đọc ra từ hàm:** Hàm **`totalSupply()`** (nằm trong tab **Read Contract**).
  - Khai báo chuẩn ERC-20: `function totalSupply() public view returns (uint256)`
- **Tổng cung thực tế:**
  - Token USDT sử dụng `decimals = 6`. Vì vậy, giá trị số nguyên trả về từ hàm `totalSupply()` cần chia cho $10^6$ để ra số lượng token USDT thực tế.
  - Trên Etherscan (mục Token Tracker), tổng cung USDT trên mạng Ethereum hiện tại là hơn **70 tỷ USDT** (dao động biến động theo hoạt động Mint / Burn của Tether Treasury).

### 3. Trong tab Write Contract (với USDC: Write as Proxy), có hàm nào cho phép một địa chỉ đặc biệt đóng băng tài khoản người khác không? Nếu có, tên hàm là gì?
- **Trả lời:** **Có.**
- **Tên hàm:**
  - Với **USDT** (`0xdAC17F958D2ee523a2206206994597C13D831ec7`):
    - Trong tab **Write Contract**, hàm cho phép đóng băng tài khoản là:
      ```solidity
      addBlackList(address _evilUser)
      ```
    - **Quyền hạn:** Chỉ tài khoản người quản trị (`owner`) của hợp đồng mới có quyền gọi hàm này (thông qua modifier `onlyOwner`). Khi một địa chỉ bị đưa vào blacklist, địa chỉ đó không thể gửi hoặc nhận USDT.
    - Các hàm liên quan:
      - `removeBlackList(address _clearedUser)`: Gỡ bỏ địa chỉ khỏi danh sách đen (mở đóng băng).
      - `destroyBlackFunds(address _blackListedUser)`: Cho phép chủ hợp đồng tiêu hủy vĩnh viễn số USDT có trong ví đang bị đóng băng.
      - `getBlackListStatus(address)` hoặc `isBlackListed(address)` (trong tab **Read Contract**): Kiểm tra trạng thái đóng băng của một ví.
  - *(Tham khảo thêm với **USDC** - USD Coin trên tab **Write as Proxy**)*:
    - Hàm tương ứng là `blacklist(address _account)` do địa chỉ có vai trò `blacklister` gọi, và gỡ đóng băng bằng hàm `unBlacklist(address _account)`.
