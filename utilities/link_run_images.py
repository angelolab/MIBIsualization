"""
Link all FoV images of a run.

Utility script to link the BMP images of each FoV of a single run into a common
directory for a more efficient review of the run.

The `SAVE` flag has to be set to `True` before running.

The output of the script is
- one txt file with the input command parameters.
- one image link per FoV.

Run with:
    py link_run_images.py /path/to/rundir n_points
"""

import os, sys

#SAVE = True
SAVE = False

# save input command to file
if SAVE:
    f = open("input_cmd.txt", "x")
    f.write(f'{" ".join(sys.argv)}\n')
    f.close()

# get run dir from argument
run_dir = ''
if len(sys.argv) > 1:
    run_dir = sys.argv[1]
print(f'run dir: {run_dir}')

n_points = 2 # debug
if len(sys.argv) > 2:
    n_points = int(sys.argv[2])
print(f'Attempting loop over {n_points} points:')
for i in range(n_points):
    point_id = i + 1
    print()
    print(f'Going for point {point_id}')
    image_file = os.path.join(run_dir, f'Point{point_id}/RowNumber0/Depth_Profile0/Depth0/Image.bmp')
    cmd = f'ls {image_file}'
    print(cmd)
    if SAVE: os.system(cmd)
    cmd = f'ln -s {image_file} Image_point{point_id}.bmp'
    print(cmd)
    if SAVE: os.system(cmd)
