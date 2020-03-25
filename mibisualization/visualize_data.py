import os
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from mibidata import tiff, mibi_image as mi, combine_tiffs

#GRAPH_DEBUG = 1
GRAPH_DEBUG = 0

#SAVE = True
SAVE = False

# known masses
mass_NA = 22.99
mass_Y = 88.91
mass_TA = 180.95
mass_AU = 196.97
# ref: https://en.wikipedia.org/wiki/Periodic_table

# TODO: implement unit tests at least for the utility functions!!!


def get_know_masses_df():
    """Build a dataframe containing the atomic masses of know elements.

    Returns
    -------
    df_known_masses : `~pandas.DataFrame`
        Dataframe containing the atomic masses of know elements.
    """

    l_dict_known_masses = [{'Element': 'Na', 'Mass': mass_NA},
                           {'Element': 'Y', 'Mass': mass_Y},
                           {'Element': 'Ta', 'Mass': mass_TA},
                           {'Element': 'Au', 'Mass': mass_AU}]
    df_known_masses = pd.DataFrame(l_dict_known_masses)
    return df_known_masses


def plot_toggle_image(data1, data2, title='', ax=None,
                      brighten_image=False, hi_res=False,
                      style_kwargs=None):
    """Plot 2-D toggle image.

    Plot 2 images in the same axes and allow the user to toggle between them by
    pressing the 't' key. The user might need to click on the image first in
    order for the toggle to work.

    Parameters
    ----------
    data1 : `~numpy.ndarray`
        2-D image data to plot. This image will be visible at the beginning.
    data2 : `~numpy.ndarray`
        2-D image data to plot. This image will be hidden until toggling.
    title : str, optional
        Title for the plot.
    ax : `~matplotlib.axes.Axes`, optional
        Axes of the figure for the plot.
    brighten_image: bool, optional
        If activated, a gamma correction of 1/2 is applied to the image. In this
        case, the color scale is not meaningful, so no color scale bar is shown.
    hi_res: bool, optional
        This parameter controls the size and resolution of the plotted image:
        * False will set the size to 8x8 (medium size image).
        * True wil set the resolution to 250 dpi (large image).
    style_kwargs : dict, optional
        Style options for the plot.

    Returns
    -------
    ax2 : `~matplotlib.axes.Axes`
        Axes of the figure containing the plot of the 2 images.
    """

    ax1, im1 = plot_image(data1, ax=ax,
                          title=title,
                          brighten_image=brighten_image,
                          hi_res=hi_res, style_kwargs=style_kwargs)
    plt.ioff() # deactivate interactive mode in order not to show the next plot
    # and avoid empty white space in the jupyter notebook (probably not
    # necessary for pure python code)
    ax2, im2 = plot_image(data2, ax=ax1,
                          title=title,
                          brighten_image=brighten_image,
                          hi_res=hi_res, style_kwargs=style_kwargs)
    plt.ion() # turn interactive mode back on to be able to toggle
    im2.set_visible(False)

    def toggle_images(event):
        """Toggle the visible state of the two images via the 't' key."""

        # TODO: toggle also the visibility of the z axis color bar!!!
        # TODO: toggle also the plot title!!! (I could have different titles
        #       for each image!!!)

        if event.key != 't':
            return
        b1 = im1.get_visible()
        b2 = im2.get_visible()
        im1.set_visible(not b1)
        im2.set_visible(not b2)
        plt.draw()

    plt.connect('key_press_event', toggle_images)

    plt.show()

    return ax2


