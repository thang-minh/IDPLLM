# ui_utils/quotes.py
import random

QUOTES = [
    "Đọc nhiều, biết nhiều, rồi ta sẽ thành... siêu nhân tài liệu!",
    "Tri thức là sức mạnh, tài liệu là vũ khí!",
    "Mỗi trang PDF là một hành trình khám phá.",
    "Hãy để AI làm việc, còn bạn cứ chill thôi!",
    "Chìa khóa thành công nằm ở việc hiểu rõ tài liệu.",
    "Học hỏi không ngừng – bí quyết của mọi nhà vô địch.",
    "Thông tin đúng, quyết định chuẩn, thành công gần ngay!",
    "Từ dữ liệu thô đến kiến thức tinh túy – hành trình bắt đầu!",
    "Đừng để tài liệu làm khó bạn, hãy làm chủ nó!",
    "Một tài liệu tốt là người bạn đồng hành đáng tin cậy."
]

def get_random_quote():
    return random.choice(QUOTES)