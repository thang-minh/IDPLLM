import os
import random
from faker import Faker
from datetime import datetime, timedelta  # <-- ĐÃ IMPORT timedelta

fake = Faker('vi_VN')

# --- Cấu hình ---
BASE_DIR = "data/document_classification"
TRAIN_RATIO = 0.8
NUM_PER_CLASS = 50  # 40 train + 10 test

# Tạo thư mục
def create_dirs():
    for split in ['train', 'test']:
        for doc_type in ['Hop_dong_lao_dong', 'Hoa_don_GTGT', 'Bien_ban_hop']:
            os.makedirs(os.path.join(BASE_DIR, split, doc_type), exist_ok=True)

# --- 1. Hợp đồng lao động ---
def generate_hop_dong_lao_dong(idx):
    positions = ["Nhân viên Kinh doanh", "Kỹ sư Phần mềm", "Trưởng phòng Hành chính",
                 "Nhân viên Kế toán", "Chuyên viên Nhân sự", "Lập trình viên", "Giám sát sản xuất"]
    contract_types = ["xác định thời hạn", "không xác định thời hạn", "thời vụ", "thử việc"]
    salary_list = [8000000, 10000000, 12000000, 15000000, 18000000, 20000000, 25000000, 30000000]

    def money_to_text(amount):
        if amount >= 10**7:
            return f"{amount // 10**6} triệu"
        elif amount >= 10**6:
            return f"{amount // 10**6} triệu {amount % 10**6 // 1000} nghìn"
        else:
            return f"{amount // 1000} nghìn"

    company_name = fake.company()
    company_address = fake.address().replace("\n", ", ")
    employer_name = fake.name()
    employer_title = random.choice(["Giám đốc", "Trưởng phòng Nhân sự", "Phó giám đốc"])
    employee_name = fake.name()
    employee_dob = fake.date_of_birth(minimum_age=22, maximum_age=50).strftime("%d/%m/%Y")
    employee_address = fake.address().replace("\n", ", ")
    employee_id = fake.random_number(digits=9, fix_len=True)
    contract_type = random.choice(contract_types)
    position = random.choice(positions)
    salary = random.choice(salary_list)
    salary_text = money_to_text(salary)
    duration = random.choice(["6 tháng", "12 tháng", "24 tháng", "36 tháng", "không xác định thời hạn"])
    start_date = fake.date_this_decade().strftime("%d/%m/%Y")
    contract_no = f"{idx:03d}/2025/HĐLĐ-QĐ"
    sign_date = fake.date_this_year().strftime("%d/%m/%Y")
    sign_day, sign_month, sign_year = sign_date.split("/")

    template = f"""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
HỢP ĐỒNG LAO ĐỘNG
Số: {contract_no}

Hôm nay, ngày {sign_day} tháng {sign_month} năm {sign_year}, tại {company_address}.

Chúng tôi gồm:

BÊN A (NGƯỜI SỬ DỤNG LAO ĐỘNG):
- Tên đơn vị: {company_name}
- Địa chỉ: {company_address}
- Đại diện: Ông/Bà {employer_name} - Chức vụ: {employer_title}

BÊN B (NGƯỜI LAO ĐỘNG):
- Họ và tên: {employee_name}
- Sinh ngày: {employee_dob}
- CMND/CCCD: {employee_id}
- Địa chỉ: {employee_address}

Hai bên thống nhất ký kết hợp đồng lao động loại {contract_type} với nội dung sau:

ĐIỀU 1: CÔNG VIỆC VÀ ĐỊA ĐIỂM LÀM VIỆC
- Vị trí công việc: {position}
- Địa điểm làm việc: {company_address}

ĐIỀU 2: THỜI HẠN HỢP ĐỒNG
- Thời hạn: {duration}
- Bắt đầu từ: {start_date}

ĐIỀU 3: CHẾ ĐỘ LƯƠNG
- Mức lương chính: {salary:,} VNĐ/tháng
  (Bằng chữ: {salary_text} đồng)
- Hình thức trả lương: Chuyển khoản ngày 30 hàng tháng

ĐIỀU 4: QUYỀN VÀ NGHĨA VỤ
- Thực hiện theo Bộ luật Lao động Việt Nam hiện hành.

Hợp đồng được lập thành 02 bản có giá trị pháp lý ngang nhau.

ĐẠI DIỆN BÊN A                  ĐẠI DIỆN BÊN B
(Ký, ghi rõ họ tên)              (Ký, ghi rõ họ tên)
{employer_name}                  {employee_name}
"""
    return template.strip()

