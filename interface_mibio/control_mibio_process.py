"""
Script to launch the tiff generation step of MIBI/O (a.k.a. mibio).

The slide background (bg) subtraction is performed at this step, though it can
be turned off via the `remove_slide_bg` variable.

The script first edits the mibio config file to specify the corresponding
parameters for slide background removal and TIFF generation.
Then, it builds the system call with the corresponding command line options
and it creates a subprocess that launches mibio via the command line
interface (CLI).

Since mibio still opens the GUI and keeps it open after the
process is finished, the script waits for a period of time (controled by the
`timeout_sec` variable). After the time has finished, the script checks for
the existence of the output TIFF file and its integrity (in terms of file size
and file change). The program exits if the output TIFF is not generated or not
finished after the timeout. If the TIFF integrity check passes, a subfolder is
created for the output files from mibio. On top of that, the config and log
files from mibio are copied along in order to keep track of the parameters
used for the generation and bg subtraction.

The script can be used to define arrays of bg thresholds for the different
methods existing and make recursive calls of mibio to run each of the
combinations and store the result files into individual folders.

At the end, the output from the script and a copy of the script can be saved
into the output folder. Currently this has to be done manually.

Run with:
 py control_mibio_process.py
To save the output of the script, use
 py control_mibio_process.py > out.mibio.log 2>&1 &
If necessary, run using nohup.
"""

import os
import pathlib
import shutil
import shlex
from subprocess import Popen, PIPE
import time
#from shutil import copyfile
import json

#DEBUG = 0
DEBUG = 1


def relative_path(path, reference_path):
    """Build a path relative to another path."""
    # this function is hard coded; need to find common root and count common
    # dirs and non-common dirs
    relative_path = pathlib.Path('../../..').joinpath(path.relative_to('/home/user/path'))
    return relative_path


def run(mibio_path, mibio_cmd, timeout_sec, output_subdir_name, config_file_path, log_file_path, output_file_path):
    """Run one instance of mibio and save output."""
    # sanity check: the output file should not exist
    if output_file_path.exists():
        print(f'WARNING! output file {output_file_path} exists!!!')
        print('Terminating.')
        return 0
    # create log file to store output
    output_log_file_path = output_file_path.parent.joinpath('out.launch_mibio.log')
    output_log_file = open(output_log_file_path, 'w')
    # launch process
    # in winubuntu:
    # - I need to be in the mibio directory in order to launch it
    # - filepaths should be relative to mibio dir
    current_dir = os.getcwd()
    mibio_dir = str(mibio_path.parent)
    print(f'cd {mibio_dir}')
    output_log_file.write(f'cd {mibio_dir}\n')
    os.chdir(mibio_dir)
    cmd = mibio_cmd
    print(cmd)
    output_log_file.write(cmd + '\n')
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    print(f'process ID: {proc.pid}')
    output_log_file.write(f'process ID: {proc.pid}\n')
    print('cd -')
    output_log_file.write('cd -\n')
    os.chdir(current_dir)
    # wait for process to finish
    time.sleep(timeout_sec)
    # check that process finished (look for output files), otherwhise wait longer (try a few times - loop)
    # the output fle should exist and be non empty!!!
    n_trials = 3
    for i in range(n_trials):
        try:
            output_file_size = os.path.getsize(output_file_path)
            break
        except FileNotFoundError:
            output_file_size = -1
            time.sleep(timeout_sec/10)
    if DEBUG:
        print(f'trials: {i + 1}') #debug
        print(f'output file size: {output_file_size}') #debug
    if output_file_size <= 0:
        print('Failed')
        return 0
    # wait a few more seconds in case file writing is not complete
    time.sleep(timeout_sec/10)
    output_file_size = os.path.getsize(output_file_path)
    print(f'output file size: {output_file_size}')
    output_log_file.close
    # if process finished correctly: save output in a subfolder
    output_dir_path = output_file_path.parent.joinpath(output_subdir_name)
    print(f'mkdir {output_dir_path}')
    output_dir_path.mkdir()
    final_output_file_path = output_dir_path.joinpath(output_file_path.name)
    output_file_path.replace(final_output_file_path) # move file
    # save also output log file
    final_output_log_file_path = output_dir_path.joinpath(output_log_file_path.name)
    output_log_file_path.replace(final_output_log_file_path) # move file
    # save also config and log files
    final_config_file_path = output_dir_path.joinpath(config_file_path.name)
    shutil.copyfile(config_file_path, final_config_file_path) # copy file
    final_log_file_path = output_dir_path.joinpath(log_file_path.name)
    shutil.copyfile(log_file_path, final_log_file_path) # copy file
    # WARNING: the log being copied is the full mibio log, not just the specific part referring to this job
    return 1

