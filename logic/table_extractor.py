# logic/table_extractor.py
import pdfplumber
import pandas as pd
import io

def generate_unique_column_names(columns):
    """Tạo tên cột duy nhất nếu có trùng lặp."""
    seen = {}
    new_columns = []
    for i, col_name in enumerate(columns):
        # Xử lý tên cột rỗng hoặc None
        original_name = str(col_name) if col_name is not None and str(col_name).strip() != "" else f" cột_trống_{i}"
        
        name_to_check = original_name
        count = seen.get(name_to_check, 0)
        
        if count > 0: # Tên cột đã tồn tại
            new_name = f"{original_name}_{count}"
        else:
            new_name = original_name
            
        new_columns.append(new_name)
        seen[name_to_check] = count + 1
        # Cập nhật lại seen cho tên gốc nếu tên mới được tạo để lần sau nó tăng count đúng
        if new_name != original_name:
             seen[original_name] = seen.get(original_name,0) +1

    return new_columns

def extract_tables_from_pdf(file_bytes):
    """
    Trích xuất tất cả bảng từ PDF thành list DataFrame, kèm số trang.
    Đảm bảo tên cột là duy nhất.
    Trả về: List[Tuple[int, pd.DataFrame]]
    """
    tables = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_tables = page.extract_tables()
                for table_data in page_tables:
                    if table_data and len(table_data) > 0: # Đảm bảo table_data không rỗng và có ít nhất 1 dòng (cho header)
                        header_row = table_data[0]
                        data_rows = table_data[1:]

                        # Xử lý header: đảm bảo không có None và tạo tên duy nhất
                        # Chuyển None thành chuỗi rỗng trước khi tạo tên duy nhất để xử lý nhất quán
                        processed_header = [str(h) if h is not None else '' for h in header_row]
                        unique_header = generate_unique_column_names(processed_header)
                        
                        try:
                            df = pd.DataFrame(data_rows, columns=unique_header)
                            tables.append((i + 1, df))
                        except Exception as df_error:
                            print(f"Lỗi khi tạo DataFrame ở trang {i+1} với header đã xử lý: {df_error}. Dữ liệu bảng: {table_data}")
                            # Fallback: nếu vẫn lỗi, thử tạo DataFrame không header
                            try:
                                df = pd.DataFrame(table_data) # pdfplumber trả về list of lists
                                # Tạo header mặc định duy nhất nếu DataFrame được tạo thành công
                                df.columns = generate_unique_column_names([f"col_{k}" for k in range(len(df.columns))])
                                tables.append((i + 1, df))
                            except Exception as fallback_df_error:
                                print(f"Lỗi fallback khi tạo DataFrame ở trang {i+1}: {fallback_df_error}")
                                # Bỏ qua bảng này nếu không thể xử lý
    except Exception as e:
        raise ValueError(f"Lỗi khi mở hoặc xử lý PDF bằng pdfplumber: {e}")
    return tables

def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Chuyển DataFrame thành bytes cho Excel (xlsx) để tải về.
    """
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_bytes = output.getvalue()
    except Exception as e:
        raise ValueError(f"Lỗi khi chuyển DataFrame sang Excel: {e}")
    return excel_bytes