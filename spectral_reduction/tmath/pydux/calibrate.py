def calibrate(objectlist,gratcode,secondord,gratcode2):
    from astropy.io import fits
    import numpy as np
    from tmath.wombat.getmswave import getmswave
    from tmath.wombat.womscipyrebin import womscipyrebin
    from tmath.pydux.obs_extinction import obs_extinction
    #extinction terms from Allen, 3rd edition
    extwave= [2400.,2600.,2800.,3000.,3200.,3400.,3600.,3800., \
              4000.,4500.,5000.,5500.,6000.,6500.,7000.,8000., \
              9000.,10000.,12000.,14000.]
    extvals=[68.0,89.0,36.0,4.5,1.30,0.84,0.68,0.55,0.46,0.31, \
             0.23,0.195,0.170,0.126,0.092,0.062,0.048,0.039, \
             0.028,0.021]
    fluxfits=fits.open('fluxstar'+gratcode+'.fits')
    fluxstar=fluxfits[0].data
    fluxhead=fluxfits[0].header
    fluxwavezero=float(fluxhead['CRVAL1'])
    fluxwavedelt=float(fluxhead['CDELT1'])
    fluxwave=np.arange(len(fluxstar))*fluxwavedelt+fluxwavezero
    fluxairmass=float(fluxhead['AIRMASS'])
    fluxname=fluxhead['OBJECT']
    try:
        fluxnum=int(fluxhead['OBSNUM'])
    except KeyError:
        fluxnum=0
    if (secondord):
        fluxfits2=fits.open('fluxstar'+gratcode2+'.fits')
        fluxstar2=fluxfits[0].data
        fluxhead2=fluxfits[0].header
        fluxwavezero2=float(fluxhead2['CRVAL1'])
        fluxwavedelt2=float(fluxhead2['CDELT1'])
        fluxwave2=np.arange(len(fluxstar2))*fluxwavedelt2+fluxwavezero2
        fluxairmass2=float(fluxhead2['AIRMASS'])
        fluxname2=fluxhead2['OBJECT']
        try:
            fluxnum2=int(fluxhead2['OBSNUM'])
        except KeyError:
            fluxnum2=0
    observat=fluxhead['OBSERVAT'].strip().lower()
    sitefactor=obs_extinction(observat)
    infile=open(objectlist,'r')
    for msfile in infile:
        msfile=msfile.strip()
        if ('.fits' not in msfile):
            msfile=msfile+'.fits'
        multifits=fits.open(msfile)
        multispec=multifits[0].data
        mshead=multifits[0].header
        objectname=mshead['OBJECT']
        print('The object is: {}'.format(objectname))
        airmass=float(mshead['AIRMASS'])
        exptime=float(mshead['EXPTIME'])
        if (exptime < 1):
            exptime=1.0
        num_apertures=multispec.shape[1]
        num_bands=multispec.shape[0]
        wavearr=np.zeros((multispec.shape[2],multispec.shape[1]))
        if (secondord):
            multispec2=multispec.copy()
            mshead2=mshead.copy()
        for i in range(0,num_apertures):
            print('\nAperture {}:'.format(i+1))
            wave=getmswave(mshead,i)
            extinction=womscipyrebin(extwave,extvals,wave)
            extfactor=np.exp(extinction*sitefactor*airmass)
            fluxstartmp=womscipyrebin(fluxwave,fluxstar,wave)
            wdelt=wave[1]-wave[0]
            for j in range(0,num_bands):
                multispec[j,i,:]=multispec[j,i,:]*extfactor       #extinction
                multispec[j,i,:]=multispec[j,i,:]/fluxstartmp     #flux
                multispec[j,i,:]=multispec[j,i,:]/exptime         #adjust to time
                multispec[j,i,:]=multispec[j,i,:]*10**(-19.44)    #AB->fnu
                multispec[j,i,:]=multispec[j,i,:]*2.99792458e18/wave/wave #fnu->flm
            if (secondord):
                fluxstartmp2=womscipyrebin(fluxwave2,fluxstar2,wave)
                for j in range(0,num_bands):
                    multispec2[j,i,:]=multispec2[j,i,:]*extfactor       #extinction
                    multispec2[j,i,:]=multispec2[j,i,:]/fluxstartmp     #flux
                    multispec2[j,i,:]=multispec2[j,i,:]/exptime         #adjust to time
                    multispec2[j,i,:]=multispec2[j,i,:]*10**(-19.44)    #AB->fnu
                    multispec2[j,i,:]=multispec2[j,i,:]*2.99792458e18/wave/wave #fnu->flm
        msfile='c'+gratcode+msfile
        mshead.set('FLUX_Z',fluxairmass,'airmass of flux standard')
        mshead.set('FLUX_NUM',fluxnum,'obsnum of flux standard')
        mshead.set('FLUX_OBJ',fluxname,'id of flux standard')
        outhdu=fits.PrimaryHDU(multispec)
        hdul=fits.HDUList([outhdu])
        hdul[0].header=mshead.copy()
        hdul.writeto(msfile,overwrite=True)
        hdul.close()
        if (secondord):
            msfile='c'+gratcode2+msfile
            mshead2.set('FLX2_Z',fluxairmass,'airmass of flux second ord. standard')
            mshead2.set('FLX2_NUM',fluxnum,'obsnum of flux second ord. standard')
            mshead2.set('FLX2_OBJ',fluxname,'id of flux second ord. standard')
            outhdu=fits.PrimaryHDU(multispec2)
            hdul=fits.HDUList([outhdu])
            hdul[0].header=mshead2.copy()
            hdul.writeto(msfile2,overwrite=True)
            hdul.close()

    infile.close()
    fluxfits.close()
    if (secondord):
        fluxfits2.close()
    print('calibrate')
    print(objectlist,gratcode,secondord,gratcode2)
    return

