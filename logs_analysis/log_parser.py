from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional

from common import BBM_INSTANCE_IDS, FASP_INSTANCE_IDS, LOGS_DIR, Solver

TIMEOUT_SEC = 1800
TIMEOUT_SEC_MARGIN = 3
MEMORY_THRESHOLD = 6 * 10**7


fixed_points_patterns = {
    "aeon": re.compile(r"Found (\d+) fixed points"),
    "fasp": re.compile(r"^(\d+)", flags=re.MULTILINE),
    "bmsa": re.compile(r"SAT \(full\)\s*:\s*(\d+)"),
    "pyboolnet": re.compile(r"Found (\d+) steady states"),
    "mc": re.compile(r"exact arb int (\d+)"),
}


@unique
class AbortType(Enum):
    TIMEOUT = "TIMEOUT"
    OUT_OF_MEMORY = "OUT_OF_MEMORY"
    UNKNOWN_ERROR = "ERROR"


@dataclass
class Result:
    num_fixed_points: Optional[int] = None
    cpu: Optional[float] = None
    abort_type: Optional[AbortType] = None


def parse_time_command_output(output: str) -> tuple[float, int]:
    # verbose
    user_time_m = re.search(r"^\s+User time \(seconds\): (\d+\.\d+)", output, flags=re.MULTILINE)
    sys_time_m = re.search(r"^\s+System time \(seconds\): (\d+\.\d+)", output, flags=re.MULTILINE)
    assert user_time_m and sys_time_m
    cpu = sum(map(lambda x: float(x.group(1)), (user_time_m, sys_time_m)))

    mem_m = re.search(r"^\s+Maximum resident set size \(kbytes\): (\d+)", output, flags=re.MULTILINE)
    assert mem_m
    mem = int(mem_m.group(1))

    return cpu, mem


def parse_log_default(log_file: str, p: re.Pattern[str]) -> Result:
    with open(log_file, "r") as f:
        content_raw = f.read()

    res = Result()

    fixed_points_m = p.search(content_raw)
    cpu, mem = parse_time_command_output(content_raw)
    if fixed_points_m:
        res.num_fixed_points = int(fixed_points_m.group(1))
        assert cpu <= TIMEOUT_SEC
        res.cpu = cpu
    elif cpu > TIMEOUT_SEC - TIMEOUT_SEC_MARGIN:
        res.abort_type = AbortType.TIMEOUT
    elif mem > MEMORY_THRESHOLD:
        res.abort_type = AbortType.OUT_OF_MEMORY
    else:
        res.abort_type = AbortType.UNKNOWN_ERROR

    return res


def parse_pyboolnet_log(log_file: str) -> Result:
    with open(log_file, "r") as f:
        content_raw = f.read()

    res = Result()

    fixed_points_m = fixed_points_patterns["pyboolnet"].search(content_raw)
    cpu, mem = parse_time_command_output(content_raw)
    if cpu > TIMEOUT_SEC - TIMEOUT_SEC_MARGIN:
        res.abort_type = AbortType.TIMEOUT
    elif fixed_points_m:
        res.num_fixed_points = int(fixed_points_m.group(1))
        res.cpu = cpu
    elif mem > MEMORY_THRESHOLD:
        res.abort_type = AbortType.OUT_OF_MEMORY
    else:
        res.abort_type = AbortType.UNKNOWN_ERROR

    return res


def parse_saf_logs(biolqm_log_file: str, log_file: Optional[str]) -> Result:
    with open(biolqm_log_file, "r") as f:
        content_raw = f.read()

    if "javax.xml.stream.XMLStreamException" in content_raw or "java.lang.NegativeArraySizeException" in content_raw:
        assert log_file is None
        return Result(abort_type=AbortType.UNKNOWN_ERROR)

    biolqm_cpu, _ = parse_time_command_output(content_raw)

    if biolqm_cpu > TIMEOUT_SEC - TIMEOUT_SEC_MARGIN:
        return Result(abort_type=AbortType.TIMEOUT)

    assert "+ exit_status=0" in content_raw and log_file is not None

    with open(log_file, "r") as f:
        content_raw = f.read()

    res = parse_log_default(log_file, fixed_points_patterns["bmsa"])
    if res.cpu is not None:
        cpu = biolqm_cpu + res.cpu
        if cpu > TIMEOUT_SEC:
            res = Result(abort_type=AbortType.TIMEOUT)
        else:
            res.cpu = cpu

    return res


