# Báo cáo Thực hành Lab 02 — Giao dịch trên Blockchain (Ethereum Sepolia)

## 1. Bảng so sánh giao dịch

| Trường | Giao dịch thành công | Giao dịch thất bại |
| :--- | :--- | :--- |
| **Mã băm giao dịch** | `0xaad397fe12c5762a20f43cdb445e91b054318f6741e6c8e5988ad66cb86502dd` | Không có (Giao dịch bị chặn tại ví, chưa được phát tán lên mạng on-chain) |
| **Số tiền chuyển** | `0.01 ETH` | `2,096 SepoliaETH` |
| **Phí giao dịch thực trả** | `0.000051818698806 ETH` | `0 ETH` (Chưa gửi vào block nên không tốn phí) |
| **Trạng thái** | Thành công (`Success` - Block 11770417) | Thất bại / Bị chặn (`Xem xét cảnh báo`) |
| **Nguyên nhân (nếu thất bại)** | Không có (Giao dịch hợp lệ, tài khoản đủ số dư) | Số dư ví `admid` không đủ để chi trả `2,096 SepoliaETH` cùng phí gas; MetaMask phát cảnh báo thiếu số dư (*Insufficient funds*) và ngăn chặn thực hiện giao dịch. |

---

## 2. Câu hỏi thảo luận

**Nếu bạn chuyển nhầm cho người lạ, có lấy lại được không? Vì sao?**

> Nếu bạn chuyển nhầm tiền mã hóa cho người lạ trên mạng blockchain, bạn hoàn toàn không thể tự ý lấy lại số tiền đó được. Nguyên nhân là do mạng blockchain hoạt động theo cơ chế phi tập trung với tính chất bất biến (immutability), không có cơ quan quản lý hay bên thứ ba trung gian nào có quyền can thiệp hay đảo ngược (revert) các giao dịch đã được xác nhận vào khối. Cách duy nhất để lấy lại tiền là chủ động liên hệ và trông chờ vào thiện chí của người nhận tự nguyện chuyển trả lại cho bạn.
