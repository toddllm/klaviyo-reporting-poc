import pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))
