# pyrevit stuff
from pyrevit import revit, script, forms
logger = script.get_logger()
output = script.get_output()

# get the revit document
doc = revit.doc

import sys

# import duHast modules
sys.path.append(r"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor-NET48\src")


import os
import pkgutil
import importlib

def test_package_modules(package_name):
    try:
        
        package = importlib.import_module(package_name)
        package_path = package.__path__
        
        for importer, mod_name, ispkg in pkgutil.iter_modules(package_path):
            full_mod_name = "{package_name}.{mod_name}".format(package_name=package_name, mod_name=mod_name)
            try:
                importlib.import_module(full_mod_name)
                print("Imported: {full_mod_name}".format(full_mod_name=full_mod_name))
            except Exception as e:
                print("Failed to import: {full_mod_name}: {e}".format(full_mod_name=full_mod_name, e=e))
                
    except Exception as e:
        print("Failed to load package {package_name}: {e}".format(package_name=package_name, e=e))


def test_all_modules(package_name):
    counter_success = 0
    counter_failure = 0
    
    package = importlib.import_module(package_name)
    
    for importer, modname, ispkg in pkgutil.walk_packages(
        package.__path__, 
        package.__name__ + "."
    ):
        try:
            importlib.import_module(modname)
            counter_success += 1
        except Exception as e:
            
            print("=====\n{modname}: \n{e}".format(modname=modname, e=e))
            counter_failure += 1

    print("Success: {success}, Failure: {failure}".format(success=counter_success, failure=counter_failure))

# test duHast modules
#test_package_modules("duHast")
# test_all_modules("duHast")
test_all_modules("duHast")