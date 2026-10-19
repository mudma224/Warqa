FROM warqa/docile:latest

RUN uv pip install --python /opt/docile-venv/bin/python streamlit
