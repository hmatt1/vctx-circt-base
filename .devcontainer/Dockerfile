FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.14.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    clang \
    cmake \
    curl \
    git \
    libbz2-dev \
    libffi-dev \
    libgdbm-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    ninja-build \
    pkg-config \
    tk-dev \
    uuid-dev \
    xz-utils \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

RUN curl -fsSLO "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
  && tar -xzf "Python-${PYTHON_VERSION}.tgz" \
  && cd "Python-${PYTHON_VERSION}" \
  && ./configure --prefix=/usr/local/python-3.14t --with-ensurepip=install --disable-gil \
  && make -j"$(nproc)" \
  && make install \
  && ln -sf /usr/local/python-3.14t/bin/python3.14 /usr/local/python-3.14t/bin/python3.14t

ENV PATH="/usr/local/python-3.14t/bin:${PATH}"

USER vscode
WORKDIR /workspace
