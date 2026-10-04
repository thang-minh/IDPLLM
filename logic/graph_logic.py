# # logic/graph_logic.py
# import fitz  # PyMuPDF
# import json
# import networkx as nx
# from streamlit_agraph import agraph, Node, Edge, Config
# from logic.common_processing import generate_groq_response
# import asyncio

# async def extract_entities(api_key, text):
#     """
#     Dùng AI để trích xuất thực thể: Tên Công Ty, Mã Dự Án, Ngày tháng.
#     """
#     prompt = f"""
#     Bạn là một AI trích xuất thông tin. Hãy đọc văn bản sau và trích xuất các thông tin quan trọng dưới dạng JSON.
#     Chỉ lấy: 
#     1. "company": Tên công ty hoặc đối tác (viết tắt nếu dài).
#     2. "project_code": Mã dự án hoặc số hợp đồng/số hóa đơn (nếu có).
    
#     Văn bản: "{text[:3000]}" 
    
#     Trả về JSON duy nhất (không giải thích):
#     {{
#         "company": "Tên công ty hoặc null",
#         "project_code": "Mã dự án hoặc null"
#     }}
#     """
#     try:
#         response = await generate_groq_response(api_key, prompt, system_message="Trả về JSON raw.", temperature=0.1)
#         # Làm sạch JSON (đôi khi AI thêm ```json)
#         cleaned_json = response.replace("```json", "").replace("```", "").strip()
#         return json.loads(cleaned_json)
#     except:
#         return {"company": None, "project_code": None}

# async def build_graph_data(uploaded_files, api_key):
#     """
#     Xử lý danh sách file và tạo Nodes/Edges cho Streamlit Agraph.
#     """
#     nodes = []
#     edges = []
    
#     # Dùng set để tránh tạo trùng node
#     existing_nodes = set()

#     for uploaded_file in uploaded_files:
#         # 1. Đọc nội dung file (Trang 1)
#         try:
#             doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
#             text = doc[0].get_text() if len(doc) > 0 else ""
#             file_name = uploaded_file.name
            
#             # Reset con trỏ file sau khi đọc để các module khác dùng nếu cần
#             uploaded_file.seek(0) 
#         except Exception:
#             continue

#         # 2. Tạo Node cho File (Màu xanh dương)
#         if file_name not in existing_nodes:
#             nodes.append(Node(id=file_name, label=file_name, size=20, color="#4F8BF9", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/2965/2965335.png](https://cdn-icons-png.flaticon.com/512/2965/2965335.png)")) # Icon PDF
#             existing_nodes.add(file_name)

#         # 3. Trích xuất Entity bằng AI
#         if api_key:
#             entities = await extract_entities(api_key, text)
            
#             # --- Xử lý Node: CÔNG TY (Màu Cam) ---
#             company = entities.get("company")
#             if company and company != "null":
#                 # Chuẩn hóa tên (viết hoa)
#                 company_id = f"ORG:{company.upper()}"
#                 if company_id not in existing_nodes:
#                     nodes.append(Node(id=company_id, label=company, size=30, color="#FF9F1C", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/4300/4300059.png](https://cdn-icons-png.flaticon.com/512/4300/4300059.png)")) # Icon Building
#                     existing_nodes.add(company_id)
                
#                 # Nối File -> Công ty
#                 edges.append(Edge(source=file_name, target=company_id, label="liên quan", color="#BDC3C7"))

#             # --- Xử lý Node: MÃ DỰ ÁN (Màu Tím) ---
#             prj_code = entities.get("project_code")
#             if prj_code and prj_code != "null":
#                 prj_id = f"PRJ:{prj_code.upper()}"
#                 if prj_id not in existing_nodes:
#                     nodes.append(Node(id=prj_id, label=prj_code, size=25, color="#8E44AD", shape="circularImage", image="[https://cdn-icons-png.flaticon.com/512/1087/1087815.png](https://cdn-icons-png.flaticon.com/512/1087/1087815.png)")) # Icon Tag
#                     existing_nodes.add(prj_id)
                
#                 # Nối File -> Mã dự án
#                 edges.append(Edge(source=file_name, target=prj_id, label="thuộc mã", color="#BDC3C7"))
    
#     return nodes, edges

# logic/graph_logic.py

import io
import re
import json
from collections import defaultdict
from typing import List, Dict, Any, Tuple

from streamlit_agraph import Node, Edge

