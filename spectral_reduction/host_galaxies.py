from __future__    import print_function
import numpy as np
import pandas as pd
import os
import csv

path_to_trunk = os.path.expandvars('$UCSC_SPECPIPE/spectral_reduction/trunk/')
if not os.path.exists(path_to_trunk):
    raise RuntimeError('Error : $UCSC_SPECPIPE variable is undefined or incorrect!')

#function to read host galaxy metadata and make file for night
def make_host_metadata(configDict):
    # kyle_host_meta = pd.read_csv(path_to_trunk+'host_galaxy_metadata/Foundation_Spectroscopy.csv')
    # foundation_host_meta = pd.read_csv(path_to_trunk+'host_galaxy_metadata/Foundation_Offsets_and_Position_Angles.csv')
    # swope_host_meta = pd.read_csv(path_to_trunk+'host_galaxy_metadata/Foundation_Offsets_and_Position_Angles_Swope.csv', header=7)

    with open(path_to_trunk+'host_galaxy_metadata/Foundation_Spectroscopy.csv') as kyle_file:
        kyle_host_meta = csv.reader(kyle_file, delimiter=',')
        host_reds = {}
        for row in kyle_host_meta:
            host_reds[row[0].strip().lower()] = row[12].strip()

    with open(path_to_trunk+'host_galaxy_metadata/Foundation_Offsets_and_Position_Angles.csv') as found_file:
        foundation_host_meta = csv.reader(found_file, delimiter=',')
        host_seps = {}
        host_angs = {}
        for row in foundation_host_meta:
            host_seps[row[0].strip().lower()] = row[12].strip()
            host_angs[row[0].strip().lower()] = row[13].strip()

    with open(path_to_trunk+'host_galaxy_metadata/Foundation_Offsets_and_Position_Angles_Swope.csv') as swope_file:
        swope_host_meta = csv.reader(swope_file, delimiter=',')
        host_seps = {}
        host_angs = {}
        for row in swope_host_meta:
            if row[0].strip().lower() not in host_seps.keys():
                host_reds[row[0].strip().lower()] = row[1].strip()
                host_seps[row[0].strip().lower()] = row[19].strip()
                host_angs[row[0].strip().lower()] = row[20].strip()


    #get sn folder name and find host data
    targ_list = []
    for imgType,typeDict in configDict.items():
        if imgType in ['STD','SCI']:
            for chan,objDict in typeDict.items():
                for obj,fileList in objDict.items():
                    if 'host' in obj.lower():
                        targ_list.append(obj.lower().split('_')[0])
                        print (obj)

    with open('pre_reduced/HOST_METADATA.txt', 'w') as host_file:
        host_file.write('# SN z sep ang\n')
        for SN in host_seps:
            if SN.lower() in targ_list:
                print (SN.lower(), host_reds[SN],host_seps[SN],host_angs[SN])
                host_file.write(SN.lower() + ' ' + host_reds[SN] + ' ' + host_seps[SN] + ' ' + host_angs[SN]+'\n')

def calculate_ap_data(sn, inst, seeing = 1., ap_scale=.0015):
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    import cosmo

    #get z
    print (sn)
    with open('../HOST_METADATA.txt') as host_file:
        for line in host_file.readlines():
            if line.split()[0] == sn:
                z, sep, ang, = float(line.split()[1]), float(line.split()[2]), float(line.split()[3])

        cosmo_data = cosmo.calculate(z)
        DA, DL_Mpc = cosmo_data[5], cosmo_data[7]

        theta_radian = ap_scale/DA
        theta = theta_radian*180*3600/np.pi



        test = sep/3600.
        c1 = SkyCoord(0.*u.degree, 0.*u.degree, distance=DL_Mpc*u.Mpc, frame='icrs')
        c2 = SkyCoord(0.*u.degree, test*u.degree, distance=DL_Mpc*u.Mpc, frame='icrs')
        sep_Mpc = c1.separation_3d(c2)


        sep_pix = sep/inst.get('pixel_scale')

        ap_width_min = seeing/inst.get('pixel_scale')
        if theta < seeing:
            ap_width = ap_width_min
        else:
            ap_width = theta/inst.get('pixel_scale')

        ap_binning = raw_input('Enter aperture spatial binning [1]: ') or 1
        ap_binning = float(ap_binning)

        ap_width = ap_width/ap_binning
        sep_pix = sep_pix/ap_binning

        print ('AP Width: ', ap_width, 'Sep kpc', sep_Mpc/1000., 'Sep pix: ', sep_pix)

        if sep_pix < ap_width:
            print ('APERTURE AT SN POSITION OVERLAPS')
            create_sn_ap = False
        else:
            create_sn_ap = True

        return sep_pix, create_sn_ap

def write_host_ap(ap_width, sep_pix, create_sn_ap, name):
    aps = glob.glob('../master_files/ap*')
    for ap in aps:
        print (ap.split('/')[-1])
    ref_ap = raw_input('Choose aperture for reference: ')

    if create_sn_ap:
        sn_direction = raw_input('Choose SN direction [1]: ')
        sn_direction = float(sn_direction)

    with open('../master_files/'+ref_ap) as ref_ap_file:
        with open('database/ap'+name,'w') as host_ap_file:
            ref_ap_data = ref_ap_file.readlines()
            for i, r_line in enumerate(ref_ap_data):
                if 'begin' in r_line and 'aperture' in r_line:
                    host_ap_file.write(r_line.replace(r_line.split()[2], name))

                elif 'image' in r_line:
                    host_ap_file.write(r_line.replace(r_line.split()[1], name))

                elif 'low' in line and 'reject' not in line:
                    low = str(-1.*apwidth/2.) 
                    host_ap_file.write(line.replace(line.split()[2], low))
                elif 'high' in line and 'reject' not in line:
                    high = str(apwidth/2.) 
                    host_ap_file.write(line.replace(line.split()[2], high))

                else:
                    host_ap_file.write(r_line)

            if create_sn_ap:
                host_ap_file.write('\n')
                for i, r_line in enumerate(ref_ap_data):
                    if 'begin' in r_line and 'aperture' in r_line:
                        host_ap_file.write(r_line.replace((r_line.split()[2] + ' 1'), name + ' 2'))

                    elif 'image' in r_line:
                        host_ap_file.write(r_line.replace(r_line.split()[1], name))

                    if 'begin' not in r_line and 'aperture' in r_line:
                        host_ap_file.write(r_line.replace(r_line.split()[2], '2'))

                    elif 'low' in line and 'reject' not in line:
                        low = str(-1.*apwidth/2. + sn_direction*sep_pix) 
                        host_ap_file.write(line.replace(line.split()[2], low))
                    elif 'high' in line and 'reject' not in line:
                        high = str(apwidth/2. + sn_direction*sep_pix) 
                        host_ap_file.write(line.replace(line.split()[2], high))
                    else:
                        host_ap_file.write(r_line)


#function to generate aperture data from host file


#function to find lris slit image



