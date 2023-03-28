FROM python:3.11

RUN apt-get update \
    && apt-get install -y --no-install-recommends glabels lpr \
    && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

 