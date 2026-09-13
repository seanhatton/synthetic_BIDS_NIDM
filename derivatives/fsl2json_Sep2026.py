#!/usr/bin/env python3
#
# Export FSL FIRST/FAST statistics to JSON
#
# FIRST and FAST were run in separate subdirectories per subject
#   with default settings
# Expecting derivatives\fsl\sub-0x\ses-01\sub-0x_FIRST_all_fast_origsegs.nii.gz
#   derivatives\fsl\sub-0x\ses-01\sub-0x_FAST_pve_*.nii.gz
# Creating derivatives\fsl\sub-0x\ses-01\segstats.json
# Run the script from top of FSL derivative folder
# Version: 13 September 2025

import json, os, argparse, glob
import nibabel as nib
import numpy as np

#%% Parser
parser_features = argparse.ArgumentParser(
    description='Export FSL FIRST/FAST statistics to json',
    epilog='''
        Example usage: python fsl2json.py /path/to/fsl_derivatives
        ''')
parser_features.add_argument('indir',
                    metavar='i',
                    type=str,
                    help='the path to the FSL derivatives folder')
args_features = parser_features.parse_args()

def compute_stats(infile, low_thresh, high_thresh):
    """Compute voxel count and volume for given threshold range using nibabel."""
    img = nib.load(infile)
    data = img.get_fdata()
    mask = (data >= low_thresh) & (data <= high_thresh)
    voxels = int(np.count_nonzero(mask))
    volume = round(float(voxels * np.prod(img.header.get_zooms()) / 1e6), 1)
    return voxels, volume

FIRST_dict = {'Background': 0,
                'Left-Thalamus-Proper': 10,
                'Left-Caudate': 11,
                'Left-Putamen': 12,
                'Left-Pallidum': 13,
                'Left-Hippocampus': 17,
                'Left-Amygdala': 18,
                'Left-Accumbens-area': 26,
                'Right-Thalamus-Proper': 49,
                'Right-Caudate': 50,
                'Right-Putamen': 51,
                'Right-Pallidum': 52,
                'Right-Hippocampus': 53,
                'Right-Amygdala': 54,
                'Right-Accumbens-area': 58}
FAST_dict = {'csf': 0,
             'gray': 1,
             'white': 2}

wkdir = args_features.indir
os.chdir(wkdir)
subj_list = (glob.glob('sub-*'))

for subj in subj_list:
    print('##### Processing ' + subj + '#####')
    # Look for ses-01 subdirectory (or any session directory)
    sessions = glob.glob(subj + '/*-01')
    if not sessions:
        sessions = glob.glob(subj + '/*')
    if not sessions:
        print(f'No session directories found for {subj}')
        continue
    session = sessions[0]  # Use first session found
    
    infile = session + '/' + subj + '_FIRST_all_fast_origsegs.nii.gz'
    outfile = session + '/segstats.json'
    results_dict = {}

    ## FIRST results
    for roi,thresh in FIRST_dict.items():
        print('The ' + roi + ' ROI has a threshold of ' + str(thresh))
        if thresh == 0:
            l_thresh = 0
        else:
            l_thresh = thresh - 0.5
        u_thresh = thresh + 0.5
        voxels, volume = compute_stats(infile, l_thresh, u_thresh)
        results_dict[roi] = {'voxels': voxels, 'volume_ml': volume}
    ## FAST results
    for roi,pve in FAST_dict.items():
        print('Partial volume estimation for ' + roi)
        fastfile = session + '/' + subj + '_FAST_pve_' + str(pve) + '.nii.gz'
        voxels, volume = compute_stats(fastfile, 0.5, 1.0)
        results_dict[roi] = {'voxels': voxels, 'volume_ml': volume}
    ## Dump to JSON
    with open(outfile, 'w') as convert_file: 
        convert_file.write(json.dumps(results_dict, indent = 4))

print('Complete!')
