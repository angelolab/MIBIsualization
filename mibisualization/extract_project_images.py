"""
Script to extract PNG images from all channels of all FOVs of a project.

This script takes an FOV list and a folder of MIBItiff files  as input and
extracts one image per FOV per channel and saves it as a PNG file.
The images are stored in a subfolder of the input MIBItiff folder called PNGs.
Inside, one folder per FOV will be saves, containing one PNG image per channel.
"""

import os

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from mibidata import tiff
from mibisualization import visualize_data as viz

mpl.use('Agg') # non-interactive backend

#SAVE_OUTPUT = True
SAVE_OUTPUT = False

FOV_list_file = 'output_files/FOV_List.csv'
#panel_file = '' # not needed for now

input_path = 'output_files/MIBItiff'

output_path = os.path.join(input_path, 'PNGs')

# ensure that the output path does not exist
if SAVE_OUTPUT:
    if os.path.exists(output_path):
        raise FileExistsError(f'Output folder {output_path} exists! '
                              'Exiting to avoid overwriting.')
    else:
        print(f'Creating output folder {output_path}')
        os.makedirs(output_path)

# read FOV list
df_fov_list = pd.read_csv(FOV_list_file)
print(df_fov_list)

# select channels
#a_masses = np.array([98, 113])
a_masses = None # use all masses

if a_masses is None:
    # use all channels
    a_masses = np.arange(10, 220)

a_masses.sort()
print(f'a_masses = {a_masses}')

# dark plot style
plt.style.use('dark_background')

# loop over FOVs
for fov in df_fov_list['FOV Name']:
    print(f'\nGoing for FOV {fov}')

    # open input images
    image_path = os.path.join(input_path, f'{fov}.tiff')
    print(f'file: {image_path}')
    image = tiff.read(image_path)
    print(f'channels {sorted(image.channels)}') # sorted by mass

    if SAVE_OUTPUT:
        output_path_fov = os.path.join(output_path, fov)
        print(f'Creating output folder {output_path_fov}')
        os.makedirs(output_path_fov)

    # loop over channels
    for ch_order, channel in enumerate(sorted(image.channels)):
        mass = channel[0]
        target = channel[1]

        if mass in a_masses: # selected channels
            print()
            print(f'\nchannel {ch_order}: mass {mass}, target {target}')

            im = image[mass]
            counts = im.sum()
            ax, img, fig = viz.plot_image(im,
                                     ax=None,
                                     title=f'{fov} ({mass}, \'{target}\')' + ' ' + str("{:.2e}".format(counts)),
                                     brighten_image=True, hi_res=False)
            plt.tight_layout()
            if SAVE_OUTPUT:
                png_file = os.path.join(output_path_fov,
                                        f'{fov}_{mass}_{target}.png')
                print(f'Saving image to {png_file}')
                plt.savefig(png_file, dpi=300)
            plt.close(fig) # save memory
