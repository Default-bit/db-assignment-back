FROM python:3.11.4

ENV PYTHONUNBUFFERED 1

# Copy the application code from your project root to the Docker image
COPY . .

RUN pip install -r requirements.txt
RUN pip install pydantic[email]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]