from __future__    import print_function
import os
import util
import datetime
from astropy.io import fits, ascii

path_to_trunk = os.path.expandvars('$UCSC_SPECPIPE/spectral_reduction/trunk/')
if not os.path.exists(path_to_trunk):
    raise RuntimeError('Error : $UCSC_SPECPIPE variable is undefined or incorrect!')

kast_blue = {'name': 'kast_blue',
             'arm': 'blue',
             'read_noise': 3.7,
             'gain': 1.2,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1,
             'biassec': '[1:2048,318:350]', #matt: this doesn't matter
             # 'trimsec': '[50:2010,7:287]',
             # 'trimsec': '[80:1850,7:287]',
             # 'flatsec': '[80:1850,50:287]',
             # 'trimsec': '[80:1850,40:330]', #8-31-19 good
             # 'flatsec': '[80:1850,80:330]', #8-31-19 good
             # 'trimsec': '[80:1850,20:300]', #3-31-21 ToO
             # 'flatsec': '[80:1850,20:300]', #3-31-21 ToO
             # 'trimsec': '[80:1650,20:300]', #4-2-17
             # 'flatsec': '[80:1650,20:300]', #4-2-17 
             # 'trimsec': '[80:1850,20:300]', #3-21-21
             # 'flatsec': '[80:1850,20:300]', #3-21-21
             'trimsec': '[80:1850,30:300]', #Kirsty 5-30-22
             'flatsec': '[80:1850,30:300]', #Kirsty 5-30-22
             # 'trimsec': '[26:1976,22:302]', # temporary
             'archive_zero_file': path_to_trunk + 'KAST_cals/Zero_blue_20180206.fits',
             'archive_flat_file': path_to_trunk + 'KAST_cals/RESP_blue.fits',
             'archive_sens': path_to_trunk + 'KAST_cals/fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'KAST_cals/bstarblue.fits',
             # 'archive_arc_extracted': path_to_trunk + 'KAST_cals/Blue_Arc_Ref.ms.fits',
             'archive_arc': path_to_trunk + 'KAST_cals/ARC_blue.fits',
             'archive_arc_extracted_id': path_to_trunk + 'KAST_cals/idARC_blue.ms',
             # 'archive_arc_aperture': path_to_trunk + 'KAST_cals/apBlue_Arc_Ref',
             'line_list': path_to_trunk+'KAST_cals/lines.dat',
             'extinction_file': path_to_trunk + 'KAST_cals/lick_extinction.dat',
             'observatory': 'lick',
             'sky_file': path_to_trunk + 'KAST_cals/licksky.fits',
             'section': 'middle line',
             'pyzap_boxsize': 5, # approximate seeing in pixels
             'pyzap_nsigma': 16,
             'pyzap_subsigma': 2.8,
             'approx_extract_line': 145,
             'approx_extract_column': 1000,
             'pixel_scale': .43, #arcsec/pix
             'spatial_binning': 1.,
             'flat_regions': [[0,300]],
             'flat_good_region': [1200, 1300]
             }


