# Supplementary Material for "A SAT-based Method for Counting All Singleton Attractors in Boolean Networks"

## Directory Structure

```text
.
├── benchmarks
│   ├── biodivine-boolean-models
│   │   └── models
│   └── fASP
│       └── dataset
│           ├── BBM
│           ├── Random
│           └── Selected
├── build
│   ├── docker
│   │   ├── aeon
│   │   ├── fasp
│   │   ├── gen-an
│   │   ├── proposed
│   │   ├── pyboolnet
│   │   ├── saf
│   │   └── saf-count
│   └── proposed_src
│       ├── lib
│       ├── project
│       └── src
│           └── main
│               └── scala
├── logs
│   ├── aeon
│   ├── direct_sharpsat-td
│   ├── fasp_conj
│   ├── fasp_src
│   ├── gen-an
│   ├── hybrid_bmsa
│   ├── hybrid_d4-anytime
│   ├── hybrid_sharpsat-td
│   ├── indirect_sharpsat-td
│   ├── pyboolnet
│   ├── saf
│   └── saf-count
└── logs_analysis
    └── results
```

## Supplementary Proof and Plot

We added the supplementary proof and cactus plot (see `proof_and_plot.pdf`).

## Detailed Results

We included the detailed results in `logs_analysis/results`.
Here are the short descriptions of each file:

- `cpu.csv`: CPU times for each solver per instance on BBM instances
- `cpu_fasp.csv`: CPU times for each solver per instance on fASP instances
- `cpu_selected.csv`: CPU times for each solver per instance on Selected instances
- `fixed_points.csv`: The number of fixed points for each solver per instance on BBM instances
- `fixed_points_fasp.csv`: The number of fixed points for each solver per instance on fASP instances
- `solved_per_set.csv`: The number of solved instances for each solver per benchmark set
- `solved_per_fps_range.csv`: The number of solved instances for each solver per #fixed points range
- `solved_per_vars_range.csv`: The number of solved instances for each solver per #vars range
- `cnf_stats.csv`: The comparison of CNF stats between Direct, Indirect, and Hybrid translations

- `cactus_log.eps`: Cactus plot on BBM instances
- `cactus_random_log.eps`: Cactus plot on Pseudo-random instances
- `cactus_all_log.eps`: Cactus plot on all instances
- `cactus_log.pdf`: PDF version of `cactus_log.eps`
- `cactus_random_log.pdf`: PDF version of `cactus_random_log.eps`
- `cactus_all_log.pdf`: PDF version of `cactus_all_log.eps`
- `*.dat`: Dat files for drawing the cactus plots

## How to Build

### Docker

See `build.sh` in each directory `build/docker/*`.

### Proposed Method

Install `sbt` and run `sbt assembly` in `build/proposed_src`.

## How to Run

Add `--ulimit cpu=<TIME_LIMIT>` option if you want to set a time limit.

### AEON

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark aeon <INPUT_FILENAME>
```

### fASP-conj

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark fasp <INPUT_FILENAME> -c
```

### fASP-src

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark fasp <INPUT_FILENAME> -c -e source
```

### PyBoolNet

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark pyboolnet <INPUT_FILENAME>
```

### gen-an

This will convert an input file (`.sbml` or `.bnet`) to `.an`.

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark gen-an <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> <INPUT_FILENAME>
```

### SAF

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark saf <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> <INPUT_FILENAME>
```

### SAF + SharpSAT-TD

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark saf-count <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> <INPUT_FILENAME>
```

### Proposed Method

#### Direct + SharpSAT-TD

DECOT is the `-decot` option for SharpSAT-TD.
See [here](https://github.com/Laakeri/sharpsat-td#flags) for more details.

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark bsaf \
    /app/solve-sharpsat.sh <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> t <INPUT_FILENAME> <DECOT>
```

#### Indirect + SharpSAT-TD

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark bsaf \
    /app/solve-sharpsat.sh <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> p <INPUT_FILENAME> <DECOT>
```

#### Hybrid + SharpSAT-TD

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark bsaf \
    /app/solve-sharpsat.sh <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> h3 <INPUT_FILENAME> <DECOT>
```

#### Hybrid + BDD_MINISAT_ALL

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark bsaf \
    /app/solve-bmsa.sh <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> h3 <INPUT_FILENAME>
```

#### Hybrid + d4 anyTimeCounter

This will terminate if the number of models exceeds the given threshold.

```sh
docker run -t --rm -v <DIR_CONTAINING_INPUT_FILE>:/benchmark bsaf \
    /app/solve-d4-anytime.sh <JAVA_HEAP_SIZE> <JAVA_STACK_SIZE> h3 <INPUT_FILENAME> <THRESHOLD>
```

## Benchmarks

We conducted the experiments using instances from the
[biodivine-boolean-models (BBM)](https://github.com/sybila/biodivine-boolean-models) and
[fASP](https://github.com/giang-trinh/fASP) repositories.
Instances in `benchmarks/fASP/dataset/BBM` were not taken directly from the fASP repository.
Since the fASP repository only contains 211 BBM instances, while the BBM repository now has 230,
we copied `.bnet` files from the BBM repository into that directory to make a complete list.
Additionally, we added identity functions to nodes that have no update functions, as they did in the fASP repository.
We also added identity functions to nodes declared in the `.sbml` file but not in the `.bnet` file
to ensure consistency of results between solvers using `.bnet` files and other solvers.

## How to Analyze Log Files

Install `python` and `gnuplot`, then run the following commands:

```sh
cd logs_analysis
python fps_and_cpu.py; python num_solved.py; python cnf_stats.py
./cactus_log.plt; ./cactus_random_log.plt
cat results/time_for_cactus.dat results/time_fasp_for_cactus.dat >results/time_all_for_cactus.dat; ./cactus_all_log.plt
```

The resulting files will be generated in `logs_analysis/results` (we have already included them).
