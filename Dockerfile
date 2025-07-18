FROM ghcr.io/astral-sh/uv:python3.11-alpine

ADD . /leah
WORKDIR /leah
RUN uv sync --frozen
CMD ["uv", "run", "src/main.py"]
