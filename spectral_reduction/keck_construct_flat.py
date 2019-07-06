import os,sys,pdb,argparse,shutil,glob,subprocess,shlex
from time import sleep
import numpy as np

from astropy.io import fits
from astropy.io import ascii

import scipy
from scipy import signal
from scipy import interpolate
from scipy import optimize
from scipy import signal, ndimage

from optparse import OptionParser

import matplotlib

# this backend will catch buttons, but it could
# cause an issue with tex and/or MNRAS and arXiv?
# so be careful you copy/paste these imports elsewhere
matplotlib.use("Qt5Agg")
matplotlib.rcParams[u'keymap.yscale'].remove(u'l')
from matplotlib import pyplot as plt
import matplotlib.lines as mlines


##########
#
# This is the general class for applying corrections to stacked
# color free pixel flats. The idea is allow the user to flag
# exclusion regions (e.g. due to telluric bands or chip edge effects), 
# and then patch them up accordingly.
#
# The code flow is:
#   1. User supplies color free pixel flat as input
#   2. Plot window/images are displayed
#   3. User is prompted to mask regions
#   4. After the regions are masked, the user fits the regions
#     4a. Program computes the average (median) column which is
#         essentially the master illumination profile
#     4b. For each masked column, the master profile is subtracted,
#         the remaining flux is fit with a spline in order to
#         create a theoretical sky model for the column. Really,
#         it's sky+pixel-to-pixel variations, but the spline isn't a
#         true spline fit in the sense that it does not by definition
#         pass through every point; there is a parameter 's' which
#         modulates the number of knots in the fit. The assumption is
#         that the pixel to pixel variations will be encoded in the
#         residuals of the fit, while the sky flux (which varies over 
#         many pixels) will be modeled out. For more info, see the 
#         documentation on scipy.interpolate.UnivariateSpline.
#     4c. The residuals between the sky model and the observed data
#         are computed.
#     4d. The residuals are added to the master profile and this
#         quantity is used to replace the masked column.
#   5. Finally the user can save the corrected flat to a file.
#         
##########


