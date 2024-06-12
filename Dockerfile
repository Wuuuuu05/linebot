# 使用 Python 官方的輕量級版本作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 將當前目錄下的所有文件複製到工作目錄中
COPY . /app

# 安裝所需的 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 暴露應用程式運行的端口
EXPOSE 5000

# 設置應用程式的啟動命令
CMD ["gunicorn", "-b", "0.0.0.0:5000", "main:app"]
