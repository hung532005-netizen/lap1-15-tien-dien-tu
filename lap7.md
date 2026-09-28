# BÁO CÁO NỘP BÀI - LAB 07 (ECO2432)
## Bài toán Kinh tế: Phân tích Chi phí Vận hành (Gas Economics) và Thẩm định Tính khả thi Ứng dụng Blockchain

> **Môn học:** ECO2432 – Web3 Starter  
> **Nguyên lý cốt lõi:** *"Đây là bài toán kinh tế, không phải bài toán kỹ thuật — Một sản phẩm chạy được về mặt kỹ thuật nhưng chi phí giao dịch cao hơn giá trị giao dịch thì không có mô hình kinh doanh."* (Ứng dụng Lý thuyết Chi phí Giao dịch - Transaction Cost Economics của Ronald Coase).  
> **Chuẩn đầu ra:** Sinh viên tính toán chính xác chi phí vận hành hàng tháng của hệ thống Smart Contract trên các tầng mạng khác nhau (Layer 1 vs Layer 2), phân tích đối tượng chịu phí, hành vi người dùng và kết luận chuẩn xác về tính khả thi kinh tế.

---

## BƯỚC 1: HIỂU CẤU TRÚC PHÍ GIAO DỊCH (GAS ECONOMICS)

### 1. Bản chất kinh tế của Gas trong EVM (Ethereum Virtual Machine)
- **Gas không phải là một loại tiền tệ:** Gas là đơn vị định lượng chuẩn hóa mức độ tiêu hao tài nguyên tính toán (CPU, bộ nhớ RAM) và tài nguyên lưu trữ trạng thái lâu dài (Disk Storage - SSTORE) trên mạng lưới phi tập trung.
- **Cơ chế định giá theo thị trường (EIP-1559):**
  $$\text{Đơn giá Gas (Gas Price)} = \text{Base Fee} + \text{Priority Fee (Tip)}$$
  Trong đó:
  - $\text{Base Fee}$: Phí cơ sở do giao thức tự động điều chỉnh theo nhu cầu khối của mạng lưới (được đốt bỏ để giảm lạm phát ETH).
  - $\text{Priority Fee}$: Tiền thưởng khuyến khích validator ưu tiên đóng gói giao dịch.
  - Đơn vị tính: $1\text{ Gwei} = 10^{-9}\text{ ETH} = 0,000000001\text{ ETH}$.

### 2. Công thức tính chi phí giao dịch
$$\text{Chi phí giao dịch (ETH)} = \text{Lượng gas tiêu thụ} \times \text{Đơn giá gas (Gwei)} \times 10^{-9}$$
$$\text{Chi phí giao dịch (USD)} = \text{Chi phí giao dịch (ETH)} \times \text{Giá ETH (USD)}$$

### 3. Phân tích chi phí tính toán so với chi phí lưu trữ (Storage vs. Computation)
- **Chi phí cố định (Base Gas):** Mọi giao dịch gửi lên Ethereum đều tiêu tốn tối thiểu $21.000\text{ gas}$ để xác thực chữ ký mật mã (ECDSA) và khởi tạo giao dịch.
- **Chi phí lưu trữ (State Storage - SSTORE) là thao tác đắt đỏ nhất:**
  - Ghi một biến mới vào ô nhớ lâu dài (từ giá trị `0` thành khác `0`): Tiêu tốn $\sim 20.000\text{ gas}$.
  - Sửa đổi một biến đã tồn tại (từ khác `0` thành khác `0`): Tiêu tốn $\sim 5.000\text{ gas}$.
  - *Lý do kinh tế:* Dữ liệu lưu trong State Storage đòi hỏi toàn bộ hàng chục nghìn Full Node trên thế giới phải lưu trữ vĩnh viễn trong ổ cứng SSD (gây ra hiện tượng phình to trạng thái - State Bloat). Cơ chế Gas phải định giá rất đắt cho SSTORE để ngăn chặn tấn công spam tài nguyên mạng.
