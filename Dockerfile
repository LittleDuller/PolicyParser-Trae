FROM python:3.11-slim

WORKDIR /app

# 为了加速构建，避免在 docker 里配置环境带来不便，这里简单使用 pip 安装 pyproject 解析的依赖
RUN pip install -U pip && \
    pip install "fastapi[standard]>=0.136.0" "pydantic>=2.13.2" "jinja2>=3.1.6" "langchain-core>=1.3.0" "langchain-qwq>=0.3.4" "langgraph>=1.1.8" "markdownify>=1.2.2"

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
