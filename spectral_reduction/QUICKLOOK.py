#!/usr/bin/env python

import sys
from optparse import OptionParser
import util
import quick_reduc
import time
import glob

description = "> Fast reduction of spectra "
usage = "%prog  \t [option] \n Recommended syntax: %prog -i -c"

if __name__ == "__main__":
    parser = OptionParser(usage=usage, description=description, version="0.1" )
    #parser.add_option("-d", "--dispersion", dest="dispersion", action="store_true",help='chose interactively dispersion line')
    #parser.add_option("-t", "--trace", dest="trace", action="store_true", help=' trace extraction with another frame')
    #parser.add_option("-s", "--sens", dest="sens", default='', type="str", help=' use sensitivity curve from this list')
    #parser.add_option("-a", "--arc", dest="arc", default='', type="str", help=' use arc from this list ')
    parser.add_option("-a", "--arc", dest="arc", action="store_true",help='identify arcs of the same night')
    parser.add_option("-i", "--interactive_extraction", dest="interactive_extraction", action="store_true",help='extract spectrum interactively')
    #parser.add_option("-r", "--check_reidentify_arc", dest="check_reidentify_arc", action="store_true",help='check the reidentification')
    parser.add_option("-c", "--cosmic", dest="cosmic", action="store_true",help='cosmic ray removal')
    #parser.add_option("-o", "--overlapping_region", dest="overlapping_region", action="store_true",help='check overlapping region')
    option, args = parser.parse_args()

    starttime = time.time()

    util.delete('*.png')

    #if len(args) < 1:
    #    sys.argv.append('--help')
    #option, args = parser.parse_args()

    if len(args) > 1:
        files=[]
        sys.argv.append('--help')
        option, args = parser.parse_args()
    elif len(args) == 1:
        files = util.readlist(args[0])
    else:
        listfile = glob.glob('*.fits')
        files_science = []
        files_arc = []
        #print 'checking your files ...'
        for img in listfile:
            _type = ''
            hdr0 = util.readhdr(img)
            _type=util.readkey3(hdr0, 'object')
            if _type.startswith("arc"):
                files_arc.append(img)
            else:
                files_science.append(img)

    _cosmic = option.cosmic
    if not _cosmic:   _cosmic = False
    
    _interactive_extraction = option.interactive_extraction
    if not _interactive_extraction:   _interactive_extraction = False

    _arc= option.arc
    if not _arc:   _arc = False

    if len(files_science) > 0:
        print '\n#######################################\n### start of reduction'
        outputfile = quick_reduc.reduce(files_science,files_arc, _cosmic, _interactive_extraction,_arc)
        stoptime = time.time()
        print '\n### wow, only ' + str(stoptime - starttime) + ' seconds'
        print '\n### end of reduction'
        print '\n#######################################'
    else:
        print '\n### problem, exit '
        sys.exit()