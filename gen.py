"""
Script sinh dữ liệu văn bản giả lập cho bài toán phân loại tài liệu.

Áp dụng các kỹ thuật tăng độ khó:
  1. Ẩn/xóa tiêu đề tài liệu (35% file)
  2. Nhiễu OCR mạnh và đa dạng (~30% file)
  3. Trộn nội dung chéo giữa các class (15% file)
  4. Mở rộng lên 6 template đa dạng, có template cực ngắn
  5. Thêm biến thể viết tắt, viết thường, sai chính tả nhẹ

3 class: Hop_dong_lao_dong | Hoa_don_GTGT | Bien_ban_hop
"""

import os
import random
from pathlib import Path
from datetime import datetime, timedelta

from faker import Faker

# ==========================
# CẤU HÌNH
# ==========================

fake = Faker("vi_VN")

# Google Colab
BASE_DIR = Path("data/document_classification")

# Nếu chạy local, thay bằng:
# BASE_DIR = Path("data/document_classification")

TRAIN_RATIO = 0.8
NUM_PER_CLASS = 300        # Tăng lên 300 để có thêm đa dạng
CLEAR_OLD_FILES = True
SEED = 42

random.seed(SEED)
Faker.seed(SEED)

DOC_TYPES = [
    "Hop_dong_lao_dong",
    "Hoa_don_GTGT",
    "Bien_ban_hop",
]

# Xác suất áp dụng các kỹ thuật làm khó
PROB_HIDE_TITLE     = 0.35   # 35% file không có tiêu đề rõ ràng
PROB_OCR_NOISE      = 0.30   # 30% file bị nhiễu OCR
PROB_CROSS_CONTENT  = 0.15   # 15% file bị trộn nội dung chéo
PROB_SHORT_TEMPLATE = 0.15   # 15% file dùng template cực ngắn


# ==========================
# TIỆN ÍCH CHUNG
# ==========================

def create_dirs():
    for split in ["train", "test"]:
        for doc_type in DOC_TYPES:
            (BASE_DIR / split / doc_type).mkdir(parents=True, exist_ok=True)


def clear_old_txt_files():
    if not BASE_DIR.exists():
        return
    for split in ["train", "test"]:
        for doc_type in DOC_TYPES:
            folder = BASE_DIR / split / doc_type
            if folder.exists():
                for f in folder.glob("*.txt"):
                    f.unlink()


