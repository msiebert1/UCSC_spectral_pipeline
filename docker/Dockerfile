FROM ubuntu:latest

ENV PATH="/root/miniconda3/bin:${UCSC_SPECPIPE}:${PATH}"
ARG PATH="/root/miniconda3/bin:${UCSC_SPECPIPE}:${PATH}"
RUN apt-get update
RUN apt-get install -y xgterm
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh

RUN conda config --add channels http://ssb.stsci.edu/astroconda
RUN conda create -n iraf27 python=2.7 iraf-all pyraf-all stsci
RUN conda create -n py36 python=3.6
WORKDIR /home