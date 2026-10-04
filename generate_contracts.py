# import os
# import random
# from faker import Faker
# from datetime import datetime, timedelta  # <-- ĐÃ IMPORT timedelta

# fake = Faker('vi_VN')

# # --- Cấu hình ---
# BASE_DIR = "data/document_classification"
# TRAIN_RATIO = 0.8
# NUM_PER_CLASS = 50  # 40 train + 10 test

# # Tạo thư mục
# def create_dirs():
#     for split in ['train', 'test']:
#         for doc_type in ['Hop_dong_lao_dong', 'Hoa_don_GTGT', 'Bien_ban_hop']:
#             os.makedirs(os.path.join(BASE_DIR, split, doc_type), exist_ok=True)

# # --- 1. Hợp đồng lao động ---
# def generate_hop_dong_lao_dong(idx):
#     positions = ["Nhân viên Kinh doanh", "Kỹ sư Phần mềm", "Trưởng phòng Hành chính",
#                  "Nhân viên Kế toán", "Chuyên viên Nhân sự", "Lập trình viên", "Giám sát sản xuất"]
#     contract_types = ["xác định thời hạn", "không xác định thời hạn", "thời vụ", "thử việc"]
#     salary_list = [8000000, 10000000, 12000000, 15000000, 18000000, 20000000, 25000000, 30000000]

#     def money_to_text(amount):
#         if amount >= 10**7:
#             return f"{amount // 10**6} triệu"
#         elif amount >= 10**6:
#             return f"{amount // 10**6} triệu {amount % 10**6 // 1000} nghìn"
#         else:
#             return f"{amount // 1000} nghìn"

#     company_name = fake.company()
#     company_address = fake.address().replace("\n", ", ")
#     employer_name = fake.name()
#     employer_title = random.choice(["Giám đốc", "Trưởng phòng Nhân sự", "Phó giám đốc"])
#     employee_name = fake.name()
#     employee_dob = fake.date_of_birth(minimum_age=22, maximum_age=50).strftime("%d/%m/%Y")
#     employee_address = fake.address().replace("\n", ", ")
#     employee_id = fake.random_number(digits=9, fix_len=True)
#     contract_type = random.choice(contract_types)
#     position = random.choice(positions)
#     salary = random.choice(salary_list)
#     salary_text = money_to_text(salary)
#     duration = random.choice(["6 tháng", "12 tháng", "24 tháng", "36 tháng", "không xác định thời hạn"])
#     start_date = fake.date_this_decade().strftime("%d/%m/%Y")
#     contract_no = f"{idx:03d}/2025/HĐLĐ-QĐ"
#     sign_date = fake.date_this_year().strftime("%d/%m/%Y")
#     sign_day, sign_month, sign_year = sign_date.split("/")

#     template = f"""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
# Độc lập - Tự do - Hạnh phúc
# ---
# HỢP ĐỒNG LAO ĐỘNG
# Số: {contract_no}

# Hôm nay, ngày {sign_day} tháng {sign_month} năm {sign_year}, tại {company_address}.

# Chúng tôi gồm:

# BÊN A (NGƯỜI SỬ DỤNG LAO ĐỘNG):
# - Tên đơn vị: {company_name}
# - Địa chỉ: {company_address}
# - Đại diện: Ông/Bà {employer_name} - Chức vụ: {employer_title}

# BÊN B (NGƯỜI LAO ĐỘNG):
# - Họ và tên: {employee_name}
# - Sinh ngày: {employee_dob}
# - CMND/CCCD: {employee_id}
# - Địa chỉ: {employee_address}

# Hai bên thống nhất ký kết hợp đồng lao động loại {contract_type} với nội dung sau:

# ĐIỀU 1: CÔNG VIỆC VÀ ĐỊA ĐIỂM LÀM VIỆC
# - Vị trí công việc: {position}
# - Địa điểm làm việc: {company_address}

# ĐIỀU 2: THỜI HẠN HỢP ĐỒNG
# - Thời hạn: {duration}
# - Bắt đầu từ: {start_date}

# ĐIỀU 3: CHẾ ĐỘ LƯƠNG
# - Mức lương chính: {salary:,} VNĐ/tháng
#   (Bằng chữ: {salary_text} đồng)
# - Hình thức trả lương: Chuyển khoản ngày 30 hàng tháng

# ĐIỀU 4: QUYỀN VÀ NGHĨA VỤ
# - Thực hiện theo Bộ luật Lao động Việt Nam hiện hành.

# Hợp đồng được lập thành 02 bản có giá trị pháp lý ngang nhau.

