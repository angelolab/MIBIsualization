"""
User-defined parameters necessary to run MIBI/O.

The list of parameters includes parameters:
 - specific to the installation of MIBI/O.
 - specific to the analysis, i.e. parameters to pass to the MIBI/O system call.
 - specific for the control of the MIBI/O process.

TODO: the parameters could be as well specified in another format, i.e. json or
xml file, instead of a python file.
"""

import pathlib

mibio_path =                        pathlib.Path('/path/to/mibio/executable')
mibio_helper_files_dir_path =       pathlib.Path('/usually__~/.mibio')

data_path =                         pathlib.Path('/path/to/data')
xml_path =                          data_path.joinpath('slide.xml')
panel_path =                        data_path.joinpath('panel.csv')
fovs =                              [1,2,3,5,8,13]

fov_size =                          500
remove_slide_bg =                   True
recalibrate_mass =                  False

# mass window
mass_start = -0.3
mass_stop = 0

# good parameter set: {ev: 1000000, au: 50, ta: 20}
use_default_slide_bg_removal_pars = False
bg_thresholds_ev =                  [0,20,50,70,1000000] if not use_default_slide_bg_removal_pars else [0.2]
bg_thresholds_au =                  [0,25,50,75,100] if not use_default_slide_bg_removal_pars else [50]
bg_thresholds_ta =                  [0,10,20,30,40] if not use_default_slide_bg_removal_pars else [20]
bg_removal_types =                  ['events', 'Au', 'Ta']

# safe timeouts around 180 times the number of fovs
timeout_sec =                       180*len(fovs)
n_trials =                          3
