"""
Script to launch the tiff generation step of MIBI/O via the command line interface

The slide background (bg) subtraction is performed at this step, although it is 
toggleable via the `remove_slide_bg` variable

The script first edits the mibio config file to reflect the input parameters
for the slide background removal and TIFF generation, as found in `params_bg.py`
Then, it builds the system call with the corresponding command line options and
it creates a subprocess that launches mibio via the command line interface (CLI)

Since mibio still opens the GUI and keeps it open after the process is finished,
the script waits for a period of time (controlled by the `timeout_sec` variable).
After the time as finished, the script checks for the existence of the output TIFF
file and measures the change in its file size.  The program exits if the output
TIFF is not generated or not finished after the timeout. If the TIFF integrity
check passes, a subfolder is created for the output files from mibio. The config
and output log files from mibio are stored in this subfolder as well to keep track
of the parameters used for the generation and bg subtraction.

The script can be used to iteratively generate TIFFs over arrays of background
thresholds for different subtraction methods. This is accomplished via repeated
calls to the mibio CLI; TIFFs with different parameters are saved separately in
their corresponding subdirectory.

TODO: Add option to save parameter file in subdirectory (txt file will do)

Run with:
    py control_mibio_process.py
To save the output of the script, use:
    (nohup) py control_mibio_process.py > out.mibio.log 2>&1 &
To monitor progress while the script runs in the background, use:
    tail -f out.mibio.log
To stop process in nohup, use:
    kill -9 `PID`
where `PID` is the process id number output when starting nohup
"""

import sys
import pathlib
import shutil
import shlex
from subprocess import Popen, PIPE
import time
from datetime import datetime
import json
import xml.etree.ElementTree as ET

# inputs in 'params_bg.py'
import params_bg as params

# dictionary of background removal terms
bg_dict = {
    'events' : 'event',
    'Au' : 'gold',
    'Ta' : 'tantalum'
}

# printing background removal process
def print_loops(bg_removal_type : str, thresh):
    print()
    if not params.remove_slide_bg:
        print('No bg removal selected')
    elif params.remove_slide_bg and bg_removal_type not in params.bg_removal_types:
        print(f'No looping over {bg_dict[bg_removal_type]} thresholds required')
    else:
        print(f'Looping over {bg_dict[bg_removal_type]} threshold: {thresh}')

# editing config file before mibio call
def edit_config(bg_thres_ev,bg_thres_au,bg_thres_ta):
    with open(params.config_file_path, 'r+') as config_file:
        json_data = json.load(config_file)
        # select mass window
        json_data['Generator.DefaultMassStart'] = -0.3
        json_data['Generator.DefaultMassStop'] = 0.0
        # initialize the auto bg removal options (no bg removal)
        json_data['Generator.BackgroundRemovalAuto.events'] = False
        json_data['Generator.BackgroundRemovalAuto.197'] = False
        json_data['Generator.BackgroundRemovalAuto.181'] = False
        # initialize the bg thresholds (high threshold => no bg removal)
        json_data['Generator.BackgroundRemovalValue.events'] = 1000000
        json_data['Generator.BackgroundRemovalValue.197'] = 1000000
        json_data['Generator.BackgroundRemovalValue.181'] = 1000000
        # select slide bg removal type
        if not params.remove_slide_bg:
            output_subdir_name = 'bg_none'
        else:
            output_subdir_name = 'bg'
            if params.use_default_slide_bg_removal_pars:
                output_subdir_name += '_default'
            if 'autoevents' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalAuto.events'] = True
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += '_autoevents'
            if 'autoAu' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalAuto.197'] = True
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += '_autoau'
            if 'autoTa' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalAuto.181'] = True
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += '_autota'
            if 'events' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalValue.events'] = bg_thres_ev
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += f'_events_{bg_thres_ev:03}'
            if 'Au' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalValue.197'] = bg_thres_au
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += f'_au_{bg_thres_au:03}'
            if 'Ta' in params.bg_removal_types:
                json_data['Generator.BackgroundRemovalValue.181'] = bg_thres_ta
                if not params.use_default_slide_bg_removal_pars:
                    output_subdir_name += f'_ta_{bg_thres_ta:03}'
        config_file.seek(0)
        json.dump(json_data, config_file, indent=4)
        config_file.truncate()
        return output_subdir_name

