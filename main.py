import pandas as pd
import datetime as dt
import json
from functions.prep_data import import_data
from functions.agg_data import create_sample_df

d = open('./config.json')
config = json.load(d)
d.close()

output_file = f"sample_datasets/{config['output_file']}"

files = config['input_files']

columns_mapping = {
  'ship_date': None if config['input_columns']['ship_date'] == 'None' else config['input_columns']['ship_date'],
  'tracking_number': None if config['input_columns']['tracking_number']  == 'None' else config['input_columns']['tracking_number'],
  'city': None if config['input_columns']['city']  == 'None' else config['input_columns']['city'],
  'state': None if config['input_columns']['state']  == 'None' else config['input_columns']['state'],
  'postal_code': None if config['input_columns']['postal_code']  == 'None' else config['input_columns']['postal_code'],
  'country': None if config['input_columns']['country']  == 'None' else config['input_columns']['country'],
  'weight': None if config['input_columns']['weight']  == 'None' else config['input_columns']['weight'],
  'dimensions': None if config['input_columns']['dimensions']  == 'None' else config['input_columns']['dimensions'],
  'length': None if config['input_columns']['length']  == 'None' else config['input_columns']['length'],
  'width': None if config['input_columns']['width']  == 'None' else config['input_columns']['width'],
  'height': None if config['input_columns']['height']  == 'None' else config['input_columns']['height']
}

# Tests to ensure value is present for mandatory columns, raises an error if not
mandatory_columns = ['postal_code', 'weight', 'dimensions'] if config['additional_params']['dims_combined'] == 'True' else ['postal_code', 'weight', 'length', 'width', 'height']
for column in mandatory_columns:
  assert columns_mapping[column] != None, f'Necessary Column [{column}] is Missing'

# DO NOT TOUCH FIRST TWO INPUTS
df = import_data(
  files,
  columns_mapping,
  True if config['additional_params']['dims_combined'] == 'True' else False,
  True if config['additional_params']['is_lbs']  == 'True' else False
  )

sample_df = create_sample_df(df, columns_mapping)

print(len(sample_df))
print(sample_df.head(50))

sample_df.to_csv('output/data.csv', index=False)
sample_df.to_csv(output_file, index=False)