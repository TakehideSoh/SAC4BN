import argparse
import os
import re
import shutil
import tempfile

from libsbml import readSBML


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sbml_file", required=True)
parser.add_argument("-a", "--an_file", required=True)
args = vars(parser.parse_args())

sbml_file = args["sbml_file"]
an_file = args["an_file"]

document = readSBML(sbml_file)
model = document.getModel()
mplugin = model.getPlugin("qual")
transitions = mplugin.getListOfTransitions()

non_source_nodes: list[str] = []
for t in transitions:
    outputs = tuple(t.getListOfOutputs())
    assert len(outputs) == 1
    s = outputs[0].getQualitativeSpecies()
    if t.getListOfFunctionTerms():
        non_source_nodes.append(s)


with tempfile.NamedTemporaryFile("w", dir=os.path.dirname(an_file), delete=False) as tf:
    print(tf.name)

    with open(an_file, "r") as f:
        is_last_line_blank = False
        for line in f:
            if not line.strip():
                is_last_line_blank = True
                continue

            if "->" in line and "when" not in line:
                if is_last_line_blank:
                    v_m = re.search(r"^\"([^\"]+)\"", line.strip())
                    assert v_m is not None
                    v = v_m.group(1)

                    if v not in non_source_nodes:
                        print(line.strip())
                        is_last_line_blank = False
                        continue

            tf.write(line)
            is_last_line_blank = False

shutil.move(tf.name, an_file)
