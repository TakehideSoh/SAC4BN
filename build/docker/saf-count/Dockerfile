FROM ubuntu:22.04

RUN apt update && apt install -y git cmake make g++ libgmp-dev libmpfr-dev

WORKDIR /usr/local/src/

RUN git clone https://github.com/Laakeri/sharpsat-td.git
RUN cd sharpsat-td && ./setupdev.sh static

FROM ubuntu:22.04

RUN apt update && apt install -y --no-install-recommends unzip default-jre time

COPY --from=0 /usr/local/src/sharpsat-td/bin/* /usr/local/bin/
COPY saf.jar solve.sh /app/

WORKDIR /benchmark

ENTRYPOINT ["time", "-v", "/app/solve.sh"]