class fitFlatClass(object):
    
    
    #
    # Basic class init
    #
    def __init__(self,image,fig):
        
        # data
        self.rawData = 1.*image # observed
        self.flatModelData = 1.*image # model
        self.flatCorrData = 1.*image # new flat (obs corrected by model)
        self.masterProfile = 0.*image[:,0] + 1. # single column illumination profile
        
        # figure
        self.fig = fig
        
        # spline smoothing (used in fitting)
        # use larger values to accept worse fits,
        # smaller values to mimic true spline
        self.splineSmooth = 1.
        
        # dict of fit regions
        self.regionDict = {}
        
        
        # dummy region dict
        self.dummyRegion = {'colLo': -1,
                            'colUp': -1,
                            'done': False,
                            'store': False}
        
    #   
    # This is the general function for handling clicks on the canvas
    #
    def skyRegion_onClick(self,event):
        
        # don't actually want to do anything for this
        return
        
    #   
    # This is the general function for handling key presses on the canvas
    #   
    def skyRegion_onKeyPress(self,event):
        
        # get the axes for plotting and cursor detection
        ax_list = self.fig.axes
        
        ax1 = ax_list[0]
        ax2 = ax_list[1]
        ax3 = ax_list[2]
        ax4 = ax_list[3]
        ax5 = ax_list[4]
                
        # make sure the cursor was in the correct axis
        if event.inaxes is ax4:
        
            # get the cursor position
            rowPress = event.ydata
            colPress = event.xdata
            
            # match row to nearst existing pixel
            if rowPress < 0:
                row = 0
            elif rowPress >= 0 and rowPress <= self.rawData.shape[0]:
                row = rowPress
            else:
                row = self.rawData.shape[0]
                
            # match col to nearest existing pixel
            if colPress < 0:
                col = 0
            elif colPress >= 0 and colPress <= self.rawData.shape[1]:
                col = colPress
            else:
                col = self.rawData.shape[1]
            
                
            if event.key == 'l':
                outStr = 'Adding lower column'
                print outStr
                self.dummyRegion['colLo'] = col
            
            elif event.key == 'u': 
                outStr = 'Adding upper column'
                print outStr
                self.dummyRegion['colUp'] = col
            
            elif event.key == 'd':
                outStr = 'Adding region to dict'
                print outStr
                self.dummyRegion['done'] = True
                self.dummyRegion['store'] = True
            
            elif event.key == 'q':
                outStr = 'Discarding region'
                print outStr
                self.dummyRegion['done'] = True
                self.dummyRegion['store'] = False
                        
            else:
                print 'Unrecognized key'
        
        
        return
        
    #    
    # Add a fitting region to the current sky model object
    #   name - the name of the region (e.g. region1)
    #   rowLo - the lower row enclosing the region
    #   rowUp - the upper row enclosing the region
    #
    # Updates the sky region dictionary
    #   
    def add_fit_region(self,name,colLo=-1,colUp=-1):
        
        # reset the dummy region dict
        self.dummyRegion['colLo'] = -1
        self.dummyRegion['colUp'] = -1
        self.dummyRegion['done'] = False
        self.dummyRegion['store'] = False
        
        # init region
        newRegion = flatFitRegion(name)
                
        # get the axes for plotting and cursor detection
        ax_list = self.fig.axes
        ax1 = ax_list[0]
        ax2 = ax_list[1]
        ax3 = ax_list[2]
        ax4 = ax_list[3]
        ax5 = ax_list[4]
        
        # user gave regions
        if colLo > 0 and colUp > 0:
            
            # populate the dummy variable
            self.dummyRegion['colLo'] = colLo
            self.dummyRegion['colUp'] = colUp
            self.dummyRegion['done'] = True
            self.dummyRegion['store'] = True
        
        # enter interactive    
        else:
        
            # print instructions
            outStr = 'Hover over the row you\'d like to add\n'
            outStr += 'Press L to mark a lower column\n'
            outStr += 'Press U to mark an upper column\n'
            outStr += 'Press D to add the region\n'
            outStr += 'Press Q to discard the region\n'
            print outStr            
            
            # connect the key press event here
            cid = self.fig.canvas.mpl_connect('button_press_event', self.skyRegion_onClick)
            cid2 = self.fig.canvas.mpl_connect('key_press_event', self.skyRegion_onKeyPress)
            
            lnL = ''
            lnU = ''
            
            while not self.dummyRegion['done']:
                
                if lnL:
                    lnL.remove()
                if lnU:
                    lnU.remove()
                                                
                lnL = ax4.axvline(x=self.dummyRegion['colLo'],c='#0d8202',lw=2.,ls='--')
                lnU = ax4.axvline(x=self.dummyRegion['colUp'],c='#6ef961',lw=2.,ls='--')
                
                # update the plot
                plt.pause(0.05)

            # disconnect
            self.fig.canvas.mpl_disconnect(cid)                
            self.fig.canvas.mpl_disconnect(cid2)                

                
        # flip order if necessary
        if self.dummyRegion['colLo'] > self.dummyRegion['colUp']:
            errStr = 'Had to flip the high/low columns...'
            print errStr
            colTemp = self.dummyRegion['colLo']
            self.dummyRegion['colLo'] = self.dummyRegion['colUp']
            self.dummyRegion['colUp'] = colTemp
            
        # assign values
        colLo = int(self.dummyRegion['colLo'])
        colUp = int(self.dummyRegion['colUp'])
        newRegion.colLo = colLo
        newRegion.colUp = colUp
        newRegion.flux = self.rawData[:,colLo:colUp]
        
        # store in the dict
        if self.dummyRegion['store']:
            self.regionDict[name] = newRegion
            
            
        # update the plot
        self.refresh_plot()
        
        return 0
    #
    # Remove a sky fitting region and update the 
    # sky region dictionary
    #
    def remove_fit_region(self,name=''):
               
        if len(name) > 0:
            trash = self.regionDict.pop(name, None)
                
        elif len(name) == 0:
            
            while True:
                outStr = 'Here\'s the info on the fitting regions:\n'
                for key in self.regionDict.keys():
                    region = self.regionDict[key]
                    outStr += '{} {} {}\n'.format(region.name,region.colLo,region.colUp)
                outStr += 'Enter the name of the region to delete, or Q to quit: '
                usrResp = raw_input(outStr).strip().upper()
            
                # delete the entry
                if usrResp in self.regionDict.keys():
                    trash = self.regionDict.pop(usrResp, None)
                    self.refresh_plot()
                    break
                    
                elif usrResp == 'Q':
                    outStr = 'Quitting region deletion...'
                    print outStr
                    break
                    
                else:
                    outStr = 'I do not understand, try again...'
                    print outStr
                    
        else:
            outStr = 'Something went wrong...'
            print outStr
            
        
        return 0
        
        
    #
    # update the master profile by excluding regions and
    # averaging (median) across rows
    #    
    def update_master_profile(self):
        
        maskedData = np.array([])
        colArr = np.array([])
        
        # unpack the exclusion regions
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            newCols = np.arange(region.colLo,region.colUp,1)
            colArr = np.append(colArr,newCols)
            
            
        maskedData = self.rawData[:,np.arange(self.rawData.shape[1]) != colArr]
        maskedData = maskedData[:,0,:] # weird
         
        # snippet for sanity checks           
        #fig=plt.figure(figsize=(6,6))    
        #ax1 = plt.subplot2grid((4,4),(0,0),rowspan=2,colspan=4)
        #ax2 = plt.subplot2grid((4,4),(2,0),rowspan=2,colspan=4)
        #ax1.imshow(self.rawData,origin='lower',vmin=0.95,vmax=1.05)
        #ax2.imshow(maskedData,origin='lower',vmin=0.95,vmax=1.05)
        #plt.show(block=True)
        #pdb.set_trace()
        
        updatedProfile = np.median(maskedData,axis=1)
        self.masterProfile = 1.*updatedProfile
        
        return 0
        
    #    
    # update the plot to reflect current state of the object
    #   
    def refresh_plot(self):
        
        # get the axes for plotting and cursor detection
        ax_list = self.fig.axes
        ax1 = ax_list[0]
        ax2 = ax_list[1]
        ax3 = ax_list[2]
        ax4 = ax_list[3]
        ax5 = ax_list[4]
        
        ax1.cla()
        ax2.cla()
        ax3.cla()
        ax4.cla()
        ax5.cla()
        
        modColArr = np.array([])
        # get cols where sky model is defined
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            newCols = np.arange(region.colLo,region.colUp,1)
            modColArr = np.append(modColArr,newCols)
        modColArr = modColArr.astype(int)
        
                
        # ax1 data
        blueSkyData = np.median(self.rawData[:,300:1500],axis=0)
        if len(modColArr) > 0:
            blueSkyModel = np.median(self.flatModelData[:,300:1500],axis=0)
        else:
            blueSkyModel = 0.*blueSkyData
        blueSkyX = np.arange(300,1500,1)

    
    
        # ax2 data
        midSkyData = np.median(self.rawData[:,1800:2100],axis=0)
        midSkyX = np.arange(1800,2100,1)
    
        # ax3 data
        redSkyData = np.median(self.rawData[:,2700:3200],axis=0)
        if len(modColArr) > 0:
            redSkyModel = np.median(self.flatModelData[:,2700:3200],axis=0)
        else:
            redSkyModel = 0.*redSkyData
        redSkyX = np.arange(2700,3200,1)

        # plot blue sky
        try:
            ax1.plot(blueSkyX,blueSkyData,c='k',ls='-',lw=3.)
            ax1.plot(blueSkyX,blueSkyModel,c='r',ls='--',lw=3.)
        except Exception as e:
            print e
            pdb.set_trace()

        #plot profile
        ax2.plot(midSkyX,midSkyData,c='k',ls='-',lw=3.)
        
        #plot red sky
        ax3.plot(redSkyX,redSkyData,c='k',ls='-',lw=3.)
        ax3.plot(redSkyX,redSkyModel,c='r',ls='--',lw=3.)

        # image
        ax4.imshow(self.rawData,aspect=1.,origin='lower',vmin=0.9,vmax=1.1)

        # residuals
        ax5.imshow(self.flatCorrData,aspect=1.,origin='lower',vmin=0.9,vmax=1.1)
        
        # over plot the sky regions
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            # lower
            ax4.axvline(x=region.colLo,c='#990000',lw=2,ls='--')
            # upper
            ax4.axvline(x=region.colUp,c='#ff4f4f',lw=2,ls='--')
            
        # sparse axis labels
        ax1.set_xlabel('column')
        ax1.set_ylabel('counts')
        ax2.set_xlabel('column')
        ax3.set_xlabel('column')
    
        ax1.set_yticklabels([])
        ax1.set_xticks([300,500,700,900,1100,1300])
        ax1.set_xticklabels([300,500,700,900,1100,1300])

        ax2.set_yticklabels([])
        ax2.set_xticks([1800,1900,2000,2100])
        ax2.set_xticklabels([1800, 1900, 2000, 2100])
    
        ax3.set_yticklabels([])
        ax3.set_xticks([2800,2900,3000,3100])
        ax3.set_xticklabels([2800,2900,3000,3100])
            
        
        # ranges on image plots
        ax4.set_xlim([0,self.rawData.shape[1]])
        ax4.set_ylim([0,self.rawData.shape[0]])
        
        ax5.set_xlim([0,self.rawData.shape[1]])
        ax5.set_ylim([0,self.rawData.shape[0]])
        
        return 0
        
    #
    # Fit the sky flux data column by column and 
    # update the sky model attribute
    #    
    def fit_sky_background(self,FIT_METHOD='LM'):
        
        # init
        skyImage = np.array([]) # actual sky data
        skyModel = np.array([]) # model of sky data
        skyModelFull = 0.*self.rawData # model across entire chip
        colArr = np.array([])
        
        # update the master profile
        outStr = 'Updating the master profile (takes a bit...)'
        print outStr
        self.update_master_profile()
        
        # stack the regions, but preserve the row pixel numbers in rowArr
        # this will be trickier if I implement curved sky regions
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            newCols = np.arange(region.colLo,region.colUp,1)
            colArr = np.append(colArr,newCols)
            
            if len(skyImage) == 0:
                skyImage = 1.*region.flux
            else:
                skyImage = np.hstack((skyImage,1.*region.flux))
                
                
        colArr = colArr.astype(int)
        # for each col, fit flux as a function of pixel number   
        for i in xrange(skyImage.shape[1]): 
            if i % 50 == 0:  
                print 'Working on col {} / {}'.format(i,skyImage.shape[1])
            
            # get the fit data for this column            
            fitX = np.arange(0,skyImage.shape[0]) # abscissa is row pixel number
            fitY = skyImage[fitX,i] - self.masterProfile # grab all rows in a single column
            
            # fit with a spline
            
            splineFit = interpolate.UnivariateSpline(fitX, fitY, s=self.splineSmooth)
            skyTheo = splineFit(fitX)
            
            # subtract fit from observed
            residual = self.rawData[:,colArr[i]] - skyTheo
            
            # add self.masterProfile back in
            skyModelFull[:,colArr[i]] = residual #+ self.masterProfile
            
            
            # plot?
            # if colArr[i] == 3348:
            #     PLOT=True
            # else:
            #     PLOT=False
            PLOT = False
            if PLOT:
                fig=plt.figure(figsize=(6,6))    
                axMain = plt.subplot2grid((4,4),(0,0),rowspan=4,colspan=6)
                axMain.plot(fitX,fitY,c='k',ls='',marker='.')
                axMain.plot(fitX,skyTheo,c='r',ls='--',lw=0.5)
                plt.show()
                pdb.set_trace()
                                       
            
            
        # insert into the full object image (no trasposing needed??)
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            newCols = np.arange(region.colLo,region.colUp,1)
            newCols = newCols.astype(int)
            
            self.flatModelData[:,newCols] = skyModelFull[:,newCols] # obviously check this
        
        return 0
        
        
        
    #   
    # This is the method for updating the final data product
    # of this class. Substitutes the model in the masked regions
    #   
    def subsitute_model_flat(self):
        # insert into the full object image (no trasposing needed??)
        for key in self.regionDict.keys():
            region = self.regionDict[key]
            newCols = np.arange(region.colLo,region.colUp,1)
            newCols = newCols.astype(int)
            self.flatCorrData[:,newCols] = 1.*self.flatModelData[:,newCols] 
        self.refresh_plot()
        return 0
        
    #
    # Substitutes the data in a user supplied region with self.masterProfile
    # This is useful if there is a region of the data that is simply trash
    #
    def hard_mask(self,name=''):
        
        # sub the master profile
        # inefficient, don't care
        if len(name) > 0:
            colLo = self.regionDict[usrResp].colLo
            colUp = self.regionDict[usrResp].colUp
            for i in xrange(colUp-colLo):
                self.flatCorrData[:,colLo+i] = self.masterProfile
            self.refresh_plot()                
        elif len(name) == 0:
            
            while True:
                outStr = 'Here\'s the info on the fitting regions:\n'
                for key in self.regionDict.keys():
                    region = self.regionDict[key]
                    outStr += '{} {} {}\n'.format(region.name,region.colLo,region.colUp)
                outStr += 'Enter the name of the region to mask, or Q to quit: '
                usrResp = raw_input(outStr).strip().upper()
            
                # sub the master profile
                # inefficient, don't care
                if usrResp in self.regionDict.keys():
                    colLo = self.regionDict[usrResp].colLo
                    colUp = self.regionDict[usrResp].colUp
                    for i in xrange(colUp-colLo):
                        self.flatCorrData[:,colLo+i] = self.masterProfile
                    self.refresh_plot()
                    break
                    
                elif usrResp == 'Q':
                    outStr = 'Quitting region deletion...'
                    print outStr
                    break
                    
                else:
                    outStr = 'I do not understand, try again...'
                    print outStr
                    
        else:
            outStr = 'Something went wrong...'
            print outStr
            
        
        return 0
        
        
        
    #
    # Substitutes the model correct flat for raw data and wipes 
    # the exclusion regions. This could be useful for iteratively 
    # improving the flat, but is really just and experiment and
    # not intended for actual use
    #    
    def refine(self):
        self.rawData = 1.*self.flatCorrData
        self.regionDict = {}
        self.refresh_plot()
        return 0
        
    #    
    # Save the model corrected flat
    # This will overwrite existing files automatically
    # (i.e. it assumes the user has already confirmed write)
    #    
    def save_flat(self,outFile):
        
        # clear space
        if os.path.isfile(outFile):
            os.remove(outFile)
        
        # write correct flat data
        hdu = fits.PrimaryHDU(self.flatCorrData)
        hdu.writeto(outFile,output_verify='ignore')  
        
        return 0
        
        
