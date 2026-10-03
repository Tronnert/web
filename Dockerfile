FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir flask gunicorn pillow "pymongo==3.12.3"

COPY app.py .

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