# run call to mibio cli
def run(mibio_path : pathlib.Path, mibio_cmd : str, timeout_sec : float, output_subdir_name : str, config_file_path : pathlib.Path, log_file_path : pathlib.Path, output_file_path : pathlib.Path):
    # output file shouldn't exist
    if output_file_path.exists():
        print(f'WARNING! Output file {output_file_path} exists!')
        print('Terminating...')
        return 0

    # create log file
    output_log_file_path = output_file_path.parent.joinpath('out.launch_mibio.log')
    output_log_file = output_log_file_path.open(mode='r+')

    # redirect stdout+stderr to log file
    save_stdout, save_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = output_log_file

    # print date+time
    print(f'start date: {datetime.now()}')

    # print and run command
    print(mibio_cmd)
    proc = Popen(shlex.split(mibio_cmd), stdout=PIPE, stderr=PIPE)
    print(f'process ID: {proc.pid}')
    time.sleep(timeout_sec)

    # probe output file size for 'finish signal'
    output_file_size = 0
    for i in range(params.n_trials):
        try:
            output_file_size = output_file_path.stat().st_size
            break
        except FileNotFoundError:
            output_file_size = -1
            time.sleep(timeout_sec/10)
    if output_file_size <= 0:
        print('Failed')
        return 0
    time.sleep(timeout_sec/10)
    output_file_size = output_file_path.stat().st_size
    print(f'output file size: {output_file_size}')

    # redirect output to previous states
    sys.stdout, sys.stderr = save_stdout, save_stderr
    print(output_log_file.read())
    output_log_file.close()

    # copy/move relevant outputs to subdirectory
    output_dir_path = output_file_path.parent.joinpath(output_subdir_name)
    print(f'mkdir {output_dir_path}')
    output_dir_path.mkdir()
    final_output_file_path = output_dir_path.joinpath(output_file_path.name)
    output_file_path.replace(final_output_file_path)
    final_output_log_path = output_dir_path.joinpath(output_log_file_path.name)
    output_log_file_path.replace(final_output_log_path)
    final_config_file_path = output_dir_path.joinpath(config_file_path.name)
    shutil.copyfile(str(config_file_path), str(final_config_file_path))
    final_log_file_path = output_dir_path.joinpath(log_file_path.name)
    shutil.copyfile(str(log_file_path),str(final_log_file_path))
    # WARNING: the log being copied is the full mibio log, not just the log in relation to this job
    return 1

# main process - loops over bg arrays and assembles commands to mibio cli
def main():
    tree = ET.parse(str(params.xml_path))
    root = tree.getroot()

    fovs = []
    for fov_num in params.fovs:
        fovs.append(f"Point{fov_num}-{root[0][fov_num+3].attrib['PointName']}")
    if not params.output_tiff_path.is_dir():
        params.output_tiff_path.mkdir()
    
    valid_bg_methods = ['events', 'Au', 'Ta', 'autoevents', 'autoAu', 'autoTa']

    for bg_method in params.bg_removal_types:
        if bg_method not in valid_bg_methods:
            print('Failed')
            raise ValueError(f'Invalid bg method: {bg_method}')

    if params.remove_slide_bg:
        print(f'Selected bg methods: {params.bg_removal_types}')

    for bg_thres_ev in params.bg_thresholds_ev:
        print_loops('events',bg_thres_ev)
        for bg_thres_au in params.bg_thresholds_au:
            print_loops('Au',bg_thres_au)
            for bg_thres_ta in params.bg_thresholds_ta:
                print_loops('Ta', bg_thres_ta)
                print()
                output_subdir_name = edit_config(bg_thres_ev,bg_thres_au,bg_thres_ta)

                cmd = (str(params.mibio_path) + ' generate_tiff ' + str(params.xml_path) + ' ' + str(params.panel_path) + ' ' + str(params.fov_size) + ' --fovs ' + ' '.join(fovs))
                cmd += f' --remove_slide_background {params.remove_slide_bg}'
                cmd += f' --mass_recal {params.recalibrate_mass}'

                job_status = run(params.mibio_path, cmd, params.timeout_sec, output_subdir_name, params.config_file_path, params.log_file_path, params.output_file_path)

                if job_status:
                    print('Job Done')
                if not params.remove_slide_bg or 'Ta' not in params.bg_removal_types:
                    break
            if not params.remove_slide_bg or 'Au' not in params.bg_removal_types:
                break
        if not params.remove_slide_bg or 'events' not in params.bg_removal_types:
            break

    print('Finished loop over thresholds')

main()
