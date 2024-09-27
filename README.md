Instructions for using the Parcel Sim Tool Data Clean-Up Module:

Step 1: Clone repository to your computer.

Step 2: Install any necessary dependencies.
  Should only need to install Pandas, Datetime, and Numpy
  Run command <pip install pandas/datetime/numpy>
  
Step 3: Open config.json and enter necessary information
  <input_files>; list: List all files to be used for input data. Files need to have the same column configuration and should be saved as UTF-8 encoded
                       csv's. Only need to update the file names, keep file path the same.
  <output_file>; string: Name of output file. This creates a copy of the ouput data.csv that can be used to re-run the simulation on the same dataset
                         if needed.
  <input_columns>; dictionary: DO NOT TOUCH THE KEYS. Values should be entered as strings and match the column names in the source data files. If the
                               source does not have the necessary column, fill in a value of "None".
  <additional_params>; dictionary: DO NOT TOUCH THE KEYS. Values should be entered as strings.
    <dims_combined>: Indicates if all dimensions are contained in a single column, typically separated by an 'x'. Input should be string "True" or "False"
    <is_lbs>: Indicates if weight units are lbs. Input should be string "True" or "False", "False" if weight is in oz.

Step 4: Open a terminal, navigate to where you locally stored the module, and run <python3 main.py>

Step 5 [Optional]: Upload data to GCP Bucket to run the simulation
