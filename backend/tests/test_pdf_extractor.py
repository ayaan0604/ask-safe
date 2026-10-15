from io import BytesIO

from pypdf import PdfWriter

from app.services.pdf_extractor import extract_pages



def create_test_pdf()->bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=300, height= 300)

    buffer = BytesIO()
    writer.write(buffer)

    return buffer.getvalue()

def test_blank_pdf_has_no_extractable_text():
    pdf_bytes = create_test_pdf()

    try:
        extract_pages(pdf_bytes)
        assert False, "expected extraction to fail"
    except ValueError as e:
        assert "No extractable text" in str(e)

if __name__ == "__main__":
    test_blank_pdf_has_no_extractable_text()