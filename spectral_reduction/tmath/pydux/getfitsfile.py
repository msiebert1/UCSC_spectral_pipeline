def getfitsfile(name,fitstype):
    from astropy.io import fits
    done=False
    while (not done):
        inputfile=input('Name of fits file for the {}? ({} added if necessary) '.format(name,fitstype))
        inputfile=inputfile.strip()
        if (fitstype not in inputfile):
            inputfile=inputfile+fitstype
        try:
            fitsdata=fits.open(inputfile)
        except OSError:
            print('File {} cannot be opened.'.format(inputfile))
        else:
            fitsdata.close()
            done=True
    return inputfile

