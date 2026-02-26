import os
from fastapi import UploadFile
import PyPDF2
from pdf2image import convert_from_bytes
import docx

class FileHandler:
    @staticmethod
    async def extract_text(file: UploadFile, max_chars: int = 32000) -> str:
        """
        从 txt, md, pdf, docx 中提取文本。
        如果超过 max_chars，保留最后 max_chars 字符（根据需求）。
        """
        content = ""
        filename = file.filename.lower()
        file_bytes = await file.read()

        try:
            if filename.endswith(('.txt', '.md')):
                content = file_bytes.decode('utf-8')
            
            elif filename.endswith('.pdf'):
                # 处理 PDF 文本提取
                # 注意：需要将 bytes 写入临时文件或使用 BytesIO，这里为简化直接用临时文件逻辑
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"

            elif filename.endswith('.docx'):
                import io
                doc = docx.Document(io.BytesIO(file_bytes))
                for para in doc.paragraphs:
                    content += para.text + "\n"
            
            else:
                return "Unsupported file format."

        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
        
        # 此时游标在末尾，重置以便后续可能的其他操作
        await file.seek(0)

        # 截断处理：保留最近的 32k 内容
        if len(content) > max_chars:
            return content[-max_chars:]
        return content

    @staticmethod
    async def convert_pdf_to_images(file: UploadFile):
        """
        将上传的 PDF (PPT) 转换为图片列表 (Base64 或 临时路径)。
        这里我们直接返回 PIL Image 对象列表，后续由 Logic 层处理存储或 Base64 转换。
        """
        file_bytes = await file.read()
        await file.seek(0) # 重置游标
        
        try:
            # convert_from_bytes 需要系统安装 poppler
            images = convert_from_bytes(file_bytes, fmt='jpeg')
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            raise e