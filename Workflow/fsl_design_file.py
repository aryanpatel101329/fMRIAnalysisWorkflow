#!/usr/bin/env python3
# Libraries used
import confound_extraction
import json
import nibabel as nib
import numpy as np
import os
import pandas as pd
import pathlib

# USER NOTE: Code only adapted for BIDS format without multiple subjects, sessions, tasks or runs.
# USER NOTE: LOAD design.fsf into FSL for more Contrast Analysis

# USER INPUT: Enter the relative path for the BIDS root directory
bids_dir = "Checkerboard"
# USER INPUT: Enter the relative path from 'bids_dir' to unprocessed 'func' directory (e.g. sub-01/func/)
func_dir = "/sub-01/func/"

# Full working directory
workdir = str(pathlib.Path().resolve())

# Import template for design.fsf file. 
design_file = "design.fsf"

## Make new directory for FSL output
os.mkdir(bids_dir + "FSL")

### Manipulate design.fsf file. Assumes only one subject & one task. ###
# Read fsf file to convert each line into a list
with open(design_file, "r") as fsf:
    data = fsf.readlines()

## Finds derivative BOLD images & Confounds files in BIDSDIR
imagedir = bids_dir + "/derivatives" + func_dir
for filename in os.listdir(imagedir):
    if filename.endswith("bold.nii.gz"):
        img = filename
    elif filename.endswith("bold.json"):
        img_desc = filename
    elif filename.endswith("confounds_timeseries.tsv"):
        confounds = filename

## TR [JSON Find & Place]
with open(imagedir + img_desc, "r") as TR:
    TR_data = json.load(TR)
    rep_time = TR_data['RepetitionTime']

## Number of Volumes [Number of lines in TSV file]
timeseries = pd.read_csv(imagedir + confounds, sep = "\t")
volumes = timeseries.shape[0]

## Number of EVs (Tasks)
# Create directory for all event text files
os.mkdir("Events")

for filename in os.listdir(bids_dir + func_dir):
    if filename.endswith("events.tsv"):
        raw_events = filename

# Read events file
events_file = pd.read_csv(bids_dir + func_dir + raw_events, sep = "\t")
# Get all unique event types
events = list(dict.fromkeys(events_file["trial_type"]))

# Create the text file for each event's onset and duration times
for event in events:
    events_copy = events_file[events_file["trial_type"] == event]
    events_copy["trial_type"] = 1
    events_copy.to_csv("Events/" + event + ".txt", sep = "\t", header = False, index = False)

# The number of event files created (or the total number of EVs for FSL analysis)
total_events = len(events)

## Total Voxels
bold_img = nib.load(imagedir + img)
dimensions = bold_img.header["dim"][1:5]
total_voxels = np.prod(dimensions)

## fMRIPrep Confounds File
confound_extraction.confound_extraction(imagedir + confounds, workdir, confounds)


# Changes the design.fsf file for FSL
for i, line in enumerate(data):
    # Changes Output Folder
    if "set fmri(outputdir)" in line:
        data[i] = "set fmri(outputdir) \"" + workdir + "/" + bids_dir + "FSL\"\n"

    # Changes Input 4D Image
    if "set feat_files(1) " in line:
        data[i] = "set feat_files(1) \"" + workdir + "/" + imagedir + img[:-7] + "\"\n"
    
    # Changes TR (Repitition Time)
    if "set fmri(tr)" in line:
        data[i] = "set fmri(tr) " + str(float(rep_time)) + "\n"

    # Change the number of Volumes (Total BOLD Images)
    if "set fmri(npts)" in line:
        data[i] = "set fmri(npts) " + str(volumes) + "\n"

    # Number of Contrasts (Assuming Identity Design Matrix) & EVs
    if "set fmri(evs_orig) " in line:
        data[i] = "set fmri(evs_orig) " + str(total_events) + "\n"
    if "set fmri(evs_real) " in line:
        data[i] = "set fmri(evs_real) " + str(2 * total_events) + "\n"
    if "set fmri(ncon_orig) " in line:
        data[i] = "set fmri(ncon_orig) " + str(total_events) + "\n"
    if "set fmri(ncon_real) " in line:
        data[i] = "set fmri(ncon_real) " + str(total_events)  + "\n"

    # Change the number of Total Voxels
    if "set fmri(totalVoxels)" in line:
        data[i] = "set fmri(totalVoxels) " + str(total_voxels) + "\n"

    # Change the additional confounds file
    if "set confoundev_files(1) " in line:
        data[i] = "set confoundev_files(1) \"" + workdir + "/" + "confounds_timeseries.txt\"\n"
        break


## Multi-line Changes

