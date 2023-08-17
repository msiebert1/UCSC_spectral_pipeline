from __future__    import print_function


def esi_fix_ap():
    #! /bin/sh
    import sys,glob,os,re
    
    # spatial scale: arcsec/pixel along slit
    scale_dict = {
        '1' : 0.120,
        '2' : 0.127,
        '3' : 0.134,
        '4' : 0.137,
        '5' : 0.144,
        '6' : 0.149,
        '7' : 0.153,
        '8' : 0.158,
        '9' : 0.163,
        '10': 0.168
    }
    
    ap_files=glob.glob('database/ap*esi*[!.bak]')
    
    try:
     print('\n')
     file = str(input('Enter aperture file name for rescaling: ['+ap_files[0]+']')) or str(ap_files[0])
     print(file)
    except IndexError:
     print('\n')
     print('Cannot find any apertures with normal name format, please enter filename')
     name = str(input('File name: '))
     file='database/'+name
    
    try:
     print('\n### Making a backup of aperture file '+file+'->'+file+'.bak')
     #print('cp '+file+' '+file+'.bak')
     os.system('cp '+file+' '+file+'.bak')
    except KeyError:
     print('Cant find your aperture in the datbase folder')
    
    
    try:
     refap = str(input('Enter reference trace number (leftmost bluest order is 1, rightmost is 10) [5]:')) or '5'
     #print('Using '+refap+' as your reference aperture')
     print('\n### Scaling all apertures in '+file+' to  your reference aperture '+refap)
    except IndexError:
     print('Specify a trace numer')
     refap = str(input('Enter reference trace number (leftmost bluest order is 1,, rightmost is 10) [5]:')) or '5'
    
    scaling_ap=scale_dict[str(refap)]
    #print(scale_dict)
    for key in scale_dict:
        scale_dict[key] = scaling_ap/scale_dict[key]
        #print(key,scaling_ap,scale_dict[key])
    print('Scale factors for each aperture: \n',scale_dict)
    
    
    with open(file, 'r') as f:
     rows=[line for line in f]
     for r,entry in enumerate(rows):
      if entry.startswith('\taperture\t'+str(refap)):
       #print(entry)
       ap_rows=rows[int(r):int(r+11)]
       break
    
    #print(ap_rows)
    print('\n')
    
    try:
        ll_bkg=float(ap_rows[10].split()[1].split(':')[0])
        lu_bkg=float(ap_rows[10].split()[1].split(':')[1].split(',')[0])
        rl_bkg=float(ap_rows[10].split()[1].split(':')[1].split(',')[1])
        ru_bkg=float(ap_rows[10].split()[1].split(':')[2])
    except IndexError:
        bk1=float(ap_rows[10].split()[1].split(':')[0])
        bk2=float(ap_rows[10].split()[1].split(':')[1])
        bk3=float(ap_rows[10].split()[2].split(':')[0])
        bk4=float(ap_rows[10].split()[2].split(':')[1])
        bkg_list=sorted([bk1,bk2,bk3,bk4])
        ll_bkg,lu_bkg,rl_bkg,ru_bkg=bkg_list[0],bkg_list[1],bkg_list[2],bkg_list[3]


    ap_dict = {
        'low'   : float(ap_rows[3].split()[1]),
        'high'  : float(ap_rows[4].split()[1]),
        'xmin'  : float(ap_rows[6].split()[1]),
        'xmax'  : float(ap_rows[7].split()[1]),
        'll_bkg': ll_bkg,
        'lu_bkg': lu_bkg,
        'rl_bkg': rl_bkg,
        'ru_bkg': ru_bkg
    }

    
    
    print(ap_dict)
    
    with open(file, 'r') as f:
       with open(file+'.temp', 'w') as f2:
            #rows = [line.strip('\t').strip('\n') for line in f]
            rows=[line for line in f]
            #print(len(rows),len(rows2))
            for r,entry in enumerate(rows):
             #print(r,entry)
             if entry.startswith('\taperture'):
                ap_num=entry.split()[1]
                ap_scaling=scale_dict[str(ap_num)]
                #print('ap num:',ap_num,' required scaling:',ap_scaling)
             if entry.startswith('\tlow'):
                if entry.startswith("\t\tlow_reject"):
                  continue
                low_num=entry.split()[1]
                low_new=float(ap_dict['low'])*float(ap_scaling) 
                #print(entry) 
                #print(entry.replace(low_num, str("%.3f" % round(low_new, 3)), 1))
                f2.write(entry.replace(low_num, str("%.3f" % round(low_new, 3)), 1))
                continue
             if entry.startswith('\thigh'):
                if entry.startswith("\t\thigh_reject"):
                  continue
                high_num=entry.split()[1]
                high_new=float(ap_dict['high'])*float(ap_scaling) 
                #print(entry) 
                #print(entry.replace(high_num, str("%.3f" % round(high_new, 3)), 1))
                f2.write(entry.replace(high_num, str("%.3f" % round(high_new, 3)), 1))
                continue
             if entry.startswith('\t\txmin'):
                xmin_num=entry.split()[1]
                xmin_new=float(ap_dict['xmin'])*float(ap_scaling) 
                #print(entry) 
                #print(entry.replace(xmin_num, str("%.3f" % round(xmin_new, 3)), 1))
                f2.write(entry.replace(xmin_num, str("%.3f" % round(xmin_new, 3)), 1))
                continue
             if entry.startswith('\t\txmax'):
                #print(entry)
                xmax_num=entry.split()[1]
                xmax_new=float(ap_dict['xmax'])*float(ap_scaling) 
                #print(entry) 
                #print(entry.replace(xmax_num, str("%.3f" % round(xmax_new, 3)), 1))
                f2.write(entry.replace(xmax_num, str("%.3f" % round(xmax_new, 3)), 1))
                continue
             if entry.startswith('\t\tsample'):
                sample=entry.split()[1].split(':')

                ll_bkg=float(ap_dict['ll_bkg'])
                lu_bkg=float(ap_dict['lu_bkg'])
                rl_bkg=float(ap_dict['rl_bkg'])
                ru_bkg=float(ap_dict['ru_bkg'])
                
                ll_bkg_new=float(ap_dict['ll_bkg'])*float(ap_scaling) 
                lu_bkg_new=float(ap_dict['lu_bkg'])*float(ap_scaling) 
                rl_bkg_new=float(ap_dict['rl_bkg'])*float(ap_scaling) 
                ru_bkg_new=float(ap_dict['ru_bkg'])*float(ap_scaling) 
                #print('###########################')
                #print(ap_scaling)
                #print(ll_bkg,lu_bkg,rl_bkg,ru_bkg)
                #print(ll_bkg_new,lu_bkg_new,rl_bkg_new,ru_bkg_new)
                #print('entry:',entry)
                #print('sample       %.3f:%.3f,%.3f:%.3f'%(round(ll_bkg_new, 3),round(lu_bkg_new, 3),round(rl_bkg_new, 3),round(ru_bkg_new, 3)))
                #print('###########################')
                entry='     sample %.3f:%.3f,%.3f:%.3f\n'%(round(ll_bkg_new, 3),round(lu_bkg_new, 3),round(rl_bkg_new, 3),round(ru_bkg_new, 3))
                #entry=entry.replace(ll_bkg+':', str("%.3f:" % round(ll_bkg_new, 3)), 1)
                #entry=entry.replace(lu_bkg+',', str("%.3f," % round(lu_bkg_new, 3)), 1)
                #entry=entry.replace(rl_bkg+':', str("%.3f:" % round(rl_bkg_new, 3)), 1)
                #entry=entry.replace(':'+ru_bkg, str(":%.3f" % round(ru_bkg_new, 3)), 1)

                f2.write(entry)
                continue
             else:
              f2.write(rows[r])
       f2.close()
    
    
    os.system('cp -r '+file+'.temp '+file)
    os.system('rm '+file+'.temp')
   
    return(file)

