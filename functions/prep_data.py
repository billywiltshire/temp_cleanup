import pandas as pd
import math
import re

def import_data(file_names, column_mapping, dims_combined, is_lbs):

    df = pd.DataFrame()

    for file in file_names:
        file_df = pd.read_csv(file,
                    dtype={
                        column_mapping['tracking_number']: 'str',
                        column_mapping['postal_code']:'str'
                    }
                )
        df = pd.concat([df, file_df], ignore_index=True)

    # Take sample before cleaning to reduce compute and improve performance
    # if len(df) > 15000:
    #     df = df.sample(15000)
    # else:
    #     df = df

    df[column_mapping['postal_code']] = clean_zip(df, column_mapping['postal_code'])

    df[column_mapping["weight"]] = clean_weight(df, column_mapping["weight"], is_lbs)

    address_components = [column_mapping['city'], column_mapping['state'], column_mapping['country']]

    for component in address_components:
        if component == None:
            continue
        else:
            df[component] = df[column_mapping['city']] = clean_address_components(df, component)

    if dims_combined == True:
        df['length'], df['width'], df['height'] = clean_dims(df, column_mapping['dimensions'], 'x')
    else:
        df['length'] = df[column_mapping['length']]
        df['width'] = df[column_mapping['width']]
        df['height'] = df[column_mapping['height']]

    return df

def clean_zip(df, zip_column):

    zips = df[zip_column].astype(str).to_list()

    def append_leading_zero(zipcode):
        if zipcode.find('-') > 0:
            zip = zipcode.split('-')
            zipcode = zip[0]
            # zipcode = zipcode[:5]
        else:
            zipcode = zipcode[:5] if len(zipcode) > 5 else zipcode

        if len(zipcode) == 3:
            zipcode = '00' + zipcode[:5]
        elif len(zipcode) == 4:
            zipcode = '0' + zipcode[:5]

        return zipcode

    cleaned_zips = [append_leading_zero(zip) for zip in zips]

    return cleaned_zips

def clean_weight(df, weight_column, is_lbs):
    
    try:
        weights = df[weight_column].astype(float).to_list()
    except:
        weights = df[weight_column].astype(str).to_list()
        weights = [convert_weight_to_pounds(weight) for weight in weights]

    if not is_lbs:
        weights_cleaned = [round(math.ceil(weight) / 16, 2) for weight in weights]
    else:
        weights_cleaned = weights

    return weights_cleaned

def convert_weight_to_pounds(weight_str):
    """
    Converts a weight string in the format 'Xlb Yoz' to a float representing the weight in pounds.
    
    Args:
    weight_str (str): The weight string in the format 'Xlb Yoz'
    
    Returns:
    float: The weight in pounds
    """
    # Regular expression to extract pounds and ounces
    pattern = r'(\d+)lb\s*(\d*)oz'
    
    # Search the weight string using the pattern
    match = re.search(pattern, weight_str.strip())
    
    if match:
        # Extract pounds and ounces from the match groups
        pounds = int(match.group(1))
        ounces = int(match.group(2)) if match.group(2) else 0
        
        # Convert ounces to pounds (1 pound = 16 ounces)
        total_pounds = pounds + ounces / 16.0
    else:
        total_pounds = weight_str
        
    return total_pounds

def clean_dims(df, dims_column, delimiter):

    package_dimensions = df[dims_column].astype(str).to_list()

    lengths = []
    widths = []
    heights = []

    for package in package_dimensions:

        dimensions = package.split(delimiter)

        if len(dimensions) == 3:
          lengths.append(dimensions[0].strip())
          widths.append(dimensions[1].strip())
          heights.append(dimensions[2].strip())
        else:
          lengths.append('N/A')
          widths.append('N/A')
          heights.append('N/A')

    return lengths, widths, heights

def clean_address_components(df, address_column):

    address_part = df[address_column].astype(str).to_list()

    cleaned_parts = [part.strip().upper() for part in address_part]

    return cleaned_parts