#       
# This is the class used for defining modeling regions
#       
class flatFitRegion(object):
    def __init__(self,name):
        self.name = name
        self.colLo = 0
        self.colUp = 1
        self.flux = np.array([])





def parse_cmd_args():
    ''' Parse the command line options '''

    # init parser
    descStr = 'Utility for masking bad regions on a flat field '
    parser = argparse.ArgumentParser(description=descStr)

    # required args
    parser.add_argument('flat_file',type=str,
                       help='the flat field to inspect/mask')

    # optional
    parser.add_argument('-v','--verbose',
                        help='print diagnostic info',action='store_true')
    parser.add_argument('-c','--clobber',action='store_true',
                        help='Clobber files already in pre_reduced/ but not subdirs')

    # parse
    cmdArgs = parser.parse_args()

    # logic mapping to my args/kwargs
    FLAT_FILE = cmdArgs.flat_file
    VERBOSE = cmdArgs.verbose
    CLOBBER = cmdArgs.clobber

    # package up
    args = (FLAT_FILE,) # no args implemented yet
    kwargs = {}
    kwargs['VERBOSE'] = VERBOSE
    kwargs['CLOBBER'] = CLOBBER

    return (args,kwargs)






############################################################################



#---------------------------------------------------------------------------
# 
# construct_flat - Model a flat field from slitflat data
#
# Inputs:
#    A 2D color free slit flat
#
# Assumes:
#
#
# Returns:
#    Zero, but writes files to disk
#
#
# Description:
#   1. User supplies color free pixel flat as input
#   2. Plot window/images are displayed
#   3. User is prompted to mask regions
#   4. After the regions are masked, the user fits the regions
#     4a. Program computes the average (median) column which is
#         essentially the master illumination profile
#     4b. For each masked column, the master profile is subtracted,
#         the remaining flux is fit with a spline in order to
#         create a theoretical sky model for the column. Really,
#         it's sky+pixel-to-pixel variations, but the spline isn't a
#         true spline fit in the sense that it does not by definition
#         pass through every point; there is a parameter 's' which
#         modulates the number of knots in the fit. The assumption is
#         that the pixel to pixel variations will be encoded in the
#         residuals of the fit, while the sky flux (which varies over 
#         many pixels) will be modeled out. For more info, see the 
#         documentation on scipy.interpolate.UnivariateSpline.
#     4c. The residuals between the sky model and the observed data
#         are computed.
#     4d. The residuals are added to the master profile and this
#         quantity is used to replace the masked column.
#   5. Finally the user can save the corrected flat to a file.
#
# Author:
#   J. Brown, UCSC Astronomy Dept
#   brojonat@ucsc.edu
#   2018 Nov 14
#

