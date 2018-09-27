def fitspl(wave,flux,airlimit,fig):
    """fit spline to spectrum"""
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.interpolate import splrep,splev
    import tmath.wombat.womconfig as womconfig
    from tmath.wombat.womget_element import womget_element
    from tmath.pydux.wave_telluric import wave_telluric
    from tmath.wombat.yesno import yesno
    from tmath.wombat.onclick import onclick
    from tmath.wombat.onkeypress import onkeypress

#    global nsplinepoints, tmpsplptsx, tmpsplptsy, pflag
    
    # starting points for spline
    bandpts = np.array([3000, 3050, 3090, 3200, 3430, 3450, 3500, 3550, 3600, \
               3650, 3700, 3767, 3863, 3945, 4025, 4144, 4200, 4250, \
               4280, 4390, 4450, 4500, 4600, 4655, 4717, 4750, 4908, \
               4950, 5000, 5050, 5100, 5150, 5200, 5250, 5280, 5350, \
               5387, 5439, 5500, 5550, 6100, 6150, 6400, 6430, 6650, \
               6700, 6750, 6800, 7450, 7500, 7550, 8420, 8460, 8520, \
               8570, 8600, 8725, 8770, 9910, 10000, 10200, 10300, \
               10400, 10500, 10600, 10700])
    locsinrange=np.logical_and((bandpts > wave[10]),(bandpts < wave[-10]))
    useband=bandpts[locsinrange]
    for i,_ in enumerate(useband):
        index=womget_element(wave,useband[i])
        useband[i]=index
    # useband now has indices of wavelength positions

    if (min(flux) < 0):
        flux[np.where(flux < 0)]=0.0
    plt.cla()
    plt.plot(wave,flux,drawstyle='steps-mid',color='k')
    xmin,xmax=plt.xlim()
    ymin,ymax=plt.ylim()
    plt.xlim([xmin,xmax])
    plt.ylim([ymin,ymax])
    if (airlimit):
        loc=wave_telluric(wave,'high')
    else:
        loc=wave_telluric(wave,'low')
    #invert loc and convert all good sections to np.nan so they won't plot
    loc=np.invert(loc)
    wavetell=wave.copy()
    fluxtell=flux.copy()
    wavetell[loc]=np.nan
    fluxtell[loc]=np.nan
    plt.plot(wavetell,fluxtell,drawstyle='steps-mid',color='violet')
    womconfig.nsplinepoints=len(useband)
    womconfig.tmpsplptsx=wave[useband].copy().tolist()
    womconfig.tmpsplptsy=[]
    for i,_ in enumerate(useband):
        womconfig.tmpsplptsy.append(np.mean(flux[useband[i]-2:useband[i]+3]))
    spline=splrep(womconfig.tmpsplptsx,womconfig.tmpsplptsy,k=3)
    splineresult=splev(wave,spline)
    plt.cla()
    plt.plot(wave,flux,drawstyle='steps-mid',color='k')
    plt.plot(wavetell,fluxtell,drawstyle='steps-mid',color='violet')
    if (len(womconfig.tmpsplptsx) > 0):
        plt.plot(womconfig.tmpsplptsx,womconfig.tmpsplptsy,'ro')
        plt.plot(wave,splineresult,color='g')
    plt.xlabel('Wavelength')
    plt.ylabel('Flux')
    plt.xlim([xmin,xmax])
    plt.ylim([ymin,ymax])
    plt.pause(0.01)
    done=False
    print('Is this OK? ')
    answer=yesno('n')
    if (answer == 'y'):
        done = True
    while (not done):
        plotdone=False
        while (not plotdone):
            plt.cla()
            plt.plot(wave,flux,drawstyle='steps-mid',color='k')
            plt.plot(wavetell,fluxtell,drawstyle='steps-mid',color='violet')
            if (len(womconfig.tmpsplptsx) > 0):
                plt.plot(womconfig.tmpsplptsx,womconfig.tmpsplptsy,'ro')
                plt.plot(wave,splineresult,color='g')
            plt.xlabel('Wavelength')
            plt.ylabel('Flux')
            plt.xlim([xmin,xmax])
            plt.ylim([ymin,ymax])
            plt.pause(0.01)
            print('Change scale? ')
            answer=yesno('n')
            if (answer == 'y'):
                plt.cla()
                plt.plot(wave,flux,drawstyle='steps-mid',color='k')
                plt.plot(wavetell,fluxtell,drawstyle='steps-mid',color='violet')
                if (len(womconfig.tmpsplptsx) > 0):
                    plt.plot(womconfig.tmpsplptsx,womconfig.tmpsplptsy,'ro')
                    plt.plot(wave,splineresult,color='g')
                plt.xlabel('Wavelength')
                plt.ylabel('Flux')
                print('Click corners of box to change plot scale')
                newlims=plt.ginput(2, timeout=-1)
                xmin=newlims[0][0]
                ymin=newlims[0][1]
                xmax=newlims[1][0]
                ymax=newlims[1][1]
                plt.cla()
                plt.plot(wave,flux,drawstyle='steps-mid',color='k')
                plt.plot(wavetell,fluxtell,drawstyle='steps-mid',color='violet')
                if (len(womconfig.tmpsplptsx) > 0):
                    plt.plot(womconfig.tmpsplptsx,womconfig.tmpsplptsy,'ro')
                    plt.plot(wave,splineresult,color='g')
                plt.xlabel('Wavelength')
                plt.ylabel('Flux')
                plt.xlim([xmin,xmax])
                plt.ylim([ymin,ymax])
                plotdone=True
            else:
                plotdone = True
            
                
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        cid2 = fig.canvas.mpl_connect('key_press_event', onkeypress)
        print('\nClick on continuum points for spline fit.')
        print('Left button or (a)    = add point')
        print('Middle button or (s) = delete point')
        print('Right button or (d)  = done\n')
        womconfig.pflag=''
        while (womconfig.pflag != 'done'):
            plt.pause(0.01)
        fig.canvas.mpl_disconnect(cid)
        fig.canvas.mpl_disconnect(cid2)

        splptsy=[z for _,z in sorted(zip(womconfig.tmpsplptsx,womconfig.tmpsplptsy))]
        splptsx=sorted(womconfig.tmpsplptsx)
        spline=splrep(splptsx,splptsy,k=3)
        splineresult=splev(wave,spline)
        plt.plot(wave,splineresult,drawstyle='steps-mid',color='g')
        plt.pause(0.01)
        print('Is this fit OK? ')
        answer=yesno('y')
        if (answer == 'y'):
            done=True

    return splineresult