- **Tại sao Layer 2 Rollups (Base, Arbitrum, Optimism) lại rẻ hơn $\sim 100$ lần:**
  - Layer 2 thực thi tính toán và cập nhật state ở bên ngoài (off-chain), sau đó nén hàng nghìn giao dịch thành một gói dữ liệu (Rollup batch) và chỉ gửi bằng chứng/dữ liệu blob (EIP-4844 blobs) về Layer 1.
  - Chi phí gas Layer 1 được chia đều cho hàng ngàn người dùng, giúp đơn giá hiệu dụng trên mỗi giao dịch giảm từ $50 - 100$ lần (thậm chí tới $200 - 500$ lần sau nâng cấp Dencun).

---

## BƯỚC 2: BÀI TOÁN KINH TẾ CÂU LẠC BỘ SINH VIÊN (THẺ TÍCH ĐIỂM BLOCKCHAIN)

### 1. Thông số đầu vào của mô hình
- **Quy mô hoạt động:** $N = 1.000\text{ lượt cộng điểm/tháng}$.
- **Bản chất nghiệp vụ:** Mỗi lượt cộng điểm là một giao dịch gọi Smart Contract ghi nhận dữ liệu vào bộ nhớ lâu dài (cập nhật số dư điểm của sinh viên).
- **Điều kiện thị trường giả định:**
  - Đơn giá gas: $20\text{ Gwei} = 20 \times 10^{-9}\text{ ETH}$.
  - Giá ETH thị trường: $3.000\text{ USD/ETH}$.

### 2. Xác định các kịch bản tiêu thụ Gas
Để bảo đảm tính khách quan và khoa học kinh tế, bài toán được phân tích qua 3 kịch bản tiêu thụ gas:
- **Kịch bản A (Gas lý thuyết thuần SSTORE - $20.000\text{ gas}$):** Căn cứ theo định mức ghi biến mới độc lập trong tài liệu tham khảo.
- **Kịch bản B (Giao dịch ghi dữ liệu thực tế - $50.000\text{ gas}$):** Bao gồm $21.000\text{ base gas}$ + phí nạp calldata + logic cập nhật mapping điểm danh/điểm thưởng.
- **Kịch bản C (Giao dịch chuẩn Token ERC-20 - $65.000\text{ gas}$):** Áp dụng mô hình chuẩn `ClubTokens.sol` / `ClassPoint.sol` (gồm kiểm tra quyền hạn `onlyOwner`, cập nhật `balanceOf`, `totalSupply` và phát sinh `Transfer` event).

---

### 3. Bảng tính toán chi phí vận hành hàng tháng (Câu a & Câu b)

| Chỉ số tính toán | Công thức / Đơn vị | Kịch bản A<br>*(20.000 gas)* | Kịch bản B (Thực tế)<br>*(50.000 gas)* | Kịch bản C (Chuẩn ERC-20)<br>*(65.000 gas)* |
| :--- | :---: | :---: | :---: | :---: |
| **Lượng gas / 1 giao dịch** | $\text{Gas}$ | $20.000$ | $50.000$ | $65.000$ |
| **Đơn giá gas L1** | $\text{Gwei}$ | $20$ | $20$ | $20$ |
| **Phí 1 giao dịch L1 (ETH)** | $\text{Gas} \times 20 \times 10^{-9}$ | $0,00040\text{ ETH}$ | $0,00100\text{ ETH}$ | $0,00130\text{ ETH}$ |
| **Phí 1 giao dịch L1 (USD)** | $\text{Phí ETH} \times 3.000$ | **$1,20 USD** | **$3,00 USD** | **$3,90 USD** |
| Quy đổi VNĐ (tỷ giá 25.000) | $\text{VNĐ/lượt}$ | $\sim 30.000\text{ VNĐ}$ | $\sim 75.000\text{ VNĐ}$ | $\sim 97.500\text{ VNĐ}$ |
| **(a) TỔNG CHI PHÍ THÁNG - LAYER 1 (USD)** | $\text{Phí 1 tx} \times 1.000$ | **$1.200 USD** | **$3.000 USD** | **$3.900 USD** |
| **Tổng chi phí tháng - Layer 1 (VNĐ)** | $\text{Tổng USD} \times 25.000$ | **30.000.000 VNĐ** | **75.000.000 VNĐ** | **97.500.000 VNĐ** |
| --- | --- | --- | --- | --- |
| **Hệ số giảm giá Layer 2** | $\text{Rẻ hơn } 100 \text{ lần}$ | $\div 100$ | $\div 100$ | $\div 100$ |
| **Phí 1 giao dịch L2 (USD)** | $\text{Phí L1} / 100$ | **$0,012 USD** | **$0,030 USD** | **$0,039 USD** |
| Quy đổi VNĐ L2 (tỷ giá 25.000) | $\text{VNĐ/lượt}$ | $\sim 300\text{ VNĐ}$ | $\sim 750\text{ VNĐ}$ | $\sim 975\text{ VNĐ}$ |
| **(b) TỔNG CHI PHÍ THÁNG - LAYER 2 (USD)** | $\text{Tổng L1} / 100$ | **$12 USD** | **$30 USD** | **$39 USD** |
| **Tổng chi phí tháng - Layer 2 (VNĐ)** | $\text{Tổng USD} \times 25.000$ | **300.000 VNĐ** | **750.000 VNĐ** | **975.000 VNĐ** |

