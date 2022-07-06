import numpy as np
import os
import glob
from Xana import Xana
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
import time



def mask_streaks(ana, database_id, nbins=6, thres_quant=.99, qvalue=0.06, phiwidth=2., show=False):
    """Calculate a new mask that masks streaks.

    Args:
        nbins (int): the number of time bins. Instead of averaging all images, the function is
            looping ofer nbin time bins.
        thres: (float): the threshold to identify streaks.
        phiwidth (float): the angular width of a masked streak.
        show (bool): if a plot should be created showing the results.

    Returns:
        newmask (np.ndarray): the new mask.

    """

    newmask = ana.setup.mask.copy()

    nframes = ana.meta.loc[database_id, 'nframes']
    stepsize = nframes // nbins

    phimap = ana.setup.ai.chiArray()*180/np.pi

    for first in range(0,nframes-stepsize,stepsize):
        avr = ana.get_series(database_id, first=first, last=first+stepsize, verbose=False)
        avr = avr.mean(0)
        I, q, p = ana.setup.ai.integrate2d(avr, 200, mask=~newmask, method="cython", )
        qbin = np.argmin(np.abs(q-qvalue))
        thres = np.quantile(I[:,qbin], thres_quant)
        if not thres > np.std(I[:,qbin])+np.mean(I[:,qbin]):
            return newmask

        phiinds = I[:,qbin] > thres
        for phi in p[phiinds]:
            ind = (phimap < (phi+phiwidth/2)) & (phimap > (phi-phiwidth/2))
            newmask[ind] = 0

        if show:
            I, q, p = ana.setup.ai.integrate2d(avr, 200, mask=~newmask, method="cython", dummy=np.nan)
            if first == 0:
                fig, axs = plt.subplots(3, 1, figsize=(8,8), constrained_layout=True)

                a = axs.flat[1]
                my_cmap = plt.get_cmap('inferno')
                pc = a.imshow(I.T, norm=LogNorm(), extent=[p[-1], p[0], q[0], q[-1]], origin='lower', aspect="auto")
                a.hlines(qvalue, -150, 150, lw=2, ls='--', color='k')
                a.set_xlabel('phi')
                a.set_ylabel('q (nm-1)')

                a = axs.flat[0]
                avr[newmask==0] = np.nan
                im = a.imshow(avr, norm=LogNorm())

                a = axs.flat[2]
                ln, = a.plot(I[:,qbin], 'o', ms=2)
                a.hlines(thres, 0, 360, lw=2, ls='--', color='k')
                a.set_xlabel('phi')
                a.set_ylabel(f'intensity at q={q[qbin]:.2}nm-1')
                fig.canvas.draw()
                time.sleep(5)
            else:
                pc.set_data(I.T)

                avr[newmask==0] = np.nan
                im.set_data(avr)

                ln.set_ydata(I[:,qbin])
                axs.flat[2].autoscale()

            fig.canvas.draw()

    # if not os.path.isdir('./masks/'):
    #     os.mkdir('masks')
    # filename = f'./masks/mask_{database_id:06}.npy'
    # np.save(filename, newmask)
    # print(f"New mask saved as: {filename}")

    return newmask