# --- 2. Hóa đơn GTGT ---
def generate_hoa_don_gtgt(idx):
    sellers = [fake.company() for _ in range(5)]
    buyer_is_company = random.random() < 0.7
    buyer_name = fake.company() if buyer_is_company else fake.name()
    buyer_company = fake.company() if buyer_is_company else ""

    items = [
        ("Dịch vụ tư vấn", random.randint(1, 5), random.randint(500000, 2000000)),
        ("Phần mềm quản lý", 1, random.randint(10000000, 50000000)),
        ("Thiết bị văn phòng", random.randint(1, 3), random.randint(2000000, 10000000)),
        ("In ấn tài liệu", random.randint(100, 500), random.randint(500, 2000)),
    ]
    item_name, qty, unit_price = random.choice(items)
    amount = qty * unit_price
    vat = int(amount * 0.1)
    total = amount + vat

    # --- SỬA LỖI Ở ĐÂY ---
    # Gán kết quả của .replace() vào một biến trước
    seller_address = fake.address().replace('\n', ', ')
    # ---------------------

    template = f"""HÓA ĐƠN GIÁ TRỊ GIA TĂNG
Số: {fake.bothify(text='???/####/HD')}
Ký hiệu: AA/25E
Ngày {fake.date_this_year().strftime('%d/%m/%Y')}

Đơn vị bán hàng: {random.choice(sellers)}
Mã số thuế: {fake.random_number(digits=10, fix_len=True)}-{fake.random_digit()}
Địa chỉ: {seller_address}  # <-- Sử dụng biến đã tạo ở trên
Điện thoại: 0{fake.random_number(digits=9)}

Họ tên người mua: {buyer_name}
Đơn vị: {buyer_company}
Mã số thuế: {fake.random_number(digits=10, fix_len=True)}-{fake.random_digit() if buyer_is_company else ''}

STT | Tên hàng hóa, dịch vụ | ĐVT | Số lượng | Đơn giá | Thành tiền
----|-----------------------|-----|----------|---------|------------
1   | {item_name}           | {random.choice(['Cái', 'Bộ', 'Tháng', 'Lần'])} | {qty} | {unit_price:,} | {amount:,}

Cộng tiền hàng: {amount:,} VNĐ
Thuế suất GTGT: 10%
Tiền thuế GTGT: {vat:,} VNĐ
Tổng tiền thanh toán: {total:,} VNĐ

Số tiền viết bằng chữ: {number_to_words(total)} đồng.

Người mua hàng           Người bán hàng
(Ký, ghi rõ họ tên)         (Ký, đóng dấu)
"""
    return template.strip()
