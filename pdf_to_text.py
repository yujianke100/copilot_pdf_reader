import os
import PyPDF2
from typing import Dict, List, Optional

def read_pdf(
    file_path: str,
    password: str = None,
    pages: Optional[List[int]] = None
) -> Dict:
    """
    读取 PDF 文件并提取文本内容，支持加密 PDF 和页面选择。
    
    Args:
        file_path: PDF 文件路径
        password: 可选，解密 PDF 的密码
        pages: 可选，指定提取的页面列表（1-indexed）。如果为 None，则提取所有页面。
        
    Returns:
        包含 PDF 内容和元数据的字典
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"文件未找到: {file_path}"
        }
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # 检查 PDF 是否加密
            is_encrypted = pdf_reader.is_encrypted
            if is_encrypted:
                if not password:
                    return {
                        "success": False,
                        "error": "PDF 文件已加密，请提供密码。",
                        "is_encrypted": True,
                        "password_required": True
                    }
                if not pdf_reader.decrypt(password):
                    return {
                        "success": False,
                        "error": "密码错误或无法解密 PDF。",
                        "is_encrypted": True,
                        "password_required": True
                    }
            
            # 提取元数据
            metadata = {}
            if pdf_reader.metadata:
                for key, value in pdf_reader.metadata.items():
                    metadata[key.strip('/')] = value
            
            # 确定需要提取的页面
            total_pages = len(pdf_reader.pages)
            pages_to_extract = pages or list(range(1, total_pages + 1))
            zero_indexed_pages = [p - 1 for p in pages_to_extract if 1 <= p <= total_pages]
            
            # 提取页面内容
            content = {}
            for page_number in zero_indexed_pages:
                page = pdf_reader.pages[page_number]
                content[page_number + 1] = page.extract_text()
            
            return {
                "success": True,
                "is_encrypted": is_encrypted,
                "total_pages": total_pages,
                "extracted_pages": list(content.keys()),
                "metadata": metadata,
                "content": content
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"处理 PDF 时出错: {str(e)}"
        }

def save_pdf_text_to_folder(pdf_folder: str, text_folder: str, password: str = None):
    """
    批量解析 PDF 文件并保存提取的文本到指定文件夹。
    
    Args:
        pdf_folder: PDF 文件所在文件夹路径
        text_folder: 保存解析文本的目标文件夹路径
        password: 可选，解密 PDF 的密码
    """
    if not os.path.exists(text_folder):
        os.makedirs(text_folder)

    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            result = read_pdf(pdf_path, password)
            
            if not result["success"]:
                print(f"解析失败: {filename} - {result['error']}")
                continue
            
            text_path = os.path.join(text_folder, f"{os.path.splitext(filename)[0]}.txt")
            with open(text_path, 'w', encoding='utf-8') as text_file:
                for page_num, page_text in result["content"].items():
                    text_file.write(f"### Page {page_num}\n\n{page_text}\n\n")
            
            print(f"解析完成: {filename} -> {text_path}")

if __name__ == "__main__":
    pdf_folder = "./pdf"
    text_folder = "./text"
    save_pdf_text_to_folder(pdf_folder, text_folder)
