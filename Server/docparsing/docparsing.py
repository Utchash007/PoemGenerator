from pypdf import PdfReader
from pathlib import Path
import docx

from pathlib import Path

def recieve_file(upload) -> str:
    """Return extracted text string from UploadFile/file-like. Empty string on unsupported/empty."""
    filename = getattr(upload, "filename", None) or getattr(upload, "name", None)
    if not filename:
        return ""
    ext = Path(filename).suffix.lower()
    file_obj = getattr(upload, "file", upload)
    try:
        file_obj.seek(0)
    except Exception:
        pass

    if ext == ".pdf":
        return pdf_parse(file_obj) or ""
    if ext == ".docx":
        return docx_parse(file_obj) or ""
    return ""



def docx_parse(file_obj_or_path) -> str:
    """Read .docx text and return single string."""
    try:
        document = docx.Document(file_obj_or_path)
        return "\n".join(p.text for p in document.paragraphs)
    except docx.opc.exceptions.PackageNotFoundError:
        return ""
    except Exception:
        return ""



def pdf_parse(file_obj) -> str:
    
    reader = PdfReader(file_obj)
    return "\n".join((p.extract_text() or "") for p in reader.pages)