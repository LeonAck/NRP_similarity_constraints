import sys
import os

invoke_str = "invoke"

# Enable importing the modules in the 'invoke' folder
if invoke_str in os.getcwd():
    os.chdir(os.getcwd()[:os.getcwd().index(invoke_str) + len(invoke_str)])
else:
    os.chdir(os.path.join(os.getcwd(), invoke_str))

sys.path.insert(1, os.getcwd())

# Add Docstrings as Descriptions to Tests

def pytest_itemcollected(item):
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
