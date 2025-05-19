FROM ubuntu:22.04

RUN apt update && apt install -y wget make gcc zlib1g-dev

WORKDIR /usr/local/src/
RUN wget http://www.sd.is.uec.ac.jp/toda/code/bdd_minisat_all-1.0.2.tar.gz
RUN tar xvzf bdd_minisat_all-1.0.2.tar.gz
RUN cd bdd_minisat_all-1.0.2 && make r -j2

FROM ubuntu:22.04

RUN apt update && apt install -y --no-install-recommends unzip default-jre time

COPY --from=0 /usr/local/src/bdd_minisat_all-1.0.2/bdd_minisat_all_release /usr/local/bin/
COPY saf.jar solve.sh /app/

WORKDIR /benchmark

ENTRYPOINT ["time", "-v", "/app/solve.sh"]
