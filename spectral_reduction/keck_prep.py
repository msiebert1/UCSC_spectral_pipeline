from __future__ import print_function
import os,sys,pdb,shutil,glob,argparse,subprocess,shlex
from time import sleep
import numpy as np

from astropy.io import fits
from astropy.io import ascii
from astropy.coordinates import SkyCoord
from astropy import units as u

import scipy
from scipy import signal
from scipy import interpolate
from scipy import optimize
from scipy import signal, ndimage

from pyraf import iraf
iraf.noao(_doprint=0)
iraf.imred(_doprint=0)
iraf.ccdred(_doprint=0)
iraf.twodspec(_doprint=0)
iraf.longslit(_doprint=0)
iraf.onedspec(_doprint=0)
iraf.specred(_doprint=0)
import pyds9 as pyds9
#from pyds9 import *


class StandardStar():
    ''' A class representing our standard star targets '''
    def __init__(self,ra='',dec=''):
        self.coord = SkyCoord('{} {}'.format(ra,dec), 
                                frame='icrs',
                                unit=(u.hourangle, u.deg))

def show_ds9_list(listFile,instanceName='default'):
    ''' display a list of images in a DS9 instance '''
    
    fileNameArr = np.array([])
    
    # read in the filenames
    with open(listFile,'r') as fin:
        for line in fin:
            if line[0] != '#':
                fileName = line.split()[0]
                fileNameArr = np.append(fileNameArr,fileName)
    
    #Setup the DS9 instance
    disp = pyds9.DS9(instanceName)
    disp.set("frame delete all")
    disp.set("view image no")
    disp.set("view colorbar no")
    disp.set("view panner no")
    disp.set("view info yes")
    disp.set("view magnifier no")
    disp.set("view buttons no")
    disp.set("tile yes")
    disp.set("tile column")
    disp.set("width 1200")
    disp.set("height 275")
      
    #Display the images
    for i in xrange(len(fileNameArr)):
        disp.set("frame {}".format(i))
        ds9cmd = "file fits {}".format(fileNameArr[i])
        disp.set(ds9cmd)
        disp.set("scale mode minmax")
        disp.set("regions delete all")
        disp.set("scale log")
        disp.set("wcs align yes")
        disp.set("cmap invert yes")  
        disp.set(ds9cmd)
    
    return disp


def construct_standard_star_library():
    ''' Construct a library of standard stars '''
    ssl = {
        'BD174708': StandardStar(ra='22:11:31.38', dec='+18:05:34.2'),
        'BD262606': StandardStar(ra='14:49:02.36', dec='+25:42:09.1'),
        'BD284211': StandardStar(ra='21:51:11.02', dec='+28:51:50.4'),
        'BD332642': StandardStar(ra='15:51:59.89', dec='+32:56:54.3'),
        'FEIGE15': StandardStar(ra='01:49:09.49', dec='+13:33:11.8'),
        'FEIGE24': StandardStar(ra='02:35:07.59', dec='+03:43:56.8'),
        'FEIGE25': StandardStar(ra='02:38:37.79', dec='+05:28:11.3'),
        'FEIGE34': StandardStar(ra='10:39:36.74', dec='+43:06:09.2'),
        'FEIGE56': StandardStar(ra='12:06:47.24', dec='+11:40:12.7'),
        'FEIGE66': StandardStar(ra='12:37:23.52',dec='+25:03:59.9'),
        'FEIGE92': StandardStar(ra='14:11:31.88', dec='+50:07:04.1'),
        'FEIGE98': StandardStar(ra='14:38:15.75', dec='+27:29:32.9'),
        'Feige110':StandardStar(ra='23:19:58.4', dec='-05:09:56.2'),
        'G158100': StandardStar(ra='00:33:54', dec='-12:07:57'), ###
        'G191b2b': StandardStar(ra='05:05:30.62', dec='+52:49:51.9'),
        'GD71': StandardStar(ra='05:52:27.62', dec='+15:53:13.2'),
        'GD248': StandardStar(ra='23:26:07', dec='+16:00:21'), ###
        'HD19445': StandardStar(ra='03:08:25.59', dec='+26:19:51.4'),
        'HD84937':StandardStar(ra='09:48:56.1',dec='+13:44:39.3'),
        'HZ43':  StandardStar(ra='13:16:21.85', dec='+29:05:55.4'),
        'HZ44': StandardStar(ra='13:23:35.26', dec='+36:07:59.5'),
        'LTT1020':StandardStar(ra='01:54:50.27',dec='-27:28:35.7'),
        'LTT1788': StandardStar(ra='03:48:22.61', dec='-39:08:37.0'),
        'LTT2415': StandardStar(ra='05:56:24.74', dec='-27:51:32.4'),
        'LTT3218': StandardStar(ra='08:41:32.43', dec='-32:56:32.9'),
        'LTT3864': StandardStar(ra='10:32:13.62', dec='-35:37:41.7'),
        'LTT4364': StandardStar(ra='11:45:42.92', dec='-64:50:29.5')
        }
    return ssl


