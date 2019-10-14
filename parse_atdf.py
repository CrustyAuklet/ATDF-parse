import sys
import os
import argparse

import logging
from pathlib import Path

from reader import ATDFReader
import atdf

LOGGER = logging.getLogger('atdf.atdf_parser')

def run():
    parser = argparse.ArgumentParser(description='Atmel Device Description Parser (version 0.1)')
    #parser.add_argument("-o", "--output", dest='out_name', help="Name of output file (overides default)")
    parser.add_argument("-q", "--quiet", dest='quiet', action="store_true", help="Don't print to console")
    parser.add_argument("-v", "--verbose", dest='verbose', action="store_true", help="Show developer info")
    parser.add_argument('files', nargs='+', help="files to convert", metavar="file")

    #sys.argv.append('atdf_files/XMEGA/ATxmega128A1U.atdf')
    # print help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    argv = parser.parse_args()

    filenames = argv.files
    if len(filenames) == 0:
        parser.print_usage()
        print("    Please include files to convert...")
        sys.exit(1)

    # if args.out_name is None:
    #     args.out_name = os.path.splitext(args.in_fname)[0]+".h"
    for inputfile in filenames:
        if Path(inputfile).is_file():
            df = ATDFReader(inputfile)
            modules = df.getModules()

            module_list = [ atdf.Module(m) for m in modules.getchildren() ]
            module_list.sort(key=lambda x: x.name)

            ofile = open(f'{Path(inputfile).stem}.txt', 'w')

            for m in module_list:
                ofile.write("\n\n/********** MODULE START **********/\n")
                ofile.write(f"{m}\n")
                for rg in m.registerGroups:
                    ofile.write(f"    {rg}\n")
                    for r in rg.registers:
                        ofile.write(f"        {r}\n")
                        if type(r) == atdf.Register:
                            for f in r.fields:
                                ofile.write(f"            {f}\n")

                if len(m.valueGroups) > 0:
                    ofile.write("\n    /********** ENUMS **********/\n")
                for valGroup in m.valueGroups:
                    ofile.write(f"    {valGroup}\n")
                    for val in valGroup.values:
                        ofile.write(f"        {val}\n")

                if len(m.interruptGroups) > 0:
                    ofile.write("\n    /********** INTERRUPTS **********/\n")
                for intGroup in m.interruptGroups:
                    ofile.write(f"    {intGroup}\n")
                    for i in intGroup.interrupts:
                        ofile.write(f"        {i}\n")

    return 0

if __name__ == "__main__":
    sys.exit(run())
