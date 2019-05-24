from __future__ import print_function
import os,sys,pdb,shutil,glob,subprocess,shlex
from time import sleep
import numpy as np

from astropy.io import fits
from astropy.io import ascii

import scipy
from scipy import signal
from scipy import interpolate
from scipy import optimize
from scipy import signal, ndimage


import pyds9 as pyds9
#from pyds9 import *


from optparse import OptionParser

#---------------------------------------------------------------------------
#
# isds9up - see if a named DS9 window is up
#
# Inputs:
#   ds9ID = ID ("title") of a DS9 display window
#
# Returns:
#   True if ds9ID is running, False otherwise.
#
# Description:
#   Uses the shell's xpaaccess method to see if the named ds9 window
#   is up and running.
#
# Author:
#   R. Pogge, OSU Astronomy Dept
#   pogge.1@osu.edu
#   2012 May 3
#

def isds9up(ds9ID):
    test = subprocess.Popen(['xpaaccess','-n',ds9ID],
                            stdout=subprocess.PIPE).communicate()[0]
    if int(test):
        return True
    else:
        return False



#---------------------------------------------------------------------------
#
# startDS9 - launch a named ds9 window
#
# Inputs:
#   ds9ID = ID ("title") of a DS9 display window to open
#
# Description:
#   Launches a named DS9 instance, making sure all of the IRAF
#   imtool pipes are suppresed so that IRAF won't interfere
#   with it (and vis-vers).  It sleeps for 2 seconds to allow
#   the tool to open.  This may have to be increased on slower
#   or more loaded systems.
#
# Author:
#   R. Pogge, OSU Astronomy Dept
#   pogge.1@osu.edu
#   2012 May 3
#

def startDS9(ds9ID):
    cmdStr = "ds9 -fifo none -port none -unix none -title {}".format(ds9ID)
    args = shlex.split(cmdStr)
    subprocess.Popen(args)
    sleep(3)
    
def kill_ds9(ds9ID):
    cmdStr = "ds9 quit"
    ds9ID.set(cmdStr)

def show_ds9_list(listFile,instanceName='default'):
    
    fileNameArr = np.array([])
    
    # read in the filenames
    with open(listFile,'r') as fin:
        for line in fin:
            if line[0] != '#':
                fileName = line.split()[0]
                fileNameArr = np.append(fileNameArr,fileName)
    
    #Setup the DS9 instance
    if not isds9up(instanceName):
        startDS9(instanceName)
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


def parse_keck_header(header,std_star_list='',sci_obj_list=''):
    
    imgType = '' # init so we can check if it gets set
    
    # first, determine channel; this is relatively easy
    if header['instrume'].strip().upper() == 'LRISBLUE':
        channel = 'BLUE'
    else:
        channel = 'RED'
        
    # now determine if arc/flat/std/sci
    
    # check if arc
    if 'ARC' in header['object'].strip().upper():
        imgType = 'ARC'
        
    # if no imgType, check if flat
    if not imgType: 
        if (('FLAT' in header['object'].strip().upper()) and 
            ('LONG_1.0' in header['slitname'].strip().upper())):
            imgType = 'FLAT'
        elif (('FLAT' in header['object'].strip().upper()) and 
            ('SLITLESS' in header['object'].strip().upper())):
            imgType = 'SLITLESSFLAT'
    # if still no imgType, check if std
    if not imgType:
        # loop over std stars, check if name detected in header
        # shamefully hacky
        for star in std_star_list:
            if ((star.strip().upper() in header['targname'].strip().upper().replace('+','')) or
                (star.strip().upper() in header['object'].strip().upper().replace('+',''))):
                imgType = 'STD'
                
    # if still no imgType, check if science
    if not imgType:      
        for sci in sci_obj_list:
            if ((sci.strip().upper() in header['targname'].strip().upper()) or
                (sci.strip().upper() in header['object'].strip().upper())):
                imgType = 'SCI' 
    
    # finally, give up  
    if not imgType:
        imgType = 'UNK'   
        
    res = '{} {}'.format(channel,imgType)
    return res





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
#
#
# Author:
#   J. Brown, UCSC Astronomy Dept
#   brojonat@ucsc.edu
#   2018 Oct 10
#

