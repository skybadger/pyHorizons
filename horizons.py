import csv
import os
import os.path
import json 
import numpy as np
from typing import Union, Dict, List, Tuple  

def get_horizons_data( inpath: Union[str, os.PathLike],  outpath: Union[os.PathLike, str] ) -> Dict:
    """
    Get the data from the Horizons file and return it as a dictionary.
    """
    # Check if the file exists
    if not os.path.exists(inpath):
        raise FileNotFoundError(f"File {inpath} does not exist.")
    
    # Read the data from the file
    data = []
    with open(inpath, 'r') as f:
        csvreader = csv.DictReader(f )
        for row in csvreader:
            azimuth = row.get('Azimuth', None)
            altitude = row.get('Pitch', None)
            if azimuth is not None and altitude is not None:
                newdata = { "Azimuth": float(azimuth) , "Altitude": float(altitude) } 
                data.append( newdata ) 
    
    #order the data according to the 1st field. ( azimuth ) 
    data.sort(key=lambda x: x['Azimuth'])   

    data_dict = { key: [] for key in data[0].keys() }
    for row in data:
        for key in data_dict.keys():
            data_dict[key].append( row[key] )   
       
    # Group by azimuth buckets (e.g., 0-10, 10-20, etc.)
    bucket_size = 1
    buckets = {}
    
    for az, alt in zip(data_dict['Azimuth'], data_dict['Altitude']):
        bucket_key = int(az // bucket_size) * bucket_size
        if bucket_key not in buckets:
            buckets[bucket_key] = []
        buckets[bucket_key].append(alt)
    
    # Update the dictionary with averaged values
    out_data = list()
    for bucket_key in sorted(buckets.keys()):
        data = dict()
        data['Azimuth'] = float( bucket_key )
        data['Altitude'] = -1 * float( np.mean(buckets[bucket_key]) )
        out_data.append( data )
    
    # Save the data as a JSON file
    with open(outpath, 'w') as f:
        json.dump(out_data, f, indent=4)
    
    # Save the data as a CSV file
    with open(outpath.replace(".json", ".csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow( ["Azimuth", "Altitude"])
        for i in range(len(out_data )): 
            writer.writerow( [out_data[i]["Azimuth"], out_data[i]["Altitude"]] )
    
    return data_dict
    
    
if __name__ == "__main__":
    inpath = "data set1.csv"  # Replace with your actual file path
    outpath = "data set1_out.json"  # Replace with your desired output path
    data = get_horizons_data(inpath, outpath)
    print(f"Data has been processed and saved to JSON and CSV at {outpath}.")

    exit()