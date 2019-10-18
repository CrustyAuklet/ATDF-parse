from pathlib import Path
import shutil

#from jinja2 import Template
import jinja2

from reader import ATDFReader
import atdf

device = "ATxmega128A1U"

df = ATDFReader(f"device_files/XMEGAA/{device}.atdf")
modules = df.getModules()
module_list = [ atdf.Module(m) for m in modules.getchildren() ]

shutil.rmtree(f"src/{device}", ignore_errors=True)
Path(f"src/{device}").mkdir(exist_ok=True, parents=True)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)

t = templateEnv.get_template('RegisterGroup.hpp.in')

for m in module_list:
    # open the output file
    ofile = open(f"src/{device}/{m.name}.hpp", 'w')
    code = t.render(module=m)
    ofile.write(code)
    ofile.close()
