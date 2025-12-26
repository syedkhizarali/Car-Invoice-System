# Deployment Guide
# 🚀 Car Repair Invoice - Deployment Guide

## Prerequisites
- Python 3.8 or higher
- Git installed
- Streamlit Cloud account (free)

## Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/syedkhizarali/car-invoice.git
   cd car-invoice
   
## Local Installation
1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `streamlit run app.py`
4. Open browser: http://localhost:8501

## Cloud Deployment Options

### Option 1: Streamlit Cloud (Free)
1. Push code to GitHub
2. Visit share.streamlit.io
3. Connect GitHub repository
4. Deploy with one click

### Option 2: Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]