# ĐẠI DIỆN BÊN A                  ĐẠI DIỆN BÊN B
# (Ký, ghi rõ họ tên)              (Ký, ghi rõ họ tên)
# {employer_name}                  {employee_name}
# """
#     return template.strip()

# # --- 2. Hóa đơn GTGT ---
# def generate_hoa_don_gtgt(idx):
#     sellers = [fake.company() for _ in range(5)]
#     buyer_is_company = random.random() < 0.7
#     buyer_name = fake.company() if buyer_is_company else fake.name()
#     buyer_company = fake.company() if buyer_is_company else ""

#     items = [
#         ("Dịch vụ tư vấn", random.randint(1, 5), random.randint(500000, 2000000)),
#         ("Phần mềm quản lý", 1, random.randint(10000000, 50000000)),
#         ("Thiết bị văn phòng", random.randint(1, 3), random.randint(2000000, 10000000)),
#         ("In ấn tài liệu", random.randint(100, 500), random.randint(500, 2000)),
#     ]
#     item_name, qty, unit_price = random.choice(items)
#     amount = qty * unit_price
#     vat = int(amount * 0.1)
#     total = amount + vat

#     # --- SỬA LỖI Ở ĐÂY ---
#     # Gán kết quả của .replace() vào một biến trước
#     seller_address = fake.address().replace('\n', ', ')
#     # ---------------------

#     template = f"""HÓA ĐƠN GIÁ TRỊ GIA TĂNG
# Số: {fake.bothify(text='???/####/HD')}
# Ký hiệu: AA/25E
# Ngày {fake.date_this_year().strftime('%d/%m/%Y')}

# Đơn vị bán hàng: {random.choice(sellers)}
# Mã số thuế: {fake.random_number(digits=10, fix_len=True)}-{fake.random_digit()}
# Địa chỉ: {seller_address}  # <-- Sử dụng biến đã tạo ở trên
# Điện thoại: 0{fake.random_number(digits=9)}

# Họ tên người mua: {buyer_name}
# Đơn vị: {buyer_company}
# Mã số thuế: {fake.random_number(digits=10, fix_len=True)}-{fake.random_digit() if buyer_is_company else ''}

# STT | Tên hàng hóa, dịch vụ | ĐVT | Số lượng | Đơn giá | Thành tiền
# ----|-----------------------|-----|----------|---------|------------
# 1   | {item_name}           | {random.choice(['Cái', 'Bộ', 'Tháng', 'Lần'])} | {qty} | {unit_price:,} | {amount:,}

# Cộng tiền hàng: {amount:,} VNĐ
# Thuế suất GTGT: 10%
# Tiền thuế GTGT: {vat:,} VNĐ
# Tổng tiền thanh toán: {total:,} VNĐ

# Số tiền viết bằng chữ: {number_to_words(total)} đồng.

# Người mua hàng           Người bán hàng
# (Ký, ghi rõ họ tên)         (Ký, đóng dấu)
# """
#     return template.strip()
# # --- 3. Biên bản họp ---
# def generate_bien_ban_hop(idx):
#     purposes = [
#         "Triển khai kế hoạch kinh doanh quý IV",
#         "Đánh giá hiệu suất nhân sự",
#         "Thảo luận dự án phần mềm mới",
#         "Kiểm tra tiến độ sản xuất",
#         "Họp cổ đông thường niên"
#     ]
#     attendees = [fake.name() for _ in range(random.randint(4, 8))]
#     decisions = [
#         "Phê duyệt ngân sách 500 triệu cho dự án.",
#         "Tăng cường đào tạo nhân sự kỹ thuật.",
#         "Ra mắt sản phẩm mới vào tháng 12.",
#         "Ký hợp đồng với đối tác ABC.",
#     ]

#     date = fake.date_this_year()
#     time_start = fake.time(pattern="%H:%M")
#     start_dt = datetime.strptime(time_start, "%H:%M")
#     end_dt = start_dt + timedelta(hours=random.randint(1, 3))
#     time_end = end_dt.strftime("%H:%M")

#     # Dùng "\n".join() thay chr(10)
#     attendees_list = "\n".join([f"- Ông/Bà {name}" for name in attendees])
#     decisions_list = "\n".join([f"- {d}" for d in random.sample(decisions, k=2)])

#     template = f"""CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
# Độc lập - Tự do - Hạnh phúc
# ---
# BIÊN BẢN HỌP

# Số: {idx:03d}/BB-HĐQT
# Thời gian: Từ {time_start} đến {time_end}, ngày {date.strftime('%d/%m/%Y')}
# Địa điểm: Phòng họp tầng 3, trụ sở {fake.company()}

# Chủ trì: Ông/Bà {attendees[0]} - Chức vụ: {random.choice(['Giám đốc', 'Trưởng phòng'])}

