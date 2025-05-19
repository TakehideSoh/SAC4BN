import argparse
import time
import os

from pyboolnet.file_exchange import bnet2primes
from pyboolnet.trap_spaces import compute_steady_states
from pyboolnet.attractors import compute_attractors

MAX_OUTPUT = 2**31 - 1

parser = argparse.ArgumentParser()
parser.add_argument("bnet_file")
parser.add_argument("-a", "--attractor", action="store_true")
args = vars(parser.parse_args())

bnet_file = os.path.abspath(args["bnet_file"])

print("# Computing primes")
start = time.perf_counter()
primes = bnet2primes(bnet_file)
elapsed_time = time.perf_counter() - start
print(f"# Done ({elapsed_time:.3f} s)")

n = 0
if args["attractor"]:
    print("\n# Computing attractors")
    start = time.perf_counter()
    attractors = compute_attractors(primes, "asynchronous")
    elapsed_time = time.perf_counter() - start
    print(f"# Done ({elapsed_time:.3f} s)")

    print(f"is_complete: {attractors['is_complete']}")
    for x in attractors["attractors"]:
        if x["is_steady"]:
            n += 1
else:
    print("\n# Computing steady states")
    start = time.perf_counter()
    steady = compute_steady_states(primes, MAX_OUTPUT)
    elapsed_time = time.perf_counter() - start
    print(f"# Done ({elapsed_time:.3f} s)")
    n = len(steady)

print(f"\nFound {n} steady states.")
