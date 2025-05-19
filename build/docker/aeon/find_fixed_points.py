import argparse
import os

from biodivine_aeon import BooleanNetwork, FixedPoints, SymbolicAsyncGraph

parser = argparse.ArgumentParser()
parser.add_argument("bn_file")
args = vars(parser.parse_args())

bn_file = os.path.abspath(args["bn_file"])

bn = BooleanNetwork.from_file(bn_file)
if bn_file.endswith(".bnet"):
    bn = bn.infer_regulatory_graph()
stg = SymbolicAsyncGraph(bn)

print(f"BN has {bn.num_vars()} variables.")
print([bn.get_variable_name(v) for v in bn.variables()])

fixed_points = FixedPoints.symbolic(stg)

print(f"Found {int(fixed_points.cardinality())} fixed points.")
