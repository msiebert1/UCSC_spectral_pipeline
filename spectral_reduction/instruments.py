from __future__    import print_function
import os
path_to_trunk = os.path.expandvars('$UCSC_SPECPIPE/spectral_reduction/trunk/')
if not os.path.exists(path_to_trunk):
	raise RuntimeError('Error : $UCSC_SPECPIPE variable is undefined or incorrect!')

kast_blue = {'name': 'kast_blue',
			 'read_noise': 3.7,
			 'gain': 1.2,
			 'grism': 'temp',
			 'filter': 'temp',
			 'slit': 'temp',
			 'dispaxis': 1,
			 'biassec': '[1:2048,318:350]',
			 'trimsec': '[50:1900,10:300]',
			 # 'trimsec': '[30:2000,5:285]', YC
			 'archive_zero_file': path_to_trunk + 'Zero_blue_20180206.fits',
			 # 'archive_flat_file': path_to_trunk + 'Resp_blue_20180206.fits', THIS FLAT IS GARBAGE
			 'archive_flat_file': path_to_trunk + 'RESP_blue.fits',
			 'archive_sens': path_to_trunk + 'sens_function_blue_20180206.fits',
			 'archive_arc_extracted': path_to_trunk + 'tbb1070.ms.fits',
			 'archive_arc_extracted_id': path_to_trunk + 'id/idtbb1070.ms',
			 # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
			 'line_list': path_to_trunk+'lines.dat',
			 'extinction_file': path_to_trunk + 'lick_extinction.dat',
			 'observatory': 'lick',
			 'sky_file': path_to_trunk + 'licksky.fits',
			 'section': 'middle line'}


kast_red = { 'name': 'kast_red',
             'read_noise': 3.8,
			 'gain': 1.9,
			 'grism': 'temp',
			 'filter': 'temp',
			 'slit': 'temp',
			 'dispaxis': 2, 
			 'biassec': '[360:405,1:2725]',
			 'trimsec': '[60:355,125:2280]',
			 # 'trimsec': '[55:355,95:2500]', YC
			 'archive_zero_file': path_to_trunk + 'Zero_red_20180206.fits',
			 # 'archive_flat_file': path_to_trunk + 'Resp_red_20180206.fits',
			 'archive_flat_file': path_to_trunk + 'RESP_red.fits',
			 'archive_sens': path_to_trunk + 'sens_function_red_20180206.fits',
			 'archive_arc_extracted': path_to_trunk + 'tbr1103.ms.fits',
			 'archive_arc_extracted_id': path_to_trunk + 'id/idtbr1103.ms',
			 # 'line_list': path_to_trunk+'Lines_He_Hg_Cd_HgA_Ne_KAST.dat',
			 'line_list': path_to_trunk+'lines.dat',
			 'extinction_file': path_to_trunk + 'lick_extinction.dat',
			 'observatory': 'lick',
			 'sky_file': path_to_trunk + 'licksky.fits',
			 'section': 'middle column'}
