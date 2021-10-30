# MIBIsualization

Visualization tools for MIBItiff data.

**MIBItiff** is the data format used by [IONpath](https://www.ionpath.com) to store and visualize the processed [MIBIscope](https://www.ionpath.com/mibiscope/) data in the [MIBItracker](https://www.ionpath.com/mibitracker/).
It is basicaly a multipage tiff file with specific metadata information, relevant to the analysis of Multiplexed Ion Beam Imaging (MIBI) data.
For details about the MIBItiff format, visit IONpath's [mibitracker-client](https://github.com/ionpath/mibitracker-client) open source repository in Github, especially the [MibiImage](https://github.com/ionpath/mibitracker-client/blob/master/MibiImage_Tutorial.ipynb) jupyter notebook tutorial.

This repository contains several modules:

### mibisualization

This is the main module of the repository. This module contains the tools necessary for the visualization of MIBItiff files.

This module contains a python source file with helper functions in order to plot MIBItiff data and a few jupyter notebooks that:
1. demonstrate how to use the helper functions.
2. help with the visualization of the several steps of the low level analysis (background subtraction and image cleaning) of the MIBI data.

The notebooks are particularly useful to visualize the data coming out from the MIBI/O (a.k.a. mibio) analysis software from IONpath or the MIBItracker.
The notebooks are stored in a clean state, but can be run immediately to obtain meaningful plots that exemplify the usage of the visualization tools, using the data stored in the *sample_data* module.

### interface_mibio

This modue is in charge of interfacing the MIBI/O (a.k.a. mibio) program via the command line interface, using system calls.

This module is only intended for advanced users. It contains two python files:
* `control_mibio_process.py` builds the system calls to mibio and stores the output in a specific folder, according to the background selection specified in `params_bg.py`.
* `params_bg.py` defines parameters to be used by `control_mibio_process.py` in order to modify the system call to mibio. The parameters in this file are either installation-specific or analysis-specific.

In order to install and use this module, only the scripts inside the module and a regular python3 installation are required (no conda is necessary).

### sample_data

This module contains real MIBI data used within the notebooks of the *mibisualization* module.
The data represents one point (a.k.a. FoV or ROI) in one run (a.k.a. slide) and comes in the form of:
* MIBItiff files containing image data for each of the cleaning steps:
    - raw binned images (in subfolder `bg_none`).
    - slide bg removal (in subfolder `bg_au_050_ta_020`).
    - isobaric corrections (characterized only for channel 115; with suffix `-MassCorrected`).
    - denoising (with suffix `-Filtered`).
* CSV files containing panel information and spectral data.
* JSON files containing cleaning parameters: isobaric correction and denoising parameters.

The slide bg was removed using thresholds of 50 and 20 counts for the gold and tantalum channels respectively.

### utilities

This module contains utility scripts (tools) to help handle the data:
- `link_run_images.py`: python script to link all FoV images of a single run into a common directory.

## Installation

- Install the Python 3.7 version from [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
 - Clone the repository in your computer. If using a bash-like terminal:
 ```bash
cd <installation_dir>
git clone https://github.com/angelolab/MIBIsualization.git
cd MIBIsualization
 ```
 - Install the conda environment:
 ```bash
 conda env create -f environment.yml
```

## Usage

- Activate the conda environment with:
```bash
conda activate mibisualization
 ```
 - Start using the jupyter notebooks.
 - Optional: after finishing, to deactivate the conda environment, use:
 ```bash
 conda deactivate
 ```
