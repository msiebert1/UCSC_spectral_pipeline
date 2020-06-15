import copy
import sqlite3 as sq3
import matplotlib.pyplot as plt

class spectrum(object):
    """A generic class to represent a spectrum and its associated metadata
    """
    def __init__(self, wavelength = None, flux = None, err = None, meta_dict=None):
        self.wavelength = wavelength
        self.flux = flux
        self.err = err
        self.meta_dict = meta_dict


def grab_all_spec_data(sql_input, db_file = None):

    if db_file is None:
        db_file = glob.glob('*.db')[0]

    con = sq3.connect(db_file)
    print ("Collecting data from", db_file, "...")
    cur = con.cursor()

    spec_Array = []

    spec_table = cur.execute('PRAGMA TABLE_INFO({})'.format("SPECTRA"))
    spec_cols = [tup[1] for tup in cur.fetchall()]
    cur.execute(sql_input)
 
    spec_metadata = {}
    spec_list = []
    for row in cur:
        """retrieve spectral metadata.
        """
        for i, value in enumerate(row):
            if spec_cols[i] == 'RAW_FLUX':
                flux = np.frombuffer(value, dtype='>f8')
            elif spec_cols[i] == 'RAW_ERR':
                err = np.frombuffer(value, dtype='>f8')
            else:
                spec_metadata[spec_cols[i]] = value
        wave = np.arange(len(flux))*spec_metadata['WAVEDELT']+spec_metadata['MINWAVE']
        spec =  spectrum(wavelength=wave, flux=flux, err=err, meta_dict=spec_metadata)
        spec_list.append(copy.deepcopy(spec))
        
    for spec in spec_list:
        print(spec.meta_dict['FILENAME'])
    print (len(spec_list), 'Total Spectra found')
    return spec_list

def query_and_plot(sql_input):
    spec_list = grab_all_spec_data(query)
    plt.figure(figsize=[15,7])
    buff=0.3
    for i, nspec in enumerate(np.asarray(spec_list)):
        plt.plot(nspec.wavelength, nspec.flux - i*buff, drawstyle='steps-mid', label=nspec.meta_dict['FILENAME'])
        plt.fill_between(nspec.wavelength, nspec.flux - i*buff - nspec.err, nspec.flux - i*buff + nspec.err, color = 'gray')
        plt.legend(fontsize=15, loc=1)
    plt.show() 

