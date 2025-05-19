FROM ubuntu:22.04

RUN apt update && apt install -y git default-jdk maven

WORKDIR /usr/local/src/
RUN git clone https://github.com/colomoto/bioLQM.git
WORKDIR /usr/local/src/bioLQM
RUN mvn package

FROM ubuntu:22.04

RUN apt update && apt install -y --no-install-recommends ca-certificates curl default-jre python3.11 time
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.11 get-pip.py && rm -f get-pip.py

RUN pip3.11 install python-libsbml

COPY --from=0 /usr/local/src/bioLQM/target/ /app/target/
COPY modify_an.py convert.sh /app/

WORKDIR /benchmark

ENTRYPOINT ["time", "-v", "/app/convert.sh"]
