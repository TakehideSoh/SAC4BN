from __future__ import annotations

import glob
import re
from dataclasses import dataclass

from common import (BBM_INSTANCE_IDS, FASP_INSTANCE_IDS, LOGS_DIR,
                    PSEUDO_RANDOM_INSTANCE_IDS, RESULTS_DIRNAME,
                    SELECTED_INSTANCE_IDS, Solver)

header_p = re.compile(r"^p cnf (\d+) (\d+)")
cl_p = re.compile(r"^(-?\d+\s+)+0")
s_p = re.compile(r"\s+")


@dataclass
class Result:
    encode_finished: bool = False
    num_vars: int = 0
    num_cls: int = 0
    num_lits: int = 0


def parse_log(log_file: str) -> Result:
    with open(log_file, "r") as f:
        content_raw = f.read()

    if "+ exit_status=0" not in content_raw:
        return Result()

    res = Result(True)
    for line in content_raw.split("\n"):
        header_m = header_p.search(line)
        if header_m is not None:
            res.num_vars = int(header_m.group(1))
            res.num_cls = int(header_m.group(2))
            res.num_lits = 0

        cl_m = cl_p.search(line)
        if cl_m is not None:
            res.num_lits += len(s_p.split(cl_m.group().strip(" 0")))

    return res


def parse_all() -> dict[str, dict[Solver, Result]]:
    res_all: dict[str, dict[Solver, Result]] = dict()
    for id_ in BBM_INSTANCE_IDS:
        print(id_)
        d: dict[Solver, Result] = dict()

        # Tseitin
        d[Solver.TSEITIN_SHARPSAT_TD] = parse_log(glob.glob(f"{LOGS_DIR}/direct_sharpsat-td/bbm/*id-{id_}*/*.log")[0])

        # PI
        d[Solver.PI_SHARPSAT_TD] = parse_log(glob.glob(f"{LOGS_DIR}/indirect_sharpsat-td/bbm/*id-{id_}*/*.log")[0])

        # Hybrid
        d[Solver.HYBRID_SHARPSAT_TD] = parse_log(glob.glob(f"{LOGS_DIR}/hybrid_sharpsat-td/bbm/*id-{id_}*/*.log")[0])

        res_all[id_] = d

    for id_ in FASP_INSTANCE_IDS:
        print(id_)
        d = dict()

        # Tseitin
        d[Solver.TSEITIN_SHARPSAT_TD] = parse_log(
            glob.glob(f"{LOGS_DIR}/direct_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0]
        )

        # PI
        d[Solver.PI_SHARPSAT_TD] = parse_log(
            glob.glob(f"{LOGS_DIR}/indirect_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0]
        )

        # Hybrid
        d[Solver.HYBRID_SHARPSAT_TD] = parse_log(
            glob.glob(f"{LOGS_DIR}/hybrid_sharpsat-td/fasp/**/{id_}.bnet.log", recursive=True)[0]
        )

        res_all[id_] = d

    return res_all


def format_float(t: float) -> str:
    return f"{t:.3f}"


solvers = [Solver.TSEITIN_SHARPSAT_TD, Solver.PI_SHARPSAT_TD, Solver.HYBRID_SHARPSAT_TD]
names = ["T", "P", "H"]
res_all = parse_all()

csv_rows = [
    ["Ins"]
    + ["Enc"] * len(names)
    + ["#Var"] * (len(names) - 1)
    + ["#Cl"] * (len(names) - 1)
    + ["#Lit"] * (len(names) - 1)
]
csv_rows.append([""] + names + names[1:] * 3)

for ids in (BBM_INSTANCE_IDS, PSEUDO_RANDOM_INSTANCE_IDS, SELECTED_INSTANCE_IDS):
    row = [""]
    row += [
        str(sum(map(lambda r: not r.encode_finished, [res_all[id_][solver] for id_ in ids]))) for solver in solvers
    ]

    # Var
    pi_ratios = []
    hybrid_ratios = []
    for id_ in ids:
        tseitin_value = res_all[id_][Solver.TSEITIN_SHARPSAT_TD].num_vars
        assert tseitin_value > 0

        pi_value = res_all[id_][Solver.PI_SHARPSAT_TD].num_vars
        if pi_value > 0:
            pi_ratios.append(pi_value / tseitin_value)

        hybrid_value = res_all[id_][Solver.HYBRID_SHARPSAT_TD].num_vars
        assert hybrid_value > 0
        hybrid_ratios.append(hybrid_value / tseitin_value)

        print(tseitin_value, pi_value, hybrid_value)
    print(sum(pi_ratios) / len(pi_ratios))
    print(sum(hybrid_ratios) / len(hybrid_ratios))
    row += [format_float(sum(pi_ratios) / len(pi_ratios)), format_float(sum(hybrid_ratios) / len(hybrid_ratios))]

    # Cl
    pi_ratios = []
    hybrid_ratios = []
    for id_ in ids:
        tseitin_value = res_all[id_][Solver.TSEITIN_SHARPSAT_TD].num_cls
        assert tseitin_value > 0

        pi_value = res_all[id_][Solver.PI_SHARPSAT_TD].num_cls
        if pi_value > 0:
            pi_ratios.append(pi_value / tseitin_value)

        hybrid_value = res_all[id_][Solver.HYBRID_SHARPSAT_TD].num_cls
        assert hybrid_value > 0
        hybrid_ratios.append(hybrid_value / tseitin_value)

        print(tseitin_value, pi_value, hybrid_value)
    print(sum(pi_ratios) / len(pi_ratios))
    print(sum(hybrid_ratios) / len(hybrid_ratios))
    row += [format_float(sum(pi_ratios) / len(pi_ratios)), format_float(sum(hybrid_ratios) / len(hybrid_ratios))]

    # Lit
    pi_ratios = []
    hybrid_ratios = []
    for id_ in ids:
        tseitin_value = res_all[id_][Solver.TSEITIN_SHARPSAT_TD].num_lits
        assert tseitin_value > 0

        pi_value = res_all[id_][Solver.PI_SHARPSAT_TD].num_lits
        if pi_value > 0:
            pi_ratios.append(pi_value / tseitin_value)

        hybrid_value = res_all[id_][Solver.HYBRID_SHARPSAT_TD].num_lits
        assert hybrid_value > 0
        hybrid_ratios.append(hybrid_value / tseitin_value)

        print(tseitin_value, pi_value, hybrid_value)
    print(sum(pi_ratios) / len(pi_ratios))
    print(sum(hybrid_ratios) / len(hybrid_ratios))
    row += [format_float(sum(pi_ratios) / len(pi_ratios)), format_float(sum(hybrid_ratios) / len(hybrid_ratios))]

    csv_rows.append(row)

with open(f"{RESULTS_DIRNAME}/cnf_stats.csv", "w") as f:
    for row in csv_rows:
        f.write(",".join(row))
        f.write("\n")