def plot_image(data, title='', ax=None,
               brighten_image=False, hi_res=False,
               style_kwargs=None):
    """Plot 2-D image.

    Parameters
    ----------
    data : `~numpy.ndarray`
        2-D image data to plot.
    title : str, optional
        Title for the plot.
    ax : `~matplotlib.axes.Axes`, optional
        Axes of the figure for the plot.
    brighten_image: bool, optional
        If activated, a gamma correction of 1/2 is applied to the image. In this
        case, the color scale is not meaningful, so no color scale bar is shown.
    hi_res: bool, optional
        This parameter controls the size and resolution of the plotted image:
        * False will set the size to 8x8 (medium size image).
        * True wil set the resolution to 250 dpi (large image).
    style_kwargs : dict, optional
        Style options for the plot.

    Returns
    -------
    ax : `~matplotlib.axes.Axes`
        Axes of the figure containing the plot.
    image : `~matplotlib.image.AxesImage`
    """
    # create plot
    if not hi_res:
        fig = plt.figure(figsize=(8, 8)) # medium size images
    else:
        #fig = plt.figure(dpi=300) # high resolution (very large images)
        fig = plt.figure(dpi=250) # medium-high resolution (large images)
    do_not_close_fig = False
    if ax is None:
        ax = fig.add_subplot(111)
        # if no axis object is passed by ref, the figure should remain open
        do_not_close_fig = True
    if style_kwargs is None:
        style_kwargs = dict()

    if not 'cmap' in style_kwargs:
        style_kwargs['cmap'] = 'afmhot'

    print(f'counts: {data.sum()}')

    # image might need some brightening method to enhance contrast
    if (brighten_image):
        # apply gamma
        data = np.power(data, 1/2)
        #data = np.power(data, 0.3)
        # in this case, the color scale is not meaningful

    image = ax.imshow(data,
                      origin='upper', # same as image raster order
                      interpolation='none',
                      **style_kwargs)
    # TODO: specify pixels/binning!!!
    # TODO: check if there are any plotting/display tools from
    #       mibitracker_client that we can use!!!

    # set title and axis names
    ax.set_title(title)
    #ax.set_xlabel('x / pixel')
    #ax.set_ylabel('y / pixel')

    if not brighten_image:
        # draw color scale bar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(image, cax=cax, label='counts')

    if not do_not_close_fig:
        # close figure to avoid white canvases
        plt.close(fig)
    return ax, image


def read_spectrum_from_csv(spectrum_file):
    """Read spectrum from a csv file and convert to appropriate format.

    Parameters
    ----------
    spectrum_file : str
        path to csv file containing the spectrum.

    Returns
    -------
    spectrum_df : `~pandas.DataFrame`
        spectrum table with columns of bins, counts (optional, mass).
    """
    spectrum_df = pd.read_csv(spectrum_file, index_col='bin')

    try:
        spectrum_df['counts']
    except KeyError:
        try:
            spectrum_df['count']
        except KeyError:
            depth_cols = [col for col in spectrum_df.columns if 'Depth' in col]
            spectrum_df['counts'] = spectrum_df[depth_cols].sum(axis=1)
            spectrum_df.drop(depth_cols, axis=1, inplace=True)
    # TODO: try to avoid nested try-except blocks!!!

    return spectrum_df


def plot_spectrum(spectrum_df, plot_mass=False, title='', ax=None,
                  plot_wide=False, style_kwargs=None):
    """Plot spectrum.

    Parameters
    ----------
    spectrum_df : `~pandas.DataFrame`
        spectrum table with columns of bins, counts (optional, mass).
    plot_mass: bool, optional
        Wether to plot mass spectrum or TOF bin spectrum.
    title : str, optional
        Title for the plot.
    ax : `~matplotlib.axes.Axes`, optional
        Axes of the figure for the plot.
    plot_wide: bool, optional
        Wether to make plot wide or not.
    style_kwargs : dict, optional
        Style options for the plot.

    Returns
    -------
    ax : `~matplotlib.axes.Axes`
        Axes of the figure containing the plot.
    """
    # create plot
    if not plot_wide:
        fig = plt.figure(figsize=(8, 6))
    else:
        fig = plt.figure(figsize=(18, 4))
    do_not_close_fig = False
    if ax is None:
        ax = fig.add_subplot(111)
        # if no axis object is passed by ref, the figure should remain open
        do_not_close_fig = True
    if style_kwargs is None:
        style_kwargs = dict()

    print(f'counts: {spectrum_df.counts.sum()}')

    if not plot_mass:
        spectrum_im = ax.plot(spectrum_df.counts,
                              **style_kwargs)
    else:
        spectrum_im = ax.plot(spectrum_df['m/z'], spectrum_df.counts,
                              **style_kwargs)

    # set title and axis names
    ax.set_title(title)
    if not plot_mass:
        ax.set_xlabel('TOF bin')
    else:
        ax.set_xlabel('m/z')
    ax.set_ylabel('counts')

    # eventually close figure to avoid white canvases
    if not do_not_close_fig:
        plt.close(fig)
    return ax


