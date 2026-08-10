FROM ubuntu:24.04 AS base

ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    libstdc++-13-dev \
    ca-certificates \
    ccache \
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
    lld \
    ninja-build \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    tk-dev \
    uuid-dev \
    xz-utils \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

FROM base AS builder

ARG PYTHON_VERSION=3.14.0
ARG CIRCT_REPO=https://github.com/llvm/circt.git
ARG CIRCT_REF=main
WORKDIR /opt
RUN curl -fsSLO "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz" \
  && tar -xzf "Python-${PYTHON_VERSION}.tgz" \
  && cd "Python-${PYTHON_VERSION}" \
  && ./configure --prefix=/opt/python-3.14t --with-ensurepip=install --disable-gil \
  && make -j"$(nproc)" \
  && make install \
  && ln -sf /opt/python-3.14t/bin/python3.14 /opt/python-3.14t/bin/python3.14t

ENV PATH="/opt/python-3.14t/bin:${PATH}"
ENV PYTHON_GIL=0

WORKDIR /opt/circt
RUN git clone --branch "${CIRCT_REF}" "${CIRCT_REPO}" . \
  && git submodule update --init --recursive \
  && git fetch --tags

RUN python3.14t -m pip install --upgrade pip setuptools wheel \
  && python3.14t -m pip install nanobind pyyaml numpy pybind11

ENV CCACHE_DIR=/ccache
RUN --mount=type=cache,id=ccache,target=/ccache \
    cmake -S llvm/llvm -B build-python -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DCMAKE_C_COMPILER_LAUNCHER=ccache \
    -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
    -DLLVM_ENABLE_LLD=ON \
    -DCMAKE_INSTALL_PREFIX=/opt/circt/install-python \
    -DLLVM_ENABLE_PROJECTS=mlir \
    -DLLVM_EXTERNAL_PROJECTS=circt \
    -DLLVM_EXTERNAL_CIRCT_SOURCE_DIR=/opt/circt \
    -DLLVM_TARGETS_TO_BUILD=host \
    -DMLIR_ENABLE_BINDINGS_PYTHON=ON \
    -DCIRCT_BINDINGS_PYTHON_ENABLED=ON \
    -DPython_ROOT_DIR=/opt/python-3.14t \
    -DPython_EXECUTABLE=/opt/python-3.14t/bin/python3.14t \
    -DPython3_ROOT_DIR=/opt/python-3.14t \
    -DPython3_EXECUTABLE=/opt/python-3.14t/bin/python3.14t \
    -DLLVM_FORCE_VC_REPOSITORY=https://github.com/llvm/llvm-project \
  && cmake --build build-python --target install-CIRCTPythonModules -- -j"$(nproc)"

RUN --mount=type=cache,id=ccache,target=/ccache \
    cmake --build build-python --target install-MLIRPythonModules -- -j"$(nproc)"

RUN --mount=type=cache,id=ccache,target=/ccache \
    cmake --build build-python --target arcilator -- -j"$(nproc)"

ARG OSS_CAD_SUITE_URL=https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-08-09/oss-cad-suite-linux-x64-20260809.tgz
WORKDIR /opt
RUN curl -fsSL "${OSS_CAD_SUITE_URL}" -o oss-cad-suite.tgz \
  && tar -xzf oss-cad-suite.tgz \
  && rm oss-cad-suite.tgz

FROM base AS final

# Copy only the compiled python and circt binaries from the builder stage
COPY --from=builder /opt/python-3.14t /opt/python-3.14t
COPY --from=builder /opt/circt/install-python /opt/circt/install-python
COPY --from=builder /opt/circt/build-python/bin/arcilator /usr/local/bin/arcilator
COPY --from=builder /opt/oss-cad-suite /opt/oss-cad-suite

ENV PATH="/opt/python-3.14t/bin:/opt/oss-cad-suite/bin:${PATH}"
ENV PYTHON_GIL=0

# Configure site-packages so python can find circt and mlir
RUN PY_SITE=$(python3.14t -c 'import site; print(site.getsitepackages()[0])') \
  && mkdir -p "$PY_SITE" \
  && printf '%s\n' '/opt/circt/install-python/python_packages/circt_core' > "$PY_SITE/circt_local.pth" \
  && printf '%s\n' '/opt/circt/install-python/python_packages/mlir_core' >> "$PY_SITE/circt_local.pth"

RUN python3.14t -c "import sys, circt; print('CIRCT ready; gil enabled:', sys._is_gil_enabled())"

WORKDIR /workspace