from logic.common_processing import (
    convert_pdf_to_txt,
    convert_pdf_to_images,
    extract_text_from_list_of_images,
    generate_groq_response,
)


# =========================================================
# CONFIG
# =========================================================

ENTITY_COLORS = {
    "document": "#4F46E5",
    "company": "#16A34A",
    "tax_code": "#F59E0B",
    "project": "#9333EA",
    "contract": "#DC2626",
    "invoice": "#0891B2",
    "person": "#DB2777",
    "date": "#64748B",
}

ENTITY_ICONS = {
    "document": "📄",
    "company": "🏢",
    "tax_code": "🧾",
    "project": "📌",
    "contract": "📑",
    "invoice": "💵",
    "person": "👤",
    "date": "📅",
}


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_text_from_uploaded_pdfs(uploaded_files, poppler_path_env=None) -> List[Dict[str, Any]]:
    """
    Đọc nhiều PDF.
    Nếu PDF có text layer thì lấy text trực tiếp.
    Nếu text quá ít thì fallback OCR.
    """
    documents = []

    for uploaded_file in uploaded_files:
        try:
            file_bytes = uploaded_file.getvalue()

            text = convert_pdf_to_txt(io.BytesIO(file_bytes))
            extraction_method = "pdf_text"

            if len(text.strip()) < 100:
                try:
                    images = convert_pdf_to_images(
                        io.BytesIO(file_bytes),
                        dpi=180,
                        first_page=1,
                        last_page=None,
                        poppler_path=poppler_path_env,
                    )
                    ocr_text = extract_text_from_list_of_images(
                        images,
                        lang="vie+eng",
                        preprocess=True,
                    )
                    text = text + "\n" + ocr_text
                    extraction_method = "ocr"
                except Exception as e:
                    extraction_method = f"pdf_text_only_ocr_failed: {e}"

            documents.append({
                "file_name": uploaded_file.name,
                "text": text.strip(),
                "text_length": len(text.strip()),
                "extraction_method": extraction_method,
            })

        except Exception as e:
            documents.append({
                "file_name": uploaded_file.name,
                "text": "",
                "text_length": 0,
                "extraction_method": f"error: {e}",
            })

    return documents


# =========================================================
# REGEX ENTITY EXTRACTION
# =========================================================

def clean_entity(value: str) -> str:
    value = str(value or "").strip()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" .,:;|-_/\\")
    return value


def dedupe_list(items: List[str]) -> List[str]:
    seen = set()
    output = []

    for item in items:
        clean = clean_entity(item)

        if not clean:
            continue

        key = clean.lower()

        if key not in seen:
            seen.add(key)
            output.append(clean)

    return output


def extract_entities_by_regex(text: str) -> Dict[str, List[str]]:
    """
    Trích xuất thực thể bằng rule/regex.
    Đây là fallback local, không cần API.
    """
    entities = {
        "company": [],
        "tax_code": [],
        "project": [],
        "contract": [],
        "invoice": [],
        "person": [],
        "date": [],
    }

    if not text:
        return entities

    # Mã số thuế
    entities["tax_code"] += re.findall(
        r"(?:MST|Mã số thuế|Ma so thue)\s*[:\-]?\s*(\d{10}(?:-\d{3})?)",
        text,
        flags=re.IGNORECASE,
    )

    # Số hóa đơn
    entities["invoice"] += re.findall(
        r"(?:Số hóa đơn|So hoa don|Invoice No|Invoice Number|Số)\s*[:\-]?\s*([A-Z0-9\-\/]{3,30})",
        text,
        flags=re.IGNORECASE,
    )

    # Số hợp đồng
    entities["contract"] += re.findall(
        r"(?:Số hợp đồng|So hop dong|Contract No|Hợp đồng số)\s*[:\-]?\s*([A-Z0-9\-\/]{3,40})",
        text,
        flags=re.IGNORECASE,
    )

    # Mã dự án
    entities["project"] += re.findall(
        r"(?:Mã dự án|Ma du an|Project ID|Project Code|Dự án)\s*[:\-]?\s*([A-Z0-9\-\/ ]{3,60})",
        text,
        flags=re.IGNORECASE,
    )

    # Công ty / đơn vị
    company_patterns = [
        r"(?:Công ty|Cong ty|Tên đơn vị|Ten don vi|Bên bán|Ben ban|Bên mua|Ben mua)\s*[:\-]?\s*([A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-&]{5,100})",
        r"((?:CÔNG TY|Công ty|Cong ty)\s+[A-ZÀ-Ỹa-zà-ỹ0-9\s\.\-&]{5,100})",
    ]

    for pattern in company_patterns:
        entities["company"] += re.findall(pattern, text, flags=re.IGNORECASE)

    # Người đại diện / nhân sự
    person_patterns = [
        r"(?:Đại diện|Dai dien|Người lao động|Nguoi lao dong|Họ tên|Ho ten|Chủ trì|Chu tri|Thư ký|Thu ky)\s*[:\-]?\s*([A-ZÀ-Ỹ][A-ZÀ-Ỹa-zà-ỹ\s]{3,60})",
    ]

    for pattern in person_patterns:
        entities["person"] += re.findall(pattern, text, flags=re.IGNORECASE)

    # Ngày tháng
    entities["date"] += re.findall(
        r"\b(?:0?[1-9]|[12]\d|3[01])[/\-](?:0?[1-9]|1[0-2])[/\-](?:19|20)\d{2}\b",
        text,
    )

    for key in entities:
        entities[key] = dedupe_list(entities[key])[:10]

    return entities


