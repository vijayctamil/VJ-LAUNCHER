import hou
import sys

if len(sys.argv) < 2:
    print("Error: No Houdini file provided.")
    sys.exit(1)

hip_file = sys.argv[1]

try:
    hou.hipFile.load(hip_file)
    print("Successfully loaded:", hip_file)

    nodes = [node.path() for node in hou.node("/").allSubChildren()]
    print("NODE_LIST_START")
    for node in nodes:
        print(node)
    print("NODE_LIST_END")
except Exception as e:
    print("Error loading Houdini file:", e)
