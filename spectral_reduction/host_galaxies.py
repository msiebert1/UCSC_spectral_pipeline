from __future__    import print_function
import numpy as np
import pandas as pd
import os
import csv
import glob
import pdb
import instruments

path_to_trunk = os.path.expandvars('$UCSC_SPECPIPE/spectral_reduction/trunk/')
if not os.path.exists(path_to_trunk):
    raise RuntimeError('Error : $UCSC_SPECPIPE variable is undefined or incorrect!')

#function to read host galaxy metadata and make file for night
def make_host_metadata(configDict):
    #TODO: update to include r_kron_rad

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
            print (row[0].strip().lower())
            host_seps[row[0].strip().lower()] = row[12].strip()
            host_angs[row[0].strip().lower()] = row[13].strip()

    with open(path_to_trunk+'host_galaxy_metadata/Foundation_Offsets_and_Position_Angles_Swope.csv') as swope_file:
        swope_host_meta = csv.reader(swope_file, delimiter=',')
        # host_seps = {}
        # host_angs = {}
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
                        print (obj.lower().split('_')[0])

    # pdb.set_trace()
    with open('pre_reduced/HOST_METADATA.txt', 'w') as host_file:
        host_file.write('# SN z sep ang\n')
        for SN in host_seps:
            if SN.lower() in targ_list:
                print (SN.lower(), host_reds[SN],host_seps[SN],host_angs[SN])
                host_file.write(SN.lower() + ' ' + host_reds[SN] + ' ' + host_seps[SN] + ' ' + host_angs[SN]+'\n')
            if SN.lower().replace('-','') in targ_list:
                print (SN.lower().replace('-',''), host_reds[SN],host_seps[SN],host_angs[SN])
                host_file.write(SN.lower().replace('-','') + ' ' + host_reds[SN] + ' ' + host_seps[SN] + ' ' + host_angs[SN]+'\n')
                

def calculate_ap_data(sn, inst, seeing = 1., ap_scale=.0015):
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    import cosmo

    # r_kron_rad = 8.91 #arcsec (make part of function)
    ap_widths_arcsec = [1.,1.5,2.,3.]#arcsec
    ap_widths_kpc = [.001,.0015,.002,.003]#Mpc

    ap_binning = raw_input('Enter aperture spatial binning [1]: ') or 1
    ap_binning = float(ap_binning)
    print ('Finding metadata for: ', sn)

    with open('../HOST_METADATA.txt') as host_file:
        for line in host_file.readlines():
            if line.split()[0] == sn:
                z, sep, ang, r_kron_rad = float(line.split()[1]), float(line.split()[2]), float(line.split()[3]), float(line.split()[4])


        cosmo_data = cosmo.calculate(z)
        DA, DL_Mpc = cosmo_data[5], cosmo_data[7]

        sep_pix = sep/inst.get('pixel_scale')
        sep_pix = sep_pix/ap_binning
        #convert separation to physical separation
        # test = sep/3600.
        # c1 = SkyCoord(0.*u.degree, 0.*u.degree, distance=DL_Mpc*u.Mpc, frame='icrs')
        # c2 = SkyCoord(0.*u.degree, test*u.degree, distance=DL_Mpc*u.Mpc, frame='icrs')
        # sep_Mpc = c1.separation_3d(c2)

        ap_pixs_phys = []
        ap_pixs_sky = []

        print ('Sep (pix): ', sep_pix)
        #physical apertures
        for w in ap_widths_kpc:
            theta_radian = w/DA
            theta = theta_radian*180*3600/np.pi

            suffix = ''
            if theta < seeing:
                print ('Physical size smaller than seeing: ', seeing, 'arcsec')
                suffix = '_BAD'
                ap_width = theta/inst.get('pixel_scale')
            else:
                ap_width = theta/inst.get('pixel_scale')
            ap_width = ap_width/ap_binning


            if sep_pix < ap_width:
                print ('Adding AP Width (pix): ', ap_width, '= '+str(w*1000.)+' kpc')
                print ('SN POSITION OVERLAPS, NOT ADDING')
                ap_pixs_phys.append((ap_width,False,suffix))
            else:
                print ('Adding AP Width (pix): ', ap_width, '= '+str(w*1000.)+' kpc')
                ap_pixs_phys.append((ap_width,True,suffix))




        for th in ap_widths_arcsec:
            suffix = ''
            if th < seeing:
                print ('Physical size smaller than seeing: ', seeing, 'arcsec')
                suffix = '_BAD'
                ap_width = th/inst.get('pixel_scale')
            else:
                ap_width = th/inst.get('pixel_scale')
            ap_width = ap_width/ap_binning

            if sep_pix < ap_width:
                print ('Adding AP Width (pix): ', ap_width, '= '+str(th)+' arcsec')
                print ('SN POSITION OVERLAPS, NOT ADDING')
                ap_pixs_sky.append((ap_width,False,suffix))
            else:
                print ('Adding AP Width (pix): ', ap_width, '= '+str(th)+' arcsec')
                ap_pixs_sky.append((ap_width,True,suffix))

        suffix = ''
        if r_kron_rad < seeing:
            suffix = '_BAD'
        ap_width_kron = (r_kron_rad/inst.get('pixel_scale')/ap_binning, False, suffix)
        print ('Adding AP Width Kron (pix): ', ap_width_kron[0], '= '+str(r_kron_rad)+' arcsec')


        return ap_pixs_phys, ap_pixs_sky, ap_width_kron, sep_pix, ap_widths_arcsec, ap_widths_kpc, r_kron_rad