# --- 3. Biên bản họp ---
def generate_bien_ban_hop(idx):
    purposes = [
        "Triển khai kế hoạch kinh doanh quý IV",
        "Đánh giá hiệu suất nhân sự",
        "Thảo luận dự án phần mềm mới",
        "Kiểm tra tiến độ sản xuất",
        "Họp cổ đông thường niên"
    ]
    attendees = [fake.name() for _ in range(random.randint(4, 8))]
    decisions = [
        "Phê duyệt ngân sách 500 triệu cho dự án.",
        "Tăng cường đào tạo nhân sự kỹ thuật.",
        "Ra mắt sản phẩm mới vào tháng 12.",
        "Ký hợp đồng với đối tác ABC.",
    ]

    date = fake.date_this_year()
    time_start = fake.time(pattern="%H:%M")
    start_dt = datetime.strptime(time_start, "%H:%M")
    end_dt = start_dt + timedelta(hours=random.randint(1, 3))
    time_end = end_dt.strftime("%H:%M")

    # Dùng "\n".join() thay chr(10)
    attendees_list = "\n".join([f"- Ông/Bà {name}" for name in attendees])
    decisions_list = "\n".join([f"- {d}" for d in random.sample(decisions, k=2)])

    template = f"""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---
BIÊN BẢN HỌP

Số: {idx:03d}/BB-HĐQT
Thời gian: Từ {time_start} đến {time_end}, ngày {date.strftime('%d/%m/%Y')}
Địa điểm: Phòng họp tầng 3, trụ sở {fake.company()}

Chủ trì: Ông/Bà {attendees[0]} - Chức vụ: {random.choice(['Giám đốc', 'Trưởng phòng'])}

Thành phần tham dự:
{attendees_list}

Nội dung cuộc họp: {random.choice(purposes)}

Ý KIẾN THẢO LUẬN:
- Ông {attendees[1]}: Đề xuất tăng ngân sách marketing.
- Bà {attendees[2]}: Báo cáo tiến độ đạt 85%.
- Ông {attendees[3]}: Góp ý cải thiện quy trình.

KẾT LUẬN:
{decisions_list}

Biên bản được thông qua tại cuộc họp.

CHỦ TỌA CUỘC HỌP         THƯ KÝ CUỘC HỌP
(Ký, ghi rõ họ tên)     (Ký, ghi rõ họ tên)
{attendees[0]}          {attendees[-1]}
"""
    return template.strip()

# --- Hàm chuyển số thành chữ ---
def number_to_words(n):
    if n == 0:
        return "không đồng"

    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"]
    tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
    scales = ["", "nghìn", "triệu", "tỷ"]

    def chunk_to_words(chunk):
        if chunk == 0:
            return ""
        hundred = chunk // 100
        ten = (chunk % 100) // 10
        one = chunk % 10
        words = []
        if hundred:
            words.append(units[hundred] + " trăm")
        if ten > 1:
            words.append(tens[ten])
            if one:
                words.append(units[one])
        elif ten == 1:
            words.append(teens[one])
        elif one:
            words.append(units[one])
        return " ".join(words).strip()

    parts = []
    scale_idx = 0
    while n > 0:
        chunk = n % 1000
        if chunk:
            part = chunk_to_words(chunk)
            if scale_idx > 0:
                part += " " + scales[scale_idx]
            parts.append(part)
        n //= 1000
        scale_idx += 1
    return " ".join(reversed(parts)) + " đồng"

# --- Lưu file ---
def save_file(content, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# --- Main ---
def main():
    create_dirs()
    generators = {
        'Hop_dong_lao_dong': generate_hop_dong_lao_dong,
        'Hoa_don_GTGT': generate_hoa_don_gtgt,
        'Bien_ban_hop': generate_bien_ban_hop
    }

    for doc_type, gen_func in generators.items():
        contents = [gen_func(i+1) for i in range(NUM_PER_CLASS)]
        random.shuffle(contents)

        train_count = int(NUM_PER_CLASS * TRAIN_RATIO)
        train_contents = contents[:train_count]
        test_contents = contents[train_count:]

        for i, content in enumerate(train_contents):
            filename = f"{doc_type}_train_{i+1:02d}.txt"
            save_file(content, os.path.join(BASE_DIR, 'train', doc_type, filename))

        for i, content in enumerate(test_contents):
            filename = f"{doc_type}_test_{i+1:02d}.txt"
            save_file(content, os.path.join(BASE_DIR, 'test', doc_type, filename))

        print(f"{doc_type}: {len(train_contents)} train + {len(test_contents)} test")

    print(f"\nTỔNG CỘNG: {NUM_PER_CLASS * 3} file đã tạo thành công!")

if __name__ == "__main__":
    main()