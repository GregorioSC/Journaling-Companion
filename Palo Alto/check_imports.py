import sys, importlib, inspect

# ensure project root is on path
sys.path.insert(0, ".")

for mname in ["dao.user_dao", "dao.entry_dao", "dao.insight_dao", "dao.exceptions"]:
    m = importlib.import_module(mname)
    print(f"\n=== {mname} ===")
    print("Loaded from:", m.__file__)
    if mname != "dao.exceptions":
        print("\n".join(inspect.getsource(m).splitlines()[:12]))