def esi_split_order(arc=False):
    from astropy.io import fits, ascii
    import numpy as np
    import sys,glob,os,re
    
    # pixel selection for spectral axis along the slit
    scale_dict = {
        '1' : [900,3876], #bluest order, some second order light cut before
        '2' : [831,4095],
        '3' : [701,4095],
        '4' : [0,4095],
        '5' : [0,4095],
        '6' : [0,4095],
        '7' : [0,4095],
        '8' : [0,4095],
        '9' : [0,4095],
        '10': [0,3000] # best reddest sky line 2888, so dont want to take much beyond it
        #'10': [0,3340] # reddest order, ryans numbers
    }
    
    if arc==False:
     extracted_file_list=glob.glob('*_esi_echelle_1_ex.fits')

    if arc==True:
     extracted_file_list=glob.glob('ARC_blue.ms.fits') 
   
    
    if len(extracted_file_list)==1:
     print('splitting file: ',extracted_file_list[0])
     path, filename = os.path.split(extracted_file_list[0])
     filename = os.path.splitext(filename)[0]
    if len(extracted_file_list)==0:
       print('No file has been extracted to use')
    if len(extracted_file_list)>1:
       print('Too many extracted files in this directory')
    
    hdu=fits.open(extracted_file_list[0])
    print(hdu.info())
    
    sciext = 0
    h = hdu[sciext].header
    #print('Checking fits extensions..')
    for j,nh in enumerate(hdu): # iterate through extensions to find the data
       try:
          if len(nh.data) > 1 :
          #if len(fits[nh].data) > 1 :
            print('Using %sth fits extension'%(j))
            sciext = j
            break
       except:
          pass
    
    data=hdu[sciext].data
    print(np.shape(data))
    #print(np.shape(data)[1])

    if arc==False:

     if(np.shape(data)[1]!=10):
       print('You have not extracted all 10 orders!')
       print('Specify the orders you have extracted [to be added ]')
       sys.exit()
     for i,entry in enumerate(np.rollaxis(data, 1)):
       #print(i+1,scale_dict[str(i+1)])
       y1,y2=scale_dict[str(i+1)][0],scale_dict[str(i+1)][1]
       #print(np.shape(data[:,i,y1:y2]))
       print(filename)
       newfilename = '%s_order_%s_ex.fits' %(filename[:-3],str(i+1))
       newpath = os.path.join(path, newfilename)
       try:
        fits.writeto(newpath, data[:,i,y1:y2], h, overwrite=True) # need output_verify='ignore' otherwise astropy has bug with multi extension
       except OSError as e: # catches weird astropy error
        open(newpath, 'a').close()
        fits.writeto(newpath, data[:,i,y1:y2], h, overwrite=True) 

 

    if arc==True:

     if(np.shape(data)[0]!=10):
       print('Not all orders have been extracted! Please extract all 10 arc orders')
       sys.exit()

     for i,entry in enumerate(np.rollaxis(data, 0)):
       print(i+1,scale_dict[str(i+1)])
       y1,y2=scale_dict[str(i+1)][0],scale_dict[str(i+1)][1]
       #print(np.shape(data[:,i,y1:y2]))
       print(filename,(re.sub('.ms', '', filename)))
       newfilename = '%s_order_%s.ms.fits' %(re.sub('.ms', '', filename),str(i+1))
       newpath = os.path.join(path, newfilename)
       print(newpath)
       try:
        fits.writeto(newpath, data[i,y1:y2], h, overwrite=True) # need output_verify='ignore' otherwise astropy has bug with multi extension
       except OSError as e:
        open(newpath, 'a').close()
        fits.writeto(newpath, data[:,i,y1:y2], h, overwrite=True) # need output_verify='ignore' otherwise astropy has bug with multi extension

    if arc==False:
     #split_files=sorted(glob.glob('*_order_*.fits'))
     split_files=sorted(glob.glob('[!ARC_blue_ex]*ex_order_*.fits'),key=lambda x: int(x.split("order_")[1].split(".")[0])) # orders so 1 first 10 last (not second)

    if arc==True:
     #split_files=sorted(glob.glob('../*_order_*.fits'))
     names = [os.path.basename(x) for x in glob.glob('ARC_blue_order_*.ms.fits')]
     split_files=sorted(names,key=lambda x: int(x.split("order_")[1].split(".")[0])) # orders so 1 first 10 last (not second)

    return(split_files)




