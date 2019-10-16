from pathlib import Path
import urllib.request
import zipfile
import shutil
import re
import io
import os

_packurl = "http://packs.download.atmel.com/"

def get_device_list():
    with urllib.request.urlopen(_packurl) as response:
        html = response.read().decode("utf-8")
        device_packs = re.findall(r'data-link="(Atmel\..+_DFP\..*?\.atpack)"', html)
        packs = []
        for pack in device_packs:
            searchResult = re.search(r'Atmel\.(.+)_DFP\.(.*?)\.atpack', pack)
            device = searchResult.group(1)
            version = searchResult.group(2)
            # For now the first instance in the HTML is the latest version, don't worry about else case.
            if not any(p['device'] == device for p in packs):
                packs.append( { 'device':device, 'version':version, 'url':_packurl+pack } )
        return packs

def download_packs_atdf(packs, dest):
    for p in packs:
        print(f"Downloading {p['device']} version {p['version']} ...")
        with urllib.request.urlopen(p['url']) as content:
            z = zipfile.ZipFile(io.BytesIO(content.read()))
            print(f"Extracting {p['device']} version {p['version']} ...")
            for member in [m for m in z.namelist() if m.startswith("atdf/")]:
                z.extract(member, dest+"_")
    shutil.move(dest+"_/atdf", dest)
    shutil.rmtree(dest+"_", ignore_errors=True)

if __name__ == "__main__":
    device_list = get_device_list()

    # TODO: ensure family exists
    Family = 'XMEGAA'

    shutil.rmtree(f"device_files/{Family}", ignore_errors=True)
    Path(f"device_files").mkdir(exist_ok=True, parents=True)

    device_list = [ d for d in device_list if re.search(Family, d['device']) ]
    download_packs_atdf(device_list, f"device_files/{Family}")

    # requires system to have patch command
    os.system(f"(cd device_files; patch -p1 -f --input={Family}.patch)")