# define parameters

# read environment variables
mibio_dir_path = pathlib.Path('/home/user/path/programs/mibio/v1.10.0')
#mibio_helper_files_dir_path = pathlib.Path('/home/user/path/programs/mibio/.mibio_win')
mibio_helper_files_dir_path = pathlib.Path('/home/user/.mibio') # linux version
data_path = pathlib.Path('/home/user/path/data')

# comand line intreface (CLI) options

#mibio_path = mibio_dir_path.joinpath('mibio-win32-v1.9.1-0-gbe9f133.exe')
#mibio_path = mibio_dir_path.joinpath('mibio-win32-v1.9.2-0-gcec3191.exe')
#mibio_path = mibio_dir_path.joinpath('mibio-win32-v1.10.0-0-g355b44b.exe')
mibio_path = mibio_dir_path.joinpath('mibio-linux-v1.10.0-0-g355b44b') # linux version

# project: XML, points, panel, FoV size
xml_path = data_path.joinpath('project/raw_data/run_name.xml')
fovs = 'point_name'
panel_path = data_path.joinpath('project/panel/Panel.csv')
fov_size = 500 # um

#use_default_mass_windows = True
use_default_mass_windows = False
remove_slide_bg = True
#remove_slide_bg = False
#recalibrate_mass = True
recalibrate_mass = False
#use_default_slide_bg_removal_pars = True
use_default_slide_bg_removal_pars = False
config_file_path = mibio_helper_files_dir_path.joinpath('mibio_config.json')
log_file_path = mibio_helper_files_dir_path.joinpath('mibio.log')
output_file_name = fovs.split('_')[0].split('-')[0] + '_RowNumber0_Depth_Profile0.tiff'
output_tiff_path = xml_path.parent.joinpath(xml_path.stem).joinpath(str(xml_path.stem) + '_TIFF')
if not output_tiff_path.is_dir():
    output_tiff_path.mkdir()
output_file_path = output_tiff_path.joinpath(output_file_name)

# config file options
# mass windows interval is applied to all masses in the panel
mass_windows_interval = (-0.3, 0.)
if use_default_mass_windows:
    mass_windows_interval = (-0.3, 0.3)
# bg removal types are all applied to the same TIFF file
# bg thresholds are used for different TIFF files
#bg_thresholds = [0.0, 1.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 150.0]
#bg_thresholds = [40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 150.0]
#bg_thresholds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#bg_thresholds = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]
#bg_thresholds = [0.0, 1.0, 5.0, 100.0, 150.0]
#bg_thresholds = [50.0]
#bg_thresholds_ev = [0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100]
#bg_thresholds_au = [0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100]
#bg_thresholds_ta = [0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100]
#bg_thresholds_ev = [100]
#bg_thresholds_au = [1]
#bg_thresholds_ta = [1]
bg_thresholds_ev = [1000000]
bg_thresholds_au = [50]
bg_thresholds_ta = [20]
#bg_removal_types = ['Au']
#bg_removal_types = ['Au', 'Ta']
bg_removal_types = ['Au', 'Ta']
#bg_removal_types = ['autoAu']
if use_default_slide_bg_removal_pars:
    bg_thresholds_ev = [0.2] # 20% of max
    bg_thresholds_au = [50]
    bg_thresholds_ta = [20]
    bg_removal_types = ['autoevents', 'events', 'Au', 'Ta']
# check integrity of bg removal types and the necessity for looping over thresholds
valid_bg_methods = ['events', 'Au', 'Ta', 'autoevents', 'autoAu', 'autoTa']
for bg_method in bg_removal_types:
    if bg_method not in valid_bg_methods:
        #print(f'Invalid bg method: {bg_method}')
        print('Failed')
        #return 0
        raise ValueError(f'Invalid bg method: {bg_method}')

if remove_slide_bg:
    print(f'Selected bg methods: {bg_removal_types}')

