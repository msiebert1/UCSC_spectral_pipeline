#!/usr/bin/env python3

# import lcogt, json, sys, os, requests, time
import numpy as np, glob, tarfile, shutil
from astropy.time import Time, TimeDelta
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import ascii, fits
from datetime import datetime
import subprocess
from optparse import OptionParser

def upload_spectrum_to_yse(file, inst):
    script = '/home/marley/photpipe/pythonscripts/uploadTransientData.py'
    args = ['-i',file,'--clobber','--obsgroup','UCSC',
        '--permissionsgroup','UCSC','--instrument',inst,
        '-s','/home/ckilpatrick/scripts/settings.ini','-e','--spectrum']

    try:
        r = subprocess.run([script]+args, timeout=20)
    except subprocess.TimeoutExpired as e:
        print('YSE PZ upload for',file,'expired')

if __name__ == "__main__":
    description = "Uploads spectrum ASCII files to yse-pz"
    usage = "%prog    \t [option] \n Recommended syntax: %prog"
    parser = OptionParser(usage=usage, description=description, version="0.1" )
    parser.add_option("-a", "--all", dest="all", action="store_true",
                      help='upload all files (not just combined spectra)')

    option, args = parser.parse_args()
    _all= option.all

    if _all:
        spec_files = glob.glob('*.flm')
    else:
        spec_files = glob.glob('*combined*.flm')

    keyslist = ['ra','dec','instrument','rlap','obs_date','redshift',
                    'redshift_err','redshift_quality','spectrum_notes',
                    'obs_group','groups','spec_phase','snid','data_quality']
    for spec in spec_files:
        SpecHeader = {}
        fin = open(spec)
        count = 0
        for line in fin:
            line = line.replace('\n','')
            if not count: header = np.array(line.replace('# ','').split())
            for key in keyslist:
                if line.lower().startswith('# %s '%key):
                    SpecHeader[key] = line.split()[-1]
            count += 1
        fin.close()

        snid = input('Confirm SN name [{name}]: '.format(name=SpecHeader['snid'])) or SpecHeader['snid']
        if snid != SpecHeader['snid']:
            print (spec)
            with open(spec,'r') as yse_spec:
                yse_spec_data = yse_spec.readlines()
                with open(spec.split('.')[0]+'_v2.flm','w') as yse_spec_new:
                    for i, line in enumerate(yse_spec_data):
                        if 'INSTRUMENT' in line:
                            inst = line.split('INSTRUMENT')[1].strip()
                        if 'SNID' in line:
                            yse_spec_new.write(line.replace((line.split()[2]),snid))
                        else:
                            yse_spec_new.write(line)

        # upload_spectrum_to_yse(spec, inst)








