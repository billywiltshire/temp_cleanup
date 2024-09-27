import pandas as pd
import datetime as dt

def create_sample_df(df, columns_mapping):

    records = []

    c = 1

    for index, row in df.iterrows():
    
        record = {}
        
        record['ship_date'] = dt.datetime.today().strftime('%Y-%m-%d')\
            if columns_mapping["ship_date"] == None\
            else row[columns_mapping["ship_date"]]
        
        record['tracking_number'] = c if columns_mapping["tracking_number"] == None\
            else row[columns_mapping["tracking_number"]]
        
        record['line1'] = ''
        record['city'] = '' if columns_mapping["city"] == None\
            else row[columns_mapping["city"]]
        record['state'] = '' if columns_mapping["state"] == None\
            else row[columns_mapping["state"]]
        record['postal_code'] = row[columns_mapping["postal_code"]]
        record['country'] = 'US' if columns_mapping["country"] == None else row[columns_mapping["country"]]
        record['type'] = 'residential'
        record['weight'] = row[columns_mapping["weight"]]
        record['weight_units'] = 'lb'
        record['length'] = 'N/A' if row["length"] == 0 else row["length"]
        record['width'] = 'N/A' if row["width"] == 0 else row["width"]
        record['height'] = 'N/A' if row["height"] == 0 else row["height"]
        record['tariff_code'] = ''

        records.append(record)
        c += 1

    sample_df = pd.DataFrame(records)

    #Filter out any destinations outside US
    sample_df = sample_df.loc[sample_df['country'] == 'US', :]
    #Filter out rows with un-parseable dims
    sample_df = sample_df.loc[sample_df['length'] != 'N/A', :]
    #Drop rows w/ duplicate tracking numbers
    sample_df = sample_df.drop_duplicates('tracking_number')

    return sample_df