def get_image_channel(header):
    ''' Determine LRIS camera/channel '''
    chan = header.get('INSTRUME',None)
    if chan == 'LRISBLUE':
        return 'BLUE'
    else:
        return 'RED'


def determine_image_type(header,STANDARD_STAR_LIBRARY):

    # init
    nullHeaderEntry = 'UNKNOWN'
    ARC_LAMP_KEYS = ['MERCURY','NEON','ARGON','CADMIUM',
                 'ZINC','HALOGEN','KRYPTON','XENON',
                 'FEARGON','DEUTERI']
    FLAT_LAMP_KEYS = ['FLAMP1','FLAMP2']
    pointingTolerance = 20. # arcseconds

    chan = get_image_channel(header)
    imageType = '{} '.format(chan)

    # if lamps are on, it is a calibration image

    # arcs
    for i,key in enumerate(ARC_LAMP_KEYS):
        if header.get(key,nullHeaderEntry).strip().lower() == 'on':
            imageType += 'ARC'
            return imageType

    # flats
    for i,key in enumerate(FLAT_LAMP_KEYS):
        if header.get(key,nullHeaderEntry).strip().lower() == 'on':
            imageType += 'FLAT'
            return imageType

    # suppose the lamps were left off or something, but we're not taking
    # tracking exposures. Would this capture twilight flats? Probably not.
    if header.get('ROTMODE',nullHeaderEntry).strip().lower() == 'stationary':
        imageType += 'CAL'
        return imageType

    # if the expTime is <1, its a calibration, but of unknown type
    ttime = header.get('TTIME',nullHeaderEntry)
    if ttime == nullHeaderEntry or float(ttime) < 1.:
        imageType += 'CAL'
        return imageType

    # if the coordinates are within 10" of a known standard, its probably a standard
    # in the weird case where a true science object is close to a standard, this
    # will require a by-hand fix, but that is rather unlikely.
    pointingCenterStr = '{} {}'.format(header.get('RA',nullHeaderEntry),
                                    header.get('DEC',nullHeaderEntry))
    pointingCenter = SkyCoord(pointingCenterStr, 
                              frame='icrs',
                              unit=(u.hourangle, u.deg))
    for i,standardKey in enumerate(STANDARD_STAR_LIBRARY):
        standard = STANDARD_STAR_LIBRARY[standardKey]
        sep = pointingCenter.separation(standard.coord)
        if sep.arcsecond < pointingTolerance:
            imageType += 'STD'
            return imageType

    # no lamps on, non zero exposure time, not near a standard:
    # it's probably a science frame
    imageType += 'SCI'
    return imageType

def add_boolean_arg(parser,name,default=False,help_string=''):
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--' + name, dest=name, action='store_true',
                        help=help_string)
    group.add_argument('--no_' + name, dest=name, action='store_false',
                        help='DO NOT: {}'.format(help_string))
    parser.set_defaults(**{name:default})


