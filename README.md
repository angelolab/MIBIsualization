# MIBIsualization

Visualization tools for MIBItiff data.

**MIBItiff** is the data format used by [IONpath](https://www.ionpath.com) to store and visualize the processed [MIBIscope](https://www.ionpath.com/mibiscope/) data in the [MIBItracker](https://www.ionpath.com/mibitracker/).
It is basicaly a multipage tiff file with specific metadata information, relevant to the analysis of Multiplexed Ion Beam Imaging (MIBI) data.
For details about the MIBItiff format, visit IONpath's [mibitracker-client](https://github.com/ionpath/mibitracker-client) open source repository in Github, especially the [MibiImage](https://github.com/ionpath/mibitracker-client/blob/master/MibiImage_Tutorial.ipynb) jupyter notebook tutorial.

This repository contains two modules:

### mibisualization

This is the main module of the repository. This module contains the tools necessary for the visualization of MIBItiff files.

This module contains a python source file with helper functions in order to plot MIBItiff data and a few jupyter notebooks that:
1. demonstrate how to use the helper functions.
2. help with the visualization of the several steps of the low level analysis (background subtraction and image cleaning) of the MIBI data.

The notebooks are particularly useful to visualize the data coming out from the MIBI/O (a.k.a. mibio) analysis software from IONpath or the MIBItracker.

### interface_mibio

This is a secondary module of the repository. This modue is in charge of interfacing the MIBI/O (a.k.a. mibio) via the command line interface, using system calls.

This module is only intended for advanced users. It contains a single python file that builds the system calls to mibio. There are many parameters that can be configured inside the script.

In order to install and use this module, only the script inside the module and a regular python3 installation are required (no conda is necessary). The following sections refer to the main module of this repository.

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
