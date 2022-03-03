# See here for image contents: https://github.com/microsoft/vscode-dev-containers/blob/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT=3-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Optional] Allow the vscode user to pip install globally w/o sudo
ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN if ! cat /etc/group | grep -e "^pip-global:" > /dev/null 2>&1; then groupadd -r pip-global; fi \
    && usermod -a -G pip-global vscode \
    && umask 0002 && mkdir -p ${PIP_TARGET} \
    && chown :pip-global ${PIP_TARGET} \
    && ( [ ! -f "/etc/profile.d/00-restore-env.sh" ] || sed -i -e "s/export PATH=/export PATH=\/usr\/local\/pip-global:/" /etc/profile.d/00-restore-env.sh )

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1

# Install Tesseract OCR
# https://www.kkaneko.jp/tools/ubuntu/tesseract_buildout.html

# Install Dev Tools
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends git cmake cmake-curses-gui cmake-gui wget

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends build-essential gcc g++ make libtool texinfo dpkg-dev pkg-config

# Install Leptonica Library
# [Args] Leptonica Library version: master, 1.82.0, 1.81.0, 1.80.0
ARG LEPTONICA_TAG="master"
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends zlib1g-dev
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends libpng-dev libjpeg-dev libtiff5-dev libsdl-gfx1.2-dev libsdl-image1.2-dev libsdl1.2-dev libavcodec-dev libavdevice-dev libavformat-dev libavutil-dev
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends python3-enchant python3-poppler-qt5
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends python3-enchant python3-poppler-qt5
RUN cd /tmp \
    && git clone --branch=${LEPTONICA_TAG} --depth=1 https://github.com/DanBloomberg/leptonica.git leptonica \
    && cd leptonica \
    && mkdir build \
    && cd build \
    && cmake -DBUILD_PROG=ON -DCMAKE_C_FLAGS="-DPIC -fPIC" -DCMAKE_CXX_FLAGS="-DPIC -fPIC" .. \
    && make \
    && make install \
    && /sbin/ldconfig

# Install Tesseract OCR
# [Args] Tesseract OCR version: main, 5.1.0, 5.0.0, 4.1.3, 4.1.0, 4.0.0
ARG TESSERACT_TAG="main"
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends automake libcairo2-dev libpango1.0-dev libopenjp2-7-dev libtool libcurl4-openssl-dev gawk zlib1g-dev
RUN cd /tmp \
    && git clone --branch=${TESSERACT_TAG} --depth=1 https://github.com/tesseract-ocr/tesseract.git tesseract \
    && cd tesseract \
    && ./autogen.sh \
    && ./configure --enable-static --disable-shared --with-gnu-ld \
    && make CFLAGS="-fopenmp -DPIC -fPIC -O2 -std=c++17" CXXFLAGS="-fopenmp -DPIC -fPIC -O2 -std=c++17" LIBS="-lz -lpng -ljpeg -ltiff -lwebp -lopenjp2" \
    && make install \
    && /sbin/ldconfig

# Install Tesseract data
RUN cd /usr/local/share \
    && mv tessdata tessdata.org \
    && git clone --recursive --depth=1 https://github.com/tesseract-ocr/tessdata_best.git tessdata

# Install Tesseract training
RUN cd /tmp/tesseract \
    && make training LIBS="-lz -lpng -ljpeg -ltiff -lwebp -lopenjp2" \
    && make training-install

# Install langdata
RUN cd /usr/local/share \
    && git clone --recursive --depth=1 https://github.com/tesseract-ocr/langdata_lstm langdata
