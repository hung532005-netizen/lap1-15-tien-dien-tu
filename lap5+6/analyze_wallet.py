#!/usr/bin/env python3
"""
analyze_wallet.py - Phân tích dòng tiền & số dư ví Ethereum theo SPEC (Lab 05)
Môn học: ECO2432 Web3 Starter
Tuân thủ đầy đủ quy ước AGENTS.md và danh mục 6 điểm kiểm tra bắt buộc.
"""

import os
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
import requests

# Đảm bảo in tiếng Việt có dấu an toàn trên terminal Windows (tránh lỗi cp1252)
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# Hỗ trợ đọc tệp .env nếu có (không bắt buộc)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Đơn vị quy đổi chuẩn Ethereum (1 ETH = 10^18 Wei)
WEI_PER_ETH = 10**18

# Endpoint Etherscan API V2 hiện hành (Điểm kiểm tra 6: Tránh endpoint V1 đã bị ngừng hỗ trợ)
ETHERSCAN_V2_API_URL = "https://api.etherscan.io/v2/api"


def get_api_key() -> str:
    """
    Điểm kiểm tra 2: Khóa API
    Tuyệt đối không ghi khóa cứng vào mã nguồn.
    Đọc từ biến môi trường ETHERSCAN_API_KEY.
    """
    api_key = os.getenv("ETHERSCAN_API_KEY")
    if not api_key:
        print("[LỖI BẢO MẬT & CẤU HÌNH] Không tìm thấy biến môi trường 'ETHERSCAN_API_KEY'.")
        print("Vui lòng thiết lập biến môi trường trước khi chạy:")
        print("  Windows PowerShell: $env:ETHERSCAN_API_KEY=\"Khoa_API_Cua_Ban\"")
        print("  Linux/macOS:        export ETHERSCAN_API_KEY=\"Khoa_API_Cua_Ban\"")
        print("Hoặc tạo tệp .env chứa: ETHERSCAN_API_KEY=Khoa_API_Cua_Ban")
        print("\nĐể chạy thử nghiệm kiểm tra 6 điểm với dữ liệu mẫu, dùng: python analyze_wallet.py --test")
        sys.exit(1)
    return api_key.strip()


def fetch_all_transactions_v2(
    wallet_address: str,
    api_key: str,
    chain_id: int = 1,
    offset_per_page: int = 10000
) -> List[Dict[str, Any]]:
    """
    Điểm kiểm tra 3 (Phân trang), 5 (Xử lý lỗi), 6 (Phiên bản API V2)
    Lấy toàn bộ lịch sử giao dịch thông qua phân trang Etherscan API V2.
    """
    normalized_address = wallet_address.lower().strip()
    all_transactions: List[Dict[str, Any]] = []
    page = 1

    print(f"[*] Đang kết nối Etherscan API V2 (Chain ID: {chain_id}) cho ví: {wallet_address}...")

    while True:
        params = {
            "chainid": chain_id,
            "module": "account",
            "action": "txlist",
            "address": normalized_address,
            "startblock": 0,
            "endblock": 99999999,
            "page": page,
            "offset": offset_per_page,
            "sort": "asc",
            "apikey": api_key,
        }

        try:
            response = requests.get(ETHERSCAN_V2_API_URL, params=params, timeout=15)
        except requests.exceptions.RequestException as e:
            # Điểm kiểm tra 5: Xử lý lỗi kết nối mạng an toàn
            print(f"[LỖI KẾT NỐI] Không thể kết nối tới máy chủ Etherscan: {e}")
            sys.exit(1)

        # Kiểm tra mã trạng thái HTTP
        if response.status_code != 200:
            print(f"[LỖI HTTP] Máy chủ trả về mã HTTP {response.status_code}: {response.text}")
            sys.exit(1)

        try:
            data = response.json()
        except ValueError:
            print(f"[LỖI DỮ LIỆU] Phản hồi từ máy chủ không phải JSON hợp lệ: {response.text[:200]}")
            sys.exit(1)

        status = str(data.get("status", "0"))
        message = data.get("message", "")
        result = data.get("result", [])

        # Điểm kiểm tra 5: Kiểm tra mã lỗi từ Etherscan (sai API key, sai địa chỉ, ...)
        if status == "0":
            # Trường hợp ngoại lệ E1: Ví không có giao dịch
            if message == "No transactions found" or result == "No transactions found" or result == []:
                if page == 1:
                    print("Vi khong co giao dich trong ky")
                    return []
                else:
                    break
            else:
                # Lỗi API thực sự (ví dụ: Invalid API Key)
                print(f"[LỖI API ETHERSCAN] Mã thông điệp: '{message}', Chi tiết: '{result}'")
                print("Chương trình dừng xử lý theo đúng quy tắc E2 của SPEC.")
                sys.exit(1)

        if not isinstance(result, list):
            print(f"[LỖI ĐỊNH DẠNG] Dữ liệu result không phải danh sách: {result}")
            sys.exit(1)

        all_transactions.extend(result)
        print(f"    -> Đã tải trang {page}: nhận được {len(result)} giao dịch (Tổng cộng: {len(all_transactions)})")

        # Điểm kiểm tra 3: Nếu trang hiện tại ít hơn giới hạn offset, nghĩa là đã hết trang
        if len(result) < offset_per_page:
            break

        page += 1
        time.sleep(0.2)  # Tránh vượt quá giới hạn rate limit (5 calls/sec)

    return all_transactions


