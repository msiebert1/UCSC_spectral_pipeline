from __future__    import print_function

def reduce(imglist, files_arc, files_flat, _cosmic, _interactive_extraction,_arc):
    import string
    import os
    import re
    import sys
    import pdb
    os.environ["PYRAF_BETA_STATUS"] = "1"
    try:      from astropy.io import fits as pyfits
    except:      import   pyfits
    import numpy as np
    import glob
    import util
    import instruments
    import combine_sides as cs
    import cosmics
    from pyraf import iraf
    import pyzapspec

    dv = util.dvex()
    scal = np.pi / 180.
    
    if not _interactive_extraction:
        _interactive = False
    else:
        _interactive = True

    if not _arc:
        _arc_identify = False
    else:
        _arc_identify = True

    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.ccdred(_doprint=0)
    iraf.twodspec(_doprint=0)
    iraf.longslit(_doprint=0)
    iraf.onedspec(_doprint=0)
    iraf.specred(_doprint=0)
    iraf.disp(inlist='1', reference='1')

    toforget = ['ccdproc', 'imcopy', 
                'specred.apall', 'longslit.identify', 
                'longslit.reidentify', 'specred.standard',
                'longslit.fitcoords', 'onedspec.wspectext']
    for t in toforget:
        iraf.unlearn(t)
    iraf.ccdred.verbose = 'no'
    iraf.specred.verbose = 'no'
    iraf.ccdproc.darkcor = 'no'
    iraf.ccdproc.fixpix = 'no'
    iraf.ccdproc.flatcor = 'no'
    iraf.ccdproc.zerocor = 'no'
    iraf.ccdproc.ccdtype = ''

    iraf.longslit.mode = 'h'
    iraf.specred.mode = 'h'
    iraf.noao.mode = 'h'
    iraf.ccdred.instrument = "ccddb$kpno/camera.dat"

    list_arc_b = []
    list_arc_r = []
    
    for arcs in files_arc:
        hdr = util.readhdr(arcs)
        br, inst = instruments.blue_or_red(arcs)
        
        if br == 'blue':
            list_arc_b.append(arcs)
        elif br == 'red':
            list_arc_r.append(arcs)
        else:
            errStr = '{} '.format(str(util.readkey3(hdr, 'VERSION')))
            errStr += 'not in database'
            print(errStr)
            sys.exit()
    
    asci_files = []
    newlist = [[],[]]

    print('\n### images to reduce :',imglist)
    #raise TypeError
    for img in imglist:
        if instruments.blue_or_red(img)[0] == 'blue':
            newlist[0].append(img)
        elif instruments.blue_or_red(img)[0] == 'red':
            newlist[1].append(img)

    if len(newlist[1]) < 1:
        newlist = newlist[:-1]
    elif len(newlist[0]) < 1:
        newlist = newlist[1:]
    else:
        sides = raw_input("Reduce which side? ([both]/b/r): ")
        if sides == 'b':
            newlist = newlist[:-1]
        elif sides == 'r':
            newlist = newlist[1:]
            
    for imgs in newlist:
        print (imgs)
        hdr = util.readhdr(imgs[0])
        br, inst = instruments.blue_or_red(imgs[0])
        if br == 'blue':
            flat_file = '../RESP_blue'
        elif br == 'red':
            flat_file = '../RESP_red'
        else:
            errStr = 'Not in intrument list'
            print(errStr)
            sys.exit()
                
        iraf.specred.dispaxi = inst.get('dispaxis')
        iraf.longslit.dispaxi = inst.get('dispaxis')

        _gain = inst.get('gain')
        _ron = inst.get('read_noise')
        iraf.specred.apall.readnoi = _ron
        iraf.specred.apall.gain = _gain

        _object0 = util.readkey3(hdr, 'OBJECT')
        _date0 = util.readkey3(hdr, 'DATE-OBS')

        _object0 = re.sub(' ', '', _object0)
        _object0 = re.sub('/', '_', _object0)
        nameout0 = str(_object0) + '_' + inst.get('name') + '_' + str(_date0)

        nameout0 = util.name_duplicate(imgs[0], nameout0, '')
        timg = nameout0
        print('\n### now processing :',timg,' for -> ',inst.get('name'))
        if len(imgs) > 1:
            img_str = ''
            for i in imgs:
                img_str = img_str + i + ','
            iraf.imcombine(img_str, output=timg)
        else:
            img = imgs[0]
            if os.path.isfile(timg):
                os.system('rm -rf ' + timg)
            iraf.imcopy(img, output=timg)
        
        # should just do this by hand
        iraf.ccdproc(timg, output='', 
                           overscan='no', 
                           trim='no', 
                           zerocor="no", 
                           flatcor="yes", 
                           readaxi='line',
                           flat=flat_file, 
                           Stdout=1)

        img = timg

        #raw_input("Press Enter to continue...")
        if _cosmic:
            print('\n### starting cosmic removal')
            
            # array, header = cosmics.fromfits(img)
            # c = cosmics.cosmicsimage(array, 
            #                          gain=inst.get('gain'), readnoise=inst.get('read_noise'), 
            #                          sigclip = 5, sigfrac = 0.5, objlim = 2.0)
            # c.run(maxiter = 5)
            # cosmics.tofits('cosmic_' + img, c.cleanarray, header)
            # img='cosmic_' + img

            outimg,outmask,header = pyzapspec.pyzapspec(img, 
                                                        outfile='cosmic_{}'.format(img), 
                                                        WRITE_OUTFILE = True,
                                                        boxsize=inst.get('pyzap_boxsize'))
            img = 'cosmic_{}'.format(img)

            print('\n### cosmic removal finished')
        else:
            print('\n### No cosmic removal, saving normalized image for inspection???')
            

        if inst.get('arm') == 'blue' and len(list_arc_b)>0:
            arcfile = list_arc_b[0]
        elif inst.get('arm') == 'red' and len(list_arc_r)>0:
            arcfile = list_arc_r[0]
        else:
            arcfile=None
        
        if arcfile is not None and not arcfile.endswith(".fits"):
            arcfile=arcfile+'.fits'

        if not os.path.isdir('database/'):
                os.mkdir('database/')
        
        #There is a bug in identify when the path to the coordlist is too long
        #This is my hacky workaround for now, the file  is deleted later
        os.system('cp ' + inst.get('line_list') + ' .')

        if _arc_identify:
            if not os.path.isdir('../master_files/'):
                os.mkdir('../master_files/')

            arcref = None

            if br == 'blue':
                arcfile = 'ARC_blue.fits' #THIS IS A HACK
                wave_sol_file = 'idARC_blue.ms'
            elif br == 'red':
                arcfile = 'ARC_red.fits' #THIS IS A HACK
                wave_sol_file = 'idARC_red.ms'
            
            masters = [os.path.basename(x) for x in glob.glob('../master_files/*')]
            if wave_sol_file in masters:
                wave_sol= raw_input("Use your master wavelength solution? [y]/n: ") or 'y'
                if wave_sol.strip().lower() == 'y':
                    print ('Copying master file')
                    arc_ex=re.sub('.fits', '.ms.fits', arcfile)
                    os.system('cp ' + '../master_files/' + wave_sol_file + ' ./database/')
                else:
                    os.system('cp ' + '../' + arcfile + ' .')
                    arc_ex=re.sub('.fits', '.ms.fits', arcfile)
                    print('\n### arcfile : ',arcfile)
                    print('\n### arcfile extraction : ',arc_ex)
                    print(inst.get('line_list'))

                    # remove the file from the extract destination
                    if os.path.isfile(arc_ex):
                        os.remove(arc_ex)

                    iraf.specred.apall(arcfile, 
                                        output=arc_ex, 
                                        line = inst.get('approx_extract_line'), 
                                        nsum=10, 
                                        interactive='no', 
                                        extract='yes',
                                        find='yes', 
                                        nfind=1 ,
                                        format='multispec', 
                                        trace='no',
                                        back='no',
                                        recen='no')
                    iraf.longslit.identify(images=arc_ex, 
                                            section='line {}'.format(inst.get('approx_extract_line')),
                                            coordli='lines.dat',
                                            function = 'spline3',
                                            order=3, 
                                            mode='h')
                    os.system('cp ' + 'database/' + wave_sol_file + ' ../master_files/')
            else:
                os.system('cp ' + '../' + arcfile + ' .')
                arc_ex=re.sub('.fits', '.ms.fits', arcfile)
                print('\n### arcfile : ',arcfile)
                print('\n### arcfile extraction : ',arc_ex)
                print(inst.get('line_list'))
                iraf.specred.apall(arcfile, 
                                    output=arc_ex, 
                                    line = 'INDEF', 
                                    nsum=10, 
                                    interactive='no', 
                                    extract='yes',
                                    find='yes', 
                                    nfind=1 ,
                                    format='multispec', 
                                    trace='no',
                                    back='no',
                                    recen='no')
                iraf.longslit.identify(images=arc_ex, 
                                        section=inst.get('section'),
                                        coordli='lines.dat',
                                        function = 'spline3',
                                        order=3, 
                                        mode='h')
                os.system('cp ' + 'database/' + wave_sol_file + ' ../master_files/')
        else:
            if br == 'blue':
                arcfile = 'ARC_blue.fits' #THIS IS A HACK
            elif br == 'red':
                arcfile = 'ARC_red.fits' #THIS IS A HACK
                
            os.system('cp ' + '../' + arcfile + ' .')
            arc_ex=re.sub('.fits', '.ms.fits', arcfile)

            arcref = inst.get('archive_arc_extracted')
            arcref_img = string.split(arcref, '/')[-1]
            arcref_img = arcref_img.replace('.ms.fits', '')
            arcrefid = inst.get('archive_arc_extracted_id')
            os.system('cp ' + arcref + ' .')
            arcref = string.split(arcref, '/')[-1]
            os.system('cp ' + arcrefid + ' ./database')

            aperture = inst.get('archive_arc_aperture')
            os.system('cp ' + aperture + ' ./database')

            print('\n###  arcfile : ',arcfile)
            print('\n###  arcfile extraction : ',arc_ex)
            print('\n###  arc reference : ',arcref)
            
            # read for some meta data to get the row right
            tmpHDU = pyfits.open(arcfile)
            header = tmpHDU[0].header
            try:
                spatialBin = int(header['binning'].split(',')[0])
            except KeyError:
                spatialBin = 1
            apLine = 700//spatialBin
            
            iraf.specred.apall(arcfile, 
                               output=arc_ex, 
                               ref=arcref_img, 
                               line = apLine, 
                               nsum=10, 
                               interactive='no', 
                               extract='yes',
                               find='yes', 
                               nfind=1 ,
                               format='multispec', 
                               trace='no',
                               back='no',
                               recen='no')
                               
                                                              
            iraf.longslit.reidentify(referenc=arcref, 
                                     images=arc_ex, 
                                     interac='NO', 
                                     section=inst.get('section'), 
                                     coordli='lines.dat', 
                                     shift='INDEF', 
                                     search='INDEF',
                                     mode='h', 
                                     verbose='YES', 
                                     step=0,
                                     nsum=5,
                                     nlost=2,
                                     cradius=10, 
                                     refit='yes',
                                     overrid='yes',
                                     newaps='no')
        util.delete('lines.dat')
                                     
        

        print('\n### extraction using apall')
        result = []
        hdr_image = util.readhdr(img)
        _type=util.readkey3(hdr_image, 'object')

        if (_type.startswith("arc") or 
            _type.startswith("dflat") or 
            _type.startswith("Dflat") or 
            _type.startswith("Dbias") or 
            _type.startswith("Bias")):
            print('\n### warning problem \n exit ')
            sys.exit()
        else:
            imgex = util.extractspectrum(
                img, dv, inst, _interactive, 'obj')
            print('\n### applying wavelength solution')
            print (arc_ex)
            iraf.disp(inlist=imgex, reference=arc_ex)    

        result = result + [imgex] + [timg]
       
        # asci_files.append(imgasci)
        if not os.path.isdir(_object0 + '_ex/'):
            os.mkdir(_object0 + '_ex/')
        
        if not _arc_identify:
            util.delete(arcref)
        else:
            util.delete(arcfile)

        util.delete(arc_ex)
        #util.delete(img)
        util.delete(imgex)
        if arcref is not None:
            util.delete(arcref)
        util.delete('logfile')
        #if _cosmic:
            #util.delete(img[7:])
            #util.delete("cosmic_*")

        os.system('mv ' + 'd'+ imgex + ' ' + _object0 + '_ex/')

        use_sens = raw_input('Use archival flux calibration? [y]/n ')
        if use_sens != 'no':
            sensfile = inst.get('archive_sens')
            os.system('cp ' + sensfile + ' ' + _object0 + '_ex/')
            bstarfile = inst.get('archive_bstar')
            os.system('cp ' + bstarfile + ' ' + _object0 + '_ex/')

    return result
    
    
    