def parse_cmd_args():
    ''' Parse the command line options '''

    # init parser
    descStr = 'Main driver for organizing Keck LRIS data for reduction. '
    #descStr += 'Recommended calling sequence: \n \n'
    #descStr += '$ python keck_basic_2d.py -v -c \n'
    parser = argparse.ArgumentParser(description=descStr,
                                     formatter_class=argparse.RawTextHelpFormatter)

    # required args
    #parser.add_argument('requried_arg',type=str,
    #                    help='a required arguement')

    # optional
    parser.add_argument('-v','--verbose',
                        help='print diagnostic info',action='store_true')
    parser.add_argument('-c','--clobber',action='store_true',
                        help='Clobber files already in pre_reduced/ but not subdirs')
    parser.add_argument('-f','--full_clean',action='store_true',
                        help='Do a complete wipe of pre_reduced, including subdirs')
    parser.add_argument('-i', '--inspect', action='store_true',
                        help='Inspect the frames in the file lists (launches DS9 instances)')

    parser.add_argument('--regenerate_all', action='store_true',
                        help='Regenerate allList.txt file list')
    parser.add_argument('--regenerate_arc', action='store_true',
                        help='Regenerate (blue & red)ArcList.txt file lists')
    parser.add_argument('--regenerate_flat', action='store_true',
                        help='Regenerate (blue & red)FlatList.txt file lists')
    parser.add_argument('--regenerate_std', action='store_true',
                        help='Regenerate (blue & red)StdList.txt file lists')
    parser.add_argument('--regenerate_sci', action='store_true',
                        help='Regenerate (blue & red)SciList.txt file lists')


    # mutually exclusives boolean flags
    add_boolean_arg(parser,'reorganize_std', default=True,
                    help_string='Move standard star files into their directories')
    add_boolean_arg(parser,'reorganize_sci', default=True,
                    help_string='Move science files into their directories')
    add_boolean_arg(parser,'stack_cals', default=True,
                    help_string='Stack calibration frames (arcs and flats)')

    # parse
    cmdArgs = parser.parse_args()

    # logic mapping to my args/kwargs
    VERBOSE = cmdArgs.verbose
    CLOBBER = cmdArgs.clobber
    FULL_CLEAN = cmdArgs.full_clean
    REGENERATE_ALL_LIST = cmdArgs.regenerate_all
    REGENERATE_ARC_LIST = cmdArgs.regenerate_arc
    REGENERATE_FLAT_LIST = cmdArgs.regenerate_flat
    REGENERATE_STD_LIST = cmdArgs.regenerate_std
    REGENERATE_SCI_LIST = cmdArgs.regenerate_sci
    REORG_STANDARDS = cmdArgs.reorganize_std
    REORG_SCIENCE = cmdArgs.reorganize_sci
    STACK_CAL_FRAMES = cmdArgs.stack_cals

    # package up
    args = () # no args implemented yet
    kwargs = {}
    kwargs['VERBOSE'] = VERBOSE
    kwargs['CLOBBER'] = CLOBBER
    kwargs['FULL_CLEAN'] = FULL_CLEAN
    kwargs['REGENERATE_ALL_LIST'] = REGENERATE_ALL_LIST
    kwargs['REGENERATE_ARC_LIST'] = REGENERATE_ARC_LIST
    kwargs['REGENERATE_FLAT_LIST'] = REGENERATE_FLAT_LIST
    kwargs['REGENERATE_STD_LIST'] = REGENERATE_STD_LIST
    kwargs['REGENERATE_SCI_LIST'] = REGENERATE_SCI_LIST
    kwargs['REORG_STANDARDS'] = REORG_STANDARDS
    kwargs['REORG_SCIENCE'] = REORG_SCIENCE

    kwargs['STACK_CAL_FRAMES'] = STACK_CAL_FRAMES

    return (args,kwargs)