def parse_saf_sstd_logs(biolqm_log_file: str, log_file: Optional[str]) -> Result:
    with open(biolqm_log_file, "r") as f:
        content_raw = f.read()

    if "javax.xml.stream.XMLStreamException" in content_raw or "java.lang.NegativeArraySizeException" in content_raw:
        assert log_file is None
        return Result(abort_type=AbortType.UNKNOWN_ERROR)

    biolqm_cpu, _ = parse_time_command_output(content_raw)

    if biolqm_cpu > TIMEOUT_SEC - TIMEOUT_SEC_MARGIN:
        return Result(abort_type=AbortType.TIMEOUT)

    assert "+ exit_status=0" in content_raw and log_file is not None

    with open(log_file, "r") as f:
        content_raw = f.read()

    res = parse_log_default(log_file, fixed_points_patterns["mc"])
    if res.cpu is not None:
        cpu = biolqm_cpu + res.cpu
        if cpu > TIMEOUT_SEC:
            res = Result(abort_type=AbortType.TIMEOUT)
        else:
            res.cpu = cpu

    return res


def parse_proposed_bmsa_log(log_file: str) -> Result:
    with open(log_file, "r") as f:
        content_raw = f.read()

    cpu, _ = parse_time_command_output(content_raw)

    if re.search(r"^s UNSATISFIABLE", content_raw, flags=re.MULTILINE):
        assert cpu <= TIMEOUT_SEC
        return Result(0, cpu)

    return parse_log_default(log_file, fixed_points_patterns["bmsa"])


def parse_bbm_instances() -> dict[str, dict[Solver, Result]]:
    res_all: dict[str, dict[Solver, Result]] = dict()
    for id_ in BBM_INSTANCE_IDS:
        print(id_)
        d: dict[Solver, Result] = dict()

        # PyBoolNet
        d[Solver.PYBOOLNET] = parse_pyboolnet_log(glob.glob(f"{LOGS_DIR}/pyboolnet/bbm/*id-{id_}*/*.log")[0])

        # SAF
        biolqm_log_file = glob.glob(f"{LOGS_DIR}/gen-an/bbm/*id-{id_}*/*.log")[0]
        log_paths = glob.glob(f"{LOGS_DIR}/saf/bbm/*id-{id_}*/*.log")
        log_file = log_paths[0] if log_paths else None
        d[Solver.SAF] = parse_saf_logs(biolqm_log_file, log_file)

        # SAF SharpSAT-TD
        log_paths = glob.glob(f"{LOGS_DIR}/saf-count/bbm/*id-{id_}*/*.log")
        log_file = log_paths[0] if log_paths else None
        d[Solver.SAF_SHARPSAT_TD] = parse_saf_sstd_logs(biolqm_log_file, log_file)

        # fASP
        d[Solver.FASP_CONJ] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/fasp_conj/bbm/*{id_}*.log")[0], fixed_points_patterns["fasp"]
        )
        d[Solver.FASP_SRC] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/fasp_src/bbm/*{id_}*.log")[0], fixed_points_patterns["fasp"]
        )

        # AEON
        d[Solver.AEON] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/aeon/bbm/*id-{id_}*/*.log")[0], fixed_points_patterns["aeon"]
        )

        # Proposed BMSA
        d[Solver.HYBRID_BMSA] = parse_proposed_bmsa_log(glob.glob(f"{LOGS_DIR}/hybrid_bmsa/bbm/*id-{id_}*/*.log")[0])

        # Proposed SharpSAT-TD
        d[Solver.TSEITIN_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/direct_sharpsat-td/bbm/*id-{id_}*/*.log")[0], fixed_points_patterns["mc"]
        )
        d[Solver.PI_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/indirect_sharpsat-td/bbm/*id-{id_}*/*.log")[0], fixed_points_patterns["mc"]
        )
        d[Solver.HYBRID_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/hybrid_sharpsat-td/bbm/*id-{id_}*/*.log")[0], fixed_points_patterns["mc"]
        )

        res_all[id_] = d

    return res_all