# loop over event thresholds
for bg_thres_ev in bg_thresholds_ev:
    print()
    if not remove_slide_bg:
        print('No bg removal selected.')
    elif remove_slide_bg and 'events' not in bg_removal_types:
        print('No looping over event thresholds required.')
    else:
        print(f'Looping over event threshold: {bg_thres_ev}')
    # loop over gold thresholds
    for bg_thres_au in bg_thresholds_au:
        print()
        if not remove_slide_bg:
            print('No bg removal selected.')
        elif remove_slide_bg and 'Au' not in bg_removal_types:
            print('No looping over gold thresholds required.')
        else:
            print(f'Looping over gold threshold: {bg_thres_au}')
        # loop over tantalum thresholds
        for bg_thres_ta in bg_thresholds_ta:
            print()
            if not remove_slide_bg:
                print('No bg removal selected.')
            elif remove_slide_bg and 'Ta' not in bg_removal_types:
                print('No looping over tantalum thresholds required.')
            else:
                print(f'Looping over tantalum threshold: {bg_thres_ta}')

            print()
            # edit config file
            with open(config_file_path, 'r+') as config_file:
                json_data = json.load(config_file)
                # select mass window
                json_data['Generator.DefaultMassStart'] = mass_windows_interval[0]
                json_data['Generator.DefaultMassStop'] = mass_windows_interval[1]
                # initialize the auto bg removal options (no bg removal)
                json_data['Generator.BackgroundRemovalAuto.events'] = False
                json_data['Generator.BackgroundRemovalAuto.197'] = False
                json_data['Generator.BackgroundRemovalAuto.181'] = False
                # initialize the bg thresholds (high threshold => no bg removal)
                json_data['Generator.BackgroundRemovalValue.events'] = 1000000
                json_data['Generator.BackgroundRemovalValue.197'] = 1000000
                json_data['Generator.BackgroundRemovalValue.181'] = 1000000
                # select slide bg removal type
                if not remove_slide_bg:
                    output_subdir_name = 'bg_none'
                else:
                    output_subdir_name = 'bg'
                    if use_default_slide_bg_removal_pars:
                        output_subdir_name += '_default'
                    if 'autoevents' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalAuto.events'] = True
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += '_autoevents'
                    if 'autoAu' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalAuto.197'] = True
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += '_autoau'
                    if 'autoTa' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalAuto.181'] = True
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += '_autota'
                    if 'events' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalValue.events'] = bg_thres_ev
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += f'_events_{bg_thres_ev:03}'
                    if 'Au' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalValue.197'] = bg_thres_au
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += f'_au_{bg_thres_au:03}'
                    if 'Ta' in bg_removal_types:
                        json_data['Generator.BackgroundRemovalValue.181'] = bg_thres_ta
                        if not use_default_slide_bg_removal_pars:
                            output_subdir_name += f'_ta_{bg_thres_ta:03}'
                config_file.seek(0)
                json.dump(json_data, config_file, indent=4)
                config_file.truncate()

            # build the command
            # in winubuntu:
            # - I need to be in the mibio directory in order to launch it
            # - filepaths should be relative to mibio dir
            #cmd = (str(mibio_path) + ' generate_tiff ' + str(xml_path) + ' ' + str(panel_path) + ' ' + str(fov_size) + ' --fovs ' + fovs)
            cmd = ('./' + str(mibio_path.name) + ' generate_tiff ' + str(relative_path(xml_path, mibio_path)) + ' ' + str(relative_path(panel_path, mibio_path)) + ' ' + str(fov_size) + ' --fovs ' + fovs)
            if remove_slide_bg:
                cmd += ' --remove_slide_background True'
            else:
                cmd += ' --remove_slide_background False'
            if recalibrate_mass:
                cmd += ' --mass_recal True'
            else:
                cmd += ' --mass_recal False'
            #if DEBUG:
            #    print(cmd) # debug

            # define timeout for program to finish
            # this should depend on the number of points to process ~ 1 min/point
            # probably less time should be fine; there is overhead of ~ 20 sec for opening mibio
            # it depends also on the number of bg types selected: use extra 30 sec per additional bg type
            # also, for large images (i.e. 2000x2000 pix, 800 um) it takes longer (activate 250 s/point)
            # the values below have n points, n bg meths hardcoded and are meant for 1 point
            #timeout_sec = 60
            timeout_sec = 90
            #timeout_sec = 120
            #timeout_sec = 150
            #timeout_sec = 250

            # launch the process and wait for it to finish
            job_status = run(mibio_path, cmd, timeout_sec, output_subdir_name, config_file_path, log_file_path, output_file_path)

            if job_status:
                print('job done')
            if not remove_slide_bg or 'Ta' not in bg_removal_types:
                # no need to loop over tantalum thresholds
                break
        if not remove_slide_bg or 'Au' not in bg_removal_types:
            # no need to loop over gold thresholds
            break
    if not remove_slide_bg or 'events' not in bg_removal_types:
        # no need to loop over event thresholds
        break

print('Finished loop over thresholds.')
