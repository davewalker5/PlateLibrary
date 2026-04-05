FROM python:3.13-slim-bullseye

COPY platelibrary-1.15.0.0 /opt/platelibrary

WORKDIR /opt/platelibrary

RUN apt-get update -y
RUN pip install --no-cache-dir /opt/platelibrary/plate_library-1.15.0-py3-none-any.whl

ENV MICROSCOPY_PLATE_LIBRARY=/var/opt/platelibrary

ENTRYPOINT [ "streamlit" ]
CMD ["run", "/opt/platelibrary/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
