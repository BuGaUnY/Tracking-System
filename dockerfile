# ใช้ Python 3.12 เป็นพื้นฐาน
FROM python:3.12

# ตั้งค่า directory ทำงาน
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เข้าสู่ container
COPY requirements.txt .

# ติดตั้ง dependencies ของระบบ
RUN apt-get update && apt-get install -y build-essential python3-dev

# ติดตั้ง dependencies ของ Python
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์โปรเจกต์ทั้งหมดเข้าไปใน container
COPY . .

# คำสั่งที่จะรันแอปพลิเคชันของคุณ
CMD ["gunicorn", "projectmanager.wsgi:application", "--bind", "0.0.0.0:8000"]
