import sys, json, os
import base64
from io import BytesIO

def extract(ext, data):
    if ext == '.pdf':
        from pypdf import PdfReader
        from io import BytesIO
        return '\n\n'.join(p.extract_text() or '' for p in PdfReader(BytesIO(data)).pages)
    if ext == '.docx':
        from docx import Document
        from io import BytesIO
        doc=Document(BytesIO(data))
        return '\n'.join(p.text for p in doc.paragraphs)+'\n'+'\n'.join(' | '.join(c.text for c in r.cells) for t in doc.tables for r in t.rows)
    if ext == '.xlsx':
        from openpyxl import load_workbook
        from io import BytesIO
        wb=load_workbook(BytesIO(data),read_only=True,data_only=True)
        return '\n'.join(f'[{ws.title}]\n'+'\n'.join(' | '.join('' if v is None else str(v) for v in row) for row in ws.iter_rows(values_only=True)) for ws in wb.worksheets)
    raise ValueError('Unsupported file format')

def render_pdf_pages(data, limit=4):
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(data)
    page_count = len(pdf)
    pages = []
    for index in range(min(page_count, limit)):
        page = pdf[index]
        width, height = page.get_size()
        scale = min(1.25, 1400 / max(width, height, 1))
        bitmap = page.render(scale=scale)
        image = bitmap.to_pil().convert('RGB')
        image.thumbnail((1400, 1400))
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=78, optimize=True)
        pages.append({'page': index + 1, 'image': base64.b64encode(buffer.getvalue()).decode('ascii')})
    pdf.close()
    return {'page_count': page_count, 'pages': pages}

def write_docx(out, data):
    from docx import Document
    x=json.loads(data.decode('utf-8'))
    doc=Document()
    doc.add_heading(x.get('title') or 'Approval Note',0)
    doc.add_paragraph('CONFIDENTIAL · LOCAL WORKBENCH DRAFT')
    for block in x.get('body','').split('\n'):
        line=block.strip()
        if not line: continue
        if line.startswith('# '): doc.add_heading(line[2:],1)
        elif line.startswith('## '): doc.add_heading(line[3:],2)
        elif line.startswith('- ') or line.startswith('* '): doc.add_paragraph(line[2:],style='List Bullet')
        else: doc.add_paragraph(line)
    doc.save(out)

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='extract': sys.stdout.write(extract(sys.argv[2],sys.stdin.buffer.read()))
    elif mode=='render-pdf-pages': sys.stdout.write(json.dumps(render_pdf_pages(sys.stdin.buffer.read())))
    elif mode=='write-docx': write_docx(sys.argv[2],sys.stdin.buffer.read())
    else: raise ValueError('Unknown helper command')
