# Use official Python image
FROM python:3.11

# Set working directory inside the container
WORKDIR /tests

# Copy only test requirements first
COPY tests/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["pytest", "--html=reports/test_report.html", "--self-contained-html", "--url", "http://server:8000"]