from pathlib import Path
import shutil

from jinja2 import Template

from reader import ATDFReader
import atdf

device = "ATxmega64A1U"

df = ATDFReader(f"device_files/XMEGAA/{device}.atdf")
modules = df.getModules()
module_list = [ atdf.Module(m) for m in modules.getchildren() ]

shutil.rmtree(f"src/{device}", ignore_errors=True)
Path(f"src/{device}").mkdir(exist_ok=True, parents=True)

t = Template(open('templates/RegisterGroup.hpp.in', 'r').read())

for m in module_list:
    ofile = open(f"src/{device}/{m.name}.hpp", 'w')
    code = t.render(module=m)
    ofile.write(code)
    ofile.close()
