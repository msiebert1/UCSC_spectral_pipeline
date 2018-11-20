from __future__    import print_function
import os
import util
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
             'biassec': '[1:2048,318:350]',
             'trimsec': '[50:2010,7:287]',
             # 'trimsec': '[30:2000,5:285]', YC
             'archive_zero_file': path_to_trunk + 'Zero_blue_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_blue_20180206.fits', THIS FLAT IS GARBAGE
             'archive_flat_file': path_to_trunk + 'RESP_blue.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_blue_20180206.fits',
             'archive_sens': path_to_trunk + 'fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'bstarblue.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbb1070.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbb1070.ms',
             'archive_arc_extracted': path_to_trunk + 'Blue_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'id/idBlue_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'apBlue_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'lines.dat',
             'extinction_file': path_to_trunk + 'lick_extinction.dat',
             'observatory': 'lick',
             'sky_file': path_to_trunk + 'licksky.fits',
             'section': 'middle line'}


kast_red = { 'name': 'kast_red',
             'arm': 'red',
             'read_noise': 3.8,
             'gain': 1.9,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 2, 
             'biassec': '[360:405,1:2725]',
             'trimsec': '[66:346,110:2500]',
             # 'trimsec': '[55:355,95:2500]', YC
             'archive_zero_file': path_to_trunk + 'Zero_red_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'RESP_red.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_red_20180206.fits',
             'archive_sens': path_to_trunk + 'fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'bstarred.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbr1103.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbr1103.ms',
             'archive_arc_extracted': path_to_trunk + 'Red_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'id/idRed_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'apRed_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'lines.dat',
             'extinction_file': path_to_trunk + 'lick_extinction.dat',
             'observatory': 'lick',
             'sky_file': path_to_trunk + 'licksky.fits',
             'section': 'middle column'}

lris_blue = {'name': 'lris_blue',
             'arm': 'blue',
             'read_noise': 3.7,
             'gain': 1.5,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1,
             'biassec': '[1:2048,318:350]',
             'trimsec': '[50:2010,7:287]',
             # 'trimsec': '[30:2000,5:285]', YC
             'archive_zero_file': path_to_trunk + 'Zero_blue_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_blue_20180206.fits', THIS FLAT IS GARBAGE
             'archive_flat_file': path_to_trunk + 'RESP_blue.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_blue_20180206.fits',
             'archive_sens': path_to_trunk + 'fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'bstarblue.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbb1070.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbb1070.ms',
             'archive_arc_extracted': path_to_trunk + 'LRIS_Blue_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'id/idLRIS_Blue_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'apLRIS_Blue_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'LRIS_lines.dat',
             'extinction_file': path_to_trunk + 'keck_extinction.dat',
             'observatory': 'keck',
             'sky_file': path_to_trunk + 'kecksky.fits',
             'section': 'middle line'}
             
lris_red = { 'name': 'lris_red',
             'arm': 'red',
             'read_noise': 4.7,
             'gain': 1.2,
             'biassec': '[360:405,1:2725]',
             'trimsec': '[66:346,110:2500]',
             # 'trimsec': '[55:355,95:2500]', YC
             'archive_zero_file': path_to_trunk + 'Zero_red_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'RESP_red.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_red_20180206.fits',
             'archive_sens': path_to_trunk + 'fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'bstarred.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbr1103.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbr1103.ms',
             'archive_arc_extracted': path_to_trunk + 'LRIS_Red_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'id/idLRIS_Red_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'apLRIS_Red_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'LRIS_lines.dat',
             'extinction_file': path_to_trunk + 'keck_extinction.dat',
             'observatory': 'keck',
             'sky_file': path_to_trunk + 'kecksky.fits',
             'section': 'middle column'}
             
goodman_m1={ 'name': 'goodman_blue',
             'arm': 'blue',
             'read_noise': 3.99,
             'gain': 2.06,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1, 
             # 'biassec': '[1:7,1:948]',
             'biassec': '[2058:2071,1:200]',
             # 'trimsec': '[380:2055,30:870]'
             'trimsec': '[1:4142,1:400]',
             # 'trimsec': '[55:355,95:2500]', YC
             'archive_zero_file': path_to_trunk + 'SOAR_cals/Zero_red_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'SOAR_cals/RESP_blue.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_red_20180206.fits',
             'archive_sens': path_to_trunk + 'SOAR_cals/fluxstarblue.fits',
             'archive_bstar': path_to_trunk + 'SOAR_cals/bstarblue.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbr1103.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbr1103.ms',
             'archive_arc_extracted': path_to_trunk + 'SOAR_cals/m1_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'SOAR_cals/id/idm1_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'SOAR_cals/apm1_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'lines.dat',
             'extinction_file': path_to_trunk + 'lick_extinction.dat',
             'observatory': 'soar',
             'sky_file': path_to_trunk + 'licksky.fits',
             'section': 'middle column'}
             
goodman_m2={ 'name': 'goodman_red',
             'arm': 'red',
             'read_noise': 3.99,
             'gain': 2.06,
             'grism': 'temp',
             'filter': 'temp',
             'slit': 'temp',
             'dispaxis': 1, 
             # 'biassec': '[1:7,1:948]',
             'biassec': '[2058:2071,1:200]',
             'trimsec': '[380:2055,30:870]',
             # 'trimsec': '[55:355,95:2500]', YC
             'archive_zero_file': path_to_trunk + 'SOAR_cals/Zero_red_20180206.fits',
             # 'archive_flat_file': path_to_trunk + 'Resp_red_20180206.fits',
             'archive_flat_file': path_to_trunk + 'SOAR_cals/RESP_red.fits',
             # 'archive_sens': path_to_trunk + 'sens_function_red_20180206.fits',
             'archive_sens': path_to_trunk + 'SOAR_cals/fluxstarred.fits',
             'archive_bstar': path_to_trunk + 'SOAR_cals/bstarred.fits',
             # 'archive_arc_extracted': path_to_trunk + 'tbr1103.ms.fits',
             # 'archive_arc_extracted_id': path_to_trunk + 'id/idtbr1103.ms',
             'archive_arc_extracted': path_to_trunk + 'SOAR_cals/m2_Arc_Ref.ms.fits',
             'archive_arc_extracted_id': path_to_trunk + 'SOAR_cals/id/idm2_Arc_Ref.ms',
             'archive_arc_aperture': path_to_trunk + 'SOAR_cals/apm2_Arc_Ref',
             # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
             'line_list': path_to_trunk+'lines.dat',
             'extinction_file': path_to_trunk + 'lick_extinction.dat',
             'observatory': 'soar',
             'sky_file': path_to_trunk + 'licksky.fits',
             'section': 'middle column'}


def blue_or_red(img):
    hdr = util.readhdr(img)
    # kast
    if util.readkey3(hdr, 'VERSION') == 'kastb':
        return 'blue', kast_blue
    elif util.readkey3(hdr, 'VERSION') == 'kastr':
        return 'red', kast_red
    # soar
    elif util.readkey3(hdr, 'WAVMODE') == '400 m1':
        return 'blue', goodman_m1
    elif util.readkey3(hdr, 'WAVMODE') == '400 m2':
        return 'red', goodman_m2
    # lris
    elif util.readkey3(hdr, 'INSTRUME') == 'LRISBLUE':
        return 'blue', lris_blue
    elif util.readkey3(hdr, 'INSTRUME') == 'LRIS':
        return 'red', lris_red
    else:
        print(util.readkey3(hdr, 'VERSION') + 'not in database')
        return None, None