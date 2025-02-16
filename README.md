# fMRIAnalysisWorkflow
 Using fMRIPrep for preprocessing, and FSL for postprocessing; statistical images from fMRI BIDS data can be produced for analysis. This tool only does First-Level Analysis.

 ## Repository Information
 This repository has:
  - a template file named "design.fsf" that will be manipulated for FSL processing on preprocessed data,
  - a "complete_workflow.sh" Shell script that will run fMRIPrep, code to manipulate "design.fsf", and FSL,
  - a "Workflow" folder with all the Shell and Python scripts needed to run
    - "fmriprep.sh": A script to run fMRIPrep
    - "fsl_design_file.py": Script that manipulates "design.fsf"
    - "confounds_extraction.py": Function called by Python script
    - "fsl.sh": A script to run FSL with "design.fsf"

 ## How To Use
 ### Prerequisites:
  - LINUX-based system required due to FSL.
  - fMRIPrep is installed via Docker or Singularity. Check https://fmriprep.org/en/stable/installation.html for instructions.
  - FSL must be installed. Check https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/FslInstallation.html for instructions.

 ### Instructions:
 1. Paste the following files alongside the BIDS data you want to analyse. (Check the __References__ section for the link to the data used)
 ![image](https://github.com/user-attachments/assets/e6b7e0ed-9f1c-407f-a7e4-9f5e80a177db) <br/>
 2. Open the "Workflow" folder and open "fmriprep.sh" and make the appropriate changes to the file. This includes the root BIDS directory, in this case, the full path to SharedStates, the participant label, which we set as "01", and the FreeSurfer License file path. The FreeSurfer License can be downloaded from: https://surfer.nmr.mgh.harvard.edu/registration.html <br/>
    <i>Note: If using SharedStates, make sure to remove the derivatives folder to make room for fMRIPrep derivatives.</i>
 4. In the "Workflow" folder, open "fsl_design_file.py" and change these two lines. We can change "Checkerboard" to "SharedStates". The file path to the "func" folder is via "sub-01/ses-1/func", so this change must be made as well.
 ![image](https://github.com/user-attachments/assets/ced187a8-49ac-466b-8f75-15b35b91e0e6)
 5. Using the Terminal. Make your working directory the directory above the BIDS root directory; one directory above SharedStates, in this case.
 6. Run "./complete_workflow.sh" in the terminal.
 7. After running. Use FSLEYES, MRIcroGL, or other visualisation softwares to view the statistics from FSL.
 8. For further analyses, check the __Notes__ section below.

### Notes
This workflow only has a identity design matrix. For example, in the SharedStates data set, in Subject-01, Session-1, Task-Other, there are 4 event types: Cue, Action, Situation, and Interoception. This script only creates 4 statistices; one for each event type. For further analysis:
1. Run "Feat_gui" in the terminal.
2. Select "Statistics" at the top and under "Select FEAT directory", select the folder that is one directory above the root BIDS directory with the suffix ".feat". <br/>
   ![image](https://github.com/user-attachments/assets/f4a5b919-de32-4f7e-8ef5-782cd00e316a) <br/>
   ![image](https://github.com/user-attachments/assets/cb7294cd-09a3-48b5-b869-9091e61491ae)
3. Under the "Stats" tab, select "Full Model Setup" <br/>
   ![image](https://github.com/user-attachments/assets/7288299d-845b-4077-b5b3-c9830adfb855) <br/>
4. Select the "Contrasts & F-Tests" tab in the new window that opened. Increase the number of contrasts and analyse the data further!
   ![image](https://github.com/user-attachments/assets/cf075bfd-e5d3-4462-a269-22ebae15ba18) <br/>
   Use https://web.mit.edu/fsl_v5.0.10/fsl/doc/wiki/GLM.html for more information on how to use contrasts in FSL.

 ## References
 <ins>Data Used For Testing</ins>: Oosterwijk, S., Snoek, L., Rotteveel, M., Barrett, L. F., & Scholte, H. S. (2017). Shared states: using MVPA to test neural overlap between self-focused emotion imagery and other-focused emotion understanding. Social cognitive and affective neuroscience, 12(7), 1025-1035.
 https://openneuro.org/datasets/ds002547/versions/1.0.0
