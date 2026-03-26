FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 下载NLTK数据
RUN python -m nltk.downloader punkt wordnet stopwords

# 下载Spacy模型
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8010

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
