# Change bids_dir to appropriate BIDS root directory
bids_dir="PATH/TO/"
cd $bids_dir
# Create new directory for fMRIPrep output
mkdir derivatives
# Need to install with docker and have docker opened. Follow https://fmriprep.org/en/stable/installation.html (Docker or Singularity)
# Change participant to appropriate number. e.g. --participant-label 01
# Skip validation if necessary. Remove if BIDS validation required
# Change path to directory for FreeSurfer License location. For more information: https://fmriprep.org/en/stable/usage.html#fs-license 
fmriprep-docker $bids_dir $bids_dir/derivatives participant --participant-label 0_ --skip-bids-validation --fs-license-file PATH/TO/license.txt
# To alter fMRIPrep runs: https://fmriprep.org/en/stable/usage.html#the-command-line-interface-of-the-docker-wrapper 