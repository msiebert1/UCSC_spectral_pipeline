#!/usr/bin/env python
from __future__ import print_function

import sys
from optparse import OptionParser
import util
import quick_reduc,quick_reduc_esi
import time
import glob
import matplotlib
from astropy.io import fits

matplotlib.use('TkAgg')

description = "> Fast reduction of spectra "
usage = "%prog    \t [option] \n Recommended syntax: %prog -i -c"

if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description, version="0.1" )
    #parser.add_option("-d", "--dispersion", dest="dispersion",
    #                  action="store_true",help='chose interactively dispersion line')
    #parser.add_option("-t", "--trace", dest="trace",
    #                  action="store_true", help=' trace extraction with another frame')
    #parser.add_option("-s", "--sens", dest="sens",
    #                  default='', type="str", help=' use sensitivity curve from this list')
    #parser.add_option("-a", "--arc", dest="arc",
    #                  default='', type="str", help=' use arc from this list ')
    #parser.add_option("-r", "--check_reidentify_arc", dest="check_reidentify_arc",
    #                  action="store_true",help='check the reidentification')
    #parser.add_option("-o", "--overlapping_region", dest="overlapping_region",
    #                  action="store_true",help='check overlapping region')
    parser.add_option("-a", "--arc", dest="arc", action="store_true",
                      help='identify arcs of the same night')
    parser.add_option("-i", "--interactive_extraction", dest="interactive_extraction",
                      action="store_true",help='extract spectrum interactively')
    parser.add_option("-c", "--cosmic", dest="cosmic",
                      action="store_true",help='cosmic ray removal')
    parser.add_option("-f", "--fast", dest="fast",
                      action="store_true",help='fast reduction')
    parser.add_option("--host", dest="host",
                      action="store_true",help='host reduction')
    parser.add_option("--no-flat", dest="nflat",
                      action="store_true",help='do not flat field')
    parser.add_option("--cedit", dest="cedit",
                      action="store_true",help='cosmic ray removal with manual trace editing')
    parser.add_option("--crmask", dest="crmask",
                      action="store_true",help='creates a bad pixel mask from cr rejection for imcombine')
    parser.add_option("--crnew", dest="crnew",
                      action="store_true",help='new cr algorithm to work better with new keck data')
    parser.add_option("--ex", dest="extract",
                      action="store_true",help='combined, cr rejected files already exist. skip straight to flatfielding and extraction')
    parser.add_option("--rename", dest="rename",
                      action="store_true",help='rename the object with user input')
    parser.add_option("-e", dest="esi",
                      action="store_true",help='esi reductions required flag')
    #parser.add_option("--fftrace", dest="fftrace",
    #                  action="store_true",help='exact trace for flat fielding')

    option, args = parser.parse_args()

    starttime = time.time()

    util.delete('*.png')
    _arc= option.arc
    _fast= option.fast
    _host= option.host
    _nflat= option.nflat
    _cedit= option.cedit
    _crmask= option.crmask
    _crnew= option.crnew
    _ex= option.extract
    _rename= option.rename
    _esi= option.esi
    #_fftrace= option.fftrace

    if len(args) > 1:
        files=[]
        sys.argv.append('--help')
        option, args = parser.parse_args()
    elif len(args) == 1:
        files = util.readlist(args[0])
    else:
        listfile = glob.glob('t*.fits')
        #import pdb; pdb.set_trace()
        files_science = []
        files_arc = []
        files_sky = []
        files_flat = []
        #try:
        # if "ESI" in fits.open(listfile[0])[0].header['INSTRUME']:
        #    _esi='True'
        #except KeyError:
        #    _esi='False'
        if _esi:
         files_arc.append('../ARC_blue.fits')
         files_flat.append('../toFlat_blue.fits')
        else:
         files_arc.append('../ARC_blue.fits')
         files_arc.append('../ARC_red.fits')

        #print 'checking your files ...'
        for img in listfile:
            _type = ''
            hdr0 = util.readhdr(img)
            # _type=util.readkey3(hdr0, 'object')
            _type=hdr0.get('object', None)
            # if _type.startswith("arc"):
            if _type != None and _type.startswith("arc"):
                files_arc.append(img)
            elif 'RESP' in img:
                files_flat.append(img)
            else:
                files_science.append(img)
            #print(files_arc,files_flat,files_science)


    _cosmic = option.cosmic
    if not _cosmic:
        _cosmic = False
    
    _interactive_extraction = option.interactive_extraction
    if not _interactive_extraction:
        _interactive_extraction = False

    
    if not _arc:
        _arc = False

    if len(files_science) > 0:
        print('\n#######################################\n### start of reduction')
        #import pdb;pdb.set_trace()
        if _esi:
            print('\nFor ESI there are 10 orders, with different spatial scales')
            print('\nWe extract one reference aperture, & scale the other 9 apertures to match the physical size of the reference')
            print('To start, set aperture centres:')
            print('> Set leftmost order to aperture 1')
            print('> Set rightmost order to aperture 10 (and everthing inbetween)')
            print('\nThen fit one aperture of your choice')
            print('\n#######################################')
            outputfile = quick_reduc_esi.reduce(files_science, files_arc, files_flat, _cosmic, _interactive_extraction,_arc,_fast,_host,_nflat,_cedit,_crmask,_crnew,_ex,_rename)
        else:
         outputfile = quick_reduc.reduce(files_science, files_arc, files_flat, _cosmic, _interactive_extraction,_arc,_fast,_host,_nflat,_cedit,_crmask,_crnew,_ex,_rename)
        stoptime = time.time()
        print('\n### wow, only ' + str(stoptime - starttime) + ' seconds')
        print('\n### end of reduction')
        print('\n#######################################')
    else:
        print('\n### problem, exit ')
        sys.exit()
