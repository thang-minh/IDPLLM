# logic/graph_logic.py
import fitz  # PyMuPDF
import json
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from logic.common_processing import generate_groq_response
import asyncio

async def extract_entities(api_key, text):
    """
    Dùng AI để trích xuất thực thể: Tên Công Ty, Mã Dự Án, Ngày tháng.
    """
    prompt = f"""
    Bạn là một AI trích xuất thông tin. Hãy đọc văn bản sau và trích xuất các thông tin quan trọng dưới dạng JSON.
    Chỉ lấy: 
    1. "company": Tên công ty hoặc đối tác (viết tắt nếu dài).
    2. "project_code": Mã dự án hoặc số hợp đồng/số hóa đơn (nếu có).
    
    Văn bản: "{text[:3000]}" 
    
    Trả về JSON duy nhất (không giải thích):
    {{
        "company": "Tên công ty hoặc null",
        "project_code": "Mã dự án hoặc null"
    }}
    """
    try:
        response = await generate_groq_response(api_key, prompt, system_message="Trả về JSON raw.", temperature=0.1)
        # Làm sạch JSON (đôi khi AI thêm ```json)
        cleaned_json = response.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_json)
    except:
        return {"company": None, "project_code": None}

async def build_graph_data(uploaded_files, api_key):
    """
    Xử lý danh sách file và tạo Nodes/Edges cho Streamlit Agraph.
    """
    nodes = []
    edges = []
    
    # Dùng set để tránh tạo trùng node
    existing_nodes = set()

    for uploaded_file in uploaded_files:
        # 1. Đọc nội dung file (Trang 1)
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = doc[0].get_text() if len(doc) > 0 else ""
            file_name = uploaded_file.name
            
            # Reset con trỏ file sau khi đọc để các module khác dùng nếu cần
            uploaded_file.seek(0) 
        except Exception:
            continue

        # 2. Tạo Node cho File (Màu xanh dương)
        if file_name not in existing_nodes:
            nodes.append(Node(id=file_name, label=file_name, size=20, color="#4F8BF9", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/2965/2965335.png](https://cdn-icons-png.flaticon.com/512/2965/2965335.png)")) # Icon PDF
            existing_nodes.add(file_name)

        # 3. Trích xuất Entity bằng AI
        if api_key:
            entities = await extract_entities(api_key, text)
            
            # --- Xử lý Node: CÔNG TY (Màu Cam) ---
            company = entities.get("company")
            if company and company != "null":
                # Chuẩn hóa tên (viết hoa)
                company_id = f"ORG:{company.upper()}"
                if company_id not in existing_nodes:
                    nodes.append(Node(id=company_id, label=company, size=30, color="#FF9F1C", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/4300/4300059.png](https://cdn-icons-png.flaticon.com/512/4300/4300059.png)")) # Icon Building
                    existing_nodes.add(company_id)
                
                # Nối File -> Công ty
                edges.append(Edge(source=file_name, target=company_id, label="liên quan", color="#BDC3C7"))

            # --- Xử lý Node: MÃ DỰ ÁN (Màu Tím) ---
            prj_code = entities.get("project_code")
            if prj_code and prj_code != "null":
                prj_id = f"PRJ:{prj_code.upper()}"
                if prj_id not in existing_nodes:
                    nodes.append(Node(id=prj_id, label=prj_code, size=25, color="#8E44AD", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/1087/1087815.png](https://cdn-icons-png.flaticon.com/512/1087/1087815.png)")) # Icon Tag
                    existing_nodes.add(prj_id)
                
                # Nối File -> Mã dự án
                edges.append(Edge(source=file_name, target=prj_id, label="thuộc mã", color="#BDC3C7"))
    
    return nodes, edges