# Use i (index) from previous for loop; EV creation is after confound EV file path declaration
i += 1
## EV Creation (Each Iteration = New EV)
for ev_num, ev_name in enumerate(events):
    
    ev_template = f"""
# EV {ev_num + 1} title
set fmri(evtitle{ev_num + 1}) "{ev_name}"

# Basic waveform shape (EV {ev_num + 1})
# 0 : Square
# 1 : Sinusoid
# 2 : Custom (1 entry per volume)
# 3 : Custom (3 column format)
# 4 : Interaction
# 10 : Empty (all zeros)
set fmri(shape{ev_num + 1}) 3

# Convolution (EV {ev_num + 1})
# 0 : None
# 1 : Gaussian
# 2 : Gamma
# 3 : Double-Gamma HRF
# 4 : Gamma basis functions
# 5 : Sine basis functions
# 6 : FIR basis functions
# 8 : Alternate Double-Gamma
set fmri(convolve{ev_num + 1}) 3

# Convolve phase (EV {ev_num + 1})
set fmri(convolve_phase{ev_num + 1}) 0

# Apply temporal filtering (EV {ev_num + 1})
set fmri(tempfilt_yn{ev_num + 1}) 1

# Add temporal derivative (EV {ev_num + 1})
set fmri(deriv_yn{ev_num + 1}) 1

# Custom EV file (EV {ev_num + 1})
set fmri(custom{ev_num + 1}) "{workdir}/Events/{ev_name}.txt"
"""
    # Insert used to not overwrite other lines
    data.insert(i, ev_template)

    # Next Index/Line in design.fsf for Orthogonalisation Declaration (Always False)
    i += 1

    for j in range(len(events) + 1):
        ev_orthogonalise = f"""
# Orthogonalise EV {ev_num + 1} wrt EV {j}
set fmri(ortho{ev_num + 1}.{j}) 0
"""
        data.insert(i, ev_orthogonalise)

        # Next Index/Line in design.fsf
        i += 1


## Contrast Creation / Multi-line changes the design.fsf file for FSL
for i, line in enumerate(data):
    # Index for Contrasts
    if "set fmri(con_mode) orig" in line:
        break

# Next Index/Line in design.fsf
i += 1

# Contrast Real
for contrast_num, contrast_name in enumerate(events):
    contrast__real_base = f"""
# Display images for contrast_real {contrast_num + 1}
set fmri(conpic_real.{contrast_num + 1}) 1

# Title for contrast_real {contrast_num + 1}
set fmri(conname_real.{contrast_num + 1}) "{contrast_name}"
"""
    data.insert(i, contrast__real_base)

    # Next Index/Line in design.fsf
    i += 1

    for real_ev in range(2 * total_events):
        if (real_ev == (2 * contrast_num)):
            design_value = 1
        else:
            design_value = 0

        contrast_real_template = f"""
# Real contrast_real vector {contrast_num + 1} element {real_ev + 1}
set fmri(con_real{contrast_num + 1}.{real_ev + 1}) {design_value}
"""
        data.insert(i, contrast_real_template)

        # Next Index/Line in design.fsf
        i += 1


# Contrast Original
for contrast_num, contrast_name in enumerate(events):
    contrast_orig_base = f"""
# Display images for contrast_orig {contrast_num + 1}
set fmri(conpic_orig.{contrast_num + 1}) 1

# Title for contrast_orig {contrast_num + 1}
set fmri(conname_orig.{contrast_num + 1}) "{contrast_name}"
"""
    data.insert(i, contrast_orig_base)

    # Next Index/Line in design.fsf
    i += 1
    
    for orig_ev in range(total_events):
        if (orig_ev == contrast_num):
            design_value = 1
        else:
            design_value = 0

        contrast_orig_template = f"""
# Real contrast_orig vector {contrast_num + 1} element {orig_ev + 1}
set fmri(con_orig{contrast_num + 1}.{orig_ev + 1}) {float(design_value)}
"""
        data.insert(i, contrast_orig_template)

        # Next Index/Line in design.fsf
        i += 1


## F-Test Creation [Not Applicable, but required to make blank declarations]
for i, line in enumerate(data):
    if "set fmri(conmask_zerothresh_yn) 0" in line:
        i += 1
        data[i] = "\n"
        break

# Only Identity Design Matrix Applied
for current_ftest in range(1, total_events + 1):
    for mask_ftest in range(1, total_events + 1):

        ftest_template = f"""
# Mask real contrast/F-test {current_ftest} with real contrast/F-test {mask_ftest}?
set fmri(conmask{current_ftest}_{mask_ftest}) 0
"""
        # Only compares different contrasts (e.g. 1-2, 1-3, 2-1, 2-3, 3-1, 3-2)
        if (current_ftest != mask_ftest):
            data.insert(i, ftest_template)
            i += 1

contrast_masking = f"""
# Contrast masking - use >0 instead of thresholding?
set fmri(conmask_zerothresh_yn) 0
"""

data.insert(i, contrast_masking)

## Execute all changes to the design.fsf file
with open(design_file, "w") as file: 
    file.writelines(data)
# NOTE: Use dos2unix if going from Windows to Linux.
