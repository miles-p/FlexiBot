# Base Image is Python 3
FROM python:3

# Copy this shit to that shit
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the thing
CMD ["python", "main.py"]