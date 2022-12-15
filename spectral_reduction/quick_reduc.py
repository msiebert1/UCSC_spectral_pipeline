from __future__    import print_function

def reduce(imglist, files_arc, files_flat, _cosmic, _interactive_extraction, _arc, _fast, _host, _nflat, _cedit, _crmask, _crnew, _ex, _rename):
    import string
    import os
    import re
    import sys
    import pdb
    os.environ["PYRAF_BETA_STATUS"] = "1"
    try:      from astropy.io import fits
    except:      import   pyfits as fits
    import numpy as np
    import glob
    import util
    import instruments
    import combine_sides as cs
    import cosmics
    from pyraf import iraf
    import pyzapspec
    import host_galaxies as host_gals
    import cr_reject as cr

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
        # br, inst = instruments.blue_or_red(arcs)
        if 'blue' in arcs:
            br = 'blue'
        elif 'red' in arcs:
            br = 'red'

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
        try:
            sides = raw_input("Reduce which side? ([both]/b/r): ")
        except:
            sides = input("Reduce which side? ([both]/b/r): ")
        
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

        print (os.getcwd().split('/')[-1])
        _object0 = os.getcwd().split('/')[-1]
        # _object0 = util.readkey3(hdr, 'OBJECT')
        _date0 = util.readkey3(hdr, 'DATE-OBS')

        _object0 = re.sub(' ', '', _object0)
        _object0 = re.sub('/', '_', _object0)

        if _rename:
            try:
                _object0 = raw_input('New object name ' + '['+_object0+']: ') or _object0
            except:
                _object0 = input('New object name ' + '['+_object0+']: ') or _object0       
        # nameout0 = str(_object0) + '_' + inst.get('name') + '_' + str(_date0)
        nameout0 = str(_object0) + '_' + inst.get('name')

        nameout0 = util.name_duplicate(imgs[0], nameout0, '')
        # nameout0 = nameout0.split(':')[0][0:-2] + '.fits'
        print ('NAMEOUT:', nameout0)
        timg = nameout0
        print('\n### now processing :',timg,' for -> ',inst.get('name'))
        if os.path.isfile(timg) and not _ex:
            util.delete(timg)
        print ('IMAGES: ', imgs)

        if not _ex:
            if os.path.isfile(timg):
                util.delete(timg)

            if len(imgs) > 1:
                img_str = ''
                k=1

                if _crnew:
                    cr.cr_reject(imgs, timg, lim=100)
                else:
                    for i in imgs:
                        # util.create_bpmask([[],[]], br = 'red')
                        # raise TypeError
                        if _cosmic or _cedit or _crmask:
                            if _host and 'red' in nameout0:
                                with open('../HOST_METADATA.txt') as host_file:
                                    for line in host_file.readlines():
                                        if line.split()[0] == _object0.lower().split('_')[0]:
                                            redshift, sep, ang, r_kron_rad = float(line.split()[1]), float(line.split()[2]), float(line.split()[3]), float(line.split()[4])
                            else:
                                redshift=None

                            print('\n### starting cosmic removal')
                            files = glob.glob('*.fits')
                            if 'cosmic_{}'.format(i) not in glob.glob('*.fits'):

                                br = instruments.blue_or_red(i)[0]
                                # outimg,outmask,header = pyzapspec.pyzapspec(i,
                                #                                             outfile='cosmic_{}'.format(i),
                                #                                             WRITE_OUTFILE = True,
                                #                                             br = br,
                                #                                             img_num=k, redshift=redshift,
                                #                                             cedit=_cedit,
                                #                                             boxsize=inst.get('pyzap_boxsize',7),
                                #                                             nsigma=inst.get('pyzap_nsigma',16),
                                #                                             subsigma=inst.get('pyzap_subsigma',3))
                                if _crmask:
                                    print ('Masking cosmic rays...')
                                    outimg,outmask,header = pyzapspec.pyzapspec(i,
                                                                                outfile='cosmic_{}'.format(i),
                                                                                WRITE_OUTFILE = True,
                                                                                br = br,
                                                                                img_num=k, redshift=redshift,
                                                                                cedit=_cedit, DEBUG=False,
                                                                                boxsize=inst.get('pyzap_boxsize_mask',20),
                                                                                nsigma=inst.get('pyzap_nsigma_mask',2),
                                                                                subsigma=inst.get('pyzap_subsigma_mask',.5))
                                else:
                                    outimg,outmask,header = pyzapspec.pyzapspec(i,
                                                                                outfile='cosmic_{}'.format(i),
                                                                                WRITE_OUTFILE = True,
                                                                                br = br,
                                                                                img_num=k, redshift=redshift,
                                                                                cedit=_cedit, DEBUG=False,
                                                                                boxsize=inst.get('pyzap_boxsize',20),
                                                                                nsigma=inst.get('pyzap_nsigma',2),
                                                                                subsigma=inst.get('pyzap_subsigma',.5))
                            if _crmask:
                                iraf.ccdmask(image='zap_'+i,mask='mask_'+'zap_'+i[0:-5])
                            img = 'cosmic_{}'.format(i)
                            # img = '{}'.format(i)
                            if _crmask:
                                iraf.hedit(images=img, fields='BPM', add='yes', verify='no', value='mask_'+'zap_'+i[0:-5]+'.pl')
                            img_str = img_str + img + ','
                            

                            print('\n### cosmic removal finished')
                        else:
                            print('\n### No cosmic removal, saving normalized image for inspection???')

                            img_str = img_str + i + ','
                        k+=1
                    print (img_str)
                    if _crmask:
                        iraf.imcombine(img_str, combine='average', weight='exposure', masktype='goodvalue', output=timg)
                        iraf.imcombine(img_str, combine='median', masktype='goodvalue', output=timg[0:-5]+'_med.fits')
                    else:
                        iraf.imcombine(img_str, combine='average', weight='exposure', output=timg)
            else:
                i = imgs[0]
                if _cosmic or _cedit:
                    if _host and 'red' in nameout0:
                        with open('../HOST_METADATA.txt') as host_file:
                            for line in host_file.readlines():
                                if line.split()[0] == _object0.lower().split('_')[0]:
                                    redshift, sep, ang, r_kron_rad = float(line.split()[1]), float(line.split()[2]), float(line.split()[3]), float(line.split()[4])
                    else:
                        redshift=None
                    print('\n### starting cosmic removal')
                    files = glob.glob('*.fits')

                    if 'cosmic_{}'.format(i) not in glob.glob('*.fits'):

                        br = instruments.blue_or_red(i)[0]
                        outimg,outmask,header = pyzapspec.pyzapspec(i,
                                                                    outfile='cosmic_{}'.format(i),
                                                                    WRITE_OUTFILE = True,
                                                                    br = br,
                                                                    redshift=redshift,
                                                                    cedit=_cedit,
                                                                    boxsize=inst.get('pyzap_boxsize',7),
                                                                    nsigma=inst.get('pyzap_nsigma',16),
                                                                    subsigma=inst.get('pyzap_subsigma',3))
                    img = 'cosmic_{}'.format(i)

                    print('\n### cosmic removal finished')

                else:
                    img = i #TH: Needs to redefine img other the script will make a imcopy of the last item in imglist.
                    print('\n### No cosmic removal, saving normalized image for inspection???')

                if os.path.isfile(timg):
                    os.system('rm -rf ' + timg)
                iraf.imcopy(img, output=timg)
        else:
            print ('Skipping CR rejection and image combining')

        # should just do this by hand

        # tfits=fits.open(timg, mode='update')
        # thead=tfits[0].header
        # thead.set('DATASEC',  '[80:2296,66:346]')
        # thead.set('CCDSEC',  '[80:2296,66:346]')
        # flatfits=fits.open(flat_file + '.fits',mode='update')
        # flathead=flatfits[0].header
        # flathead.set('DATASEC',  '[80:2296,66:346]')
        # flathead.set('CCDSEC',  '[80:2296,66:346]')
        # tfits.flush()
        # flatfits.flush()

        if not _nflat:
            iraf.ccdproc(timg, output='',
                               overscan='no',
                               trim='no',
                               zerocor="no",
                               flatcor="yes",
                               readaxi='line',
                               flat=flat_file,
                               Stdout=1)
        else:
            print ('NOT FLAT FIELDING')
            iraf.ccdproc(timg, output='',
                               overscan='no',
                               trim='no',
                               zerocor="no",
                               flatcor="no",
                               readaxi='line',
                               Stdout=1)

        # if 'kast_red' in inst.get('name') or 'lris_red_new' in inst.get('name'): #Matt: did this change again?
        if 'kast_red' in inst.get('name'):
            tfits = fits.open(timg)
            tdata = tfits[0].data
            theader = tfits[0].header
            if theader.get('Mirrored', None) is None:
                print ('Mirroring Image!')
                flip_tdata = np.fliplr(tdata)
                theader.set('Mirrored',  'True')
                hdu = fits.PrimaryHDU(flip_tdata, theader)
                hdu.writeto(timg,output_verify='ignore', clobber=True)

        if _rename:
            tfits = fits.open(timg)
            tdata = tfits[0].data
            theader = tfits[0].header
            theader.set('OBJECT',  _object0)
            hdu = fits.PrimaryHDU(tdata, theader)
            hdu.writeto(timg,output_verify='ignore', clobber=True)

        img = timg


        print('\n### extraction using apall')
        result = []
        hdr_image = util.readhdr(img)
        # _type=util.readkey3(hdr_image, 'object')
        _type=hdr_image.get('object', '')
        if (_type.startswith("arc") or
            _type.startswith("dflat") or
            _type.startswith("Dflat") or
            _type.startswith("Dbias") or
            _type.startswith("Bias")):
            print('\n### warning problem \n exit ')
            sys.exit()
        else:
            try:
                match_aperture = raw_input('Match aperture? y/[n]: ') or 'n'
            except:
                match_aperture = input('Match aperture? y/[n]: ') or 'n'
            if _host:
                # match_aperture = raw_input('Match aperture? y/[n]: ') or 'n'
                if match_aperture != 'n':
                    imgex = util.extractspectrum(img, dv, inst, _interactive, 'obj', host_ex = True, match_aperture=match_aperture)
                else:
                    try:
                        seeing = raw_input('Seeing estimate? [1"]: ') or 1.
                    except:
                        seeing = input('Seeing estimate? [1"]: ') or 1.
                    seeing =float(seeing)
                    ap_pixs_phys, ap_pixs_sky, ap_width_kron, sep_pix, ap_widths_arcsec, ap_widths_kpc, r_kron_rad = host_gals.calculate_ap_data(_object0.lower().split('_')[0], inst, seeing=seeing)
                    host_gals.write_host_ap(ap_pixs_phys, ap_pixs_sky, ap_width_kron, sep_pix, nameout0.split('.')[0], ap_widths_arcsec, ap_widths_kpc, r_kron_rad, inst, img)
                    imgex = util.extractspectrum(img, dv, inst, _interactive, 'obj', host_ex = True, match_aperture=match_aperture)
            else:
                imgex = util.extractspectrum(img, dv, inst, _interactive, 'obj', match_aperture=match_aperture)

            save_ap = 'n'
            try:
                save_ap = raw_input('Save as a master aperture ? y/[n]: ')
            except:
                save_ap = input('Save as a master aperture ? y/[n]: ')
            if save_ap == 'y':
                os.system('cp ' + 'database/ap' + img[0:-5] + ' ../master_files/ap'+img[0:-5])



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
            line_list = inst.get('line_list').split('/')[-1]

            if _arc_identify:
                if not os.path.isdir('../master_files/'):
                    os.mkdir('../master_files/')

                arcref = None

                if br == 'blue':
                    arcfile = 'ARC_blue.fits' #THIS IS A HACK
                    wave_sol_file = 'idARC_blue.ms'
                    wave_sol_img = 'ARC_blue.ms.fits'
                elif br == 'red':
                    arcfile = 'ARC_red.fits' #THIS IS A HACK
                    wave_sol_file = 'idARC_red.ms'
                    wave_sol_img = 'ARC_red.ms.fits'

                masters = [os.path.basename(x) for x in glob.glob('../master_files/*')]
                if wave_sol_file in masters:
                    try:
                        wave_sol= raw_input("Use your master wavelength solution? [y]/n: ") or 'y'
                    except:
                        wave_sol= input("Use your master wavelength solution? [y]/n: ") or 'y'      
                    if wave_sol.strip().lower() == 'y':
                        print ('Copying master file')
                        arc_ex=re.sub('.fits', '.ms.fits', arcfile)
                        os.system('cp ' + '../master_files/' + wave_sol_file + ' ./database/')
                    else:
                        if br == 'blue':
                            for im in glob.glob('*.fits'):
                                if 'blue' in im and '_ex' not in im and 'zap' not in im:
                                    ref_img = im
                        elif br == 'red':
                            for im in glob.glob('*.fits') :
                                if 'red' in im and '_ex' not in im and 'zap' not in im:
                                    ref_img = im


                        try:
                            ref_img= raw_input("Reference image [{}]: ".format(ref_img)) or ref_img
                        except:
                            ref_img= input("Reference image [{}]: ".format(ref_img)) or ref_img
                        os.system('cp ' + '../' + arcfile + ' .')
                        arc_ex=re.sub('.fits', '.ms.fits', arcfile)
                        print('\n### arcfile : ',arcfile)
                        print('\n### arcfile extraction : ',arc_ex)
                        print(inst.get('line_list'))
                        # remove the file from the extract destination
                        if os.path.isfile(arc_ex):
                            os.remove(arc_ex)

                        os.system('cp ' + '../master_files/' + wave_sol_file + ' ./database/')
                        os.system('cp ' + '../master_files/' + wave_sol_img + ' ./database/')

                        iraf.specred.apall(arcfile,
                                            output=arc_ex,
                                            references = ref_img,
                                            line = 'INDEF',
                                            # nsum=10,
                                            interactive='no',
                                            extract='yes',
                                            find='no',
                                            format='multispec',
                                            trace='no',
                                            back='no',
                                            recen='no')
                        iraf.longslit.identify(images=arc_ex,
                                                # section='line {}'.format(inst.get('approx_extract_line')),
                                                coordli=line_list,
                                                function = 'legendre',
                                                order=3,
                                                mode='h')
                        # iraf.longslit.reidentify(referenc=wave_sol_img,
                        #                          images=arc_ex,
                        #                          coordli=line_list,
                        #                          shift='INDEF',
                        #                          search='INDEF',
                        #                          interac='YES',
                        #                          mode='h',
                        #                          verbose='YES',
                        #                          step=1,
                        #                          nsum=10,
                        #                          nlost=2,
                        #                          cradius=5,
                        #                          refit='yes',
                        #                          overrid='yes',
                        #                          newaps='no')
                else:
                    if br == 'blue':
                        for im in glob.glob('*.fits'):
                            if 'blue' in im and '_ex' not in im and 'zap' not in im:
                                ref_img = im
                    elif br == 'red':
                        for im in glob.glob('*.fits'):
                            if 'red' in im and '_ex' not in im and 'zap' not in im:
                                ref_img = im
                    try:
                        ref_img= raw_input("Reference image [{}]: ".format(ref_img)) or ref_img
                    except:
                        ref_img= input("Reference image [{}]: ".format(ref_img)) or ref_img
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
                                        references = ref_img,
                                        line = 'INDEF',
                                        # nsum=10,
                                        interactive='no',
                                        extract='yes',
                                        find='no',
                                        format='multispec',
                                        trace='no',
                                        back='no',
                                        recen='no')
                    iraf.longslit.identify(images=arc_ex,
                                            # section='line {}'.format(inst.get('approx_extract_line')),
                                            coordli=line_list,
                                            function = 'legendre',
                                            order=3,
                                            mode='h')
                    os.system('cp ' + 'database/' + wave_sol_file + ' ../master_files/')
                    os.system('cp ' + wave_sol_img + ' ../master_files/')
            util.delete(line_list)

            with open('database/ap' + img[0:-5]) as apfile:
                ap_data = apfile.readlines()
                count = 0
                for line in ap_data:
                    if line.startswith('begin'):
                        count+=1
                if count > 1:
                    with open('database/' + wave_sol_file) as arc:
                        with open('database/' + wave_sol_file + '_new','w') as arcex_new:
                            lines = arc.readlines()
                            for i in range(count):
                                for line in lines:
                                    if 'identify' in line:
                                        # arcex_new.write(line.replace('Ap 1', 'Ap '+ str(i+1)))
                                        arcex_new.write(line.replace(line[-6:], 'Ap '+ str(i+1) + '\n'))
                                    elif 'image' in line:
                                        # arcex_new.write(line.replace('Ap 1', 'Ap '+ str(i+1)))
                                        arcex_new.write(line.replace(line[-6:], 'Ap '+ str(i+1) + '\n'))
                                    elif 'aperture' in line:
                                        # arcex_new.write(line.replace('1', str(i+1)))
                                        arcex_new.write(line.replace(line[-3:], str(i+1) + '\n'))
                                    else:
                                        arcex_new.write(line)
                                arcex_new.write('\n')
                    os.system('cp ' + 'database/' + wave_sol_file +'_new' + ' database/'+wave_sol_file)
                    util.delete('database/'+wave_sol_file+'_new')
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

        try:
            use_master = raw_input('Use master flux calibration? [y]/n ')
        except:
            use_master = input('Use master flux calibration? [y]/n ')
        if use_master != 'n':
            os.system('cp ' + '../master_files/fluxstar' + inst.get('arm') +  '.fits ' + _object0 + '_ex/')
            os.system('cp ' + '../master_files/bstar' + inst.get('arm') +  '.fits ' + _object0 + '_ex/')
        else:
            try:
                use_sens = raw_input('Use archival flux calibration? [y]/n ')
            except:
                use_sens = input('Use archival flux calibration? [y]/n ')
            if use_sens != 'n':
                sensfile = inst.get('archive_sens')
                os.system('cp ' + sensfile + ' ' + _object0 + '_ex/')
                bstarfile = inst.get('archive_bstar')
                os.system('cp ' + bstarfile + ' ' + _object0 + '_ex/')


    return result