---

### 4. Phân tích đối tượng chịu phí & Hành vi chấp nhận (Câu c)

#### *Câu hỏi: Ai trả khoản phí này — Câu lạc bộ hay Sinh viên? Nếu sinh viên trả, họ có chấp nhận không?*

#### Phân tích Kinh tế Vi mô & Chi phí Giao dịch:
1. **Giá trị kinh tế thực của một lượt tích điểm:**
   - Một giao dịch tiêu dùng thông thường của sinh viên (mua ly trà sữa, suất cơm trưa, mua giáo trình) có giá trị từ $25.000 - 50.000\text{ VNĐ}$ ($\sim 1 - 2\text{ USD}$).
   - Lợi ích tích lũy điểm thưởng thông thường trong kinh tế bán lẻ chỉ đạt $5\% - 10\%$ giá trị hóa đơn $\rightarrow$ Mỗi lượt cộng điểm có giá trị thặng dư thực tế khoảng **$1.000 - 2.500\text{ VNĐ}$ ($\sim 0,04 - 0,10\text{ USD}$)**.

2. **Kịch bản trên Layer 1 (Ethereum Mainnet):**
   - **Nếu Sinh viên trả:**
     - Sinh viên nhận được điểm thưởng trị giá $2.000\text{ VNĐ}$, nhưng phải trả phí gas từ **$30.000 - 75.000\text{ VNĐ}$ ($1,20 - 3,00\text{ USD}$)**.
     - **Tỷ lệ Phí / Giá trị nhận được:** $\text{Phí gas} \approx 1500\% - 3750\%$ giá trị điểm thưởng!
     - *Hành vi sinh viên:* **Chắc chắn 100% sinh viên từ chối sử dụng.** Trong lý thuyết kinh tế học hành vi, không một cá nhân duy lý nào bỏ ra $75.000\text{ VNĐ}$ tiền phí để nhận về món quà/điểm thưởng trị giá $2.000\text{ VNĐ}$.
   - **Nếu Câu lạc bộ trả:**
     - Ngân sách duy trì hoạt động hàng tháng của một CLB sinh viên thông thường chỉ dao động từ $500.000 - 2.000.000\text{ VNĐ/tháng}$.
     - Phải gánh khoản phí gas từ **$30.000.000 - 75.000.000\text{ VNĐ/tháng}$ ($1.200 - $3.000 USD)** sẽ khiến ngân quỹ CLB thâm hụt nghiêm trọng và phá sản ngay tháng đầu tiên.

