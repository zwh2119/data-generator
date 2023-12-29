FROM python:3.6
MAINTAINER Wenhui Zhou

RUN pip install --upgrade pip setuptools wheel

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopencv-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy opencv-python-headless

COPY ./requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY generator.py generator_server.py log.py client.py  video_generator.py yaml_utils.py utils.py ./

CMD ["python3", "generator_server.py"]