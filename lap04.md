# Báo Cáo Thẩm Định Hợp Đồng Token - Lab 04

Tệp nguồn thẩm định: [`contracts/lab04/ClubTokens.sol`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol)

---

## 1. Bảng kết luận thẩm định quyền đặc biệt và rủi ro

| Hợp đồng | Kết luận | Tên hàm | Số dòng | Rủi ro cho người nắm giữ |
| :--- | :--- | :--- | :---: | :--- |
| **A** *(ClubTokenA)* | **An toàn về mã nguồn** (Không có quyền đặc biệt) | *Không có* | *Không có* | **Không có rủi ro từ quyền đặc biệt của chủ sở hữu:**<br>- Hợp đồng chỉ kế thừa `ERC20`, không kế thừa `Ownable`, không định nghĩa bất kỳ hàm quản trị hay modifier phân quyền nào.<br>- Toàn bộ 1,000,000 token được đúc 1 lần duy nhất trong constructor tại [dòng 8–10](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L8-L10) (`_mint(msg.sender, 1_000_000 * 10 ** decimals())`). Sau khi triển khai, mã nguồn bất biến, không ai có quyền đúc thêm hay can thiệp giao dịch.<br>- *Rủi ro ngoài mã nguồn:* 100% token ban đầu thuộc về ví deployer (`msg.sender`). Nếu người này xả bán số lượng lớn thì giá token sẽ giảm. |
| **B** *(ClubTokenB)* | **Rủi ro cao** (Lạm phát vô hạn / Pha loãng tài sản) | [`mint(address to, uint256 amount)`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L18-L20) | [Dòng 18–20](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L18-L20) | **Rủi ro lạm phát không giới hạn & Rug-pull:**<br>- Hàm `mint` sử dụng modifier `onlyOwner` ([dòng 18](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L18)), cho phép duy nhất chủ sở hữu đúc thêm token tùy ý vào bất kỳ địa chỉ nào.<br>- Mã nguồn không có trần tổng cung tối đa (`cap`) và không có khóa thời gian (`Timelock`).<br>- Chủ sở hữu có thể tự đúc số lượng lớn token rồi bán tháo vào bể thanh khoản (DEX), khiến token của người nắm giữ bị pha loãng nghiêm trọng hoặc mất trắng giá trị. |
| **C** *(ClubTokenC)* | **Rủi ro nghiêm trọng** (Honeypot / Đóng băng tài sản tùy tiện) | [`setRestricted(address user, bool status)`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L30-L32)<br>*(tác động qua [`_update`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L34-L37))* | [Dòng 30–32](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L30-L32)<br>*(và [Dòng 34–37](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L34-L37))* | **Rủi ro bị chặn bán, đóng băng tài sản (Honeypot / Censorship):**<br>- Chủ sở hữu có quyền gọi `setRestricted` ([dòng 30–32](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L30-L32), `onlyOwner`) để gắn cờ bất kỳ ví nào vào danh sách hạn chế `restricted[user] = true` ([dòng 24](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L24)).<br>- Hàm nội bộ `_update` tại [dòng 34–37](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol#L34-L37) kiểm tra `require(!restricted[from], "Dia chi bi han che");`.<br>- Khi bị hạn chế, địa chỉ đó bị chặn hoàn toàn quyền gửi đi hoặc bán token ra thị trường, dẫn đến tài sản của người nắm giữ bị phong tỏa vô thời hạn theo ý muốn đơn phương của chủ sở hữu. |

---

## 2. So sánh kết quả: Đọc thủ công vs AI hỗ trợ

### a. Đọc thủ công tìm ra gì?
- **ClubTokenA:** Nhận diện được đây là token ERC-20 tiêu chuẩn đơn giản, không kế thừa `Ownable`, chỉ đúc 1,000,000 token ở constructor cho người tạo hợp đồng. Không tìm thấy hàm nào có quyền admin.
- **ClubTokenB:** Phát hiện có kế thừa `Ownable` và thấy hàm `mint(address to, uint256 amount)` có modifier `onlyOwner` ở dòng 18–20. Nhận biết được chủ sở hữu có thể tự in thêm token.
- **ClubTokenC:** Phát hiện `mapping restricted` ở dòng 24, hàm `setRestricted` có `onlyOwner` ở dòng 30–32 và điều kiện `require(!restricted[from])` ở dòng 35 trong `_update`. Nhận biết được chủ sở hữu có quyền cấm một địa chỉ chuyển token.

### b. AI tìm thêm được gì?
- **Phân tích cơ chế kinh tế và kịch bản tấn công (Attack Vectors):**
  - Với **Token B:** AI chỉ rõ thiếu trần tổng cung (`cap`) và thiếu cơ chế bảo vệ thời gian (`Timelock`), giải thích rõ rủi ro kinh tế cụ thể là *Pha loãng vô hạn (Unlimited Dilution)* và kịch bản *Rug-pull* khi chủ dự án xả token vào pool thanh khoản DEX.
  - Với **Token C:** AI phân tích bản chất cơ chế này chính là bẫy **Honeypot**: hàm `_update` chỉ chặn chiều chuyển đi (`from`) chứ không chặn chiều nhận vào (`to`). Nghĩa là người dùng vẫn có thể mua hoặc nạp thêm token vào ví nhưng khi muốn bán/chuyển đi thì giao dịch sẽ bị revert.
- **Nhận diện quyền kế thừa từ OpenZeppelin v5:**
  - AI chỉ ra rằng cả Token B và Token C đều thừa hưởng các hàm quản trị mặc định của `Ownable` gồm `transferOwnership` và `renounceOwnership`. Nếu chủ dự án từ bỏ quyền sở hữu (`renounceOwnership`), các rủi ro từ hàm `mint` hay `setRestricted` sẽ được loại bỏ hoàn toàn.
- **Đánh giá rủi ro ngoài mã nguồn của Token A:**
  - AI lưu ý rằng dù Token A không có backdoor trong mã nguồn, nhưng 100% cung ban đầu thuộc về 1 ví triển khai nên vẫn tồn tại rủi ro tập trung hóa phân bổ (Centralization/Allocation Risk).

### c. AI có nói sai chỗ nào không?
- **Nhận diện tình trạng thiếu đầu vào:** Ở lượt phản hồi đầu tiên khi người dùng chưa cung cấp mã nguồn trực tiếp trong câu lệnh, AI đã tuân thủ đúng nguyên tắc của prompt thẩm định là cảnh báo thiếu dữ liệu trước khi hỗ trợ đọc mã từ tệp có sẵn.
- **Độ chính xác về số dòng:** AI đối chiếu chính xác từng dòng mã trong tệp `ClubTokens.sol` (dòng 8–10 của Token A; dòng 18–20 của Token B; dòng 24, 30–32, 34–37 của Token C), không bị hiện tượng ảo giác số dòng.
- **Tuân thủ nguyên tắc không khẳng định mã an toàn tuyệt đối:** AI không khẳng định Token A hoàn toàn không có rủi ro, mà phân định rõ rủi ro logic on-chain và rủi ro phân bổ thị trường, đúng theo quy ước thẩm định của `AGENTS.md`.
