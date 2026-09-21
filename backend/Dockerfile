FROM python:3.11-slim

WORKDIR /app

# libreoffice-writer: xem truoc file Word (module Tai lieu)
# lib{pango,cairo,gdk-pixbuf,ffi}: WeasyPrint dung de dung trang + ve PDF
# fonts-noto-cjk: chu Trung phon the tren letterhead, khong co thi ra o vuong
# libharfbuzz-subset0: WeasyPrint dung de nhung font vao PDF (thieu thi lui ve
#   fontTools, cham hon va se bi bo o ban WeasyPrint sau)
# poppler-utils: pdftoppm/pdftotext, dung khi doi chieu ban in voi mau giay
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-writer \
        libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi8 \
        libharfbuzz-subset0 \
        shared-mime-info fonts-noto-cjk poppler-utils && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
