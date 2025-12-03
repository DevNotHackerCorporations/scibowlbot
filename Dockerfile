FROM python:3.8
WORKDIR /opt/app/scibowlbot
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "main.py"]
