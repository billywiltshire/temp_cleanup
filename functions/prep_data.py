import pandas as pd
import math
import re

def import_data(file_names, column_mapping, dims_combined, is_lbs):

    df = pd.DataFrame()

    # Loop through input file list and create a single DataFrame
    for file in file_names:
        file_df = pd.read_csv(file,
                    dtype={
                        column_mapping['tracking_number']: 'str',
                        column_mapping['postal_code']:'str'
                    }
                )
        df = pd.concat([df, file_df], ignore_index=True)

    df = df.drop_duplicates(column_mapping['tracking_number'])
    
    if dims_combined == 'False':
        df.dropna(subset=[column_mapping['weight'],
                        column_mapping['length'],
                        column_mapping['width'],
                        column_mapping['height']],
                        how='any')
    else:
        df.dropna(subset=[column_mapping['weight']], how='any')

    #Filter out any destinations outside US
    df = df.loc[((df[column_mapping['country']] == 'US') |\
                (df[column_mapping['country']] == 'United States') |\
                (df[column_mapping['country']] == 'UNITED STATES')), :]

    #Take sample before cleaning to reduce compute and improve performance
    if len(df) > 15000:
        df['service_level'] = df[column_mapping['weight']].map(map_service_level)

        weights = df['service_level'].value_counts(normalize=True)
        print(weights)

        df = df.set_index('service_level')

        df = df.sample(n=15000, weights=weights).reset_index()
        df = df.drop('service_level', axis=1)
        print(df.head())
    else:
        df = df

    df[column_mapping['postal_code']] = clean_zip(df, column_mapping['postal_code'])

    df[column_mapping["weight"]] = clean_weight(df, column_mapping["weight"], is_lbs)

    address_components = [column_mapping['city'], column_mapping['state'], column_mapping['country']]

    for component in address_components:
        if component == None:
            continue
        else:
            df[component] = clean_address_components(df, component)

    if dims_combined == True:
        df['length'], df['width'], df['height'] = clean_dims(df, column_mapping['dimensions'], 'x')
    else:
        df['length'] = df[column_mapping['length']]
        df['width'] = df[column_mapping['width']]
        df['height'] = df[column_mapping['height']]

    return df

def clean_zip(df, zip_column):
    """
    Ensure that zipcode column contains only results of len 5.
    CSVs often cut of leading 0's assuming they are numbers, not
    strings. This function loops through zipcode column to append
    leading zeros and remove zip code extension if present.
    """

    zips = df[zip_column].astype(str).to_list()

    def append_leading_zero(zipcode):
        """
        Function to be applied to individual zipcodes in the list. Removes
        zipcode extension and applies leading zeros depending on string len.
        """
        if zipcode.find('-') > 0:
            zip = zipcode.split('-')
            zipcode = zip[0]
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
    """
    Weights need to be in lbs for the simulation. This function takes in weights column,
    converts to number if string, and converts oz to lbs if specified in config.
    """
    
    # Tests if weight column is numeric or string in nature. Converts if strings.
    try:
        weights = df[weight_column].astype(float).to_list()
    except:
        weights = df[weight_column].astype(str).to_list()
        weights = [convert_weight_to_pounds(weight) for weight in weights]

    # If weights provided in oz, converts to lbs rounded up to nearest tenth of a pound.
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
    # pattern = r'(\d+)lb\s*(\d*)oz'
    pattern = r'(?:(\d+)\s*lb)?\s*(?:(\d+(\.\d+)?)\s*oz)?'
    
    # Search the weight string using the pattern
    # match = re.search(pattern, weight_str.strip())
    match = re.fullmatch(pattern, weight_str.strip())
    
    if match:
        # Extract pounds and ounces from the match groups
        # pounds = float(match.group(1))
        # ounces = float(match.group(2)) if match.group(2) else 0

        # Extract pounds and ounces
        pounds = int(match.group(1)) if match.group(1) else 0  # Default to 0 if pounds are not provided
        ounces = float(match.group(2)) if match.group(2) else 0.0  # Default to 0.0 if ounces are not provided
        
        # Convert ounces to pounds (1 pound = 16 ounces)
        total_pounds = pounds + ounces / 16.0
    else:
        total_pounds = float(weight_str)
        
    return total_pounds

def clean_dims(df, dims_column, delimiter):
    """
    If package dims are presented in a single column separated by a delimiter,
    this function unpacks the length, width, and height into separate columns.
    """

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
    """
    Converts address components to uppercase for consistency in output dataset.
    """

    address_part = df[address_column].astype(str).to_list()

    cleaned_parts = [part.strip().upper() for part in address_part]

    return cleaned_parts

def map_service_level(x):
    """
    Maps service level to records in the data to apply weights to the sample.
    """

    if x < 1:
        return 'sub_1lb'
    elif x < 10:
        return 'economy'
    else:
        return 'ground'