kast_red = { 'name': 'kast_red',
             'arm': 'red',
             'read_noise': 3.8,
             'gain': 1.9,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 2, 
             'biassec': '[360:405,1:2725]',
             # 'biassec': '[380:400,70:2296]',#3-31-21 ToO
             # 'trimsec': '[66:346,80:2296]',
             # 'flatsec': '[110:346,80:2296]',
             # 'trimsec': '[110:370,80:2296]', #8-31-19
             # 'flatsec': '[110:370,80:2296]', #8-31-19
             # 'trimsec': '[110:370,80:2560]', #2020oi ToO
             # 'flatsec': '[110:370,80:2560]', #2020oi ToO
             # 'trimsec': '[75:365,70:2296]', #3-31-21 ToO
             # 'flatsec': '[75:365,70:2296]', #3-31-21 ToO
             # 'trimsec': '[75:365,70:2296]', #Correct for newer data
             # 'flatsec': '[75:365,70:2296]', #Correct for newer data
             # 'trimsec': '[75:340,350:2296]', #4-2-17
             # 'flatsec': '[75:340,350:2296]', #4-2-17
             # 'trimsec': '[30:320,80:2120]', #12-04-20
             # 'flatsec': '[110:330,80:2120]', #12-04-20
             # 'trimsec': '[60:350,70:2296]', #2-7-18
             # 'flatsec': '[60:350,70:2296]', #2-7-18
             'trimsec': '[75:365,70:2296]', #Kirsty 5-30-22
             'flatsec': '[75:365,70:2296]', #Kirsty 5-30-22

             'archive_zero_file': path_to_trunk + 'KAST_cals/Zero_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'KAST_cals/RESP_red.fits',
             'archive_sens': path_to_trunk + 'KAST_cals/fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'KAST_cals/bstarred.fits',
             # 'archive_arc_extracted': path_to_trunk + 'KAST_cals/Red_Arc_Ref.ms.fits',
             'archive_arc': path_to_trunk + 'KAST_cals/ARC_red.fits',
             'archive_arc_extracted_id': path_to_trunk + 'KAST_cals/idARC_red.ms',
             # 'archive_arc_aperture': path_to_trunk + 'KAST_cals/apRed_Arc_Ref',
             'line_list': path_to_trunk+'KAST_cals/lines.dat',
             'extinction_file': path_to_trunk + 'KAST_cals/lick_extinction.dat',
             'observatory': 'lick',
             'sky_file': path_to_trunk + 'KAST_cals/licksky.fits',
             'section': 'middle column',
             'pyzap_boxsize': 5,
             'pyzap_nsigma': 16,
             'pyzap_subsigma': 2.8,
             'approx_extract_line': 150,
             'approx_extract_column': 1000,
             'pixel_scale': .43, #arcsec/pix
             'spatial_binning': 1.,
             'flat_regions': [[0,300],[850,950],[1500,1750],[-400,-1]],
             'flat_good_region': [1200, 1300]
             }

lris_blue = {'name': 'lris_blue',
             'arm': 'blue',
             'read_noise': 3.7,
             # 'gain': 1.5,
             'gain': 1., #gain already applied in processing phase
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1,
             'archive_flat_file': path_to_trunk + 'LRIS_cals/RESP_blue.fits',
             'archive_sens': path_to_trunk + 'LRIS_cals/fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'LRIS_cals/bstarblue.fits',
             'archive_arc': path_to_trunk + 'LRIS_cals/ARC_blue.fits',
             'archive_arc_extracted': path_to_trunk + 'LRIS_cals/LRIS_Blue_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'LRIS_cals/idARC_blue.ms',
             'archive_arc_aperture': path_to_trunk + 'LRIS_cals/apLRIS_Blue_Arc_Ref',
             # 'line_list': path_to_trunk+'LRIS_cals/lines.dat', #this nearly hits pathname length limits
             'line_list': path_to_trunk+'LRIS_cals/lines.dat', #this nearly hits pathname length limits
             'extinction_file': path_to_trunk + 'LRIS_cals/lick_extinction.dat', # JB: need to fix
             'observatory': 'keck',
             'sky_file': path_to_trunk + 'LRIS_cals/kecksky.fits',
             'section': 'middle line',
             'pyzap_boxsize': 5,
             'pyzap_nsigma': 16,
             'pyzap_subsigma': 8,
             # 'approx_extract_line': 740, jon old
             'approx_extract_line': 200,
             'pixel_scale': .135, #arcsec/pix
             'spatial_binning': 1.,
             'flat_regions': [[0,1700]],
             'flat_good_region': [2500, 2700], 
             'flat_match_region': [2000,2200]
             }
             