def check_if_main_amp(host_ap_file, ref_ap_data, name, ap_width, is_sn_ap, sn_direction, sep_pix, num_ap):
    ap_on_main_amp = True

    for i, r_line in enumerate(ref_ap_data):
        if 'center' in r_line:
            center = float(r_line.split()[2])
        elif 'low' in r_line and 'reject' not in r_line:
            if is_sn_ap:
                low = -1.*ap_width/2. + sn_direction*sep_pix
            else:
                low = -1.*ap_width/2.

    if 'lris' in name and 'blue' in name:
        if center + low < 455:
            ap_on_main_amp = False
    if 'lris' in name and 'red' in name:
        if center + low < 0:
            ap_on_main_amp = False

    #TODO: implement for kast

    return ap_on_main_amp


def substitute_ap_data(host_ap_file, ref_ap_data, name, ap_width, is_sn_ap, sn_direction, sep_pix, num_ap):

    # if ap_on_main_amp:
    for i, r_line in enumerate(ref_ap_data):
        if 'begin' in r_line and 'aperture' in r_line:
            host_ap_file.write(r_line.replace((r_line.split()[2] + ' 1'), name + ' ' + str(num_ap)))
        elif 'image' in r_line:
            host_ap_file.write(r_line.replace(r_line.split()[1], name))
        elif 'begin' not in r_line and 'aperture' in r_line:
            host_ap_file.write(r_line.replace(r_line.split()[1], str(num_ap)))
        elif 'low' in r_line and 'reject' not in r_line:
            if is_sn_ap:
                low = str(-1.*ap_width/2. + sn_direction*sep_pix) 
            else:
                low = str(-1.*ap_width/2.) 
            host_ap_file.write(r_line.replace(r_line.split()[2], low))
        elif 'high' in r_line and 'reject' not in r_line:
            if is_sn_ap:
                high = str(ap_width/2. + sn_direction*sep_pix) 
            else:
                high = str(ap_width/2.) 
            host_ap_file.write(r_line.replace(r_line.split()[2], high))
        else:
            host_ap_file.write(r_line)


    host_ap_file.write('\n')