# Thành phần tham dự:
# {attendees_list}

# Nội dung cuộc họp: {random.choice(purposes)}

# Ý KIẾN THẢO LUẬN:
# - Ông {attendees[1]}: Đề xuất tăng ngân sách marketing.
# - Bà {attendees[2]}: Báo cáo tiến độ đạt 85%.
# - Ông {attendees[3]}: Góp ý cải thiện quy trình.

# KẾT LUẬN:
# {decisions_list}

# Biên bản được thông qua tại cuộc họp.

# CHỦ TỌA CUỘC HỌP         THƯ KÝ CUỘC HỌP
# (Ký, ghi rõ họ tên)     (Ký, ghi rõ họ tên)
# {attendees[0]}          {attendees[-1]}
# """
#     return template.strip()

# # --- Hàm chuyển số thành chữ ---
# def number_to_words(n):
#     if n == 0:
#         return "không đồng"

#     units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
#     teens = ["mười", "mười một", "mười hai", "mười ba", "mười bốn", "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"]
#     tens = ["", "", "hai mươi", "ba mươi", "bốn mươi", "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"]
#     scales = ["", "nghìn", "triệu", "tỷ"]

#     def chunk_to_words(chunk):
#         if chunk == 0:
#             return ""
#         hundred = chunk // 100
#         ten = (chunk % 100) // 10
#         one = chunk % 10
#         words = []
#         if hundred:
#             words.append(units[hundred] + " trăm")
#         if ten > 1:
#             words.append(tens[ten])
#             if one:
#                 words.append(units[one])
#         elif ten == 1:
#             words.append(teens[one])
#         elif one:
#             words.append(units[one])
#         return " ".join(words).strip()

#     parts = []
#     scale_idx = 0
#     while n > 0:
#         chunk = n % 1000
#         if chunk:
#             part = chunk_to_words(chunk)
#             if scale_idx > 0:
#                 part += " " + scales[scale_idx]
#             parts.append(part)
#         n //= 1000
#         scale_idx += 1
#     return " ".join(reversed(parts)) + " đồng"

# # --- Lưu file ---
# def save_file(content, path):
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(content)

# # --- Main ---
# def main():
#     create_dirs()
#     generators = {
#         'Hop_dong_lao_dong': generate_hop_dong_lao_dong,
#         'Hoa_don_GTGT': generate_hoa_don_gtgt,
#         'Bien_ban_hop': generate_bien_ban_hop
#     }

#     for doc_type, gen_func in generators.items():
#         contents = [gen_func(i+1) for i in range(NUM_PER_CLASS)]
#         random.shuffle(contents)

#         train_count = int(NUM_PER_CLASS * TRAIN_RATIO)
#         train_contents = contents[:train_count]
#         test_contents = contents[train_count:]

#         for i, content in enumerate(train_contents):
#             filename = f"{doc_type}_train_{i+1:02d}.txt"
#             save_file(content, os.path.join(BASE_DIR, 'train', doc_type, filename))

#         for i, content in enumerate(test_contents):
#             filename = f"{doc_type}_test_{i+1:02d}.txt"
#             save_file(content, os.path.join(BASE_DIR, 'test', doc_type, filename))

#         print(f"{doc_type}: {len(train_contents)} train + {len(test_contents)} test")

#     print(f"\nTỔNG CỘNG: {NUM_PER_CLASS * 3} file đã tạo thành công!")

# if __name__ == "__main__":
#     main()

# generate_synthetic_documents.py

import os
import random
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from faker import Faker


# ==========================
# CẤU HÌNH
# ==========================

fake = Faker("vi_VN")

# Nếu chạy trên Google Colab
BASE_DIR = Path("/content/drive/MyDrive/DACN/document_classification")

# Nếu chạy local thì dùng dòng này thay thế:
# BASE_DIR = Path("data/document_classification")

TRAIN_RATIO = 0.8

# Số file mỗi class
# 200/class => 160 train + 40 test mỗi class
NUM_PER_CLASS = 200

# True: xóa file .txt cũ trước khi tạo lại
# False: giữ file cũ và ghi thêm file mới
CLEAR_OLD_FILES = True

SEED = 42
random.seed(SEED)
Faker.seed(SEED)


DOC_TYPES = [
    "Hop_dong_lao_dong",
    "Hoa_don_GTGT",
    "Bien_ban_hop"
]


# ==========================
# TIỆN ÍCH
# ==========================

def create_dirs():
    for split in ["train", "test"]:
        for doc_type in DOC_TYPES:
            folder = BASE_DIR / split / doc_type
            folder.mkdir(parents=True, exist_ok=True)