lris_red = { 'name': 'lris_red',
             'arm': 'red',
             'read_noise': 4.7,
             # 'gain': 1.2,
             'gain': 1., #gain already applied in processing phase
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1,
             # 'dispaxis': 2, 
             'archive_flat_file': path_to_trunk + 'LRIS_cals/RESP_red.fits',
             'archive_sens': path_to_trunk + 'LRIS_cals/fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'LRIS_cals/bstarred.fits',
             'archive_arc': path_to_trunk + 'LRIS_cals/ARC_red.fits',
             'archive_arc_extracted': path_to_trunk + 'LRIS_cals/LRIS_Red_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'LRIS_cals/idARC_red.ms',
             'archive_arc_aperture': path_to_trunk + 'LRIS_cals/apLRIS_Red_Arc_Ref',
             # 'line_list': path_to_trunk+'LRIS_cals/lines.dat', #this nearly hits pathname length limits
             'line_list': path_to_trunk+'LRIS_cals/lines_lpipe.dat', #this nearly hits pathname length limits
             'extinction_file': path_to_trunk + 'LRIS_cals/lick_extinction.dat', # JB: need to fix
             'observatory': 'keck',
             'sky_file': path_to_trunk + 'LRIS_cals/kecksky.fits',
             'section': 'middle line',
             'pyzap_boxsize': 5,#21
             'pyzap_nsigma': 16,#5
             'pyzap_subsigma': 8,#2
             'approx_extract_line': 350,
             'pixel_scale': .135, #arcsec/pix
             'spatial_binning': 2.,
             'flat_regions': [[0,300],[1850,2000],[3250,3700]],
             'flat_good_region': [2500, 2700],
             'flat_match_region': [3300,3500]
             }

lris_red_new = { 'name': 'lris_red_new',
             'arm': 'red',
             'read_noise': 4.7,
             # 'gain': 1.2,
             'gain': 1., #gain already applied in processing phase
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             # 'dispaxis': 1,
             'dispaxis': 2, 
             'archive_flat_file': path_to_trunk + 'LRIS_cals/RESP_red.fits',
             'archive_sens': path_to_trunk + 'LRIS_cals/fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'LRIS_cals/bstarred.fits',
             'archive_arc': path_to_trunk + 'LRIS_cals/ARC_red.fits',
             'archive_arc_extracted': path_to_trunk + 'LRIS_cals/LRIS_Red_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'LRIS_cals/idARC_red.ms',
             'archive_arc_aperture': path_to_trunk + 'LRIS_cals/apLRIS_Red_Arc_Ref',
             # 'line_list': path_to_trunk+'LRIS_cals/lines.dat', #this nearly hits pathname length limits
             'line_list': path_to_trunk+'LRIS_cals/lines_lpipe.dat', #this nearly hits pathname length limits
             'extinction_file': path_to_trunk + 'LRIS_cals/lick_extinction.dat', # JB: need to fix
             'observatory': 'keck',
             'sky_file': path_to_trunk + 'LRIS_cals/kecksky.fits',
             'section': 'middle line',
             'pyzap_boxsize': 21,
             'pyzap_nsigma': 5,
             'pyzap_subsigma': 2,
             'approx_extract_line': 350,
             'pixel_scale': .135, #arcsec/pix
             'spatial_binning': 2.,
             'flat_regions': [[0,300],[1850,2000],[3250,3700]],
             'flat_good_region': [2500, 2700],
             'flat_match_region': [3300,3500]
             }
             