def extract_esi(img, dv, inst, _interactive, _type, automaticex=False, match_aperture = 'n',ref='',trce='yes',recenter='yes',back='fit',extract='yes'):
    # print "LOGX:: Entering `extractspectrum` method/function in
    # %(__file__)s" % globals()
    import glob
    import os
    import string
    import sys
    import re
    import datetime
    import numpy as np
    import util

    MJDtoday = 55927 + (datetime.date.today() - datetime.date(2012, 0o1, 0o1)).days
    from pyraf import iraf

    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.specred(_doprint=0)
    toforget = ['specred.apall', 'specred.transform']
    for t in toforget:
        iraf.unlearn(t)

    hdr = util.readhdr(img)
    iraf.specred.dispaxi = inst.get('dispaxis')

    imgex = re.sub('.fits', '_ex.fits', img)
    imgfast = re.sub(img.split('_')[-2] + '_', '', img)

    _reference = ref
    _extract= extract
    _fittrac = 'yes'
    _trace = trce
    _find = 'yes'
    _recenter = recenter
    _back=back
    _edit = 'yes'
    _resize='no'
    _review = 'no'
    _mode = 'q'

    _lower=dv[_type]['_lower']
    _upper=dv[_type]['_upper']

    _b_sample = dv[_type]['_b_sample']

    _minsep=130
    _maxsep=460

    # dv is from some other function....
    # dv = util.dvex()

    # Ryans params, dont work
    #_t_nsum=10      # Number of dispersion lines to be summed at each step along the dispersion.
    #_t_step=10      # Step along the dispersion axis between determination of the spectrum positions.
    _t_nlost = 20  # Number of consecutive steps in which the profile is lost before quitting the tracing in one direction. To force tracing to continue through regions of very low signal this parameter can be made large. Note, however, that noise may drag the trace away before it recovers.
    #_t_function="legendre" # t_function,s,h,"legendre",chebyshev|legendre|spline1|spline3,,"Trace fitting function"
    #_t_order=3 # Default trace function order. The order refers to the number of terms in the polynomial functions or the number of spline pieces in the spline functions.
    #_t_naverage=1 # Default number of points to average or median. Positive numbers average that number of sequential points to form a fitting point. Negative numbers median that number, in absolute value, of sequential points. A value of 1 does no averaging and each data point is used
    #_t_niterate=0 # Number of rejection iterations
    #_t_low_reject=2 # rejection sigma. Traced points deviating from the fit below and above the fit by more sigma of the residuals are rejected before refitting.
    #_t_high_reject=2 # rejection sigma. Traced points deviating from the fit below and above the fit by more sigma of the residuals are rejected before refitting.
    #_t_grow=0 # Traced points within a distance given by this parameter of any rejected point are also rejected.


    # Number of consecutive steps in which the profile is lost before quitting
    # the tracing in one direction.  To force tracing to continue through
    # regions of very low signal this parameter can be made large.  Note,
    # however, that noise may drag the trace away before it recovers.

    #print('trace ',_trace,'recenter ',_recenter,'back',_back,'interactive',_interactive,'extract',_extract,'fit order',dv[_type]['_b_order'])
    #print('t_step',dv[_type]['_t_step'],"t_nsum",dv[_type]['_t_nsum'],'t_sample',dv[_type]['_t_sample'])

    # nfind=10 minsep=_minsep,maxsep=_minsep,order='increasing' -> this doesnt pick up apertures in number order.. 1,4,6,8,10,12,14,16,18,20
    # 
    iraf.specred.apall(img, output=imgex, referen=_reference, trace=_trace, fittrac=_fittrac, find=_find,
                           recenter=_recenter, edit=_edit, order='increasing',
                           backgro=_back, lsigma=3, usigma=3, b_order=dv[_type]['_b_order'], b_function='chebyshev', b_sample=_b_sample,
                           format='multispec', extras='yes',
                           clean='yes', pfit='fit1d',
                           lower=_lower, upper=_upper,
                           width=dv[_type]['_width'],
                           radius=dv[_type]['_radius'], 
                           line=inst.get('approx_extract_column','INDEF'), nsum=dv[_type]['_nsum'], 
                           t_step=dv[_type]['_t_step'],
                           t_nsum=dv[_type]['_t_nsum'],
                           t_nlost=_t_nlost, t_sample=dv[
                               _type]['_t_sample'], resize=_resize,
                           t_order=dv[_type]['_t_order'],
                           weights=dv[_type]['_weights'], 
                           #t_function=_t_function,t_order=_t_order,t_naverage=_t_naverage,
                           #t_niterate=_t_niterate,t_low_reject=_t_low_reject,t_high_reject=_t_high_reject,t_grow=_t_grow,
                           interactive=_interactive, review=_review, mode=_mode,extract=_extract)

    

    return imgex