def main():
        
    description = 'TBD'
    usage= 'TBD'
    parser = OptionParser(usage=usage, description=description, version="0.1" )
    option, args = parser.parse_args()
    
    ### To be defined command line options ###
    CLOBBER = True
    FULL_CLEAN = False
    
    
    # set these false if you don't want to overwrite lists you've edited
    REGENERATE_ARC_LISTS = False
    REGENERATE_FLAT_LISTS = False
    REGENERATE_SCI_LISTS = False
    REGENERATE_STD_LISTS = False
    REGENERATE_ALL_LIST = False
    
    INSPECT_FRAMES = True # opens DS9 windows
    
    STACK_CAL_FRAMES = True # this should always be true (until archivals are made)
    
    REORG_STANDARDS = True # necessary for flat and skysub
    REORG_SCIENCE = True # necessary for flat and skysub
    
    FLAT_SCIENCE = False # false for now, Matt's code does this
    FLAT_STANDARD = False # false for now, Matt's code does this
    
    SKYSUB_STANDARD = False # not implemented yet
    SKYSUB_SCIENCE = False # not implemented yet
        
    # This is a list of standards
    # feel free to edit/add new ones especially if you've
    # observed a standard that isn't already included in the list; 
    # the starting point is the HST/CALSPEC list.
    std_star_list = ['G191-B2B', # white dwarf
                     'GD71', # white dwarf
                     'FEIGE34',
                     'FEIGE66',
                     'FEIGE67',
                     'GD153', # white dwarf
                     'HZ43', # white dwarf
                     'HZ44',
                     'BD322642',
                     'BD284211',
                     'FEIGE110',
                     
                     # non HST-calspec standards below
                     'BD262606',
                     'BD174708']  
                     
    # NOTE: 
    #
    # The matching is done is by checking if the objects in this list 
    # are in the headers of the file, so trim things like the prefixes
    # to avoid issues like AT2017gfl vs SN2017gfl and the like. 
    #
    # If the string in this list is in the TARGNAME or OBJECT
    # keywords, then it will be detected
    #
    sci_obj_list = ['2016gkg']
    #sci_obj_list = ['AT2018bcb','2017gfl']
    
    cwd = os.getcwd()
    if cwd.split('/')[-1] != 'pre_reduced':
        outStr = 'Looks like you\'re in: \n'
        outStr += '{}\n'.format(cwd) 
        outStr += 'Are you sure you\'re in the right directory?'
        pdb.set_trace()
            
    # empties
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
        fileType = parse_keck_header(header,
                                     std_star_list=std_star_list,
                                     sci_obj_list=sci_obj_list)
                                     
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
            print errStr
            
            pass
    
    
    
    # write the list files
    
    # arcs
    if REGENERATE_ARC_LISTS:
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
    if REGENERATE_FLAT_LISTS:
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

        
    # science
    if REGENERATE_SCI_LISTS:
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

        
    # std stars
    if REGENERATE_STD_LISTS:
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
    
    # all files
    if REGENERATE_ALL_LIST:
        with open('allList.txt','w') as fout:
            outStr = ''
            for i in xrange(len(allList)):
                outStr += '{} {}\n'.format(allList[i],allAux[i])
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
        promptStr += '  (C)ontinue with the lists as they are.\n'
        promptStr += 'I recommend you display, inspect, '
        promptStr += 'remove unwanted frames from lists, then continue.\nCommand: '
        usrRespOrig = raw_input(promptStr)
    
        try:
            usrResp = usrRespOrig.strip().upper()
        except Exception as e:
            usrResp = 'nothing'
        
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
                    
        # apply floor    
        stackBlueFlat[stackBlueFlat < 1.] = 1.
        
        # # now get rid of the color term
        # stackShape = stackBlueFlat.shape
        # for i in xrange(stackShape[1]):
        #     stackBlueFlat[:,i] /= np.median(stackBlueFlat[:,i])

        # write out 
        header.add_comment(commentStr)
        hduOut = fits.PrimaryHDU(stackBlueFlat,header)
        if os.path.isfile('RESP_blue.fits'):
            if CLOBBER:
                os.remove('RESP_blue.fits')
                hduOut.writeto('RESP_blue.fits')
        else:
            hduOut.writeto('RESP_blue.fits')
                    
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
        # apply floor
        stackRedFlat[stackRedFlat < 1.] = 1.
        
        # # now get rid of the color term
        # stackShape = stackRedFlat.shape
        # for i in xrange(stackShape[1]):
        #     stackRedFlat[:,i] /= np.median(stackRedFlat[:,i])
        
        header.add_comment(commentStr)
        hduOut = fits.PrimaryHDU(stackRedFlat,header)
        if os.path.isfile('RESP_red.fits'):
            if CLOBBER:
                os.remove('RESP_red.fits')
                hduOut.writeto('RESP_red.fits')
        else:
            hduOut.writeto('RESP_red.fits')
            
    # calibration frames are all set, now move the std/sci files to their directory
    if REORG_STANDARDS:
        for i in xrange(len(std_star_list)):
        
            stdStar = std_star_list[i]
        
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
                                
                                # optionally flatten
                                if FLAT_STANDARD:
                                    hdu = fits.open(line.split()[0])
                                    header = hdu[0].header
                                    imgData = hdu[0].data
                                    imgData /= stackBlueFlat
                                else:
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
                                # optionally flatten
                                if FLAT_STANDARD:
                                    hdu = fits.open(line.split()[0])
                                    header = hdu[0].header
                                    imgData = hdu[0].data
                                    imgData /= stackRedFlat
                                else:
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
                print 'Ok, leaving {} as is.'.format(sciObj)
            
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
                                # optionally flatten
                                if FLAT_SCIENCE:
                                    hdu = fits.open(line.split()[0])
                                    header = hdu[0].header
                                    imgData = hdu[0].data
                                    imgData /= stackBlueFlat
                                else:
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
                                # optionally flatten
                                if FLAT_SCIENCE:
                                    hdu = fits.open(line.split()[0])
                                    header = hdu[0].header
                                    imgData = hdu[0].data
                                    imgData /= stackRedFlat
                                else:
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
                                
                                
    
    # done!
    
    
    return 0
    
if __name__=='__main__':
    main()