goodman_m1={ 'name': 'goodman_blue',
             'arm': 'blue',
             'read_noise': 3.99,
             'gain': 2.06,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1, 
             'biassec': '[1:25,100:800]', # RED CAMERA
             # 'trimsec': '[400:2068,84:900]', # RED CAMERA
             # 'biassec': '[2060:2070,100:800]', # BLUE CAMERA
             # 'trimsec': '[80:2025,65:775]', # BLUE CAMERA 
             'trimsec': '[400:2025,65:775]', # BLUE CAMERA (cuts out flat field artifact)
             # 'trimsec': '[400:2068,84:900]',
             'archive_zero_file': path_to_trunk + 'SOAR_cals/Zero_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'SOAR_cals/RESP_blue.fits',
             'archive_sens': path_to_trunk + 'SOAR_cals/fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'SOAR_cals/bstarblue.fits',
             'archive_arc_extracted': path_to_trunk + 'SOAR_cals/m1_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'SOAR_cals/id/idm1_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'SOAR_cals/apm1_Arc_Ref',
             'apline': 'INDEF',
             'line_list': path_to_trunk+'SOAR_cals/lines.dat',
             'extinction_file': path_to_trunk + 'lick_extinction.dat', # JB: need to fix
             'observatory': 'soar',
             'sky_file': path_to_trunk + 'licksky.fits', # JB: need to fix
             'section': 'middle column',
             'pyzap_boxsize': 5,
             'pixel_scale': .15, #arcsec/pix
             'spatial_binning': 1.
             }
             
goodman_m2={ 'name': 'goodman_red',
             'arm': 'red',
             'read_noise': 3.99,
             'gain': 2.06,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1, 
             #'biassec': '[1:25,100:800]', # RED CAMERA
             #'trimsec': '[400:2068,84:900]', # RED CAMERA
             'biassec': '[2060:2070,100:800]', # BLUE CAMERA
             'trimsec': '[80:2025,65:775]', # BLUE CAMERA 
             'archive_zero_file': path_to_trunk + 'SOAR_cals/Zero_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'SOAR_cals/RESP_red.fits',
             'archive_sens': path_to_trunk + 'SOAR_cals/fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'SOAR_cals/bstarred.fits',
             'archive_arc_extracted': path_to_trunk + 'SOAR_cals/m2_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'SOAR_cals/id/idm2_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'SOAR_cals/apm2_Arc_Ref',
             'apline': 500,
             'line_list': path_to_trunk+'SOAR_cals/lines.dat',
             'extinction_file': path_to_trunk + 'SOAR_cals/lick_extinction.dat', # JB: need to fix
             'observatory': 'soar',
             'sky_file': path_to_trunk + 'SOAR_cals/licksky.fits', # JB: need to fix
             'section': 'middle column',
             'pyzap_boxsize': 5,
             'pixel_scale': .15, #arcsec/pix
             'spatial_binning': 1.
             }

def is_new_chip(red_img):
    hdr = fits.open(red_img)[0].header
    if 'T' in hdr.get('DATE-OBS'):
        ymd = hdr.get('DATE-OBS').split('T')[0]
        date_info = ymd.split('-')
    else:
        date_info = hdr.get('DATE-OBS').split('-')
    date = datetime.datetime(int(date_info[0]),int(date_info[1]),int(date_info[2]))
    chip_update = datetime.datetime(2021,4,15)
    if date > chip_update:
        new_chip = True
        print ('Using new chip params', new_chip)
    else:
        new_chip = False
    return new_chip

def blue_or_red(img):
    hdr = fits.open(img)[0].header
    # kast
    if util.readkey3(hdr, 'VERSION') == 'kastb':
        return 'blue', kast_blue
    elif util.readkey3(hdr, 'VERSION') == 'kastr':
        return 'red', kast_red
    # soar
    elif util.readkey3(hdr, 'WAVMODE') == '400_M1' or util.readkey3(hdr, 'WAVMODE') == '400 m1':
        return 'blue', goodman_m1
    elif util.readkey3(hdr, 'WAVMODE') == '400_M2' or util.readkey3(hdr, 'WAVMODE') == '400 m2':
        return 'red', goodman_m2
    # lris
    elif util.readkey3(hdr, 'INSTRUME') == 'LRISBLUE':
        return 'blue', lris_blue
    elif util.readkey3(hdr, 'INSTRUME') == 'LRIS' :
        if is_new_chip(img):
            return 'red', lris_red_new
        else:
            return 'red', lris_red
    else:
        print (img)
        print(util.readkey3(hdr, 'VERSION') + 'not in database')
        return None, None




        