3. **Kịch bản trên Layer 2 (Rollups: Base / Arbitrum / Optimism):**
   - Phí cho mỗi lượt cộng điểm giảm xuống chỉ còn **$300 - 750\text{ VNĐ}$ ($0,012 - 0,030\text{ USD}$)**.
   - Tổng chi phí tháng cho $1.000$ lượt chỉ còn **$300.000 - 750.000\text{ VNĐ}$ ($12 - 30\text{ USD}$)**.
   - **Mô hình khuyến nghị tối ưu:** **CÂU LẠC BỘ TRẢ KHOẢN PHÍ NÀY**.
     - *Lý do kinh tế và UX:* Nếu bắt sinh viên tự trả $500\text{ VNĐ}$, sinh viên phải thực hiện quy trình phức tạp: tạo ví Web3, mua ETH, bridge sang Layer 2 để dự trữ làm gas. Chi phí ma sát tâm lý và rào cản kỹ thuật sẽ triệt tiêu người dùng.
     - *Giải pháp công nghệ hỗ trợ kinh tế:* CLB áp dụng chuẩn **Account Abstraction (ERC-4337)** kết hợp hợp đồng **Paymaster (Gas Sponsorship)**. CLB nạp trước $30\text{ USD/tháng}$ vào quỹ Paymaster để tài trợ phí giao dịch (`gasless transaction`). Sinh viên chỉ cần quét mã QR đăng nhập bằng Google/Email, nhận điểm tức thì với trải nghiệm mượt mà như Web2 nhưng vẫn hưởng trọn tính minh bạch on-chain.

---

### 5. Kết luận về tính khả thi kinh tế (Câu d)

- **Mạng Layer 1 (Ethereum Mainnet):** **HOÀN TOÀN BẤT KHẢ THI (Economically Infeasible)**.
  - Mô hình kinh doanh bị đổ vỡ hoàn toàn do nghịch lý chi phí: $\text{Chi phí vận hành giao dịch} \gg \text{Giá trị kinh tế giao dịch mang lại}$.
- **Mạng Layer 2 (Base, Arbitrum, Optimism):** **HOÀN TOÀN KHẢ THI (Economically Feasible & Sustainable)**.
  - Tổng chi phí $\sim 300.000 - 750.000\text{ VNĐ/tháng}$ hoàn toàn nằm trong khả năng cân đối ngân quỹ của CLB hoặc kêu gọi nhà tài trợ địa phương (quán cà phê, nhà sách liên kết xung quanh trường đại học).

---

## BƯỚC 3: MỞ RỘNG CHO Ý TƯỞNG ĐỒ ÁN NHÓM (CAMPUS WEB3 PROJECT)

### 1. Ý tưởng đồ án nhóm
- **Tên đồ án:** **HCE CampusFund & Student Activity Point (SAP)**  
  *(Hệ thống Quản lý Quỹ Sinh Viên & Tích Lũy Điểm Hoạt Động Phong Trào Phi Tập Trung)*
