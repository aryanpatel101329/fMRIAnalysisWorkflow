import pandas as pd
import numpy as np
import os
import shutil

def confound_extraction(confounds_path, workdir, confounds_file):
    # Copy TSV confounds file
    shutil.copy(confounds_path, workdir)

    data = pd.read_csv(confounds_file, sep = "\t")

    # Tuple of accepted confound names
    accepted_confounds = ("t_comp_cor_", "cosine", "trans_", "rot_")

    # Empty list of accepted confound columns from imported data
    confounds = []

    for col_name, col in data.items():
        # Check if column name in imported data set is an accepted confound e.g. (cosine --> cosine00, cosine01, etc.)
        if (data[col_name].name.startswith(accepted_confounds)):
            confounds.append(data[col_name].astype(float))
        
    confounds = pd.concat(confounds, axis=1)

    # Find all columns that need to be imputed (includes any column with NaN values)
    impute_cols = confounds.columns[confounds.isna().any()].tolist()

    # For all columns with missing/NULL values, impute with mean of column
    for col in impute_cols:
        confounds.loc[0, col] = np.mean(confounds[col])

    # Convert to TSV. Then, change the file to a txt (compatible with FSL)
    confounds.to_csv(confounds_file, sep = "\t", index = False)
    os.rename(confounds_file, "confounds_timeseries.txt")

