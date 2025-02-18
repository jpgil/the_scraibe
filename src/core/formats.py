import pdfplumber
import markdownify
import pandas as pd
import unicodedata
  
def normalize_text(text):
    """Normalize text to remove non-standard encoding issues."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)  # Normalize Unicode characters
    text = text.encode("utf-8", "ignore").decode("utf-8")  # Ensure UTF-8 encoding
    text = ''.join(c for c in text if unicodedata.category(c)[0] != 'C')  # Remove control characters
    text = text.replace("\u2028", "\n")
    return text.strip()

def to_html(content):  
    from markdown_it import MarkdownIt
    md = MarkdownIt("gfm-like").enable('table')
    rendered = md.render(content)
    return rendered

def extract_markdown_from_pdf(file):
    """Extract text, tables, and NFC-encoded data from a PDF and format it as Markdown."""
    markdown_content = []
    
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            # Extract and normalize text while preserving layout
            text = page.extract_text(layout=True)  # Retains better formatting
            if text:
                text = normalize_text(text)
                text = text.replace("\n", "\n\n")  # Ensure double newlines between paragraphs
                markdown_content.append(text)

            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table).fillna("")  # Convert to DataFrame
                table_md = df.to_markdown(index=False)  # Convert to Markdown table
                markdown_content.append(table_md)

    return "\n\n".join(markdown_content)

def pdf_to_md(file):
    """Convert extracted PDF text to Markdown."""
    text = extract_text_from_pdf(file)
    md_text = markdownify.markdownify(text, heading_style="ATX")  # Convert plain text to Markdown
    return md_text
