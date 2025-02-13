# Use official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /tests

# Copy only test requirements first
COPY tests/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Copy the script and set execution permissions
COPY tests/run_all_tests.sh /tests/run_all_tests.sh
RUN chmod +x /tests/run_all_tests.sh

# Run the script for parallel execution of api tests and sequential execution of websocket tests
CMD ["/bin/sh", "-c", "/tests/run_all_tests.sh"]