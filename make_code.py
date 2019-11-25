from pathlib import Path
import shutil
import argparse
import sys
import os

#from jinja2 import Template
import jinja2

from reader import ATDFReader
import atdf

def run():
    parser = argparse.ArgumentParser(description='ATDF Code Generator')
    parser.add_argument('-i','--input', help="ATDF file to parse", type=str, dest='atdf_file', required=True)
    parser.add_argument('-t','--templates', help="Jinja Template Directory (required)", type=str, dest='template_dir', required=True)
    parser.add_argument('-o','--output', help="Output Directory", type=str, default='./', dest='output_dir')

    argv = parser.parse_args()

    df = ATDFReader(argv.atdf_file)
    module_list = [ atdf.Module(m) for m in df.getModules().getchildren() ]

    # shutil.rmtree(argv.output_dir, ignore_errors=True)
    Path(argv.output_dir).mkdir(exist_ok=True, parents=True)

    templateLoader = jinja2.FileSystemLoader(searchpath=argv.template_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)

    t = templateEnv.get_template('RegisterGroup.hpp.in')

    for m in module_list:
        module_filename = f"{m.name}.hpp"

        # overwrite old version if existing
        ofile = open(os.path.join(argv.output_dir, module_filename), 'w')
        code = t.render(module=m)
        ofile.write(code)
        ofile.close()


if __name__ == "__main__":
    sys.exit(run())