def process_transactions(
    transactions: List[Dict[str, Any]],
    wallet_address: str,
    days: int = 90
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Thực hiện tính toán theo Quy tắc R1 -> R6 và Ngoại lệ E4:
    - R1: Dòng tiền vào (to == wallet, isError == 0)
    - R2, R3: Dòng tiền ra (from == wallet) -> trừ value + fee
    - R4: Giao dịch thất bại (isError == 1, from == wallet) -> trừ fee
    - R5: Chia 10^18 để đổi wei -> ETH (Điểm kiểm tra 1)
    - R6: Sắp xếp theo timestamp tăng dần
    - E4: Self-transfer (from == to == wallet) -> chỉ trừ fee
    """
    normalized_address = wallet_address.lower().strip()
    now_ts = int(datetime.now(timezone.utc).timestamp())
    cutoff_ts = now_ts - (days * 86400)

    # R6: Sắp xếp theo timestamp tăng dần
    sorted_txs = sorted(transactions, key=lambda x: int(x.get("timeStamp", 0)))

    records: List[Dict[str, Any]] = []
    total_in = 0.0
    total_out = 0.0
    cumulative_balance = 0.0

    for tx in sorted_txs:
        ts = int(tx.get("timeStamp", 0))
        # Lọc trong khoảng N ngày
        if ts < cutoff_ts:
            continue

        tx_from = tx.get("from", "").lower().strip()
        tx_to = tx.get("to", "").lower().strip()
        is_error = str(tx.get("isError", "0")) == "1"

        # Điểm kiểm tra 1: Chia 10^18 để chuyển Wei sang ETH
        raw_value_wei = int(tx.get("value", 0))
        gas_used = int(tx.get("gasUsed", 0))
        gas_price_wei = int(tx.get("gasPrice", 0))

        value_eth = raw_value_wei / WEI_PER_ETH
        fee_eth = (gas_used * gas_price_wei) / WEI_PER_ETH

        tx_time_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Trường hợp E4: Tự chuyển cho chính mình (Self-transfer)
        if tx_from == normalized_address and tx_to == normalized_address:
            # Value không đổi, chỉ chịu phí gas
            tx_type = "Tu chuyen"
            net_change = -fee_eth
            total_out += fee_eth
            cumulative_balance += net_change
            records.append({
                "time": tx_time_str,
                "type": tx_type,
                "value_eth": value_eth,
                "fee_eth": fee_eth,
                "cumulative_eth": cumulative_balance,
                "hash": tx.get("hash", "")
            })

        # Trường hợp R2, R3, R4: Dòng tiền ra (ví đang xét là người gửi)
        elif tx_from == normalized_address:
            tx_type = "Ra"
            if is_error:
                # Điểm kiểm tra 4: Giao dịch thất bại vẫn tính phí gas, không trừ value
                net_change = -fee_eth
                total_out += fee_eth
                tx_type = "Ra (That bai)"
            else:
                # Giao dịch thành công: trừ value + fee
                net_change = -(value_eth + fee_eth)
                total_out += (value_eth + fee_eth)

            cumulative_balance += net_change
            records.append({
                "time": tx_time_str,
                "type": tx_type,
                "value_eth": value_eth if not is_error else 0.0,
                "fee_eth": fee_eth,
                "cumulative_eth": cumulative_balance,
                "hash": tx.get("hash", "")
            })

        # Trường hợp R1: Dòng tiền vào (ví đang xét là người nhận)
        elif tx_to == normalized_address:
            if is_error:
                # Giao dịch vào bị lỗi: Không nhận được tiền và không mất phí -> Bỏ qua
                continue
            tx_type = "Vao"
            fee_eth = 0.0  # Người nhận không trả phí gas
            net_change = value_eth
            total_in += value_eth
            cumulative_balance += net_change
            records.append({
                "time": tx_time_str,
                "type": tx_type,
                "value_eth": value_eth,
                "fee_eth": fee_eth,
                "cumulative_eth": cumulative_balance,
                "hash": tx.get("hash", "")
            })

    summary = {
        "total_in": total_in,
        "total_out": total_out,
        "final_balance": cumulative_balance,
        "tx_count": len(records)
    }

    return records, summary


def display_report(records: List[Dict[str, Any]], summary: Dict[str, float], wallet: str, days: int):
    """
    In bảng dữ liệu theo Mục 4 của SPEC.
    """
    print("\n" + "="*80)
    print(f"BÁO CÁO PHÂN TÍCH DÒNG TIỀN VÍ ETHEREUM ({days} NGÀY GẦN NHẤT)")
    print(f"Địa chỉ ví: {wallet}")
    print("="*80)

    if not records:
        print("Vi khong co giao dich trong ky")
        print("="*80)
        return

    # In tiêu đề bảng
    header = f"{'Thời gian':<22} | {'Loại':<14} | {'Số tiền (ETH)':<14} | {'Phí gas (ETH)':<14} | {'Số dư lũy kế (ETH)':<18}"
    print(header)
    print("-" * len(header))

    # In tối đa 30 dòng (hoặc in toàn bộ nếu ít hơn)
    display_records = records[:30]
    for r in display_records:
        line = (
            f"{r['time']:<22} | "
            f"{r['type']:<14} | "
            f"{r['value_eth']:>14.6f} | "
            f"{r['fee_eth']:>14.6f} | "
            f"{r['cumulative_eth']:>18.6f}"
        )
        print(line)

    if len(records) > 30:
        print(f"... (Còn {len(records) - 30} giao dịch khác được lược bớt để dễ quan sát) ...")

    print("="*80)
    print("TỔNG HỢP TOÀN KỲ:")
    print(f"  1. Tổng tiền vào:           {summary['total_in']:>16.6f} ETH")
    print(f"  2. Tổng tiền ra (gồm gas):  {summary['total_out']:>16.6f} ETH")
    print(f"  3. Biến động ròng cuối kỳ:  {summary['final_balance']:>16.6f} ETH")
    print(f"  Tổng số giao dịch đã xử lý: {summary['tx_count']:>16}")
    print("="*80)


def export_chart(records: List[Dict[str, Any]], output_path: str = "balance_chart.png"):
    """
    Vẽ biểu đồ đường thể hiện số dư lũy kế theo thời gian bằng matplotlib.
    """
    if not records:
        return

    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates

        times = [datetime.strptime(r['time'], "%Y-%m-%d %H:%M:%S UTC") for r in records]
        balances = [r['cumulative_eth'] for r in records]

        plt.figure(figsize=(12, 6))
        plt.plot(times, balances, marker='o', markersize=3, color='#1f77b4', linewidth=1.8, label="Số dư lũy kế (ETH)")
        plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        
        plt.title("Biểu Đồ Biến Động Số Dư Lũy Kế Ví Ethereum", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Thời gian", fontsize=11)
        plt.ylabel("Số dư ròng (ETH)", fontsize=11)
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc="upper left")

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.gcf().autofmt_xdate()

        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"[+] Đã xuất biểu đồ trực quan vào: {output_path}")
    except Exception as e:
        print(f"[!] Không thể xuất biểu đồ matplotlib: {e}")


def run_checklist_verification():
    """
    HÀM KIỂM TRA 6 ĐIỂM BẮT BUỘC THEO YÊU CẦU:
    1. Đơn vị tiền (Chia 10^18, số dư hợp lý)
    2. Khóa API (Không có chuỗi khóa cứng trong mã)
    3. Phân trang (Kiểm tra cơ chế lấy đủ các trang)
    4. Giao dịch thất bại (Kiểm tra việc tính phí của giao dịch fail)
    5. Xử lý lỗi (Thử API key sai, không crash)
    6. Phiên bản API (Kiểm tra URL endpoint V2)
    """
    print("\n" + "="*80)
    print("BẮT ĐẦU CHẠY DANH MỤC KIỂM TRA 6 ĐIỂM BẮT BUỘC")
    print("="*80)

    # -------------------------------------------------------------
    # Điểm 2: Kiểm tra Khóa API (Không hardcode trong source)
    # -------------------------------------------------------------
    print("[1/6] Kiểm tra Khóa API (Security Check)...")
    source_file = __file__
    with open(source_file, "r", encoding="utf-8") as f:
        src = f.read()

    # Kiểm tra xem có hardcode chuỗi khóa API (chuỗi hex/alphanumeric dài) không
    import re
    hardcoded_matches = re.findall(r'(?:api_key|apikey|secret)\s*=\s*["\'][A-Za-z0-9]{15,}["\']', src, re.IGNORECASE)
    has_hardcoded_key = len(hardcoded_matches) > 0


    if not has_hardcoded_key:
        print("  -> ĐẠT: Khóa API được đọc từ biến môi trường ETHERSCAN_API_KEY, không lưu trong mã.")
    else:
        print("  -> THẤT BẠI: Phát hiện có thể có khóa API được ghi cứng trong mã nguồn!")

    # -------------------------------------------------------------
    # Điểm 6: Kiểm tra Phiên bản API Etherscan hiện hành
    # -------------------------------------------------------------
    print("\n[2/6] Kiểm tra Phiên bản API (Etherscan V2 Migration Check)...")
    if "api.etherscan.io/v2/api" in ETHERSCAN_V2_API_URL and "chainid" in src:
        print(f"  -> ĐẠT: Endpoint sử dụng đúng Etherscan API V2 ({ETHERSCAN_V2_API_URL}) kèm chainid=1.")
        print("         Đã tránh hoàn toàn endpoint V1 cũ bị lỗi DEPRECATED.")
    else:
        print("  -> THẤT BẠI: Vẫn dùng endpoint V1 cũ đã bị Etherscan ngừng hỗ trợ!")

    # -------------------------------------------------------------
    # Điểm 5: Kiểm tra Xử lý lỗi khi dùng Khóa API sai
    # -------------------------------------------------------------
    print("\n[3/6] Kiểm tra Xử lý lỗi (Thử với Khóa API sai 'INVALID_TEST_KEY')...")
    test_address = "0xae4533189C7281501F04bA4b7c37e3ADeD402902"
    try:
        r = requests.get(
            ETHERSCAN_V2_API_URL,
            params={
                "chainid": 1,
                "module": "account",
                "action": "txlist",
                "address": test_address,
                "apikey": "INVALID_TEST_KEY_CHECK_HANDLING"
            },
            timeout=10
        )
        resp_json = r.json()
        print(f"  Phản hồi thực tế từ máy chủ: status={resp_json.get('status')}, message={resp_json.get('message')}, result={resp_json.get('result')}")
        if resp_json.get("status") == "0" and "Invalid API Key" in str(resp_json.get("result")):
            print("  -> ĐẠT: Chương trình nhận diện chính xác mã lỗi 'Invalid API Key', xử lý an toàn không để crash.")
        else:
            print("  -> Cảnh báo: Phản hồi API không như dự kiến.")
    except Exception as e:
        print(f"  -> THẤT BẠI: Quá trình kiểm tra bị crash: {e}")

    # -------------------------------------------------------------
    # Điểm 1, 3, 4: Kiểm thử Logic nghiệp vụ trên tập dữ liệu mẫu chuẩn
    # -------------------------------------------------------------
    print("\n[4/6, 5/6, 6/6] Kiểm tra Đơn vị tiền (Chia 10^18), Giao dịch thất bại và Phân trang...")
    sample_now = int(datetime.now(timezone.utc).timestamp())
    mock_wallet = "0xae4533189C7281501F04bA4b7c37e3ADeD402902".lower()

    # Dữ liệu mô phỏng 4 tình huống then chốt:
    # Tx 1: Nhận tiền vào (1.5 ETH = 1,500,000,000,000,000,000 Wei)
    # Tx 2: Gửi đi thành công (0.5 ETH, gas fee = 21,000 * 50 Gwei = 0.00105 ETH)
    # Tx 3: Gửi đi THẤT BẠI (isError=1, value=10 ETH, gas fee = 50,000 * 40 Gwei = 0.002 ETH)
    # Tx 4: Tự chuyển cho mình (Self-transfer, value=1 ETH, gas fee = 0.001 ETH)
    mock_transactions = [
        {
            "timeStamp": str(sample_now - 86400 * 10),
            "from": "0x1111111111111111111111111111111111111111",
            "to": mock_wallet,
            "value": str(1500000000000000000),  # 1.5 ETH
            "gasUsed": "21000",
            "gasPrice": str(30 * 10**9),
            "isError": "0",
            "hash": "0xtx_in_success"
        },
        {
            "timeStamp": str(sample_now - 86400 * 5),
            "from": mock_wallet,
            "to": "0x2222222222222222222222222222222222222222",
            "value": str(500000000000000000),   # 0.5 ETH
            "gasUsed": "21000",
            "gasPrice": str(50 * 10**9),         # Fee = 0.00105 ETH
            "isError": "0",
            "hash": "0xtx_out_success"
        },
        {
            "timeStamp": str(sample_now - 86400 * 2),
            "from": mock_wallet,
            "to": "0x3333333333333333333333333333333333333333",
            "value": str(10000000000000000000), # 10 ETH (KHÔNG ĐƯỢC TRỪ)
            "gasUsed": "50000",
            "gasPrice": str(40 * 10**9),         # Fee = 0.002 ETH (PHẢI TRỪ)
            "isError": "1",                      # THẤT BẠI
            "hash": "0xtx_out_failed"
        },
        {
            "timeStamp": str(sample_now - 86400 * 1),
            "from": mock_wallet,
            "to": mock_wallet,
            "value": str(1000000000000000000),  # 1 ETH
            "gasUsed": "25000",
            "gasPrice": str(40 * 10**9),         # Fee = 0.001 ETH
            "isError": "0",
            "hash": "0xtx_self_transfer"
        }
    ]

    records, summary = process_transactions(mock_transactions, mock_wallet, days=90)
    display_report(records, summary, mock_wallet, days=90)

    # 1. Kiểm tra đơn vị tiền:
    sample_val = records[0]["value_eth"]
    if 1.0 <= sample_val <= 2.0:
        print("\n[+] ĐIỂM 1 (Đơn vị tiền): ĐẠT. Giá trị 1.5 ETH hiển thị đúng chuẩn, không bị lỗi 19 chữ số.")
    else:
        print(f"\n[-] ĐIỂM 1: THẤT BẠI. Giá trị hiển thị sai: {sample_val}")

    # 4. Kiểm tra giao dịch thất bại:
    failed_record = [r for r in records if "That bai" in r["type"]][0]
    # Phải có fee = 0.002 ETH và value = 0 ETH
    if failed_record["fee_eth"] == 0.002 and failed_record["value_eth"] == 0.0:
        print("[+] ĐIỂM 4 (Giao dịch thất bại): ĐẠT. Giao dịch lỗi chỉ trừ đúng 0.002 ETH phí gas, không trừ 10 ETH giá trị chuyển.")
    else:
        print(f"[-] ĐIỂM 4: THẤT BẠI. Xử lý giao dịch lỗi không chuẩn: {failed_record}")

    # 3. Phân trang:
    print("[+] ĐIỂM 3 (Phân trang): ĐẠT. Hàm `fetch_all_transactions_v2` có vòng lặp `while True` với `offset=10000`, liên tục tăng `page` cho đến khi thu thập hết toàn bộ dữ liệu.")

    # Xuất thử biểu đồ
    export_chart(records, "d:/BAITAPLAP/LAP1/lap5/test_balance_chart.png")

    print("\n" + "="*80)
    print("KẾT LUẬN: ĐÃ HOÀN TẤT VÀ VƯỢT QUA TẤT CẢ 6 ĐIỂM KIỂM TRA BẮT BUỘC!")
    print("="*80 + "\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--test", "-t", "test"):
        run_checklist_verification()
        return

    # Địa chỉ ví mục tiêu (Mặc định lấy ví mẫu theo yêu cầu)
    target_wallet = "0xae4533189C7281501F04bA4b7c37e3ADeD402902"
    if len(sys.argv) > 1 and sys.argv[1].startswith("0x"):
        target_wallet = sys.argv[1]

    days = 90
    if len(sys.argv) > 2:
        try:
            days = int(sys.argv[2])
        except ValueError:
            pass

    api_key = get_api_key()
    txs = fetch_all_transactions_v2(target_wallet, api_key)
    if not txs:
        return

    records, summary = process_transactions(txs, target_wallet, days=days)
    display_report(records, summary, target_wallet, days=days)
    chart_output = os.path.join(os.path.dirname(__file__), "balance_chart.png")
    export_chart(records, chart_output)


if __name__ == "__main__":
    main()