# =========================================================
# LLM ENTITY EXTRACTION
# =========================================================

def safe_json_loads(raw: str) -> Dict[str, Any]:
    """
    Cố gắng parse JSON từ phản hồi LLM.
    """
    if not raw:
        return {}

    raw = raw.strip()

    try:
        return json.loads(raw)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw)

    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return {}

    return {}


async def extract_entities_by_llm(text: str, file_name: str, api_key: str) -> Dict[str, List[str]]:
    """
    Trích xuất entity bằng LLM.
    Output chuẩn:
    {
      "company": [],
      "tax_code": [],
      "project": [],
      "contract": [],
      "invoice": [],
      "person": [],
      "date": []
    }
    """
    if not api_key or not text.strip():
        return {}

    text_for_llm = text[:9000]

    prompt = f"""
Bạn là hệ thống trích xuất thực thể từ tài liệu hành chính/doanh nghiệp tiếng Việt.

Tên file: {file_name}

Hãy đọc nội dung dưới đây và trả về JSON hợp lệ, không markdown, không giải thích.

Schema bắt buộc:
{{
  "company": ["tên công ty/đơn vị/bên bán/bên mua"],
  "tax_code": ["mã số thuế"],
  "project": ["mã dự án/tên dự án"],
  "contract": ["số hợp đồng/mã hợp đồng"],
  "invoice": ["số hóa đơn/mã hóa đơn"],
  "person": ["người đại diện/người lao động/chủ trì/thư ký"],
  "date": ["ngày tháng quan trọng"]
}}

Quy tắc:
- Nếu không có thông tin thì trả về mảng rỗng.
- Không tự bịa.
- Chỉ lấy thông tin xuất hiện trong văn bản.

NỘI DUNG:
{text_for_llm}
"""

    system_message = "Bạn là bộ trích xuất thông tin. Chỉ trả JSON hợp lệ."

    try:
        raw = await generate_groq_response(
            api_key=api_key,
            prompt=prompt,
            system_message=system_message,
            max_tokens=1200,
        )

        data = safe_json_loads(raw)

        normalized = {
            "company": [],
            "tax_code": [],
            "project": [],
            "contract": [],
            "invoice": [],
            "person": [],
            "date": [],
        }

        for key in normalized.keys():
            value = data.get(key, [])

            if isinstance(value, str):
                value = [value]

            if isinstance(value, list):
                normalized[key] = dedupe_list([str(v) for v in value])[:10]

        return normalized

    except TypeError:
        # Nếu generate_groq_response bản cũ không hỗ trợ system_message/max_tokens
        raw = await generate_groq_response(api_key, prompt)
        data = safe_json_loads(raw)

        normalized = {
            key: dedupe_list(data.get(key, [])) if isinstance(data.get(key, []), list) else []
            for key in ["company", "tax_code", "project", "contract", "invoice", "person", "date"]
        }
        return normalized

    except Exception:
        return {}


