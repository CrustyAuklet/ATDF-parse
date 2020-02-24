from pathlib import Path
import shutil
import argparse
import sys
import os

import jinja2
from cmsis_svd.parser import SVDParser

def run():
    parser = argparse.ArgumentParser(description='CMSIS Code Generator')
    parser.add_argument('-i','--input', metavar='SVD', help="CMSIS SVD file to parse", type=str, dest='svd_file', required=True)
    parser.add_argument('-t','--templates', help="Jinja Template Directory (required)", type=str, dest='template_dir', required=True)
    parser.add_argument('-o','--output', help="Output Directory", type=str, default='./', dest='output_dir')

    argv = parser.parse_args(['-i', 'RE01_1500KB.svd', '-t', './templates/cmsis_cpp17', '-o', './test_output'])

    device = SVDParser.for_xml_file(argv.svd_file).get_device()

    # create output directory if it doesn't exist
    Path(argv.output_dir).mkdir(exist_ok=True, parents=True)

    # set jinja search path to the template directory
    templateLoader = jinja2.FileSystemLoader(searchpath=argv.template_dir)
    templateEnv = jinja2.Environment(loader=templateLoader)

    # create device file if template exists
    if os.path.exists(os.path.join(argv.template_dir, 'device.hpp.in')):
        with open(os.path.join(argv.output_dir, 'device.hpp'), 'w') as ofile:
            t = templateEnv.get_template('device.hpp.in')
            code = t.render(device=device)
            ofile.write(code)
            ofile.close()

    # create peripheral headers if a tempalte exists
    if os.path.exists(os.path.join(argv.template_dir, 'peripheral.hpp.in')):
        t = templateEnv.get_template('peripheral.hpp.in')

        for peripheral in device.peripherals:
            ofile_name = f"{peripheral.name}.hpp"
            with open(os.path.join(argv.output_dir, ofile_name), 'w') as ofile:
                device_meta = { 'name':device.name, 'vendor':device.vendor, 'version':device.version }
                code = t.render( peripheral=peripheral, device_meta=device_meta )
                ofile.write(code)
                ofile.close()

    return 0

    # module_list = [ atdf.Module(m) for m in df.getModules().getchildren() ]
    # t = templateEnv.get_template('RegisterGroup.hpp.in')

    # for m in module_list:
    #     module_filename = f"{m.name}.hpp"

    #     # overwrite old version if existing
    #     ofile = open(os.path.join(argv.output_dir, module_filename), 'w')
    #     code = t.render(module=m)
    #     ofile.write(code)
    #     ofile.close()

if __name__ == "__main__":
    sys.exit(run())
