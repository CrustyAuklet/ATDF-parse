from reader import ATDFReader
import atdf
from jinja2 import Template

df = ATDFReader("device_files/XMEGAA/ATxmega64A1U.atdf")
modules = df.getModules()
module_list = [ atdf.Module(m) for m in modules.getchildren() ]

musart = module_list[-6]
mtwi = module_list[-13]

t = Template(open('templates/RegisterGroup.hpp.in', 'r').read())
code = t.render(module=mtwi)

ofile = open("test1.hpp", 'w')
ofile.write(code)
ofile.close()