def parse_fasp_instances() -> dict[str, dict[Solver, Result]]:
    res_all: dict[str, dict[Solver, Result]] = dict()
    for id_ in FASP_INSTANCE_IDS:
        print(id_)
        d: dict[Solver, Result] = dict()

        # PyBoolNet
        d[Solver.PYBOOLNET] = parse_pyboolnet_log(glob.glob(f"{LOGS_DIR}/pyboolnet/fasp/**/{id_}.bnet.log")[0])

        # SAF
        biolqm_log_file = glob.glob(f"{LOGS_DIR}/gen-an/fasp/**/{id_}.bnet.log")[0]
        log_paths = glob.glob(f"{LOGS_DIR}/saf/fasp/**/{id_}.bnet*.log", recursive=True)
        log_file = log_paths[0] if log_paths else None
        d[Solver.SAF] = parse_saf_logs(biolqm_log_file, log_file)

        # SAF SharpSAT-TD
        log_paths = glob.glob(f"{LOGS_DIR}/saf-count/fasp/**/{id_}.bnet*.log", recursive=True)
        log_file = log_paths[0] if log_paths else None
        d[Solver.SAF_SHARPSAT_TD] = parse_saf_sstd_logs(biolqm_log_file, log_file)

        # fASP
        d[Solver.FASP_CONJ] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/fasp_conj/fasp/**/{id_}.bnet.log", recursive=True)[0], fixed_points_patterns["fasp"]
        )
        d[Solver.FASP_SRC] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/fasp_src/fasp/**/{id_}.bnet.log", recursive=True)[0], fixed_points_patterns["fasp"]
        )

        # AEON
        d[Solver.AEON] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/aeon/fasp/**/{id_}.bnet.log", recursive=True)[0], fixed_points_patterns["aeon"]
        )

        # Proposed BMSA
        d[Solver.HYBRID_BMSA] = parse_proposed_bmsa_log(
            glob.glob(f"{LOGS_DIR}/hybrid_bmsa/fasp/**/{id_}.bnet.log", recursive=True)[0]
        )

        # Proposed SharpSAT-TD
        d[Solver.TSEITIN_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/direct_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0],
            fixed_points_patterns["mc"],
        )
        d[Solver.PI_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/indirect_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0],
            fixed_points_patterns["mc"],
        )
        d[Solver.HYBRID_SHARPSAT_TD] = parse_log_default(
            glob.glob(f"{LOGS_DIR}/hybrid_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0],
            fixed_points_patterns["mc"],
        )

        res_all[id_] = d

    return res_all


def get_num_vars_from_aeon_log(log_file: str) -> int:
    with open(log_file, "r") as f:
        content_raw = f.read()

    num_vars_m = re.search(r"BN has (\d+) variables", content_raw)
    assert num_vars_m
    return int(num_vars_m.group(1))


def parse_num_vars() -> dict[str, int]:
    num_vars: dict[str, int] = dict()
    for id_ in BBM_INSTANCE_IDS:
        num_vars[id_] = get_num_vars_from_aeon_log(glob.glob(f"{LOGS_DIR}/aeon/bbm/*id-{id_}*/*.log")[0])

    for id_ in FASP_INSTANCE_IDS:
        num_vars[id_] = get_num_vars_from_aeon_log(
            glob.glob(f"{LOGS_DIR}/aeon/fasp_for_num_vars/**/{id_}*.log", recursive=True)[0]
        )

    return num_vars


def parse_num_fixed_points() -> dict[str, int]:
    num_fixed_points: dict[str, int] = dict()
    for id_ in BBM_INSTANCE_IDS:
        res = parse_log_default(
            glob.glob(f"{LOGS_DIR}/hybrid_sharpsat-td/bbm/*id-{id_}*/*.log")[0], fixed_points_patterns["mc"]
        )
        assert res.num_fixed_points is not None and res.cpu is not None
        num_fixed_points[id_] = res.num_fixed_points

    for id_ in FASP_INSTANCE_IDS:
        log_file = glob.glob(f"{LOGS_DIR}/hybrid_d4-anytime/fasp/**/{id_}*.log", recursive=True)[0]
        with open(log_file, "r") as f:
            content_raw = f.read()

        if "The number of models is greater than the given threshold" in content_raw:
            num_fixed_points[id_] = 10**30
        else:
            fixed_points_m = re.search(r"^s\s+(\d+)", content_raw, flags=re.MULTILINE)
            assert fixed_points_m
            num_fixed_points[id_] = int(fixed_points_m.group(1))

    return num_fixed_points