def read_panel_from_csv(panel_file, anonymize_targets=False):
    """Read panel from a csv file and convert to appropriate format.

    Parameters
    ----------
    panel_file : str
        path to csv file containing the panel.
    anonymize_targets: bool
        bool to anonymize panel, using the isotope as target label

    Returns
    -------
    panel_df : `~pandas.DataFrame`
        panel table
    """
    panel_df = pd.read_csv(panel_file)

    try:
        panel_df[['Mass', 'Target', 'Element']]
    except KeyError as e:
        print('Panel format not understood.')
        raise e

    panel_df = pd.read_csv(panel_file)

    if anonymize_targets:

        # keep only relevant columns
        panel_df = panel_df[['Mass', 'Target', 'Element']]

        # fill gaps

        # Xe 128 has typicaly the Element column empty
        try:
            target = panel_df['Target'][panel_df['Mass'] == 128].values[0]
            if (target == 'Xe128' and
                np.isnan(panel_df['Element'][panel_df['Mass'] ==
                                             128].values[0])):
                #print('Found Xe128') # debug
                panel_df['Element'][panel_df['Mass'] == 128] = 'Xe'
            else:
                print('Could not set element to Xe')
        except Exception as e:
            if panel_df['Element'][panel_df['Mass'] == 128].values[0] != 'Xe':
                print('Xe128 not found or error')
                raise e

        # encode element and mass into the target name
        # since i need to transform masses from int to str, I cannot simply add
        # the coumns, i need to apply a lambda funtion

        panel_df['Target'] = panel_df.apply(lambda x: x['Element'] +
                                            str(x['Mass']), axis=1)

    return panel_df


def read_isobaric_corrections(json_file, a_masses=None):
    """
    Read isobaric corrections json file.

    This function reads the isobaric corrections file in json format from
    MIBI/O and creates a dictionary of mass interferences.
    In the dictionary, the keys are masses of recipients and the values are
    lists of masses of donors to that recipient:
    {recipient1: [donor11, donor12, ...], recipient2: [donor21, donor22, ...],
    ...}

    If a list of masses is specified, only the corrections to those masses will
    be returned. If some of the specified masses are not in the json file,
    empty donor lists are returned for them.

    Parameters
    ----------
    json_file : str
        Path to the json file with the isobaric corrections. The following keys
        are required: 'RecipientMass', 'DonorMass'.
    a_masses : `~numpy.ndarray`, optional
        1-D array of selected masses to include in the dictionary.

    Returns
    -------
    dict_corrs : dict
        Dictionary containing the isobaric corrections.
    """
    with open(json_file) as jf:
        l_corrs = json.load(jf)

    dict_corrs = {}
    for corr in l_corrs:
        try:
            dict_corrs[corr['RecipientMass']].append(corr['DonorMass'])
        except KeyError:
            dict_corrs[corr['RecipientMass']] = [corr['DonorMass']]

    if a_masses is not None:
        dict_masses = {}
        for mass in a_masses:
            try:
                dict_masses[mass] = dict_corrs[mass]
            except KeyError:
                dict_masses[mass] = []
        dict_corrs = dict_masses

    return dict_corrs


