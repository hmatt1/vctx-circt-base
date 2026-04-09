FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHON_VERSION=3.14.0
ARG CIRCT_REPO=https://github.com/llvm/circt.git
ARG CIRCT_REF=main

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
    python3 \
    python3-pip \
    tk-dev \
    uuid-dev \
    xz-utils \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN curl -fsSLO "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
  && tar -xzf "Python-${PYTHON_VERSION}.tgz" \
  && cd "Python-${PYTHON_VERSION}" \
  && ./configure --prefix=/opt/python-3.14t --with-ensurepip=install --disable-gil \
  && make -j"$(nproc)" \
  && make install \
  && ln -sf /opt/python-3.14t/bin/python3.14 /opt/python-3.14t/bin/python3.14t

ENV PATH="/opt/python-3.14t/bin:${PATH}"

WORKDIR /opt/circt
RUN git clone --depth 1 --branch "${CIRCT_REF}" "${CIRCT_REPO}" . \
  && git submodule update --init --recursive

RUN python3.14t -m pip install --upgrade pip setuptools wheel \
  && python3.14t -m pip install lib/Bindings/Python

RUN python3.14t -c "import circt; print('CIRCT ready')"

WORKDIR /workspace