def clear_old_txt_files():
    if not BASE_DIR.exists():
        return

    for split in ["train", "test"]:
        for doc_type in DOC_TYPES:
            folder = BASE_DIR / split / doc_type
            if folder.exists():
                for file in folder.glob("*.txt"):
                    file.unlink()


def clean_text(text):
    lines = [line.rstrip() for line in text.splitlines()]
    cleaned = "\n".join(lines)
    return cleaned.strip()


def save_file(content, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(clean_text(content))


def random_date_this_year():
    return fake.date_this_year().strftime("%d/%m/%Y")


def random_phone():
    return "0" + str(fake.random_number(digits=9, fix_len=True))


def random_tax_code():
    if random.random() < 0.5:
        return str(fake.random_number(digits=10, fix_len=True))
    return f"{fake.random_number(digits=10, fix_len=True)}-{fake.random_number(digits=3, fix_len=True)}"


def format_money(amount):
    return f"{amount:,}".replace(",", ".")


def number_to_words_simple(n):
    """
    Hàm chuyển số đơn giản, đủ dùng cho dữ liệu giả lập.
    Không cần chính xác tuyệt đối như phần mềm kế toán thật.
    """
    if n == 0:
        return "không đồng"

    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    teens = [
        "mười", "mười một", "mười hai", "mười ba", "mười bốn",
        "mười lăm", "mười sáu", "mười bảy", "mười tám", "mười chín"
    ]
    tens = [
        "", "", "hai mươi", "ba mươi", "bốn mươi",
        "năm mươi", "sáu mươi", "bảy mươi", "tám mươi", "chín mươi"
    ]
    scales = ["", "nghìn", "triệu", "tỷ"]

    def chunk_to_words(chunk):
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

        return " ".join(words)

    parts = []
    scale_idx = 0

    while n > 0:
        chunk = n % 1000
        if chunk:
            part = chunk_to_words(chunk)
            if scales[scale_idx]:
                part += " " + scales[scale_idx]
            parts.append(part)

        n //= 1000
        scale_idx += 1

    return " ".join(reversed(parts)) + " đồng"


def maybe_ocr_noise(text, probability=0.08):
    """
    Tạo lỗi nhẹ giống OCR để model quen dữ liệu không hoàn hảo.
    Không làm quá mạnh để tránh phá văn bản.
    """
    if random.random() > probability:
        return text

    replacements = {
        "HÓA ĐƠN": random.choice(["HOA DON", "HÓA ĐƠN", "HOA ĐƠN"]),
        "GIÁ TRỊ GIA TĂNG": random.choice(["GIA TRI GIA TANG", "GIÁ TRỊ GIA TĂNG"]),
        "CỘNG HÒA": random.choice(["CONG HOA", "CỘNG HÒA"]),
        "Độc lập": random.choice(["Doc lap", "Độc lập"]),
        "Tự do": random.choice(["Tu do", "Tự do"]),
        "Hạnh phúc": random.choice(["Hanh phuc", "Hạnh phúc"]),
        "Mã số thuế": random.choice(["Ma so thue", "Mã số thuế"]),
        "Tổng tiền": random.choice(["Tong tien", "Tổng tiền"]),
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ==========================
# 1. HỢP ĐỒNG LAO ĐỘNG
# ==========================

def generate_hop_dong_lao_dong(idx):
    positions = [
        "Nhân viên Kinh doanh",
        "Kỹ sư Phần mềm",
        "Trưởng phòng Hành chính",
        "Nhân viên Kế toán",
        "Chuyên viên Nhân sự",
        "Lập trình viên",
        "Giám sát sản xuất",
        "Nhân viên Marketing",
        "Chuyên viên Chăm sóc khách hàng",
        "Nhân viên Kho vận"
    ]

    contract_types = [
        "xác định thời hạn",
        "không xác định thời hạn",
        "thử việc",
        "theo mùa vụ"
    ]

    salary_list = [
        8000000, 9000000, 10000000, 12000000, 15000000,
        18000000, 20000000, 25000000, 30000000
    ]

    company_name = fake.company()
    company_address = fake.address().replace("\n", ", ")
    employer_name = fake.name()
    employer_title = random.choice(["Giám đốc", "Phó Giám đốc", "Trưởng phòng Nhân sự"])
    employee_name = fake.name()
    employee_dob = fake.date_of_birth(minimum_age=22, maximum_age=55).strftime("%d/%m/%Y")
    employee_address = fake.address().replace("\n", ", ")
    employee_id = fake.random_number(digits=12, fix_len=True)
    position = random.choice(positions)
    contract_type = random.choice(contract_types)
    salary = random.choice(salary_list)
    duration = random.choice(["02 tháng", "06 tháng", "12 tháng", "24 tháng", "36 tháng", "không xác định thời hạn"])
    start_date = fake.date_between(start_date="-2y", end_date="+30d").strftime("%d/%m/%Y")
    sign_date = fake.date_this_year().strftime("%d/%m/%Y")
    sign_day, sign_month, sign_year = sign_date.split("/")
    contract_no = f"{idx:03d}/{random.choice(['HĐLĐ', 'HDLD'])}/{sign_year}"

    template_type = random.choice([1, 2, 3])

    if template_type == 1:
        text = f"""
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
-------------------------

HỢP ĐỒNG LAO ĐỘNG
Số: {contract_no}

Hôm nay, ngày {sign_day} tháng {sign_month} năm {sign_year}, tại {company_address}, chúng tôi gồm:

BÊN A: NGƯỜI SỬ DỤNG LAO ĐỘNG
Tên đơn vị: {company_name}
Địa chỉ: {company_address}
Đại diện: Ông/Bà {employer_name}
Chức vụ: {employer_title}
Điện thoại: {random_phone()}

BÊN B: NGƯỜI LAO ĐỘNG
Họ và tên: {employee_name}
Ngày sinh: {employee_dob}
Số CCCD/CMND: {employee_id}
Địa chỉ thường trú: {employee_address}

Hai bên thống nhất ký kết hợp đồng lao động với các điều khoản sau:

Điều 1. Công việc và địa điểm làm việc
Người lao động làm việc tại vị trí: {position}.
Địa điểm làm việc: {company_address}.

Điều 2. Loại hợp đồng và thời hạn hợp đồng
Loại hợp đồng: {contract_type}.
Thời hạn hợp đồng: {duration}.
Ngày bắt đầu làm việc: {start_date}.

Điều 3. Mức lương và hình thức trả lương
Mức lương chính: {format_money(salary)} VNĐ/tháng.
Bằng chữ: {number_to_words_simple(salary)}.
Hình thức trả lương: chuyển khoản vào cuối tháng.

Điều 4. Quyền và nghĩa vụ của các bên
Người lao động có trách nhiệm thực hiện công việc theo phân công.
Người sử dụng lao động có trách nhiệm bảo đảm điều kiện làm việc và thanh toán lương đúng hạn.

Điều 5. Điều khoản thi hành
Hợp đồng này được lập thành 02 bản có giá trị pháp lý như nhau.

ĐẠI DIỆN BÊN A                       NGƯỜI LAO ĐỘNG
(Ký, ghi rõ họ tên)                  (Ký, ghi rõ họ tên)

{employer_name}                       {employee_name}
"""
    elif template_type == 2:
        text = f"""
HỢP ĐỒNG LAO ĐỘNG

Số hợp đồng: {contract_no}

Căn cứ Bộ luật Lao động hiện hành và nhu cầu sử dụng lao động của {company_name}, hai bên gồm:

1. Người sử dụng lao động:
Công ty: {company_name}
Địa chỉ trụ sở: {company_address}
Người đại diện: {employer_name}
Chức danh: {employer_title}

2. Người lao động:
Họ tên: {employee_name}
Sinh ngày: {employee_dob}
CCCD: {employee_id}
Nơi cư trú: {employee_address}

Nội dung thỏa thuận:
- Chức danh chuyên môn: {position}
- Loại hợp đồng: {contract_type}
- Thời hạn: {duration}
- Ngày bắt đầu: {start_date}
- Lương cơ bản: {format_money(salary)} đồng/tháng
- Phụ cấp: {format_money(random.choice([500000, 1000000, 1500000, 2000000]))} đồng/tháng
- Thời giờ làm việc: 08 giờ/ngày, từ thứ Hai đến thứ Sáu
- Chế độ bảo hiểm: thực hiện theo quy định pháp luật

Hai bên cam kết thực hiện đúng các nội dung đã thỏa thuận trong hợp đồng.

Lập tại {company_address}, ngày {sign_date}.

ĐẠI DIỆN CÔNG TY                 NGƯỜI LAO ĐỘNG
{employer_name}                  {employee_name}
"""
    else:
        text = f"""
CÔNG TY: {company_name}
Địa chỉ: {company_address}

BIỂU MẪU HỢP ĐỒNG LAO ĐỘNG

Mã hợp đồng: {contract_no}
Ngày ký: {sign_date}

Thông tin nhân sự:
Họ tên người lao động: {employee_name}
Ngày sinh: {employee_dob}
Số giấy tờ tùy thân: {employee_id}
Địa chỉ liên hệ: {employee_address}

Thông tin công việc:
Vị trí tuyển dụng: {position}
Bộ phận làm việc: {random.choice(['Kinh doanh', 'Kỹ thuật', 'Hành chính', 'Kế toán', 'Nhân sự'])}
Thời hạn hợp đồng: {duration}
Loại hợp đồng: {contract_type}
Ngày nhận việc: {start_date}

Chế độ lương thưởng:
Lương thỏa thuận: {format_money(salary)} VNĐ/tháng
Hình thức trả lương: chuyển khoản ngân hàng
Ngày trả lương: ngày 30 hàng tháng

Cam kết:
Người lao động cam kết tuân thủ nội quy lao động, quy chế công ty và các quy định pháp luật liên quan.
Công ty cam kết bảo đảm quyền lợi hợp pháp cho người lao động.

Người đại diện công ty: {employer_name}
Người lao động: {employee_name}
"""

    return maybe_ocr_noise(clean_text(text))


# ==========================
# 2. HÓA ĐƠN GTGT
# ==========================

def generate_hoa_don_gtgt(idx):
    seller_name = fake.company()
    seller_address = fake.address().replace("\n", ", ")
    buyer_is_company = random.random() < 0.75
    buyer_name = fake.company() if buyer_is_company else fake.name()
    buyer_address = fake.address().replace("\n", ", ")

    product_pool = [
        ("Dịch vụ tư vấn quản lý", "Lần", random.randint(1, 3), random.randint(1000000, 5000000)),
        ("Phần mềm quản lý bán hàng", "Gói", 1, random.randint(8000000, 30000000)),
        ("Máy in văn phòng", "Cái", random.randint(1, 5), random.randint(2500000, 7000000)),
        ("Máy tính xách tay", "Cái", random.randint(1, 4), random.randint(12000000, 25000000)),
        ("Dịch vụ bảo trì hệ thống", "Tháng", random.randint(1, 12), random.randint(500000, 2000000)),
        ("Văn phòng phẩm", "Bộ", random.randint(5, 50), random.randint(50000, 300000)),
        ("In ấn tài liệu", "Trang", random.randint(100, 1000), random.randint(500, 3000)),
        ("Thiết bị mạng", "Bộ", random.randint(1, 6), random.randint(1000000, 8000000)),
    ]

    num_items = random.randint(1, 4)
    selected_items = random.sample(product_pool, k=num_items)

    rows = []
    subtotal = 0

    for i, (name, unit, qty, unit_price) in enumerate(selected_items, start=1):
        amount = qty * unit_price
        subtotal += amount
        rows.append(
            f"{i:<3} | {name:<30} | {unit:<6} | {qty:<8} | {format_money(unit_price):<12} | {format_money(amount)}"
        )

    vat_rate = random.choice([5, 8, 10])
    vat = int(subtotal * vat_rate / 100)
    total = subtotal + vat

    invoice_no = fake.bothify(text="HD#######")
    serial = random.choice(["AA/25E", "AB/25T", "CT/25P", "HD/25N"])
    date = random_date_this_year()

    template_type = random.choice([1, 2, 3])

    if template_type == 1:
        text = f"""
HÓA ĐƠN GIÁ TRỊ GIA TĂNG
Ký hiệu: {serial}
Số: {invoice_no}
Ngày lập: {date}

Đơn vị bán hàng: {seller_name}
Mã số thuế: {random_tax_code()}
Địa chỉ: {seller_address}
Điện thoại: {random_phone()}
Số tài khoản: {fake.random_number(digits=12, fix_len=True)}

Người mua hàng: {buyer_name}
Địa chỉ người mua: {buyer_address}
Mã số thuế người mua: {random_tax_code() if buyer_is_company else ""}

STT | Tên hàng hóa, dịch vụ          | ĐVT    | Số lượng | Đơn giá      | Thành tiền
----|--------------------------------|--------|----------|--------------|--------------
{chr(10).join(rows)}

Cộng tiền hàng: {format_money(subtotal)} VNĐ
Thuế suất GTGT: {vat_rate}%
Tiền thuế GTGT: {format_money(vat)} VNĐ
Tổng cộng tiền thanh toán: {format_money(total)} VNĐ
Số tiền viết bằng chữ: {number_to_words_simple(total)}

Người mua hàng                         Người bán hàng
(Ký, ghi rõ họ tên)                    (Ký, đóng dấu, ghi rõ họ tên)
"""
    elif template_type == 2:
        text = f"""
CÔNG TY BÁN HÀNG: {seller_name}
Địa chỉ: {seller_address}
MST: {random_tax_code()}

PHIẾU HÓA ĐƠN GTGT
Số hóa đơn: {invoice_no}
Ký hiệu mẫu số: {serial}
Ngày hóa đơn: {date}

Khách hàng: {buyer_name}
Địa chỉ khách hàng: {buyer_address}
Mã số thuế: {random_tax_code() if buyer_is_company else "Không có"}

Danh sách hàng hóa dịch vụ:
{chr(10).join(rows)}

Tổng tiền trước thuế: {format_money(subtotal)} đồng
Thuế GTGT ({vat_rate}%): {format_money(vat)} đồng
Tổng tiền sau thuế: {format_money(total)} đồng

Thanh toán bằng: {random.choice(['Chuyển khoản', 'Tiền mặt', 'Thẻ ngân hàng'])}
Trạng thái: Đã thanh toán

Đại diện bên bán: {fake.name()}
Người nhận hóa đơn: {fake.name()}
"""
    else:
        text = f"""
HÓA ĐƠN ĐIỆN TỬ GIÁ TRỊ GIA TĂNG

Mẫu số: 01GTKT0/001
Ký hiệu: {serial}
Số hóa đơn: {invoice_no}

Ngày tháng năm lập hóa đơn: {date}

Bên bán:
Tên đơn vị: {seller_name}
Mã số thuế: {random_tax_code()}
Địa chỉ: {seller_address}

Bên mua:
Tên đơn vị/người mua: {buyer_name}
Địa chỉ: {buyer_address}
Mã số thuế: {random_tax_code() if buyer_is_company else ""}

Nội dung hàng hóa dịch vụ:
{chr(10).join(rows)}

Cộng tiền hàng chưa thuế: {format_money(subtotal)}
Tiền thuế giá trị gia tăng: {format_money(vat)}
Tổng tiền thanh toán: {format_money(total)}
Bằng chữ: {number_to_words_simple(total)}

Người bán hàng ký điện tử
{seller_name}
"""

    return maybe_ocr_noise(clean_text(text))


# ==========================
# 3. BIÊN BẢN HỌP
# ==========================

def generate_bien_ban_hop(idx):
    purposes = [
        "Triển khai kế hoạch kinh doanh quý tới",
        "Đánh giá hiệu suất nhân sự trong tháng",
        "Thảo luận tiến độ dự án phần mềm mới",
        "Kiểm tra tiến độ sản xuất và giao hàng",
        "Họp cổ đông thường niên",
        "Tổng kết hoạt động phòng ban",
        "Xây dựng kế hoạch marketing",
        "Phân bổ ngân sách cho dự án",
        "Rà soát quy trình vận hành nội bộ"
    ]

    decisions = [
        "Phê duyệt ngân sách cho hoạt động triển khai.",
        "Giao phòng Kế hoạch lập báo cáo chi tiết trong tuần.",
        "Tăng cường đào tạo nhân sự kỹ thuật.",
        "Điều chỉnh tiến độ dự án theo tình hình thực tế.",
        "Thống nhất triển khai chiến dịch truyền thông mới.",
        "Bổ sung nhân sự hỗ trợ cho bộ phận vận hành.",
        "Rà soát lại hợp đồng với đối tác.",
        "Hoàn thiện tài liệu trước cuộc họp tiếp theo."
    ]

    company_name = fake.company()
    location = random.choice([
        f"Phòng họp tầng {random.randint(2, 10)}, trụ sở {company_name}",
        f"Văn phòng {company_name}",
        f"Hội trường chính của {company_name}",
        "Phòng họp trực tuyến qua Google Meet",
        "Phòng họp nội bộ"
    ])

    attendees = [fake.name() for _ in range(random.randint(5, 10))]
    date = fake.date_this_year()
    time_start = fake.time(pattern="%H:%M")
    start_dt = datetime.strptime(time_start, "%H:%M")
    end_dt = start_dt + timedelta(hours=random.randint(1, 3), minutes=random.choice([0, 15, 30]))
    time_end = end_dt.strftime("%H:%M")

    meeting_no = f"{idx:03d}/BBH/{date.year}"
    chair = attendees[0]
    secretary = attendees[-1]

    attendees_list = "\n".join([f"- Ông/Bà {name}" for name in attendees])
    selected_decisions = "\n".join([f"- {d}" for d in random.sample(decisions, k=random.randint(2, 4))])
    purpose = random.choice(purposes)

    template_type = random.choice([1, 2, 3])

    if template_type == 1:
        text = f"""
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
-------------------------

BIÊN BẢN HỌP
Số: {meeting_no}

Thời gian: Từ {time_start} đến {time_end}, ngày {date.strftime('%d/%m/%Y')}
Địa điểm: {location}

Chủ trì cuộc họp: Ông/Bà {chair}
Thư ký cuộc họp: Ông/Bà {secretary}

Thành phần tham dự:
{attendees_list}

Nội dung cuộc họp:
{purpose}

Ý kiến thảo luận:
- Đại diện các bộ phận trình bày tình hình thực hiện công việc.
- Các thành viên tham dự trao đổi về khó khăn, vướng mắc.
- Cuộc họp thống nhất các nhiệm vụ cần triển khai trong thời gian tới.

Kết luận cuộc họp:
{selected_decisions}

Biên bản được lập xong vào lúc {time_end} cùng ngày và đã được các thành viên thông qua.

CHỦ TRÌ CUỘC HỌP                 THƯ KÝ CUỘC HỌP
(Ký, ghi rõ họ tên)              (Ký, ghi rõ họ tên)

{chair}                          {secretary}
"""
    elif template_type == 2:
        text = f"""
BIÊN BẢN CUỘC HỌP NỘI BỘ

Đơn vị tổ chức: {company_name}
Mã biên bản: {meeting_no}
Ngày họp: {date.strftime('%d/%m/%Y')}
Thời gian họp: {time_start} - {time_end}
Địa điểm họp: {location}

Người điều hành: {chair}
Người ghi biên bản: {secretary}

Danh sách tham dự:
{attendees_list}

Chủ đề cuộc họp:
{purpose}

Nội dung chính:
1. Báo cáo tình hình thực hiện công việc.
2. Trao đổi phương án xử lý các vấn đề phát sinh.
3. Phân công nhiệm vụ cho từng bộ phận.
4. Xác định thời hạn hoàn thành các đầu việc.

Kết quả thống nhất:
{selected_decisions}

Biên bản này được gửi đến các thành viên liên quan để thực hiện.

Người chủ trì: {chair}
Người lập biên bản: {secretary}
"""
    else:
        text = f"""
CÔNG TY: {company_name}

BIÊN BẢN LÀM VIỆC / BIÊN BẢN HỌP

Số hiệu: {meeting_no}
Thời gian bắt đầu: {time_start}
Thời gian kết thúc: {time_end}
Ngày: {date.strftime('%d/%m/%Y')}
Địa điểm: {location}

Thành viên tham gia:
{attendees_list}

Nội dung làm việc:
Cuộc họp được tổ chức nhằm {purpose.lower()}.
Các thành viên đã thảo luận về tình hình hiện tại, các khó khăn trong quá trình thực hiện và đề xuất giải pháp cải thiện.

Các ý kiến được ghi nhận:
- Cần cập nhật dữ liệu báo cáo thường xuyên hơn.
- Cần có kế hoạch phối hợp giữa các phòng ban.
- Cần theo dõi tiến độ bằng biểu mẫu thống nhất.

Kết luận và phân công:
{selected_decisions}

Biên bản kết thúc vào lúc {time_end} cùng ngày.

Chủ trì: {chair}
Thư ký: {secretary}
"""

    return maybe_ocr_noise(clean_text(text))


# ==========================
# MAIN
# ==========================

def main():
    print("=" * 60)
    print("BẮT ĐẦU TẠO DỮ LIỆU TEXT GIẢ LẬP CHO PHOBERT")
    print("=" * 60)

    if CLEAR_OLD_FILES:
        print("[INFO] Đang xóa các file .txt cũ...")
        clear_old_txt_files()

    create_dirs()

    generators = {
        "Hop_dong_lao_dong": generate_hop_dong_lao_dong,
        "Hoa_don_GTGT": generate_hoa_don_gtgt,
        "Bien_ban_hop": generate_bien_ban_hop
    }

    total_files = 0

    for doc_type, gen_func in generators.items():
        contents = [gen_func(i + 1) for i in range(NUM_PER_CLASS)]
        random.shuffle(contents)

        train_count = int(NUM_PER_CLASS * TRAIN_RATIO)

        train_contents = contents[:train_count]
        test_contents = contents[train_count:]

        for i, content in enumerate(train_contents, start=1):
            filename = f"{doc_type}_train_{i:04d}.txt"
            path = BASE_DIR / "train" / doc_type / filename
            save_file(content, path)

        for i, content in enumerate(test_contents, start=1):
            filename = f"{doc_type}_test_{i:04d}.txt"
            path = BASE_DIR / "test" / doc_type / filename
            save_file(content, path)

        total_files += len(train_contents) + len(test_contents)

        print(f"[DONE] {doc_type}: {len(train_contents)} train + {len(test_contents)} test")

    print("=" * 60)
    print("HOÀN TẤT TẠO DỮ LIỆU")
    print(f"Tổng số file tạo ra: {total_files}")
    print(f"Thư mục lưu tại: {BASE_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()