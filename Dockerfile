# Python Version သတ်မှတ်ခြင်း
FROM python:3.10-slim

# App Folder တည်ဆောက်ခြင်း
WORKDIR /app

# Library များသွင်းခြင်း
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ဖိုင်အားလုံးကို Container ထဲကူးထည့်ခြင်း
COPY . .

# Bot ကို စတင် Run ခြင်း
CMD ["python", "main.py"]
