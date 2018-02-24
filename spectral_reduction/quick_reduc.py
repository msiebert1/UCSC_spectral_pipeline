
def reduce(imglist,files_arc, _cosmic, _interactive_extraction,_arc):

    import string
    import os
    import re
    import sys
    os.environ["PYRAF_BETA_STATUS"] = "1"
    try:      from astropy.io import fits as pyfits
    except:   import   pyfits
    import numpy as np
    import util
    import instruments
    import combine_sides as cs
    import cosmics
    from pyraf import iraf

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

    toforget = ['ccdproc', 'imcopy', 'specred.apall', 'longslit.identify', 'longslit.reidentify', 'specred.standard',
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
        if util.readkey3(hdr, 'VERSION') == 'kastb':
            list_arc_b.append(arcs)
        elif util.readkey3(hdr, 'VERSION') == 'kastr':
            list_arc_r.append(arcs)
        else:
            print util.readkey3(hdr, 'VERSION') + 'not in database'
            sys.exit()
    
    asci_files = []
    newlist = [[],[]]

    print '\n### images to reduce :',imglist
    #raise TypeError
    for img in imglist:
        if 'b' in img:
            newlist[0].append(img)
        elif 'r' in img:
            newlist[1].append(img)

    if len(newlist[1]) < 1:
        newlist = newlist[:-1]
    
    for imgs in newlist:
        hdr = util.readhdr(imgs[0])
        if util.readkey3(hdr, 'VERSION') == 'kastb':
            inst = instruments.kast_blue
        elif util.readkey3(hdr, 'VERSION') == 'kastr':
            inst = instruments.kast_red
        else:
            print util.readkey3(hdr, 'VERSION') + 'not in database'
            sys.exit()

        iraf.specred.dispaxi = inst.get('dispaxis')
        iraf.longslit.dispaxi = inst.get('dispaxis')

        _gain = inst.get('gain')
        _ron = inst.get('read_noise')
        iraf.specred.apall.readnoi = _ron
        iraf.specred.apall.gain = _gain

        _object0 = util.readkey3(hdr, 'OBJECT')
        _date0 = util.readkey3(hdr, 'DATE-OBS')


        _biassec0 = inst.get('biassec')
        _trimsec0 = inst.get('trimsec')

        _object0 = re.sub(' ', '', _object0)
        _object0 = re.sub('/', '_', _object0)
        nameout0 = str(_object0) + '_' + inst.get('name') + '_' + str(_date0)

        nameout0 = util.name_duplicate(imgs[0], nameout0, '')
        timg = nameout0
        print '\n### now processing :',timg,' for -> ',inst.get('name')
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
        
        zero_file = inst.get('archive_zero_file')
        os.system('cp ' + zero_file + ' .')
        zero_file = string.split(zero_file, '/')[-1]
        
        flat_file = inst.get('archive_flat_file')
        os.system('cp ' + flat_file + ' .')
        flat_file = string.split(flat_file, '/')[-1]
        
        iraf.ccdproc(timg, output='', overscan='yes', trim='yes', zerocor="no", flatcor="no", readaxi='line',
                     trimsec=str(_trimsec0),biassec=str(_biassec0), Stdout=1)

        iraf.ccdproc(timg, output='', overscan='no', trim='no', zerocor="yes", flatcor="no", readaxi='line',
                     zero=zero_file,order=3, Stdout=1)
        iraf.ccdproc(timg, output='', overscan='no', trim='no', zerocor="no", flatcor="yes", readaxi='line',
                     flat=flat_file, Stdout=1)

        img = timg

        #raw_input("Press Enter to continue...")
        print '\n### starting cosmic removal'
        if _cosmic:
            array, header = cosmics.fromfits(img)
            c = cosmics.cosmicsimage(array, gain=inst.get('gain'), readnoise=inst.get('read_noise'), sigclip = 4.5, sigfrac = 0.5, objlim = 1.0)
            c.run(maxiter = 4)
            cosmics.tofits('cosmic_' + img, c.cleanarray, header)

        print '\n### cosmic removal finished'

        img='cosmic_' + img

        if inst.get('name') == 'kast_blue':
            arcfile = list_arc_b[0]
        elif inst.get('name') == 'kast_red':
            arcfile = list_arc_r[0]
        
        if not arcfile.endswith(".fits"):
            arcfile=arcfile+'.fits'

        if os.path.isfile(arcfile):
            util.delete('t' + arcfile)
            iraf.ccdproc(arcfile, output= 't' + arcfile, overscan='yes', trim='yes', zerocor="no", flatcor="no",
                         readaxi='line', trimsec=str(_trimsec0), biassec=str(_biassec0), Stdout=1)
            arcfile = 't' + arcfile
        else:
            print '\n### warning no arcfile \n exit '
            sys.exit()

        if not os.path.isdir('database/'):
                os.mkdir('database/')
        
        if _arc_identify:
            arc_ex=re.sub('.fits', '.ms.fits', arcfile)
            print '\n### arcfile : ',arcfile
            print '\n### arcfile extraction : ',arc_ex
            iraf.specred.apall(arcfile, output='', line = 'INDEF', nsum=10, interactive='no', extract='yes',find='yes', nfind=1 ,format='multispec', trace='no',back='no',recen='no')
            iraf.longslit.identify(images=arc_ex, section=inst.get('section'),coordli=inst.get('line_list'),function = 'spline3',order=3, mode='h')
        else:
            arcref = inst.get('archive_arc_extracted')
            arcrefid = inst.get('archive_arc_extracted_id')
            os.system('cp ' + arcref + ' .')
            arcref = string.split(arcref, '/')[-1]
            os.system('cp ' + arcrefid + ' ./database')

            arc_ex=re.sub('.fits', '.ms.fits', arcfile)

            print '\n###  arcfile : ',arcfile
            print '\n###  arcfile extraction : ',arc_ex
            print '\n###  arc referenece : ',arcref
            iraf.specred.apall(arcfile, output=arc_ex, line = 'INDEF', nsum=10, interactive='no', extract='yes',find='yes', nfind=1 ,format='multispec', trace='no',back='no',recen='no')

            iraf.longslit.reidentify(referenc=arcref, images=arc_ex, interac='NO', section=inst.get('section'), 
                                    coordli=inst.get('line_list'), shift='INDEF', search='INDEF',
                                    mode='h', verbose='YES', step=0,nsum=5, nlost=2, cradius=10, refit='yes',overrid='yes',newaps='no')
        
        #print '\n### checking sky lines '
        #_skyfile = inst.get('sky_file')
        #shift = util.skyfrom2d(img, _skyfile,'True')
        #print '\n### I found a shift of : ',shift

        print '\n### extraction using apall'
        result = []
        hdr_image = util.readhdr(img)
        _type=util.readkey3(hdr_image, 'object')

        if _type.startswith("arc") or _type.startswith("dflat") or _type.startswith("Dflat") or _type.startswith("Dbias") or _type.startswith("Bias"):
            print '\n### warning problem \n exit '
            sys.exit()
        else:
            imgex = util.extractspectrum(
                img, dv, inst, _interactive, 'obj')
            print '\n### applying wavelength solution'
            iraf.disp(inlist=imgex, reference=arc_ex)   
            sensfile = inst.get('archive_sens')
            os.system('cp ' + sensfile + ' .')
            sensfile = string.split(sensfile, '/')[-1]
            if sensfile:
                print '\n### sensitivity function : ',sensfile
                imgf = re.sub('.fits', '_f.fits', img)
                _extinction = inst.get('extinction_file')
                _observatory = inst.get('observatory')
                _exptime = util.readkey3(hdr, 'EXPTIME')
                _airmass = util.readkey3(hdr, 'AIRMASS')
                util.delete(imgf)
                dimgex='d'+imgex
                iraf.specred.calibrate(input=dimgex, output=imgf, sensiti=sensfile, extinct='yes',
                                        extinction=_extinction,flux='yes', ignorea='yes', airmass=_airmass, exptime=_exptime,
                                        fnu='no')
                imgout = imgf
                imgasci = re.sub('.fits', '.asci', imgout)
                errasci = re.sub('.fits', '_err.asci', imgout)
                util.delete(imgasci)
                iraf.onedspec.wspectext(imgout + '[*,1,1]', imgasci, header='no')
                iraf.onedspec.wspectext(imgout + '[*,1,4]', errasci, header='no')
                spec = np.transpose(np.genfromtxt(imgasci))
                err = np.transpose(np.genfromtxt(errasci))
                util.delete(errasci)
                final = np.transpose([spec[0], spec[1], err[1]])
                np.savetxt(imgasci, final)

                result = result + [imgout, imgasci]

        result = result + [imgex] + [timg]
       
        asci_files.append(imgasci)
        if not os.path.isdir(_object0 + '/'):
            os.mkdir(_object0 + '/')
            for img in result:
                os.system('mv ' + img + ' ' + _object0 + '/')
        else:
            for img in result:
                os.system('mv ' + img + ' ' + _object0 + '/')
        
        if not _arc_identify:
            util.delete(arcref)
        util.delete(sensfile)
        util.delete(zero_file)
        util.delete(flat_file)
        util.delete(arc_ex)
        util.delete(arcfile)
        util.delete('logfile')
        util.delete(dimgex)
        util.delete('cosmic_*')
    print '\n### now i will merge ...'
    if len(asci_files) > 1:
        final = cs.combine_blue_red(asci_files[0], asci_files[1], _object0)
    print '\n### final result in folder ',_object0,' is ',_object0+'_merged.asci'
    return result