def extract_esi_arc(img, dv, inst,ref=''):
    # print "LOGX:: Entering `extractspectrum` method/function in
    # %(__file__)s" % globals()
    import glob
    import os
    import string
    import sys
    import re
    import datetime
    import numpy as np
    import util

    MJDtoday = 55927 + (datetime.date.today() - datetime.date(2012, 0o1, 0o1)).days
    from pyraf import iraf

    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.specred(_doprint=0)
    toforget = ['specred.apall', 'specred.transform']
    for t in toforget:
        iraf.unlearn(t)

    hdr = util.readhdr(img)
    iraf.specred.dispaxi = inst.get('dispaxis')

    _reference = ref

    arc_ex = re.sub('.fits', '.ms.fits', img)

    iraf.specred.apall(img,
                       output=arc_ex,
                       references =_reference,
                       line = 'INDEF',
                       # nsum=10,
                       interactive='no',
                       extract='yes',
                       find='no',
                       format='multispec',
                       trace='no',
                       back='no',
                       recen='no',
                       resize='yes',
                       edit='yes')

    

    return arc_ex

def extract_esi_flat(img, dv, inst,ref=''):
    # print "LOGX:: Entering `extractspectrum` method/function in
    # %(__file__)s" % globals()
    import glob
    import os
    import string
    import sys
    import re
    import datetime
    import numpy as np
    import util

    MJDtoday = 55927 + (datetime.date.today() - datetime.date(2012, 0o1, 0o1)).days
    from pyraf import iraf

    iraf.noao(_doprint=0)
    iraf.imred(_doprint=0)
    iraf.specred(_doprint=0)
    
    toforget = ['specred.apall', 'specred.transform','specred.apnorm1']
    for t in toforget:
        iraf.unlearn(t)

    hdr = util.readhdr(img)
    iraf.specred.dispaxi = inst.get('dispaxis')

    _reference = ref

    flat_ex = re.sub('.fits', '_norm.fits', img)
     
    # https://iraf.net/forum/viewtopic.php?showtopic=1461805 issue with apnorm1 vs apnormalize 
    iraf.specred.apnorm1.background = ")apnormalize.background"
    iraf.specred.apnorm1.skybox = ")apnormalize.skybox"
    iraf.specred.apnorm1.weights = ")apnormalize.weights"
    iraf.specred.apnorm1.pfit = ")apnormalize.pfit"
    iraf.specred.apnorm1.clean = ")apnormalize.clean"
    iraf.specred.apnorm1.saturation = ")apnormalize.saturation"
    iraf.specred.apnorm1.readnoise = ")apnormalize.readnoise"
    iraf.specred.apnorm1.gain = ")apnormalize.gain"
    iraf.specred.apnorm1.lsigma = ")apnormalize.lsigma"
    iraf.specred.apnorm1.usigma = ")apnormalize.usigma"

    #print(img) 
    #print(flat_ex)
    #print(_reference)
    iraf.specred.apnormalize(img,
                             output=flat_ex,
                             interactive = 'yes',
                             line=2500,
                             trace = 'no',
                             order=40,
                             recen='no',
                             resize='yes',
                             references = _reference) # Normalize 2D apertures by 1D functions

    return flat_ex



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
    import shutil
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
    iraf.disp(inlist='1', reference='1',linear='1')

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

    for arcs in files_arc:
        print(arcs)
        hdr = util.readhdr(arcs)

    for imgs in imglist:
        #print(imgs)
        br, inst = instruments.blue_or_red(imgs)
        hdr = util.readhdr(imgs)

        iraf.specred.dispaxi = inst.get('dispaxis')
        iraf.longslit.dispaxi = inst.get('dispaxis')

        _gain = inst.get('gain')
        _ron = inst.get('read_noise')
        iraf.specred.apall.readnoi = _ron
        iraf.specred.apall.gain = _gain

        #print (os.getcwd().split('/')[-1])
        _object0 = os.getcwd().split('/')[-1]
        _date0 = util.readkey3(hdr, 'DATE-OBS')
        _object0 = re.sub(' ', '', _object0)
        _object0 = re.sub('/', '_', _object0)

        if _rename:
            try:
                _object0 = raw_input('New object name ' + '['+_object0+']: ') or _object0
            except:
                _object0 = input('New object name ' + '['+_object0+']: ') or _object0       

        nameout0 = str(_object0) + '_' + inst.get('name')
        nameout0 = util.name_duplicate(imgs, nameout0, '')
        print ('NAMEOUT:', nameout0)
        timg = nameout0

        print('\n### now processing :',timg,' for -> ',inst.get('name'))
        if os.path.isfile(timg) and not _ex:
            util.delete(timg)
        print ('IMAGES: ', imgs)

        if not _ex:
            if os.path.isfile(timg):
                util.delete(timg)

        if len(imglist) > 1 and _crnew:

                print('removing cosmics and combining with new sigma clipping')
                cr.cr_reject(imglist, timg, inst, lim=0.145)

        if _cosmic and _crnew==None:
                img_str=''
                for i,entry in enumerate(imglist):
                    files = glob.glob('*.fits')
                    if 'cosmic_{}'.format(entry) not in glob.glob('*.fits'):
                        br = instruments.blue_or_red(entry)[0]
                        print('removing cosmics with pyzap')

                        outimg,outmask,header = pyzapspec.pyzapspec(entry,
                                               outfile='cosmic_{}'.format(entry),
                                               WRITE_OUTFILE = True,
                                               br = br,
                                               img_num=i+1, redshift=None,
                                               cedit=_cedit, DEBUG=False,
                                               boxsize=inst.get('pyzap_boxsize',20),
                                               nsigma=inst.get('pyzap_nsigma',2),
                                               subsigma=inst.get('pyzap_subsigma',.5))
                    img = 'cosmic_{}'.format(entry)
                    img_str = img_str + img + ','

                if len(imglist) > 1:
                 iraf.imcombine(img_str, combine='average', weight='exposure', output=timg)
                
                if len(imglist) == 1: # 1 image, cr rejection
                 iraf.imcopy(img_str, output=timg)
        else:
            print('Not removing cosmics') # 1 image, no cr rejection
            iraf.imcopy(imglist[0], output=timg)


    wave_sol_file_path=sorted(glob.glob(inst.get('archive_arc_extracted_id')))
    print(timg)

    # 

    try:
        trace_standard = raw_input('Extract standard star for flat-field trace, and to wavelength calibrate? y/[n]: ') or 'n'
    except:
        trace_standard = input('Extract standard star for flat-field trace, and to wavelength calibrate? y/[n]: ') or 'n'

    if trace_standard!= 'n': # if you want to start reductions, extract are and trace

     flat_file = '../toFlat_blue.fits'
     flat_file_norm = '../toFlat_blue_norm.fits'

     if not _nflat: # if you want to flat field  
      print('Flat fielding')
      #print(os.path.isfile(flat_file_norm))

      if os.path.isfile(flat_file_norm):
        print('Normalized flat already exists, extracting standard')

        imgex = extract_esi(timg, dv, inst, _interactive, 'obj',extract='no') # this runs apall for getting trace and ap centers
        ref_ap_name=esi_fix_ap() # rescales aperture file to make same spatial scale
     

      if not os.path.isfile(flat_file_norm):
       
       # extract standard and scale apertures
       imgex = extract_esi(timg, dv, inst, _interactive, 'obj',extract='no') # this runs apall for getting trace and ap centers
       ref_ap_name=esi_fix_ap() # rescales aperture file to make same spatial scale
     
       print('\n### Normalising flat ...')
       # Extract arc and split orders  
       print(os.path.basename(flat_file))
       flat_ex=extract_esi_flat(flat_file, dv, inst,ref=timg)

      if os.path.isfile(flat_file_norm): # if norm flat exists, try this
        try:
         hdr['FF-FLAG'] 
        except KeyError as e:
         print('\n### Applying flat field correction to ...',timg)
         iraf.ccdproc(timg,output='',
                        overscan='no',
                        trim='no',
                        zerocor="no",
                        flatcor="yes",
                        readaxi='line',
                        flat=flat_file_norm,
                        Stdout=1)

     else: 
        print('not flat fielding data')
        # extract standard and scale apertures
        imgex = extract_esi(timg, dv, inst, _interactive, 'obj',extract='no') # this runs apall for getting trace and ap centers
        ref_ap_name=esi_fix_ap() # rescales aperture file to make same spatial scale
     
     ##################################################################
     print('\n### Extracting standard with scaled reference apertures')

     if os.path.exists(imgex): 
        print('Extracted standard already exists')

        try:
            remove_ex = raw_input('Do you want to re-extract standard y/[n]: ') or 'n'
        except:
            remove_ex = input('Do you want to re-extract standard y/[n]: ') or 'n'

        if remove_ex =='n':
            obj_ap_names=esi_split_order(arc=False) # split extracted orders into files and cut the yaxis to remove some edges where trace falls off 
   
            split_ap_names=sorted(glob.glob('*_order_*.fits'))

        if remove_ex !='n':
            imgex2 = extract_esi(timg, dv, inst, _interactive, 'obj',ref=timg,trce='no',recenter='no') # runs apall again with the scaled apertures

            obj_ap_names=esi_split_order(arc=False) # split extracted orders into files and cut the yaxis to remove some edges where trace falls off 
   
            split_ap_names=sorted(glob.glob('*_order_*.fits'))

     if not os.path.exists(imgex):
        imgex2 = extract_esi(timg, dv, inst, _interactive, 'obj',ref=timg,trce='no',recenter='no') # runs apall again with the scaled apertures

        obj_ap_names=esi_split_order(arc=False) # split extracted orders into files and cut the yaxis to remove some edges where trace falls off 

        split_ap_names=sorted(glob.glob('*_order_*.fits'))


     ##################################################################
     print('\n### Extracting arc with standard star scaled reference apertures')
 
     if not os.path.isdir('../master_files/'):
            os.mkdir('../master_files/')

     if _arc_identify:

        #There is a bug in identify when the path to the coordlist is too long
        #This is my hacky workaround for now, the file  is deleted later        
        os.system('cp ' + inst.get('line_list') + ' .')
        line_list = inst.get('line_list').split('/')[-1]

        for arcfile in files_arc: # copy master arc file to object directory
          print('cp -r '+ arcfile + ' .')
          os.system('cp -r '+ arcfile + ' .') 

        if os.path.isfile(re.sub('.fits', '.ms.fits', os.path.basename(arcfile))): 
            os.remove(re.sub('.fits', '.ms.fits', os.path.basename(arcfile)))
 
        masters = [os.path.basename(x) for x in glob.glob('../master_files/*')] # grab all existing master files
        names = [os.path.basename(x) for x in glob.glob('database/id*order*.ms')] # get the arc names from the database
        wave_sol_files=sorted(names,key=lambda x: int(x.split("idARC_blue_order_")[1].split(".")[0])) # all arc names we need

        #print(wave_sol_files)
        #print(masters) # all master files
        #print(wave_sol_file_path) # all wavelength files 

        if wave_sol_file_path[0] in masters:
            print(wave_sol_file_path[0])
            print(wave_sol_file_path)
            print('wavelength solution exists, copying those files')
        else:
            print('no wavelength solution exists, doing wavelength solution')

     #if wave_sol_file in masters:
     # wave_sol_file_path is copied from cals eg. (spectral_reduction/trunk/ESI_cals/idARC_blue_order_xxx.ms)
     # for wave_sol in wave_sol_file_path:       # this is where archival arcs are copied
     #   print('cp -r '+wave_sol+' database')
     #   os.system('cp -r '+wave_sol+' database')     

     # Extract arc and split orders
     arc_ex = extract_esi_arc(os.path.basename(arcfile), dv, inst,ref=timg)
     #print(arc_ex)
     arc_ex_names=esi_split_order(arc=True)

     if len(arc_ex_names)!=10:
        print('You have not extracted all orders. Leftmost is 1, rightmost is 10')
        print('For wavelength calibration of standard, go back and make sure to extract all 10 orders')
        sys.exit()

     if len(arc_ex_names)==10: # if you extracted all orders
        if os.path.exists(timg):
            tmp_files = [re.sub('.fits', '', timg)+'_order_'+str(i+1)+'.fits' for i in range(10)] # copy files, so force iraf dispcor to work
            copy_tmp_files=[os.system('cp ' + timg +' '+ file) for file in tmp_files]
        
        for i, entry in enumerate(arc_ex_names): 
                iraf.longslit.identify(images=entry,
                coordli=line_list,
                function = 'legendre',
                order=3,
                mode='h')
        #try:
        # identify_arcs = raw_input('Identify all orders for wavelength solution [y]/[n]: ') or 'y'
        #except:
        # identify_arcs = input('Identify all orders for wavelength solution [y]/[n]: ') or 'y'
        
        #if identify_arcs=='y'
        # for i, entry in enumerate(arc_ex_names): 
        #        iraf.longslit.identify(images=entry,
        #        coordli=line_list,
        #        function = 'legendre',
        #        order=3,
        #        mode='h')
        #if identify_arcs=='n':
        # try:
        #  identify_order = raw_input('Which order do you want to extract [1]: ') or '1'
        # except:
        #  identify_order = input('Which order do you want to extract [1]: ') or '1'
            
        # for i, entry in enumerate(arc_ex_names): 
        #    if entry=='ARC_blue_order_'+identify_order+'.ms.fits':
        #        iraf.longslit.identify(images=entry,
        #        coordli=line_list,
        #        function = 'legendre',
        #        order=3,
        #        mode='h')

        #for i, entry in enumerate(arc_ex_names): 
        #    if entry=='ARC_blue_order_'+identify_order+'.ms.fits':
        #        iraf.longslit.identify(images=entry,
        #        coordli=line_list,
        #        function = 'legendre',
        #        order=3,
        #        mode='h')


     
        util.delete(line_list)

        # copy wavelength solutions in the database folder to master files
        # copy the extracted arcs used for the ws to the master files folder
        names = [os.path.basename(x) for x in glob.glob('database/id*order*.ms')] # get the arc names from the database
        wave_sol_files=sorted(names,key=lambda x: int(x.split("idARC_blue_order_")[1].split(".")[0])) # all arc names we need

        for file in wave_sol_files:
            os.system('cp ' + 'database/' + file + ' ../master_files/')

        for file in arc_ex_names:
            os.system('cp ' + file + ' ../master_files/')


        print('\n### applying wavelength solutions')

        imgex=sorted(glob.glob('[!ARC_blue_ex]*_order_*_ex.fits'),key=lambda x: int(x.split("order_")[1].split("_ex.")[0])) # keep this temporarily while testing! # keep this temporarily while testing!

        for i, entry in enumerate(arc_ex_names):
            print(imgex[i],entry) 
            iraf.disp(inlist=imgex[i], reference=entry,linear=0) # apply wavelength solution

        #######################################

        if not os.path.isdir(_object0 + '_ex/'):
            os.mkdir(_object0 + '_ex/')

        util.delete('logfile')
        
        #print(arc_ex,imgex)
        #print('mv ' + 'd'+ imgex[0] + ' ' + _object0 + '_ex/')

        move_files=[os.system('mv ' + 'd'+ file + ' ' + _object0 + '_ex/') for file in imgex]

        scale_dict = {
         '1' : [900,3876], #bluest order
         '2' : [831,4095],
         '3' : [701,4095],
         '4' : [0,4095],
         '5' : [0,4095],
         '6' : [0,4095],
         '7' : [0,4095],
         '8' : [0,4095],
         '9' : [0,4095],
         '10': [0,3900] 
        #'10': [0,3340] #reddest order
                      }
    if trace_standard== 'n':
        try:
          extract_object = raw_input('Extract science object [y]/n: ') or 'y'
        except:
          extract_object = input('Extract science object [y]/n: ') or 'y'

        if extract_object=='y':
     

            flat_file = '../toFlat_blue.fits'
            flat_file_norm = '../toFlat_blue_norm.fits'

            if os.path.isfile(flat_file_norm): # if normalised flat exists, apply ff correction
                try:
                   hdr['FF-FLAG'] 
                except KeyError as e:
                 print('\n### Applying flat field correction to ...',timg)
                 iraf.ccdproc(timg,output='',
                        overscan='no',
                        trim='no',
                        zerocor="no",
                        flatcor="yes",
                        readaxi='line',
                        flat=flat_file_norm,
                        Stdout=1)

            # extract object and scale apertures to correct spatial scale
            imgex = extract_esi(timg, dv, inst, _interactive, 'obj',extract='no') # this runs apall for getting trace and ap centers
            ref_ap_name=esi_fix_ap() # rescales aperture file to make same spatial scale

            # extract object with correct apertures
            imgex2 = extract_esi(timg, dv, inst, _interactive, 'obj',ref=timg,trce='no',recenter='no') # runs apall again with the scaled apertures
            obj_ap_names=esi_split_order(arc=False) # split extracted orders into files and cut the yaxis to remove some edges where trace falls off 
            split_ap_names=sorted(glob.glob('*_order_*.fits'))




            names = [os.path.basename(x) for x in glob.glob('../master_files/id*order*.ms')] # get the arc names from the masters

            if len(names)==0:
                #import pdb;pdb.set_trace()

                try:
                    make_wsol = raw_input('Use master wavelength calibration? [y]/n ')
                except:
                    make_wsol = input('Use master wavelength calibration? [y]/n ')
                
                if make_wsol!='y':
                    print('Using archival wavelength solution - you have been warned ;)')
                    arc_extracted = inst.get('archive_arc_extracted')
                    #os.system('cp ' + arc_extracted + ' ' + _object0)
                    os.system('cp ' + arc_extracted + ' .')
                    arc_extracted_id = inst.get('archive_arc_extracted_id')
                    #os.system('cp ' + arc_extracted_idn + ' ' + _object0)
                    #os.system('cp ' + arc_extracted_id + ' .')
                    os.system('cp ' + arc_extracted_id + ' ./database')
                    arc_ex_files = [os.path.basename(x) for x in glob.glob(arc_extracted)]
                    arc_ex_names=sorted(arc_ex_files,key=lambda x: int(x.split("order_")[1].split(".")[0])) # orders so 1 first 10 last (not second)
            if len(names)!=0:
                wave_sol_files=sorted(names,key=lambda x: int(x.split("idARC_blue_order_")[1].split(".")[0])) # sort arc .ms files
                arc_ex_files = [os.path.basename(x) for x in glob.glob('../master_files/ARC_blue_order_*.ms.fits')]
                arc_ex_names=sorted(arc_ex_files,key=lambda x: int(x.split("order_")[1].split(".")[0])) # orders so 1 first 10 last (not second)
    
                #print(names)
                #print(wave_sol_files)
    
                for file in wave_sol_files:
                 os.system('cp ' + '../master_files/' + file + ' database/')
    
                for file in arc_ex_names:
                 os.system('cp ' + '../master_files/' + file + '  .')
            
            imgex=sorted(glob.glob('[!ARC_blue_ex]*_order_*_ex.fits'),key=lambda x: int(x.split("order_")[1].split("_ex.")[0])) # keep this temporarily while testing! # keep this temporarily while testing!
            
            arc_ex_names=sorted(arc_ex_names,key=lambda x: int(x.split("order_")[1].split(".ms")[0]))

            print('\n### applying wavelength solutions')
            for i, entry in enumerate(arc_ex_names):
                print(imgex[i],entry)
                iraf.disp(inlist=imgex[i], reference=entry,linear=0) # apply wavelength solution

            if not os.path.isdir(_object0 + '_ex/'):
                os.mkdir(_object0 + '_ex/')
    
            util.delete('logfile')
                
            move_files=[os.system('mv ' + 'd'+ file + ' ' + _object0 + '_ex/') for file in imgex] # move extracted files to _ex directory

            try:
                use_master = raw_input('Use master flux calibration? [y]/n ')
            except:
                use_master = input('Use master flux calibration? [y]/n ')
            if use_master != 'n':
                os.system('cp ' + '../master_files/fluxstarorder*.fits ' + _object0 + '_ex/')
                os.system('cp ' + '../master_files/bstarorder*.fits ' + _object0 + '_ex/')
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






    ##############################################



    result=1    
    return result