def clean_text(text):
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def save_file(content, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(clean_text(content))


def random_date():
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
        h, t, o = chunk // 100, (chunk % 100) // 10, chunk % 10
        words = []
        if h:
            words.append(units[h] + " trăm")
        if t > 1:
            words.append(tens[t])
            if o:
                words.append(units[o])
        elif t == 1:
            words.append(teens[o])
        elif o:
            words.append(units[o])
        return " ".join(words)

    parts, scale_idx = [], 0
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


# ==========================
# KỸ THUẬT 1: NHIỄU OCR MẠNH
# ==========================

def apply_ocr_noise(text):
    """
    Nhiễu OCR đa dạng: thay thế từ khóa, lỗi ký tự, xóa dấu,
    nhòe số, đổi chữ hoa/thường.
    """
    # Thay thế keyword nhận dạng → làm mờ tín hiệu mạnh
    keyword_noise = {
        "HÓA ĐƠN GIÁ TRỊ GIA TĂNG": random.choice([
            "HOA DON GIA TRI GIA TANG",
            "Hóa Đơn Giá Trị Gia Tăng",
            "H.Đ. GTGT",
            "HĐ GIÁ TRỊ GIA TĂNG",
        ]),
        "HÓA ĐƠN GTGT": random.choice([
            "HOA DON GTGT", "hóa đơn gtgt", "HD-GTGT",
        ]),
        "HỢP ĐỒNG LAO ĐỘNG": random.choice([
            "HOP DONG LAO DONG",
            "Hợp Đồng Lao Động",
            "H.Đ. LAO ĐỘNG",
            "HDLD",
        ]),
        "BIÊN BẢN HỌP": random.choice([
            "BIEN BAN HOP",
            "Biên Bản Họp",
            "B.B. HỌP",
            "BB HOP",
        ]),
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM": random.choice([
            "CONG HOA XA HOI CHU NGHIA VIET NAM",
            "Cộng Hòa Xã Hội Chủ Nghĩa Việt Nam",
            "CH XHCN Việt Nam",
        ]),
        "Độc lập - Tự do - Hạnh phúc": random.choice([
            "Doc lap - Tu do - Hanh phuc",
            "Độc lập – Tự do – Hạnh phúc",
            "DL-TD-HP",
        ]),
        "Mã số thuế": random.choice(["MST", "M.S.T:", "Ma so thue", "mã số thuế"]),
        "Tổng tiền":  random.choice(["Tong tien", "TỔNG TIỀN", "Tổng Tiền"]),
        "Điều 1":     random.choice(["Đlều 1", "Diều 1", "D1."]),
        "Điều 2":     random.choice(["Đlều 2", "D2."]),
        "Người lao động": random.choice(["nguoi lao dong", "NLĐ", "Người Lao Động"]),
        "Người sử dụng lao động": random.choice(["NSDLĐ", "nguoi su dung lao dong"]),
    }

    for old, new in keyword_noise.items():
        if old in text:
            text = text.replace(old, new, 1)  # chỉ thay lần đầu

    # Nhiễu ký tự ngẫu nhiên (thêm ký tự lạ vào 1–2 vị trí)
    if random.random() < 0.4:
        pos = random.randint(len(text) // 4, len(text) * 3 // 4)
        noise_char = random.choice(["~", "|", "□", "■", "…", "°"])
        text = text[:pos] + noise_char + text[pos:]

    # Xóa ngẫu nhiên 1 dòng giữa (giả lập scan thiếu)
    if random.random() < 0.25:
        lines = text.splitlines()
        if len(lines) > 8:
            drop_idx = random.randint(2, len(lines) - 3)
            lines.pop(drop_idx)
            text = "\n".join(lines)

    return text


# ==========================
# KỸ THUẬT 2: NỘI DUNG TRỘN CHÉO
# ==========================

def cross_content_hop_dong():
    """Đoạn bổ sung kiểu hóa đơn/biên bản chèn vào hợp đồng."""
    snippets = [
        f"""
Phụ lục thanh toán:
STT | Khoản mục         | Số tiền
  1 | Lương cơ bản      | {format_money(random.randint(8,25)*1000000)} VNĐ
  2 | Phụ cấp đi lại    | {format_money(random.randint(5,20)*100000)} VNĐ
  3 | Bảo hiểm xã hội   | {format_money(random.randint(5,15)*100000)} VNĐ
""",
        f"""
Biên bản bàn giao công việc đính kèm:
Thời gian bàn giao: {random_date()}
Bên giao: {fake.name()}
Bên nhận: {fake.name()}
""",
    ]
    return random.choice(snippets)


def cross_content_hoa_don():
    """Đoạn bổ sung kiểu hợp đồng chèn vào hóa đơn."""
    snippets = [
        f"""
Điều khoản thanh toán:
Bên mua cam kết thanh toán trong vòng {random.choice([7, 14, 30])} ngày kể từ ngày nhận hóa đơn.
Trường hợp thanh toán trễ hạn sẽ chịu lãi suất {random.randint(1,3)}%/tháng theo thỏa thuận.
""",
        f"""
Ghi chú hợp đồng liên quan:
Hóa đơn này phát sinh theo Hợp đồng số {fake.bothify(text="HD-####/####")}.
Mọi khiếu nại về hàng hóa cần thực hiện trong vòng 7 ngày.
""",
    ]
    return random.choice(snippets)


def cross_content_bien_ban():
    """Đoạn bổ sung kiểu hóa đơn/hợp đồng chèn vào biên bản họp."""
    snippets = [
        f"""
Ngân sách được phê duyệt trong cuộc họp:
Hạng mục             | Số tiền
Marketing            | {format_money(random.randint(10,50)*1000000)} VNĐ
Vận hành             | {format_money(random.randint(5,30)*1000000)} VNĐ
""",
        f"""
Hợp đồng liên quan được thảo luận:
Số hợp đồng: {fake.bothify(text="HD-####/####")}
Giá trị: {format_money(random.randint(50,500)*1000000)} VNĐ
Thời hạn thực hiện: {random.randint(3,24)} tháng
""",
    ]
    return random.choice(snippets)


# ==========================
# 1. HỢP ĐỒNG LAO ĐỘNG (6 template)
# ==========================

def generate_hop_dong_lao_dong(idx, hide_title=False, ocr_noise=False, cross_content=False):
    positions = [
        "Nhân viên Kinh doanh", "Kỹ sư Phần mềm", "Trưởng phòng Hành chính",
        "Nhân viên Kế toán", "Chuyên viên Nhân sự", "Lập trình viên",
        "Giám sát sản xuất", "Nhân viên Marketing", "Chuyên viên Tư vấn",
        "Nhân viên Kho vận", "Trưởng nhóm Kinh doanh", "Kỹ thuật viên",
    ]
    contract_types = ["xác định thời hạn", "không xác định thời hạn", "thử việc", "theo mùa vụ"]
    salary_list = [8, 9, 10, 12, 15, 18, 20, 25, 30]

    company    = fake.company()
    co_addr    = fake.address().replace("\n", ", ")
    employer   = fake.name()
    emp_title  = random.choice(["Giám đốc", "Phó Giám đốc", "Trưởng phòng Nhân sự"])
    employee   = fake.name()
    emp_dob    = fake.date_of_birth(minimum_age=22, maximum_age=55).strftime("%d/%m/%Y")
    emp_addr   = fake.address().replace("\n", ", ")
    emp_id     = fake.random_number(digits=12, fix_len=True)
    position   = random.choice(positions)
    c_type     = random.choice(contract_types)
    salary     = random.choice(salary_list) * 1_000_000
    allowance  = random.choice([0, 500_000, 1_000_000, 1_500_000, 2_000_000])
    duration   = random.choice(["02 tháng", "06 tháng", "12 tháng", "24 tháng", "36 tháng", "không xác định thời hạn"])
    start_date = fake.date_between(start_date="-1y", end_date="+30d").strftime("%d/%m/%Y")
    sign_date  = random_date()
    d, m, y    = sign_date.split("/")
    contract_no = f"{idx:03d}/{random.choice(['HĐLĐ','HDLD','HĐ'])}/{y}"
    dept       = random.choice(["Kinh doanh", "Kỹ thuật", "Hành chính", "Kế toán", "Nhân sự", "Vận hành"])

    # Chọn template
    if random.random() < PROB_SHORT_TEMPLATE:
        tpl = 6   # template ngắn
    else:
        tpl = random.randint(1, 5)

    # --- Tiêu đề ---
    if hide_title:
        header = f"Số: {contract_no}\nNgày ký: {sign_date}"
    else:
        header = random.choice([
            "HỢP ĐỒNG LAO ĐỘNG",
            "HỢP ĐỒNG LAO ĐỘNG\n(Loại hợp đồng: " + c_type + ")",
            "BIỂU MẪU HỢP ĐỒNG LAO ĐỘNG",
        ])

    if tpl == 1:
        text = f"""
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---

{header}
Số: {contract_no}

Hôm nay, ngày {d} tháng {m} năm {y}, tại {co_addr}, chúng tôi gồm:

BÊN A: NGƯỜI SỬ DỤNG LAO ĐỘNG
Tên đơn vị: {company}
Địa chỉ: {co_addr}
Đại diện: Ông/Bà {employer}  |  Chức vụ: {emp_title}
Điện thoại: {random_phone()}

BÊN B: NGƯỜI LAO ĐỘNG
Họ và tên: {employee}  |  Ngày sinh: {emp_dob}
Số CCCD: {emp_id}
Địa chỉ: {emp_addr}

Điều 1. Công việc
Vị trí: {position}  |  Bộ phận: {dept}
Địa điểm làm việc: {co_addr}

Điều 2. Thời hạn hợp đồng
Loại hợp đồng: {c_type}  |  Thời hạn: {duration}
Ngày bắt đầu: {start_date}

Điều 3. Lương và phúc lợi
Lương chính: {format_money(salary)} VNĐ/tháng
{"Phụ cấp: " + format_money(allowance) + " VNĐ/tháng" if allowance else "Không có phụ cấp thêm"}
Bằng chữ: {number_to_words_simple(salary + allowance)}
Hình thức: chuyển khoản cuối tháng

Điều 4. Quyền và nghĩa vụ
Người lao động thực hiện công việc theo phân công và nội quy công ty.
Công ty bảo đảm điều kiện làm việc và thanh toán lương đúng hạn.

Điều 5. Hiệu lực
Hợp đồng có hiệu lực từ ngày {start_date}, lập thành 02 bản.

BÊN A                                BÊN B
{employer}                           {employee}
"""

    elif tpl == 2:
        text = f"""
{header}
Số hợp đồng: {contract_no}

Căn cứ Bộ luật Lao động hiện hành, hai bên thỏa thuận:

1. Người sử dụng lao động
   Công ty: {company}  |  Địa chỉ: {co_addr}
   Đại diện: {employer}  |  Chức danh: {emp_title}

2. Người lao động
   Họ tên: {employee}  |  Sinh: {emp_dob}
   CCCD: {emp_id}  |  Địa chỉ: {emp_addr}

Nội dung:
- Chức danh: {position}  |  Phòng: {dept}
- Loại HĐ: {c_type}  |  Thời hạn: {duration}
- Ngày bắt đầu: {start_date}
- Lương cơ bản: {format_money(salary)} đồng/tháng
{"- Phụ cấp: " + format_money(allowance) + " đồng/tháng" if allowance else ""}
- Thời giờ làm việc: 8 giờ/ngày, thứ Hai đến thứ Sáu
- BHXH, BHYT: theo quy định pháp luật

Hai bên cam kết thực hiện đúng các điều khoản trên.

Lập tại {co_addr}, ngày {sign_date}.

ĐẠI DIỆN CÔNG TY          NGƯỜI LAO ĐỘNG
{employer}                 {employee}
"""

    elif tpl == 3:
        text = f"""
{company.upper()}
{co_addr}
ĐT: {random_phone()}

{header}
Mã: {contract_no}  |  Ngày ký: {sign_date}

THÔNG TIN NHÂN SỰ
Họ tên: {employee}
Ngày sinh: {emp_dob}
CCCD/CMND: {emp_id}
Địa chỉ: {emp_addr}

THÔNG TIN CÔNG VIỆC
Vị trí: {position}
Bộ phận: {dept}
Loại hợp đồng: {c_type}
Thời hạn: {duration}
Ngày nhận việc: {start_date}

CHẾ ĐỘ LƯƠNG THƯỞNG
Lương thỏa thuận: {format_money(salary)} VNĐ/tháng
{"Phụ cấp thêm: " + format_money(allowance) + " VNĐ/tháng" if allowance else ""}
Tổng thu nhập: {format_money(salary + allowance)} VNĐ/tháng
Hình thức: chuyển khoản ngân hàng, ngày 30 hàng tháng

CAM KẾT
Người lao động cam kết tuân thủ nội quy, quy chế công ty.
Công ty cam kết bảo đảm quyền lợi hợp pháp cho người lao động.

Đại diện công ty: {employer}
Người lao động: {employee}
"""

    elif tpl == 4:
        probation_salary = int(salary * 0.85)
        text = f"""
{header}
(Hợp đồng thử việc - Áp dụng cho giai đoạn đầu)

Số: {contract_no}  |  Ngày: {sign_date}

Công ty {company} (gọi là Bên A) và Ông/Bà {employee} (gọi là Bên B) thỏa thuận:

§1 – Công việc
Bên B nhận vị trí {position} tại bộ phận {dept}.
Địa điểm: {co_addr}.

§2 – Thời gian thử việc
Thời gian: {random.choice(['30 ngày', '45 ngày', '60 ngày'])}, bắt đầu từ {start_date}.
Sau thử việc, nếu đạt yêu cầu sẽ ký hợp đồng chính thức loại: {c_type}.

§3 – Lương thử việc
Mức lương: {format_money(probation_salary)} VNĐ/tháng
(tương đương {85}% mức lương chính thức {format_money(salary)} VNĐ/tháng)

§4 – Điều khoản khác
Trong thời gian thử việc, hai bên có quyền chấm dứt hợp đồng với thông báo 03 ngày trước.

Bên A: {employer} ({emp_title})
Bên B: {employee}
"""

    elif tpl == 5:
        text = f"""
PHIẾU THỎA THUẬN LAO ĐỘNG
{header}
Ref: {contract_no}

Giữa:
+ Đơn vị sử dụng lao động: {company}, đại diện {employer}
+ Cá nhân: {employee}, CCCD {emp_id}, địa chỉ {emp_addr}

Thỏa thuận các điều khoản sau:
[1] Vị trí làm việc   : {position} — Phòng {dept}
[2] Loại hợp đồng     : {c_type}
[3] Thời hạn          : {duration} (từ {start_date})
[4] Lương tháng       : {format_money(salary)} VNĐ
{"[5] Phụ cấp          : " + format_money(allowance) + " VNĐ/tháng" if allowance else ""}
[{"6" if allowance else "5"}] Thời gian làm việc : 08h00 – 17h00, Thứ 2 – Thứ 6
[{"7" if allowance else "6"}] Bảo hiểm          : theo Luật BHXH hiện hành
[{"8" if allowance else "7"}] Nghỉ phép          : {random.randint(12,16)} ngày/năm

Hai bên xác nhận và ký kết ngày {sign_date}.
{employer}                           {employee}
"""

    else:  # tpl == 6: template ngắn (khó nhận diện)
        text = f"""
Số: {contract_no}
Ngày: {sign_date}

Công ty: {company}
Người lao động: {employee} — CCCD: {emp_id}
Vị trí: {position}  |  Phòng: {dept}
Thời hạn: {duration}  |  Loại: {c_type}
Bắt đầu: {start_date}
Lương: {format_money(salary)} VNĐ/tháng{(" + phụ cấp " + format_money(allowance)) if allowance else ""}

Các điều khoản khác theo quy định hiện hành của công ty và pháp luật lao động.
Đại diện: {employer}  |  NLĐ: {employee}
"""

    # Trộn nội dung chéo
    if cross_content:
        text += "\n" + cross_content_hop_dong()

    return apply_ocr_noise(text) if ocr_noise else clean_text(text)


# ==========================
# 2. HÓA ĐƠN GTGT (6 template)
# ==========================

def generate_hoa_don_gtgt(idx, hide_title=False, ocr_noise=False, cross_content=False):
    product_pool = [
        ("Dịch vụ tư vấn quản lý",      "Lần",  random.randint(1,3),   random.randint(1_000_000, 5_000_000)),
        ("Phần mềm quản lý bán hàng",    "Gói",  1,                     random.randint(8_000_000, 30_000_000)),
        ("Máy in văn phòng Canon",        "Cái",  random.randint(1,5),   random.randint(2_500_000, 7_000_000)),
        ("Máy tính xách tay",             "Cái",  random.randint(1,4),   random.randint(12_000_000, 25_000_000)),
        ("Dịch vụ bảo trì hệ thống",     "Tháng",random.randint(1,12),  random.randint(500_000, 2_000_000)),
        ("Văn phòng phẩm",                "Bộ",   random.randint(5,50),  random.randint(50_000, 300_000)),
        ("In ấn tài liệu",                "Trang",random.randint(100,1000),random.randint(500,3_000)),
        ("Thiết bị mạng switch 24 cổng",  "Bộ",   random.randint(1,6),   random.randint(1_000_000, 8_000_000)),
        ("Dịch vụ vệ sinh văn phòng",    "Tháng",random.randint(1,6),   random.randint(800_000, 2_000_000)),
        ("Bàn ghế văn phòng",            "Bộ",   random.randint(1,10),  random.randint(1_500_000, 5_000_000)),
        ("Camera an ninh",               "Cái",  random.randint(2,8),   random.randint(500_000, 2_000_000)),
        ("Dịch vụ thiết kế website",     "Gói",  1,                     random.randint(5_000_000, 20_000_000)),
    ]

    num_items = random.randint(1, 5)
    selected  = random.sample(product_pool, k=num_items)
    rows, subtotal = [], 0
    for i, (name, unit, qty, uprice) in enumerate(selected, 1):
        amt = qty * uprice
        subtotal += amt
        rows.append(f"{i:<3}| {name:<32}| {unit:<7}| {qty:<8}| {format_money(uprice):<14}| {format_money(amt)}")

    vat_rate = random.choice([5, 8, 10])
    vat      = int(subtotal * vat_rate / 100)
    total    = subtotal + vat

    invoice_no = fake.bothify(text="HD#######")
    serial     = random.choice(["AA/25E", "AB/25T", "CT/25P", "HD/25N", "AA/25T"])
    date       = random_date()
    seller     = fake.company()
    sel_addr   = fake.address().replace("\n", ", ")
    buyer_is_co= random.random() < 0.75
    buyer      = fake.company() if buyer_is_co else fake.name()
    buy_addr   = fake.address().replace("\n", ", ")
    pay_method = random.choice(["Chuyển khoản", "Tiền mặt", "Thẻ ngân hàng", "Ví điện tử"])
    pay_status = random.choice(["Đã thanh toán", "Chưa thanh toán", "Thanh toán một phần"])

    if random.random() < PROB_SHORT_TEMPLATE:
        tpl = 6
    else:
        tpl = random.randint(1, 5)

    if hide_title:
        header = f"Ký hiệu: {serial}  |  Số: {invoice_no}"
    else:
        header = random.choice([
            "HÓA ĐƠN GIÁ TRỊ GIA TĂNG",
            "HÓA ĐƠN GTGT",
            "HÓA ĐƠN ĐIỆN TỬ GIÁ TRỊ GIA TĂNG",
            "PHIẾU HÓA ĐƠN GTGT",
        ])

    row_str = "\n".join(rows)

    if tpl == 1:
        text = f"""
{header}
Ký hiệu: {serial}  |  Số: {invoice_no}  |  Ngày: {date}
Mẫu số: 01GTKT0/001

ĐƠN VỊ BÁN HÀNG
Tên: {seller}
Mã số thuế: {random_tax_code()}
Địa chỉ: {sel_addr}
ĐT: {random_phone()}  |  TK: {fake.random_number(digits=12, fix_len=True)}

NGƯỜI MUA HÀNG
Tên: {buyer}
Địa chỉ: {buy_addr}
{"Mã số thuế: " + random_tax_code() if buyer_is_co else ""}

STT| Tên hàng hóa/dịch vụ           | ĐVT    | Số lượng | Đơn giá        | Thành tiền
---|--------------------------------|--------|----------|----------------|---------------
{row_str}

Cộng tiền hàng         : {format_money(subtotal)} VNĐ
Thuế suất GTGT         : {vat_rate}%
Tiền thuế GTGT         : {format_money(vat)} VNĐ
Tổng thanh toán        : {format_money(total)} VNĐ
Bằng chữ: {number_to_words_simple(total)}
Hình thức thanh toán   : {pay_method}
Trạng thái             : {pay_status}

Người mua hàng                     Người bán hàng
(Ký, ghi rõ họ tên)                (Ký, đóng dấu)
"""

    elif tpl == 2:
        text = f"""
CÔNG TY: {seller}
Địa chỉ: {sel_addr}  |  MST: {random_tax_code()}
ĐT: {random_phone()}

{header}
Số: {invoice_no}  |  Ký hiệu: {serial}  |  Ngày: {date}

Khách hàng: {buyer}
Địa chỉ: {buy_addr}
{"MST: " + random_tax_code() if buyer_is_co else "Không có MST"}

DANH SÁCH HÀNG HÓA, DỊCH VỤ:
{row_str}

Tổng tiền trước thuế : {format_money(subtotal)} đồng
Thuế GTGT ({vat_rate}%)    : {format_money(vat)} đồng
Tổng thanh toán      : {format_money(total)} đồng

Thanh toán: {pay_method}  |  Trạng thái: {pay_status}

Đại diện bán: {fake.name()}    Người nhận: {fake.name()}
"""

    elif tpl == 3:
        text = f"""
{header}
Mẫu: 01GTKT0/001  |  Ký hiệu: {serial}  |  Số: {invoice_no}
Ngày lập: {date}

Bên bán:
  {seller}  —  MST: {random_tax_code()}
  Địa chỉ: {sel_addr}

Bên mua:
  {buyer}
  Địa chỉ: {buy_addr}
  {"MST: " + random_tax_code() if buyer_is_co else ""}

Hàng hóa/dịch vụ:
{row_str}

Chưa thuế  : {format_money(subtotal)}
GTGT {vat_rate}%   : {format_money(vat)}
Tổng cộng  : {format_money(total)}
Bằng chữ   : {number_to_words_simple(total)}

Người bán (ký điện tử): {seller}
"""

    elif tpl == 4:
        text = f"""
HOÁ ĐƠN BÁN HÀNG / PHIẾU XUẤT KHO KÈM VẬN CHUYỂN
{header if hide_title else ""}
Số chứng từ: {invoice_no}  |  Ngày: {date}

Từ: {seller} ({sel_addr})
Đến: {buyer} ({buy_addr})
{"MST người mua: " + random_tax_code() if buyer_is_co else ""}

Nội dung giao dịch:
{row_str}

Trị giá hàng        : {format_money(subtotal)} VNĐ
Thuế GTGT ({vat_rate}%)  : {format_money(vat)} VNĐ
Tổng giá trị        : {format_money(total)} VNĐ
Hình thức TT        : {pay_method}

Người lập phiếu: {fake.name()}  |  Thủ kho: {fake.name()}
"""

    elif tpl == 5:
        text = f"""
[{serial}] — {invoice_no}
Ngày xuất hóa đơn: {date}

Người bán  : {seller}
MST bán    : {random_tax_code()}
Địa chỉ   : {sel_addr}

Người mua  : {buyer}
{"MST mua   : " + random_tax_code() if buyer_is_co else ""}
Địa chỉ   : {buy_addr}

Chi tiết:
{row_str}

Tổng chưa thuế : {format_money(subtotal)}
Thuế {vat_rate}%       : {format_money(vat)}
Phải thanh toán: {format_money(total)}
Chữ            : {number_to_words_simple(total)}
TT bằng        : {pay_method}  [{pay_status}]
"""

    else:  # tpl == 6: ngắn gọn
        text = f"""
Số: {invoice_no}  |  Ngày: {date}
Người bán: {seller}  —  MST: {random_tax_code()}
Người mua: {buyer}

{row_str}

Tổng (chưa VAT): {format_money(subtotal)} VNĐ
VAT {vat_rate}%         : {format_money(vat)} VNĐ
Thanh toán      : {format_money(total)} VNĐ
"""

    if cross_content:
        text += "\n" + cross_content_hoa_don()

    return apply_ocr_noise(text) if ocr_noise else clean_text(text)


# ==========================
# 3. BIÊN BẢN HỌP (6 template)
# ==========================

def generate_bien_ban_hop(idx, hide_title=False, ocr_noise=False, cross_content=False):
    purposes = [
        "Triển khai kế hoạch kinh doanh quý tới",
        "Đánh giá hiệu suất nhân sự định kỳ",
        "Thảo luận tiến độ dự án phần mềm",
        "Kiểm tra tiến độ sản xuất và giao hàng",
        "Tổng kết hoạt động phòng ban",
        "Xây dựng kế hoạch marketing quý mới",
        "Phân bổ ngân sách cho các dự án",
        "Rà soát quy trình vận hành nội bộ",
        "Đánh giá kết quả kinh doanh tháng",
        "Họp triển khai chiến lược năm mới",
        "Thảo luận phương án mở rộng thị trường",
        "Rà soát hợp đồng với đối tác chiến lược",
    ]
    decisions = [
        "Phê duyệt ngân sách cho hoạt động triển khai.",
        "Giao phòng Kế hoạch lập báo cáo chi tiết trong tuần.",
        "Tăng cường đào tạo nhân sự kỹ thuật.",
        "Điều chỉnh tiến độ dự án theo thực tế.",
        "Thống nhất triển khai chiến dịch truyền thông mới.",
        "Bổ sung nhân sự hỗ trợ bộ phận vận hành.",
        "Rà soát lại hợp đồng với đối tác.",
        "Hoàn thiện tài liệu trước cuộc họp tiếp theo.",
        "Tổ chức đánh giá nhân sự định kỳ vào cuối tháng.",
        "Cập nhật quy trình làm việc theo tiêu chuẩn ISO.",
    ]

    company   = fake.company()
    location  = random.choice([
        f"Phòng họp tầng {random.randint(2,10)}, trụ sở {company}",
        f"Văn phòng {company}",
        f"Hội trường chính {company}",
        "Phòng họp trực tuyến qua Google Meet / Zoom",
        "Phòng họp nội bộ",
        f"Cơ sở {fake.city()} — {company}",
    ])
    n_attend  = random.randint(4, 12)
    attendees = [fake.name() for _ in range(n_attend)]
    date_obj  = fake.date_this_year()
    date_str  = date_obj.strftime("%d/%m/%Y")
    t_start   = fake.time(pattern="%H:%M")
    start_dt  = datetime.strptime(t_start, "%H:%M")
    end_dt    = start_dt + timedelta(hours=random.randint(1,3), minutes=random.choice([0,15,30,45]))
    t_end     = end_dt.strftime("%H:%M")
    meeting_no= f"{idx:03d}/BBH/{date_obj.year}"
    chair     = attendees[0]
    secretary = attendees[-1]
    purpose   = random.choice(purposes)
    sel_dec   = random.sample(decisions, k=random.randint(2,5))

    att_list  = "\n".join([f"- Ông/Bà {n}" for n in attendees])
    dec_list  = "\n".join([f"- {d}" for d in sel_dec])
    task_list = "\n".join([
        f"  + {fake.name()}: {random.choice(['Lập báo cáo', 'Theo dõi tiến độ', 'Phối hợp thực hiện', 'Tổng hợp số liệu', 'Liên hệ đối tác'])} trước ngày {fake.date_between(start_date='today', end_date='+30d').strftime('%d/%m/%Y')}"
        for _ in range(random.randint(2,4))
    ])

    if random.random() < PROB_SHORT_TEMPLATE:
        tpl = 6
    else:
        tpl = random.randint(1, 5)

    if hide_title:
        header = f"Số: {meeting_no}  |  Ngày: {date_str}"
    else:
        header = random.choice([
            "BIÊN BẢN HỌP",
            "BIÊN BẢN CUỘC HỌP NỘI BỘ",
            "BIÊN BẢN LÀM VIỆC",
            "BIÊN BẢN GHI NHỚ CUỘC HỌP",
        ])

    if tpl == 1:
        text = f"""
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập - Tự do - Hạnh phúc
---

{header}
Số: {meeting_no}

Thời gian: {t_start} – {t_end}, ngày {date_str}
Địa điểm : {location}
Chủ trì  : Ông/Bà {chair}
Thư ký   : Ông/Bà {secretary}

THÀNH PHẦN THAM DỰ ({n_attend} người):
{att_list}

NỘI DUNG CUỘC HỌP:
Mục đích: {purpose}

Ý kiến thảo luận:
- Đại diện các bộ phận trình bày tình hình thực hiện công việc.
- Các thành viên trao đổi khó khăn, vướng mắc và đề xuất giải pháp.
- Thống nhất nhiệm vụ triển khai trong thời gian tới.

KẾT LUẬN:
{dec_list}

PHÂN CÔNG THỰC HIỆN:
{task_list}

Biên bản kết thúc lúc {t_end}. Các thành viên đồng thuận thông qua.

CHỦ TRÌ                          THƯ KÝ
{chair}                          {secretary}
"""

    elif tpl == 2:
        text = f"""
{header}

Đơn vị: {company}
Mã biên bản: {meeting_no}
Ngày họp: {date_str}  |  Thời gian: {t_start} – {t_end}
Địa điểm: {location}
Người điều hành: {chair}  |  Ghi biên bản: {secretary}

Danh sách tham dự:
{att_list}

Chủ đề: {purpose}

Nội dung thảo luận:
1. Báo cáo tình hình thực hiện công việc tuần/tháng qua.
2. Trao đổi phương án xử lý vấn đề phát sinh.
3. Phân công nhiệm vụ và thời hạn hoàn thành.

Kết quả thống nhất:
{dec_list}

Phân công:
{task_list}

Biên bản gửi đến các thành viên liên quan.
Người chủ trì: {chair}  |  Người lập: {secretary}
"""

    elif tpl == 3:
        text = f"""
{company.upper()}
PHÒNG {random.choice(['NHÂN SỰ','KINH DOANH','KỸ THUẬT','KẾ TOÁN','TỔNG HỢP']).upper()}

{header}
Ref: {meeting_no}

Thời điểm:
- Bắt đầu : {t_start} ngày {date_str}
- Kết thúc : {t_end} ngày {date_str}
- Địa điểm : {location}

Tham dự:
{att_list}

Chủ đề làm việc:
{purpose}

Tóm tắt nội dung:
Cuộc họp tập trung rà soát tiến độ công việc, tháo gỡ khó khăn
và đề xuất giải pháp cải thiện hiệu quả hoạt động.

Quyết định:
{dec_list}

Phân công:
{task_list}

Chủ trì: {chair}
Thư ký : {secretary}
"""

    elif tpl == 4:
        text = f"""
MINUTES OF MEETING (BIÊN BẢN HỌP)
{header if hide_title else ""}
Meeting ID: {meeting_no}

Date    : {date_str}
Time    : {t_start} – {t_end}
Venue   : {location}
Company : {company}
Chair   : {chair}
Recorder: {secretary}

Attendees ({n_attend}):
{att_list}

Agenda / Nội dung:
{purpose}

Discussion / Thảo luận:
- Các bên đã trình bày quan điểm về tình hình hiện tại.
- Thống nhất hướng xử lý và phân công công việc cụ thể.

Agreed Actions / Kết luận:
{dec_list}

Action Items:
{task_list}

Signed / Ký:
{chair} (Chủ trì)        {secretary} (Thư ký)
"""

    elif tpl == 5:
        text = f"""
{header}
[{meeting_no}] — {date_str} — {company}

Họp lúc {t_start}, địa điểm: {location}
Kết thúc lúc {t_end}.

Người tham dự:
{att_list}

Vấn đề thảo luận:
{purpose}

Ý kiến các bên:
Sau khi trao đổi, các thành viên thống nhất những nội dung sau:
{dec_list}

Công việc tiếp theo:
{task_list}

Cuộc họp kết thúc. Biên bản được lập và lưu hành nội bộ.
{chair} / {secretary}
"""

    else:  # tpl == 6: ngắn gọn
        text = f"""
Số: {meeting_no}  |  Ngày: {date_str}
Công ty: {company}
Thời gian: {t_start} – {t_end}  |  Địa điểm: {location}

Tham dự: {", ".join(attendees[:5])}{"..." if n_attend > 5 else ""}
Chủ trì: {chair}  |  Thư ký: {secretary}

Nội dung: {purpose}

Kết luận:
{dec_list}

{chair} (Chủ trì) — {secretary} (Thư ký)
"""

    if cross_content:
        text += "\n" + cross_content_bien_ban()

    return apply_ocr_noise(text) if ocr_noise else clean_text(text)


# ==========================
# MAIN
# ==========================

def main():
    print("=" * 65)
    print("SINH DỮ LIỆU VĂN BẢN — DATASET TĂNG ĐỘ KHÓ")
    print("=" * 65)
    print(f"  Số file/class     : {NUM_PER_CLASS}")
    print(f"  Tỉ lệ train/test  : {TRAIN_RATIO:.0%} / {1-TRAIN_RATIO:.0%}")
    print(f"  Ẩn tiêu đề        : {PROB_HIDE_TITLE:.0%} file")
    print(f"  Nhiễu OCR         : {PROB_OCR_NOISE:.0%} file")
    print(f"  Trộn nội dung chéo: {PROB_CROSS_CONTENT:.0%} file")
    print(f"  Template ngắn     : {PROB_SHORT_TEMPLATE:.0%} file")
    print("=" * 65)

    if CLEAR_OLD_FILES:
        print("[INFO] Xóa file .txt cũ...")
        clear_old_txt_files()

    create_dirs()

    generators = {
        "Hop_dong_lao_dong": generate_hop_dong_lao_dong,
        "Hoa_don_GTGT":      generate_hoa_don_gtgt,
        "Bien_ban_hop":      generate_bien_ban_hop,
    }

    stats = {}
    total = 0

    for doc_type, gen_fn in generators.items():
        contents = []
        n_hide = n_ocr = n_cross = 0

        for i in range(NUM_PER_CLASS):
            hide   = random.random() < PROB_HIDE_TITLE
            noise  = random.random() < PROB_OCR_NOISE
            cross  = random.random() < PROB_CROSS_CONTENT

            text = gen_fn(
                idx=i + 1,
                hide_title=hide,
                ocr_noise=noise,
                cross_content=cross,
            )
            contents.append(text)
            if hide:  n_hide  += 1
            if noise: n_ocr   += 1
            if cross: n_cross += 1

        random.shuffle(contents)
        train_n = int(NUM_PER_CLASS * TRAIN_RATIO)
        train_c = contents[:train_n]
        test_c  = contents[train_n:]

        for i, c in enumerate(train_c, 1):
            save_file(c, BASE_DIR / "train" / doc_type / f"{doc_type}_train_{i:04d}.txt")
        for i, c in enumerate(test_c, 1):
            save_file(c, BASE_DIR / "test"  / doc_type / f"{doc_type}_test_{i:04d}.txt")

        stats[doc_type] = {
            "train": len(train_c), "test": len(test_c),
            "hide": n_hide, "ocr": n_ocr, "cross": n_cross,
        }
        total += len(train_c) + len(test_c)

        print(f"\n[DONE] {doc_type}")
        print(f"       Train: {len(train_c)}  |  Test: {len(test_c)}")
        print(f"       Ẩn tiêu đề: {n_hide}  |  Nhiễu OCR: {n_ocr}  |  Nội dung chéo: {n_cross}")

    print("\n" + "=" * 65)
    print(f"HOÀN TẤT — Tổng: {total} file — Lưu tại: {BASE_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()