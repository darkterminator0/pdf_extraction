import os
import re
import pdfplumber
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .forms import PdfExtractForm

def pdf_single_page_extract(request):
    if request.method == 'POST':
        form = PdfExtractForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']

            # Ensure the temporary directory exists
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Save the uploaded file temporarily
            file_path = os.path.join(temp_dir, f.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

            extracted_text = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    print(f"Extracted text from page {page_num}:\n{page_text}\n")
                    structured_data = parse_text(page_text)
                    extracted_text.append((page_num, structured_data))

            # Generate the file URL
            relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            file_url = os.path.join(settings.MEDIA_URL, relative_file_path)

            return render(request, 'pdf/pdf_extract.html', {
                'form': form,
                'extracted_text': extracted_text,
                'pdf_url': file_url
            })
    else:
        form = PdfExtractForm()

    return render(request, 'pdf/pdf_extract.html', {'form': form})

def parse_text(text):
    structured_data = {
        "invoice_number": None,
        "order_number": None,
        "invoice_date": None,
        "due_date": None,
        "total_due": None
    }

    patterns = {
        "invoice_number": r'Invoice Number\s*([\w-]+)',
        "order_number": r'Order Number\s*([\w-]+)',
        "invoice_date": r'Invoice Date\s*([\w\s,]+)',
        "due_date": r'Due Date\s*([\w\s,]+)',
        "total_due": r'Total Due\s*\$?([\d\.,]+)'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            structured_data[key] = match.group(1).strip()

    print(f"Parsed structured data:\n{structured_data}\n")

    return structured_data