def plot_1_fov(file_name, l_channel, ax=None, file_id=''):
    """Plot a selection of channels for one FoV.

    Parameters
    ----------
    file_name : str
        Path to MIBItiff file of the FoV to use for plotting.
    l_channel : list
        List of channels to plot.
    ax : `~matplotlib.axes.Axes`, optional
        Axes of the figure for the plot.
    file_id : str, optional
        File ID to use in the title for the plots.

    Returns
    -------
    ax : `~matplotlib.axes.Axes`
        Axes of the figure containing the plots.
    """

    print()
    print(f'Plotting file: {file_name}')
    print(f' File ID: {file_id}')

    image = tiff.read(file_name)

    # TODO: allow target name anonymization!!!

    # loop over channels
    for channel, axis in zip(l_channel, ax):
        # plot image
        print(f' Channel: {channel}')
        im = image[channel]
        counts = im.sum()
        plot_image(im, ax=axis, title=str(file_id) + ': ' + str(channel) +
                   ' ' + str("{:.2e}".format(counts)), brighten_image=True)
    if GRAPH_DEBUG > 3:
        plt.show() # wait until image is closed

    if GRAPH_DEBUG > 2:
        plt.show() # don't leave at the end

    return ax

###########################################################################

def main():
    """Main function.

    Define a list of FoV files and list of channels. A large canvas is created
    with plots of each channel for each FoV. Each row in the canvas represents
    one FoV and each column represents a channel.

    Activate the global variable 'SAVE' in order to save the figure as a png
    file.
    """

    data_path = os.path.expanduser('~/common/path/to/data')
    l_file_name = []
    l_file_label = []

    print()
    print('file 1: MIBI/O MIBItiff file')
    tiff_file = os.path.join(data_path, 'file1/specific/path/to/file.tiff')
    image = tiff.read(tiff_file)
    print(f'metadata {image.metadata}')
    print(f'channels {image.channels}')
    l_file_name.append(tiff_file)
    l_file_label.append('file')

    print()
    print('file 2: MATLAB combined MIBItiff file')
    # note: the matlab pipeline does not produce MIBItiffs, so the converter
    # has to be used first (see mibitracker-client/mibidata/combine_tiffs.py)
    input_folder = os.path.join(data_path, 'file2/specific/path/to/folder/with/TIFs')
    run_path = os.path.join(data_path, 'file2/specific/path/to/run_file.xml')
    point = 'Point0'
    panel_path = os.path.join(data_path, 'file2/specific/path/to/panel_file.csv')
    slide = '0'
    size = 500 #um
    combine_tiffs.create_mibitiffs(input_folder, run_path, point, panel_path,
                                   slide, size)
    # now the combined tiff file can be used to proceed as before
    tiff_file = os.path.join(input_folder, 'combined.tiff')
    image = tiff.read(tiff_file)
    print(f'metadata {image.metadata}')
    print(f'channels {image.channels}')
    l_file_name.append(tiff_file)
    l_file_label.append('matlab_file')

    l_channel = [89, 113, 115, 128, 146, 197]
    # l_target = ['89', '113', '115', 'Xe128', '146', '197'] # not used for now
    # TODO: function that takes the panel and a list of masses and returns a
    #       list of the corresponding targets!!!
    n_files_to_plot = len(l_file_name)
    n_channels_to_plot = len(l_channel)

    # TODO: allow target name anonymization!!!

    figsize = 6 # inch
    fig, ax = plt.subplots(n_files_to_plot, n_channels_to_plot,
                           figsize=(figsize*n_channels_to_plot,
                                    figsize*n_files_to_plot))

    # loop over files and produce the plots
    count_files = 0;
    for tiff_file_name, file_label in zip(l_file_name, l_file_label):
        if count_files < n_files_to_plot:
            #plot_1_fov(tiff_file_name, l_channel, ax[count_files],
            #           file_id=count_files)
            plot_1_fov(tiff_file_name, l_channel, ax[count_files],
                       file_id=file_label)
        count_files += 1

    # save ouptut
    if SAVE:
        output_file_name = 'plot_compare_extraction.png'
        print()
        print(f'Saving image to {output_file_name}')
        plt.savefig(output_file_name)

    if GRAPH_DEBUG > 1:
        plt.show() # don't leave at the end

###########################################################################

if GRAPH_DEBUG:
    plt.show() # don't leave at the end

if __name__ == "__main__":
    main()
