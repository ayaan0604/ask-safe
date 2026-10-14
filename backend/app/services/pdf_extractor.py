from io import BytesIO
from pypdf import PdfReader



def extract_pages(pdf_bytes: bytes)-> list[dict]:
    try:
        reader = PdfReader(BytesIO(pdf_bytes))

        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")

        pages = []

        for page_number, page in enumerate(reader.pages, start = 1):
            text = (page.extract_text() or "").strip()

            if text:
                pages.append(
                    {
                        'page_number' : page_number,
                        'text' : text
                    }
                )

        if not pages:
            raise ValueError("No extractable text found in the PDF.")

        return pages

    except ValueError:
        raise

    except Exception as e:
        raise ValueError('Could not read this PDF') from e