def write_host_ap(ap_pixs_phys, ap_pixs_sky, ap_width_kron, sep_pix, name, ap_widths_arcsec, ap_widths_kpc, r_kron_rad, inst, img):
    #TODO: update to loop through apertures sizes

    aps = glob.glob('../master_files/ap*')
    for ap in (aps):
        if instruments.blue_or_red(img)[0] == 'blue' and 'blue' in ap:
            if img.split('_')[0] in ap:
                ap_r = ap.split('/')[-1]
        elif instruments.blue_or_red(img)[0] == 'red' and 'red' in ap:
            if img.split('_')[0] in ap:
                ap_r = ap.split('/')[-1]
    ref_ap = raw_input('Choose aperture for reference [{}]: '.format(ap_r)) or ap_r

    sn_direction = raw_input('Choose SN direction [1]: ') or 1
    sn_direction = float(sn_direction)

    #need to first save a master ap for host
    #TODO: create dictionary of aps with num_ap (check seeing)
    ap_dict = {}
    with open('../master_files/'+ref_ap) as ref_ap_file:
        with open('database/ap'+name,'w') as host_ap_file:
            ref_ap_data = ref_ap_file.readlines()

            num_ap = 1
            for i, ap in enumerate(ap_pixs_phys):
                ap_on_main_amp = check_if_main_amp(host_ap_file, ref_ap_data, name, ap[0], False, sn_direction, sep_pix, num_ap)
                if ap_on_main_amp:
                    substitute_ap_data(host_ap_file, ref_ap_data, name, ap[0], False, sn_direction, sep_pix, num_ap)
                    ap_dict['ap'+str(num_ap)] = str(ap_widths_kpc[i]*1000.) + '_kpc' + ap[2]
                    num_ap+=1
                else:
                    print ('Rejecting ap:', num_ap, '(does not land on same amplifier)')
                if ap[1]:
                    ap_on_main_amp = check_if_main_amp(host_ap_file, ref_ap_data, name, ap[0], True, sn_direction, sep_pix, num_ap)
                    if ap_on_main_amp:
                        substitute_ap_data(host_ap_file, ref_ap_data, name, ap[0], True, sn_direction, sep_pix, num_ap)
                        ap_dict['ap'+str(num_ap)] = str(ap_widths_kpc[i]*1000.) + '_kpc_SN' + ap[2]
                        num_ap+=1
                    else:
                        print ('Rejecting ap:', num_ap, '(does not land on same amplifier)')


            for i, ap in enumerate(ap_pixs_sky):
                ap_on_main_amp = check_if_main_amp(host_ap_file, ref_ap_data, name, ap[0], False, sn_direction, sep_pix, num_ap)
                if ap_on_main_amp:
                    substitute_ap_data(host_ap_file, ref_ap_data, name, ap[0], False, sn_direction, sep_pix, num_ap)
                    ap_dict['ap'+str(num_ap)] = str(ap_widths_arcsec[i]) + '_arcsec' + ap[2]
                    num_ap+=1
                else:
                    print ('Rejecting ap:', num_ap, '(does not land on same amplifier)')
                if ap[1]:
                    ap_on_main_amp = check_if_main_amp(host_ap_file, ref_ap_data, name, ap[0], True, sn_direction, sep_pix, num_ap)
                    if ap_on_main_amp:
                        substitute_ap_data(host_ap_file, ref_ap_data, name, ap[0], True, sn_direction, sep_pix, num_ap)
                        ap_dict['ap'+str(num_ap)] = str(ap_widths_arcsec[i]) + '_arcsec_SN' + ap[2]
                        num_ap+=1
                    else:
                        print ('Rejecting ap:', num_ap, '(does not land on same amplifier)')

            if ap_width_kron[0]:
                ap_on_main_amp = check_if_main_amp(host_ap_file, ref_ap_data, name, ap_width_kron[0], False, sn_direction, sep_pix, num_ap)
                if ap_on_main_amp:
                    substitute_ap_data(host_ap_file, ref_ap_data, name, ap_width_kron[0], False, sn_direction, sep_pix, num_ap)
                    ap_dict['ap'+str(num_ap)] = str(r_kron_rad) + '_rkron' + ap[2]
                    num_ap+=1
                else:
                    print ('Rejecting ap:', num_ap, '(does not land on same amplifier)')

    with open('HOST_AP_DATA.txt','w') as host_ap_file:
        for ap in ap_dict.keys():
            host_ap_file.write(ap + ' ' + ap_dict[ap] + '\n')


#function to generate aperture data from host file


#function to find lris slit image