def main(*args,**kwargs):
    '''
    #---------------------------------------------------------------------------
    # 
    # keck_prep - Run basic file prep for Keck/LRIS longslit reductions
    #
    # Inputs:
    #
    # Assumes:
    #  1. You are in the RAWDATA/pre_reduced directory
    #
    #
    # Returns:
    #   Zero, but writes files to disk
    #
    # Description:
    #   1. Looks in pre_reduced, finds all the files
    #   2. Parses the headers, IDs the arcs, flats, science, and std star files
    #   3. Writes the files names to 4 text files and pauses:
    #        arc_list.txt
    #        flat_list.txt
    #        sci_list.txt
    #        std_list.txt
    #        all_list.txt
    #   4. The user can edit the list files to exclude files from the analysis
    #      (e.g., if several flats were saturated) and then continue
    #   5. The flats and arcs are stacked, and the science and std star scripts
    #      are moved to the object directory. 
    #
    #   NOTE: the object name recognition will be improved and refactored to
    #         match the implementation for used in specBrowser; the current
    #         implementation is pretty hacky.
    #
    # Author:
    #   J. Brown, UCSC Astronomy Dept
    #   brojonat@ucsc.edu
    #   2018 Oct 10
    #
    '''
    
    CLOBBER = kwargs.get('CLOBBER',False)
    FULL_CLEAN = kwargs.get('FULL_CLEAN',False)
    REGENERATE_ARC_LIST = kwargs.get('REGENERATE_ARC_LIST',False)
    REGENERATE_FLAT_LIST = kwargs.get('REGENERATE_FLAT_LIST',False)
    REGENERATE_SCI_LIST = kwargs.get('REGENERATE_SCI_LIST',False)
    REGENERATE_STD_LIST = kwargs.get('REGENERATE_STD_LIST',False)
    REGENERATE_ALL_LIST = kwargs.get('REGENERATE_ALL_LIST',False)
    INSPECT_FRAMES = kwargs.get('INSPECT_FRAMES',False)
    STACK_CAL_FRAMES = kwargs.get('STACK_CAL_FRAMES',False)
    REORG_STANDARDS = kwargs.get('REORG_STANDARDS',False)
    REORG_SCIENCE = kwargs.get('REORG_SCIENCE',False)
    SKYSUB_STANDARD = kwargs.get('SKYSUB_STANDARD',False)
    SKYSUB_SCIENCE = kwargs.get('SKYSUB_SCIENCE',False)

        
    # This is a dictionary of standard star objects
    STANDARD_STAR_LIBRARY = construct_standard_star_library()
    
    cwd = os.getcwd()
    if cwd.split('/')[-1] != 'pre_reduced':
        outStr = 'Looks like you\'re in: \n'
        outStr += '{}\n'.format(cwd) 
        outStr += 'Are you sure you\'re in the right directory?'
        print(outStr)
        pdb.set_trace()

    if FULL_CLEAN:
        promptStr = 'Do you really want to wipe all dirs and txt files from pre_reduced? [y/n]: '
        usrRespOrig = raw_input(promptStr)
        if usrRespOrig and usrRespOrig[0].strip().upper() == 'Y':

            # remove all text files
            for root,dirs,filenames in os.walk('.'):

                if root == '.':
                    for directory in dirs:
                        # remove all subdirectories
                        shutil.rmtree(directory)
                        outStr = 'Removed {}'.format(directory)
                        print(outStr)
                    for filename in filenames:
                        manifest_file_list = ['blueArcList.txt','redArcList.txt',
                                              'blueFlatList.txt','redFlatList.txt',
                                              'blueStdList.txt','redStdList.txt',
                                              'blueSciList.txt','redSciList.txt',
                                              'allList.txt']
                        if filename in manifest_file_list:
                            os.remove(filename)
                            outStr = 'Removed {}'.format(filename)
                            print(outStr)


            
    # empties
    sci_obj_list = []

    blueArcList = np.array([])
    blueArcAux = np.array([])
    
    redArcList = np.array([])
    redArcAux = np.array([])
    
    blueFlatList = np.array([])
    blueFlatAux = np.array([])
    
    redFlatList = np.array([])
    redFlatAux = np.array([])
    
    blueSciList = np.array([])
    blueSciAux = np.array([])
    
    redSciList = np.array([])
    redSciAux = np.array([])
    
    blueStdList = np.array([])
    blueStdAux = np.array([])
    
    redStdList = np.array([])
    redStdAux = np.array([])
    
    allList = np.array([])
    allAux = np.array([])
            
    # get all the files
    allFiles = sorted(glob.glob('*.fits'))
    
    # parse the headers, adding to lists as you go
    for i in xrange(len(allFiles)):
        
        # read
        inFile = allFiles[i]
        hdu = fits.open(inFile)
        header = hdu[0].header
        
        # parse
        fileType = determine_image_type(header,STANDARD_STAR_LIBRARY)

        # if its a science file, track it
        target_name = header['targname']
        if (('SCI' in fileType.upper()) and (target_name not in sci_obj_list)):
            sci_obj_list.append(target_name)
                                     
        # get auxilliary header info (object, slitmask)
        auxStr = '{} '.format(header['targname'])
        auxStr += '{} '.format(header['slitname'])
        auxStr += '{} '.format(header['graname'])
        auxStr += '{} '.format(header['ttime'])
        
        # log for the full file list
        allList = np.append(allList,inFile)
        allAux = np.append(allAux,auxStr)
    
        # write to appropriate list
        if fileType.strip().upper() == 'BLUE ARC':
            blueArcList = np.append(blueArcList,inFile)
            blueArcAux = np.append(blueArcAux,auxStr)
        elif fileType.strip().upper() == 'RED ARC':
            redArcList = np.append(redArcList,inFile)
            redArcAux = np.append(redArcAux,auxStr)

        elif fileType.strip().upper() == 'BLUE FLAT':
            blueFlatList = np.append(blueFlatList,inFile)
            blueFlatAux = np.append(blueFlatAux,auxStr)
        elif fileType.strip().upper() == 'RED FLAT':
            redFlatList = np.append(redFlatList,inFile)
            redFlatAux = np.append(redFlatAux,auxStr)

        elif fileType.strip().upper() == 'BLUE SCI':
            blueSciList = np.append(blueSciList,inFile)
            blueSciAux = np.append(blueSciAux,auxStr)
        elif fileType.strip().upper() == 'RED SCI':
            redSciList = np.append(redSciList,inFile)
            redSciAux = np.append(redSciAux,auxStr)

        elif fileType.strip().upper() == 'BLUE STD':
            blueStdList = np.append(blueStdList,inFile)
            blueStdAux = np.append(blueStdAux,auxStr)
        elif fileType.strip().upper() == 'RED STD':
            redStdList = np.append(redStdList,inFile)
            redStdAux = np.append(redStdAux,auxStr)
        else:
            errStr = '{} file type unknown...'.format(inFile)
            print(errStr)
            
            pass
    
    
    
    # write the list files
    # if the rewrite flag was set OR if the files aren't there, then write out
    WRITE_ALL_LIST = REGENERATE_ALL_LIST or not os.path.isfile('allList.txt')
    WRITE_ARC_LISTS = (REGENERATE_ARC_LIST or 
                       not (os.path.isfile('blueArcList.txt') or 
                            os.path.isfile('redArcList.txt')))
    WRITE_FLAT_LISTS = (REGENERATE_FLAT_LIST or
                        not (os.path.isfile('blueFlatList.txt') or 
                             os.path.isfile('redFlatList.txt')))
    WRITE_STD_LISTS = (REGENERATE_STD_LIST or
                        not (os.path.isfile('blueStdList.txt') or 
                             os.path.isfile('redStdList.txt')))
    WRITE_SCI_LISTS = (REGENERATE_SCI_LIST or 
                        not (os.path.isfile('blueSciList.txt') or 
                             os.path.isfile('redSciList.txt')))

    # all files
    if WRITE_ALL_LIST:
        with open('allList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(allList)):
                outStr += '{} {}\n'.format(allList[i],allAux[i])
            fout.write(outStr)

    # arcs
    if WRITE_ARC_LISTS:
        with open('blueArcList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(blueArcList)):
                outStr += '{} {}\n'.format(blueArcList[i],blueArcAux[i])
            fout.write(outStr)
        with open('redArcList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(redArcList)):
                outStr += '{} {}\n'.format(redArcList[i],redArcAux[i])
            fout.write(outStr)
        
    # flats
    if WRITE_FLAT_LISTS:
        with open('blueFlatList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(blueFlatList)):
                outStr += '{} {}\n'.format(blueFlatList[i],blueFlatAux[i])
            fout.write(outStr)
        with open('redFlatList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(redFlatList)):
                outStr += '{} {}\n'.format(redFlatList[i],redFlatAux[i])
            fout.write(outStr)

    # std stars
    if WRITE_STD_LISTS:
        with open('blueStdList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(blueStdList)):
                outStr += '{} {}\n'.format(blueStdList[i],blueStdAux[i])
            fout.write(outStr)
        with open('redStdList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(redStdList)):
                outStr += '{} {}\n'.format(redStdList[i],redStdAux[i])
            fout.write(outStr)
        
    # science
    if WRITE_SCI_LISTS:
        with open('blueSciList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(blueSciList)):
                outStr += '{} {}\n'.format(blueSciList[i],blueSciAux[i])
            fout.write(outStr)
        with open('redSciList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(redSciList)):
                outStr += '{} {}\n'.format(redSciList[i],redSciAux[i])
            fout.write(outStr)
    


    ##### User should do some display/QA/list editing maybe #####
    usrResp = ''
    blueArcDS9 = ''
    redArcDS9 = ''
    blueFlatDS9 = ''
    redFlatDS9 = ''
    blueSciDS9 = ''
    redSciDS9 = ''
    blueStdDS9 = ''
    redStdDS9 = ''
    
    # do visual inspection of frames via ds9 windows
    while usrResp != 'C':
        promptStr = '\nLists are written. First, read the lists, remove '
        promptStr += 'files from the lists you wish to exclude. \n'
        promptStr += 'Then you may: \n'
        promptStr += '  (D)isplay the remaining images, or \n'
        promptStr += '  (C)ontinue with the lists as they are, or \n'
        promptStr += '  (Q)uit the whole thing. \n'
        promptStr += 'I recommend you display, inspect, '
        promptStr += 'remove unwanted frames from lists, then continue.\nCommand: '
        usrRespOrig = raw_input(promptStr)
    
        try:
            usrResp = usrRespOrig.strip().upper()
        except Exception as e:
            usrResp = 'nothing'

        if usrResp == 'Q':
            sys.exit(1)
        
        # display all the images in the lists
        if usrResp == 'D':
            blueArcDS9 = show_ds9_list('blueArcList.txt',instanceName='BlueArcs')
            redArcDS9 = show_ds9_list('redArcList.txt',instanceName='RedArcs')

            blueFlatDS9 = show_ds9_list('blueFlatList.txt',instanceName='BlueFlats')
            redFlatDS9 = show_ds9_list('redFlatList.txt',instanceName='RedFlats')

            blueSciDS9 = show_ds9_list('blueSciList.txt',instanceName='BlueScience')
            redSciDS9 = show_ds9_list('redSciList.txt',instanceName='RedScience')

            blueStdDS9 = show_ds9_list('blueStdList.txt',instanceName='BlueStandards')
            redStdDS9 = show_ds9_list('redStdList.txt',instanceName='RedStandards')        
    
    # the lists are set, now construct the master cal frames
    
    if STACK_CAL_FRAMES:
        
        # stack blue arcs
        stackBlueArc = np.array([])
        commentStr = 'keck_prep: combined arcs from '
        with open('blueArcList.txt','r') as fin:
            for line in fin:
                if line[0] != '#' and len(line.split()) > 1:
                    infile = line.split()[0]
                    hdu = fits.open(infile)
                    data = hdu[0].data
                    header = hdu[0].header
                    expTime = header['ELAPTIME']
                    commentStr += '{}'.format(infile)
                    if len(stackBlueArc) == 0:
                        stackBlueArc = 1.*data/expTime
                    else:
                        stackBlueArc = stackBlueArc + data/expTime
        header.add_comment(commentStr)
        hduOut = fits.PrimaryHDU(stackBlueArc,header)
        if os.path.isfile('ARC_blue.fits'):
            if CLOBBER:
                os.remove('ARC_blue.fits')
                hduOut.writeto('ARC_blue.fits')
        else:
            hduOut.writeto('ARC_blue.fits')
        

        # stack red arcs
        stackRedArc = np.array([])
        commentStr = 'keck_prep: combined arcs from '
        with open('redArcList.txt','r') as fin:
            for line in fin:
                if line[0] != '#' and len(line.split()) > 1:
                    infile = line.split()[0]
                    hdu = fits.open(infile)
                    data = hdu[0].data
                    header = hdu[0].header
                    expTime = header['EXPTIME']
                    commentStr += '{}'.format(infile)
                    if len(stackRedArc) == 0:
                        stackRedArc = 1.*data/expTime
                    else:
                        stackRedArc = stackRedArc + data/expTime
        
        # write out
        header.add_comment(commentStr)
        hduOut = fits.PrimaryHDU(stackRedArc,header)    
        if os.path.isfile('ARC_red.fits'):
            if CLOBBER:
                os.remove('ARC_red.fits')
                hduOut.writeto('ARC_red.fits')
        else:
            hduOut.writeto('ARC_red.fits')
        
        # stack blue flats
        stackBlueFlat = np.array([])
        commentStr = 'keck_prep: combined flats from '
        with open('blueFlatList.txt','r') as fin:
            for line in fin:
                if line[0] != '#' and len(line.split()) > 1:
                    infile = line.split()[0]
                    hdu = fits.open(infile)
                    data = hdu[0].data
                    header = hdu[0].header
                    expTime = header['EXPTIME']
                    commentStr += '{} '.format(infile)
                    if len(stackBlueFlat) == 0:
                        stackBlueFlat = 1.*data
                    else:
                        stackBlueFlat = stackBlueFlat + data
                    
        # apply floor to avoid iraf crashes
        stackBlueFlat[stackBlueFlat < 1.] = 1.

        # write out 
        header.add_comment(commentStr)
        header['DISPAXIS'] = 1
        hduOut = fits.PrimaryHDU(stackBlueFlat,header)
        if os.path.isfile('FLAT_blue.fits'):
            if CLOBBER:
                os.remove('FLAT_blue.fits')
                hduOut.writeto('FLAT_blue.fits')
        else:
            hduOut.writeto('FLAT_blue.fits')

        # now do the response curve
        iraf.specred.response('FLAT_blue.fits', 
                               normaliz='FLAT_blue.fits', 
                               response='RESP_blue', 
                               interac='y', thresho='INDEF',
                               sample='*', naverage=2, function='legendre', 
                               low_rej=3,high_rej=3, order=60, niterat=20, 
                               grow=0, graphic='stdgraph')
                    
        # stack red flats
        stackRedFlat = np.array([])
        commentStr = 'keck_prep: combined flats from '
        with open('redFlatList.txt','r') as fin:
            for line in fin:
                if line[0] != '#' and len(line.split()) > 1:
                    infile = line.split()[0]
                    hdu = fits.open(infile)
                    data = hdu[0].data
                    header = hdu[0].header
                    expTime = header['ELAPTIME']
                    commentStr += '{} '.format(infile)
                    if len(stackRedFlat) == 0:
                        stackRedFlat = 1.*data
                    else:
                        stackRedFlat = stackRedFlat + data

        # apply floor to avoid iraf crashes
        stackRedFlat[stackRedFlat < 1.] = 1.
        
        header.add_comment(commentStr)
        header['DISPAXIS'] = 1
        hduOut = fits.PrimaryHDU(stackRedFlat,header)
        if os.path.isfile('FLAT_red.fits'):
            if CLOBBER:
                os.remove('FLAT_red.fits')
                hduOut.writeto('FLAT_red.fits')
        else:
            hduOut.writeto('FLAT_red.fits')

        # now do the response curve
        iraf.specred.response('FLAT_red.fits', 
                               normaliz='FLAT_red.fits', 
                               response='RESP_red', 
                               interac='y', thresho='INDEF',
                               sample='*', naverage=2, function='legendre', 
                               low_rej=3,high_rej=3, order=60, niterat=20, 
                               grow=0, graphic='stdgraph')
            
    # calibration frames are all set, now move the std/sci files to their directory
    if REORG_STANDARDS:
        for i,stdStar in enumerate(STANDARD_STAR_LIBRARY):
        
            if not os.path.isdir(stdStar):
                os.mkdir(stdStar)
            
            elif CLOBBER and not FULL_CLEAN:
                # get files and remove them
                delFiles = glob.glob('{}/*.fits'.format(stdStar))
                for j in xrange(len(delFiles)):
                    os.remove(delFiles[j])
                
            elif CLOBBER and FULL_CLEAN:
                promptStr = 'Do you really want to wipe the dir for {}? [y/n]: '.format(stdStar)
                usrRespOrig = raw_input(promptStr)
                if usrRespOrig[0].strip().upper() == 'Y':
                    shutil.rmtree(stdStar)
                    os.mkdir(stdStar)
            else:
                pass # dir is there, but no CLOBBER
            
            # now move the appropriate files
            # this is wildly inefficient but whatever
            # NOTE: if the file already exists (i.e. was not removed above)
            # then it will not be overwritten here
            with open('blueStdList.txt','r') as fin:
                for line in fin:
                    if line[0] != '#' and len(line.split()) > 1:
                        if stdStar.strip().upper() in line.split()[1].strip().upper():
                            destFile = '{}/{}'.format(stdStar,line.split()[0])
                            
                            if not os.path.isfile(destFile):
                                hdu = fits.open(line.split()[0])
                                header = hdu[0].header
                                imgData = hdu[0].data
                                
                                # optionally skysub
                                if SKYSUB_STANDARD:
                                    # not yet implemented
                                    pass

                                # place the file
                                hduOut = fits.PrimaryHDU(imgData,header)
                                hduOut.writeto(destFile,output_verify='ignore')
                                
            with open('redStdList.txt','r') as fin:
                for line in fin:
                    if line[0] != '#' and len(line.split()) > 1:
                        if stdStar.strip().upper() in line.split()[1].strip().upper():
                            destFile = '{}/{}'.format(stdStar,line.split()[0])
                            
                            if not os.path.isfile(destFile):
                                hdu = fits.open(line.split()[0])
                                header = hdu[0].header
                                imgData = hdu[0].data
                                
                                # optionally skysub
                                if SKYSUB_STANDARD:
                                    # not yet implemented
                                    pass

                                # place the file
                                hduOut = fits.PrimaryHDU(imgData,header)
                                hduOut.writeto(destFile,output_verify='ignore')
                                
            # This differs from science below. If we didn't move any
            # files into this stdStar directory, just remove it.
            if not os.listdir(stdStar):
                shutil.rmtree(stdStar)
        
        
    # standards are all set, now move the science files to their directory
    if REORG_SCIENCE:
        for i in xrange(len(sci_obj_list)):
        
            sciObj = sci_obj_list[i]
        
            if not os.path.isdir(sciObj):
                os.mkdir(sciObj)
            
            elif CLOBBER and not FULL_CLEAN:
                # get files and remove them
                delFiles = glob.glob('{}/*.fits'.format(sciObj))
                for j in xrange(len(delFiles)):
                    os.remove(delFiles[j])
                
            elif CLOBBER and FULL_CLEAN:
                promptStr = 'Do you really want to wipe the dir for {}? [y/n]: '.format(sciObj)
                usrRespOrig = raw_input(promptStr)
                if usrRespOrig and usrRespOrig[0].strip().upper() == 'Y':
                    shutil.rmtree(sciObj)
                    os.mkdir(sciObj)
            else:
                print('Ok, leaving {} as is.'.format(sciObj))
            
            # now move the appropriate files
            # this is inefficient but whatever
            # NOTE: if the file already exists (i.e. was not removed above)
            # then it will not be overwritten here
            with open('blueSciList.txt','r') as fin:
                for line in fin:
                    if line[0] != '#' and len(line.split()) > 1:
                        if sciObj.strip().upper() in line.split()[1].strip().upper():
                            destFile = '{}/{}'.format(sciObj,line.split()[0])
                            
                            if not os.path.isfile(destFile):
                                hdu = fits.open(line.split()[0])
                                header = hdu[0].header
                                imgData = hdu[0].data

                                # optionally skysub
                                if SKYSUB_SCIENCE:
                                    # not yet implemented
                                    pass

                                # place the file
                                hduOut = fits.PrimaryHDU(imgData,header)
                                hduOut.writeto(destFile,output_verify='ignore')
                                
                                
            with open('redSciList.txt','r') as fin:
                for line in fin:
                    if line[0] != '#' and len(line.split()) > 1:
                        if sciObj.strip().upper() in line.split()[1].strip().upper():
                            destFile = '{}/{}'.format(sciObj,line.split()[0])
                            
                            if not os.path.isfile(destFile):
                                hdu = fits.open(line.split()[0])
                                header = hdu[0].header
                                imgData = hdu[0].data

                                # optionally skysub
                                if SKYSUB_SCIENCE:
                                    # not yet implemented
                                    pass

                                # place the file
                                hduOut = fits.PrimaryHDU(imgData,header)
                                hduOut.writeto(destFile,output_verify='ignore')
                                
    
    return 0
    
if __name__=='__main__':
    ''' Run parsing, then main '''
    args,kwargs = parse_cmd_args()
    main(*args,**kwargs)