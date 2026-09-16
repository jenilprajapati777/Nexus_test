import json
import csv
import io
import zipfile
from bs4 import BeautifulSoup
from typing import Tuple, Dict, Any

class DocumentFileParser:
    """Parses TXT, JSON, CSV, XML, EPUB files into exact original text strings."""

    @staticmethod
    def parse_file(file_bytes: bytes, file_name: str, file_type: str) -> Tuple[str, Dict[str, Any]]:
        """Parses file content and returns (original_text, metadata)."""
        ext = file_name.split('.')[-1].lower() if '.' in file_name else file_type.lower()
        metadata = {"file_name": file_name, "file_type": ext}

        if ext in ['txt', 'text']:
            original_text = file_bytes.decode('utf-8', errors='replace')
        
        elif ext in ['json']:
            raw_str = file_bytes.decode('utf-8', errors='replace')
            data = json.loads(raw_str)
            if isinstance(data, dict):
                original_text = data.get("content") or data.get("text") or json.dumps(data, ensure_ascii=False, indent=2)
                metadata["title"] = data.get("title", file_name)
                metadata["author"] = data.get("author", "Unknown")
                metadata["chapter"] = data.get("chapter", "General")
            elif isinstance(data, list):
                original_text = "\n".join([str(item) for item in data])
            else:
                original_text = str(data)
                
        elif ext in ['csv']:
            raw_str = file_bytes.decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(raw_str))
            rows = []
            for row in reader:
                rows.append(" | ".join(row))
            original_text = "\n".join(rows)

        elif ext in ['xml', 'html']:
            raw_str = file_bytes.decode('utf-8', errors='replace')
            soup = BeautifulSoup(raw_str, 'lxml-xml' if 'xml' in ext else 'html.parser')
            # Retain text content clean
            original_text = soup.get_text(separator="\n", strip=False)

        elif ext in ['epub']:
            # EPUB is a ZIP archive containing HTML/XHTML files
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    text_parts = []
                    for filename in z.namelist():
                        if filename.endswith(('.xhtml', '.html', '.htm', '.txt')):
                            html_content = z.read(filename).decode('utf-8', errors='replace')
                            soup = BeautifulSoup(html_content, 'html.parser')
                            text_parts.append(soup.get_text(separator="\n"))
                    original_text = "\n\n".join(text_parts) if text_parts else file_bytes.decode('utf-8', errors='replace')
            except Exception:
                original_text = file_bytes.decode('utf-8', errors='replace')

        else:
            original_text = file_bytes.decode('utf-8', errors='replace')

        # Strict invariant assertion
        assert isinstance(original_text, str), "Parsed original text must be a valid string"
        return original_text, metadata