def main(*args,**kwargs):
    
    # read data
    inFile = args[0]

    hdu = fits.open(inFile)
    data = hdu[0].data
    header = hdu[0].header
    
    # set up plotting window
    plt.ion()
    #fig=plt.figure(figsize=(16,8))
    #axMain = plt.subplot2grid((6,6), (0,0), rowspan=6, colspan=6)
    #ax1 = plt.subplot2grid((6,6), (0,0), rowspan=2, colspan=2)
    #ax2 = plt.subplot2grid((6,6), (0,2), rowspan=2, colspan=2)
    #ax3 = plt.subplot2grid((6,6), (0,4), rowspan=2, colspan=2)
    #ax4 = plt.subplot2grid((6,6), (2,0), rowspan=2, colspan=6)
    #ax5 = plt.subplot2grid((6,6), (4,0), rowspan=2, colspan=6)
    
    fig=plt.figure(figsize=(16,8))
    axMain = plt.subplot2grid((36,36), (0,0), rowspan=36, colspan=36)
    ax1 = plt.subplot2grid((36,36), (0,0), rowspan=11, colspan=12)
    ax2 = plt.subplot2grid((36,36), (0,12), rowspan=11, colspan=12)
    ax3 = plt.subplot2grid((36,36), (0,24), rowspan=11, colspan=12)
    ax4 = plt.subplot2grid((36,36), (12,0), rowspan=12, colspan=36)
    ax5 = plt.subplot2grid((36,36), (24,0), rowspan=12, colspan=36)
    
    # ax1 data
    blueSkyData = np.median(data[:,300:1500],axis=0)
    blueSkyX = np.arange(300,1500,1)
    
    
    # ax2 data
    midSkyData = np.median(data[:,1800:2100],axis=0)
    midSkyX = np.arange(1800,2100,1)
    
    # ax3 data
    redSkyData = np.median(data[:,2700:3200],axis=0)
    redSkyX = np.arange(2700,3200,1)

    ax1.plot(blueSkyX,blueSkyData,c='k',ls='-',lw=3.)
    ax2.plot(midSkyX, midSkyData,c='k',ls='-',lw=3.)
    ax3.plot(redSkyX,redSkyData,c='k',ls='-',lw=3.)

    # image
    ax4.imshow(data,aspect=1.,origin='lower',vmin=0.9,vmax=1.1)
    
    # residuals
    ax5.imshow(data,aspect=1.,origin='lower',vmin=0.9,vmax=1.1)
    
    # ranges on image plots
    ax4.set_xlim([0,data.shape[1]])
    ax4.set_ylim([0,data.shape[0]])
    
    ax5.set_xlim([0,data.shape[1]])
    ax5.set_ylim([0,data.shape[0]])
    
    # sparse axis labels
    ax1.set_xlabel('column')
    ax1.set_ylabel('counts')
    ax2.set_xlabel('column')
    ax3.set_xlabel('column')
    
    ax1.set_yticklabels([])
    ax1.set_xticks([300,500,700,900,1100,1300])
    ax1.set_xticklabels([300,500,700,900,1100,1300])

    ax2.set_yticklabels([])
    ax2.set_xticks([1800,1900,2000,2100])
    ax2.set_xticklabels([1800, 1900, 2000, 2100])

    ax3.set_yticklabels([])
    ax3.set_xticks([2800,2900,3000,3100])
    ax3.set_xticklabels([2800,2900,3000,3100])    
        
    flatFitObj = fitFlatClass(data,fig)
    
    promptStr = 'Welcome to the flat fitting module!\n'
    print promptStr
    
    while True:
        
        validResps = ['A','R','F','S','U','H',  # standard options
                      'AHARD','RHARD','REFINE', # hidden options
                      'W','D','Q']              # stardard ends 
        promptStr = 'Press (a) to add an exclusion region.\n'
        promptStr += 'Press (r) to remove a region.\n'
        promptStr += 'Press (f) to fit the exclusion regions.\n'
        promptStr += 'Press (s) to substitute model in exclusion regions.\n'
        promptStr += 'Press (h) to substitute the median profile in a region\n'
        promptStr += 'Press (u) to undo everything and restart.\n'
        promptStr += 'Press (w) to write the improved flat to disk.\n'
        promptStr += 'Press (d) to enter the debugger.\n'
        promptStr += 'Press (q) to quit and do nothing.\n'
        promptStr += 'Answer: '
        usrResp = raw_input(promptStr).strip().upper()
        
        if usrResp in validResps:
            
            # add region by marking it
            if usrResp == 'A':
                promptStr = 'Enter the name of the sky region (e.g. c1): '
                name = raw_input(promptStr).strip().upper()
                flatFitObj.add_fit_region(name)
                
            # add hardcoded region
            if usrResp == 'AHARD':
                promptStr = 'Enter name colLo colUp (e.g. c1 113 171): '
                usrResp = raw_input(promptStr).upper().strip()
                try:
                    name = usrResp.split()[0]
                    colLo = int(usrResp.split()[1])
                    colUp = int(usrResp.split()[2])
                    flatFitObj.add_fit_region(name,colLo=colLo,colUp=colUp)
                except Exception as e:
                    print e
                    
                    
            # remove
            if usrResp == 'R' or usrResp == 'RHARD':
                flatFitObj.remove_fit_region()
                
            # fit sky
            if usrResp == 'F':
                flatFitObj.fit_sky_background()
              
            # substitute model in sketchy regions  
            if usrResp == 'S':
                flatFitObj.subsitute_model_flat()
                
            if usrResp == 'U':
                flatFitObj = fitFlatClass(data,fig)
                flatFitObj.refresh_plot()
                
            if usrResp == 'H':
                flatFitObj.hard_mask()
                
            if usrResp == 'REFINE':
                # this substitutes the corrected
                # flat for the input data...
                # basically an experiment, not intended for use
                flatFitObj.refine()
            
            # write file
            if usrResp == 'W':
                promptStr = 'Enter name of save file (e.g. RESP_blue): '
                outFile = raw_input(promptStr).strip()
                promptStr = 'Write to file {} [y/n]: '.format(outFile)
                usrResp = raw_input(promptStr).upper().strip()
                if usrResp == 'Y':
                    flatFitObj.save_flat(outFile)
                    break
                else:
                    print 'Ok, aborting save...'
            # debug
            if usrResp == 'D':
                pdb.set_trace()
            # quit
            if usrResp == 'Q':
                print 'Aborting...'
                break
        else:
            errStr = 'I don\'t understand, try again...'
            print errStr
    
    return 0
    
if __name__=='__main__':
    ''' Run parsing, then main '''
    args,kwargs = parse_cmd_args()
    main(*args,**kwargs)