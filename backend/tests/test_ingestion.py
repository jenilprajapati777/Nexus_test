import pytest
import json
from app.ingestion.parsers import DocumentFileParser

def test_file_parsing_text_preservation():
    # TXT
    raw_txt = "धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः ।\nमामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय ॥"
    txt_bytes = raw_txt.encode('utf-8')
    parsed_txt, meta = DocumentFileParser.parse_file(txt_bytes, "gita.txt", "txt")
    assert parsed_txt == raw_txt

    # JSON
    raw_json_dict = {"title": "Hitopadesha", "content": "अस्ति मगधदेशे चम्पकभिधाना अरण्यानी ।"}
    json_bytes = json_str = json.dumps(raw_json_dict).encode('utf-8')
    parsed_json, _ = DocumentFileParser.parse_file(json_bytes, "doc.json", "json")
    assert parsed_json == "अस्ति मगधदेशे चम्पकभिधाना अरण्यानी ।"

    # CSV
    raw_csv = "Chapter,Verse,Text\n1,1,धर्मक्षेत्रे कुरुक्षेत्रे"
    csv_bytes = raw_csv.encode('utf-8')
    parsed_csv, _ = DocumentFileParser.parse_file(csv_bytes, "verses.csv", "csv")
    assert "Chapter | Verse | Text" in parsed_csv
