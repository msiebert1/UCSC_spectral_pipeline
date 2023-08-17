from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import copy
import glob
import scipy.stats as stats

def undo_sky_rejects(masked_data, original_data, tol=100):
    num_nan_arr = []
    for i, row in enumerate(masked_data):
        num_nan = len(np.isnan(row)[np.isnan(row)==True])
        num_nan_arr.append(num_nan)
        if num_nan>tol:
            for j, pix in enumerate(row):
                masked_data[i,j] = original_data[i,j]
    return masked_data


def expand_crs(masked_data):
    nan_pixels = np.isnan(masked_data)
    masked_data[:-1, :][nan_pixels[1:, :]] = np.nan
    masked_data[1:, :][nan_pixels[:-1, :]] = np.nan
    masked_data[:, :-1][nan_pixels[:, 1:]] = np.nan
    masked_data[:, 1:][nan_pixels[:, :-1]] = np.nan
    return masked_data


def cr_reject(imglist, img_combined, inst, lim=0.145):

    exp1 = fits.open(imglist[0])

    if 'lris' in inst['name']:
        exp1_time = exp1['PRIMARY'].header['TTIME']
        skytol=100
    if 'esi_echelle' in inst['name']:
        exp1_time = exp1['PRIMARY'].header['TTIME']
        skytol=100
    else:
        exp1_time = exp1['PRIMARY'].header['EXPTIME']
        skytol=20


    all_exp_cr_rej = []
    all_exp_times = []
    for i, img in enumerate(imglist[1:]):
        exp = fits.open(img)

        #change to counts/s, difference with first image, set likely crs to nan
        if 'lris' in inst['name']:
            exp_time = exp['PRIMARY'].header['TTIME']
        if 'esi_echelle' in inst['name']:
            exp_time = exp['PRIMARY'].header['TTIME']
        else:
            exp_time = exp['PRIMARY'].header['EXPTIME']
        diff = exp['PRIMARY'].data/exp_time - exp1['PRIMARY'].data/exp1_time
        lim = 20.0*stats.median_abs_deviation(diff.ravel())

        exp_masked_data = copy.deepcopy(exp['PRIMARY'].data/exp_time)
        exp_masked_data[diff>lim] = np.nan

        if i == 0:
            exp1_masked_data = copy.deepcopy(exp1['PRIMARY'].data/exp1_time)
            exp1_masked_data[diff<-1*lim] = np.nan
            exp1_masked_data = undo_sky_rejects(exp1_masked_data, exp1['PRIMARY'].data/exp1_time, tol=skytol)
            exp1_masked_data = expand_crs(exp1_masked_data)
            masked_data1 = np.ma.masked_array(exp1_masked_data, np.isnan(exp1_masked_data))
            all_exp_cr_rej.append(masked_data1)
            all_exp_times.append(exp1_time)

        #find rows with lots of rejections and undo (likely sky lines)
        exp_masked_data = undo_sky_rejects(exp_masked_data, exp['PRIMARY'].data/exp_time, tol=skytol)

        #expand nans to 1 pix around each rejected pixel
        exp_masked_data = expand_crs(exp_masked_data)

        #create np.ma arrau for average
        masked_data = np.ma.masked_array(exp_masked_data, np.isnan(exp_masked_data))

        all_exp_cr_rej.append(masked_data)
        all_exp_times.append(exp_time)

    final_data = np.sum(all_exp_times)*np.ma.average(all_exp_cr_rej, axis=0, weights=all_exp_times)

    # plt.figure(figsize=[20,20])
    # plt.imshow(final_data,  vmin=0, vmax=100, interpolation='none', origin='lower')
    # plt.show()

    final_data=np.asarray(final_data)
    imgHDU = fits.open(imglist[0])
    imgHDU['PRIMARY'].data = final_data
    imgHDU.writeto(img_combined, overwrite=True)


    # exp1_masked_data = copy.deepcopy(exp1['PRIMARY'].data)
    # exp1_masked_data[diff<-1*lim] = np.nan


