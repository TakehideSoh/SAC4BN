FROM ubuntu:22.04

RUN apt update && apt install -y --no-install-recommends ca-certificates curl python3.11 git libncurses5 libxml2 time
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py && rm -f get-pip.py

RUN pip3.11 install --force-reinstall git+https://github.com/hklarner/pyboolnet

COPY find_steady_states.py /app/

WORKDIR /benchmark

ENTRYPOINT ["time", "-v", "python3.11", "/app/find_steady_states.py"]