def merge_entities(regex_entities: Dict[str, List[str]], llm_entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
    merged = {}

    keys = ["company", "tax_code", "project", "contract", "invoice", "person", "date"]

    for key in keys:
        merged[key] = dedupe_list(
            regex_entities.get(key, []) + llm_entities.get(key, [])
        )

    return merged


# =========================================================
# GRAPH BUILDING
# =========================================================

def make_node_id(entity_type: str, value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9À-ỹ]+", "_", value.lower()).strip("_")
    return f"{entity_type}_{safe[:80]}"


def create_entity_node(entity_type: str, value: str) -> Node:
    icon = ENTITY_ICONS.get(entity_type, "")
    color = ENTITY_COLORS.get(entity_type, "#94A3B8")

    return Node(
        id=make_node_id(entity_type, value),
        label=f"{icon} {value}",
        size=24,
        color=color,
        title=f"{entity_type}: {value}",
    )


def create_document_node(file_name: str, text_length: int, extraction_method: str) -> Node:
    return Node(
        id=f"doc_{file_name}",
        label=f"📄 {file_name}",
        size=36,
        color=ENTITY_COLORS["document"],
        title=f"Tài liệu: {file_name}\nText length: {text_length}\nMethod: {extraction_method}",
    )


def build_edges_and_nodes(documents_with_entities: List[Dict[str, Any]]) -> Tuple[List[Node], List[Edge], Dict[str, Any]]:
    """
    Tạo nodes/edges:
    - Document -> Entity
    - Document -> Document nếu cùng entity
    """
    nodes_by_id = {}
    edges = []
    edge_keys = set()

    entity_to_docs = defaultdict(list)

    for doc in documents_with_entities:
        file_name = doc["file_name"]
        doc_id = f"doc_{file_name}"

        doc_node = create_document_node(
            file_name=file_name,
            text_length=doc.get("text_length", 0),
            extraction_method=doc.get("extraction_method", "unknown"),
        )
        nodes_by_id[doc_id] = doc_node

        entities = doc.get("entities", {})

        for entity_type, values in entities.items():
            for value in values:
                entity_node = create_entity_node(entity_type, value)
                entity_id = entity_node.id

                nodes_by_id[entity_id] = entity_node
                entity_to_docs[(entity_type, value)].append(file_name)

                edge_key = (doc_id, entity_id, entity_type)

                if edge_key not in edge_keys:
                    edges.append(
                        Edge(
                            source=doc_id,
                            target=entity_id,
                            label=entity_type,
                            color="#CBD5E1",
                        )
                    )
                    edge_keys.add(edge_key)

    # Tạo liên kết tài liệu-tài liệu nếu cùng thực thể
    document_links = []

    for (entity_type, value), doc_names in entity_to_docs.items():
        unique_docs = list(dict.fromkeys(doc_names))

        if len(unique_docs) >= 2:
            for i in range(len(unique_docs)):
                for j in range(i + 1, len(unique_docs)):
                    source = f"doc_{unique_docs[i]}"
                    target = f"doc_{unique_docs[j]}"
                    edge_key = (source, target, f"shared_{entity_type}_{value}")

                    if edge_key not in edge_keys:
                        edges.append(
                            Edge(
                                source=source,
                                target=target,
                                label=f"cùng {entity_type}",
                                color="#EF4444",
                            )
                        )
                        edge_keys.add(edge_key)

                    document_links.append({
                        "source": unique_docs[i],
                        "target": unique_docs[j],
                        "shared_type": entity_type,
                        "shared_value": value,
                    })

    report = {
        "documents": documents_with_entities,
        "entity_to_docs": [
            {
                "type": entity_type,
                "value": value,
                "documents": docs,
                "count": len(set(docs)),
            }
            for (entity_type, value), docs in entity_to_docs.items()
        ],
        "document_links": document_links,
        "node_count": len(nodes_by_id),
        "edge_count": len(edges),
    }

    return list(nodes_by_id.values()), edges, report


# =========================================================
# MAIN ASYNC FUNCTION
# =========================================================

async def build_graph_data(
    uploaded_files,
    api_key: str = None,
    poppler_path_env: str = None,
    use_llm: bool = True,
):
    """
    Hàm chính để UI gọi.
    Return:
    nodes, edges, report
    """
    documents = extract_text_from_uploaded_pdfs(
        uploaded_files,
        poppler_path_env=poppler_path_env,
    )

    documents_with_entities = []

    for doc in documents:
        text = doc.get("text", "")

        regex_entities = extract_entities_by_regex(text)

        llm_entities = {}

        if use_llm and api_key:
            llm_entities = await extract_entities_by_llm(
                text=text,
                file_name=doc["file_name"],
                api_key=api_key,
            )

        entities = merge_entities(regex_entities, llm_entities)

        documents_with_entities.append({
            **doc,
            "entities": entities,
        })

    nodes, edges, report = build_edges_and_nodes(documents_with_entities)

    return nodes, edges, report