- **Kế thừa kiến trúc:** Mở rộng từ hợp đồng [`ClassPoint.sol`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/training/ClassPoint.sol) và [`ClubTokens.sol`](file:///d:/BAITAPLAP/LAP1/hce-web3-starter/contracts/lab04/ClubTokens.sol) thuộc môn học ECO2432.
- **Quy mô hoạt động dự kiến:** Phục vụ $1$ Liên chi Đoàn / Hội Sinh viên cấp Khoa gồm $\sim 300\text{ sinh viên}$ đang sinh hoạt thường xuyên.

### 2. Dự báo cơ cấu giao dịch hàng tháng

| Mã | Loại nghiệp vụ Smart Contract | Logic thực thi | Ước tính Gas/tx | Tần suất (tx/tháng) | Tổng Gas tiêu thụ/tháng |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **TX1** | Điểm danh & cộng điểm rèn luyện | Ghi nhận mapping thành viên (`SSTORE`) | $45.000$ | $800$ | $36.000.000$ |
| **TX2** | Đổi điểm lấy voucher / giáo trình cũ | Kiểm tra số dư, trừ token, phát event | $55.000$ | $200$ | $11.000.000$ |
| **TX3** | Biểu quyết giải ngân quỹ (Voting DAO) | Kiểm tra quyền thành viên, tăng biến đếm phiếu | $35.000$ | $250$ | $8.750.000$ |
| **TX4** | Đóng góp quỹ lớp & Giải ngân chi tiêu | Kiểm tra Multi-sig, chuyển quỹ nội bộ | $65.000$ | $50$ | $3.250.000$ |
| **TỔNG** | **Toàn bộ hoạt động trong 1 tháng** | — | — | **1.300 tx** | **59.000.000 gas** |

---

### 3. Bảng so sánh chi phí vận hành hàng tháng của đồ án

*Giả định: Giá ETH = $3.000 USD, Đơn giá gas L1 = 20 Gwei, Layer 2 (Base/Arbitrum) rẻ hơn 100 lần, Tỷ giá 1 USD = 25.000 VNĐ.*

| Khoản mục chi phí | Đơn vị | Mạng Ethereum L1 | Mạng Layer 2 (Base / Arbitrum) | Chênh lệch tiết kiệm |
| :--- | :---: | :---: | :---: | :---: |
| **Tổng lượng Gas tiêu thụ** | $\text{gas/tháng}$ | $59.000.000$ | $59.000.000$ | $0\%$ |
| **Tổng phí gas tiêu thụ (ETH)** | $\text{ETH/tháng}$ | $1,1800\text{ ETH}$ | $0,0118\text{ ETH}$ | Giảm $99\%$ |
| **Tổng chi phí vận hành (USD)** | $\text{USD/tháng}$ | **$3.540,00 USD** | **$35,40 USD** | Tiết kiệm **$3.504,60 USD** |
| **Tổng chi phí vận hành (VNĐ)** | $\text{VNĐ/tháng}$ | **88.500.000 VNĐ** | **885.000 VNĐ** | Tiết kiệm **87.615.000 VNĐ** |
| **Chi phí trung bình trên 1 sinh viên** | $\text{VNĐ/sv/tháng}$ | $295.000\text{ VNĐ}$ | **$2.950 VNĐ** | Giảm $99\%$ |

---

### 4. Đánh giá tính khả thi kinh tế & Kế hoạch cân đối tài chính của đồ án nhóm

1. **Phân tích khả năng tự nuôi dưỡng tài chính (Financial Self-Sustainability):**
   - Chi phí vận hành trên Layer 2 chỉ là **$885.000\text{ VNĐ/tháng}$** (tương đương mỗi sinh viên chỉ tiêu tốn chưa đầy $3.000\text{ VNĐ/tháng}$).
   - **Nguồn doanh thu bù đắp chi phí:**
     - *Phí dịch vụ trích lập:* Kế thừa cơ chế `feeBps = 100` (1%) từ `ClassPoint.sol`, trích lại $1\%$ trên tổng lượng giao dịch nộp và giải ngân quỹ lớp ($\sim 200.000\text{ VNĐ/tháng}$).
     - *Tài trợ thương mại địa phương:* Hợp tác với $2$ quán cà phê / cửa hàng photocopy gần trường để hiển thị voucher đổi điểm thưởng; mỗi đối tác tài trợ phí duy trì hệ thống $500.000\text{ VNĐ/tháng}$ $\rightarrow$ Thu nhập: $1.000.000\text{ VNĐ/tháng}$.
     - *Cân đối dòng tiền:* $\text{Dòng tiền thu} (1.200.000\text{ VNĐ}) > \text{Chi phí vận hành L2} (885.000\text{ VNĐ})$. Dự án đạt thặng dư tài chính **$+315.000\text{ VNĐ/tháng}$**.

2. **Kết luận thẩm định đồ án:**
   - Đồ án nhóm **hoàn toàn khả thi về mặt kinh tế** khi và chỉ khi được triển khai trên **Layer 2**.
   - **Khuyến nghị kiến trúc công nghệ cho đồ án:**
     1. Lựa chọn triển khai hợp đồng trên mạng **Base** hoặc **Arbitrum One** để tối ưu hóa chi phí và thừa hưởng bảo mật của Ethereum.
     2. Tích hợp giải pháp **Account Abstraction (ERC-4337)** qua nhà cung cấp dịch vụ Paymaster (Biconomy / ZeroDev / Alchemy) để tài trợ toàn bộ phí gas cho sinh viên.
     3. Loại bỏ hoàn toàn ý định triển khai trực tiếp trên Layer 1 để tránh thất bại về mô hình kinh doanh.
