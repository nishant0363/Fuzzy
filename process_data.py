import pandas as pd
from fuzzywuzzy import process, fuzz

# Write initial message to mapping.txt
with open('mapping.txt', 'w') as file:
    file.write("Processing Started. The Background processes will be shown here \n\n")

# Load input CSV and reference FMP CSV
input_csv_path = 'uploads/input.csv'
concatenated_df = pd.read_csv(input_csv_path)
fmp = pd.read_csv("Reference_FMP.csv")
fmp = fmp.sort_values(by=['State Name', 'd_name', 'sd_name'])

######################################################################################

# Function to get the best match
def get_best_match(name, list2):
    best_match = process.extractOne(name, list2)
    return best_match[0] if best_match else name

# Mapping for State Names
with open('mapping.txt', 'a') as file:
    file.write("Step 1 started. Mapping State Names \n\n")
    
mapping = {name: get_best_match(name, list(fmp['State Name'].unique())) for name in concatenated_df['StateName'].unique()}

# Function to correct name using mapping
def correct_name(name, mapping):
    return mapping.get(name, name)

# Write the mapping to a text file
with open('mapping.txt', 'a') as file:
    file.write("Mapping created for State Names \n")
    file.write(str(mapping))
    file.write("\n\n")

# Apply the corrected State Names
concatenated_df['Matched State Name'] = concatenated_df['StateName'].apply(lambda x: correct_name(x, mapping))

######################################################################################

# Function to get the best match with cache for District Names
with open('mapping.txt', 'a') as file:
    file.write("Step 2 started. Mapping District Names \n\n")

def get_best_match_with_cache_district(row, fmp, cache):
    state = row['Matched State Name']
    district = row['DistrictName']
    
    if state not in cache:
        with open('mapping.txt', 'a') as file:
            if str(cache) != "{}":
                file.write(f"Mapping created for {list(cache.keys())[-1]}'s District Names \n")
                file.write(str(cache[list(cache.keys())[-1]]))
                file.write("\n\n")
        cache[state] = {}
    
    if district not in cache[state]:
        fmp_state = fmp[fmp['State Name'] == state]
        match, score = process.extractOne(district, fmp_state['d_name'].unique(), scorer=fuzz.token_sort_ratio)
        cache[state][district] = match
    
    return cache[state][district]

cache = {}
concatenated_df['Matched District name'] = concatenated_df.apply(lambda row: get_best_match_with_cache_district(row, fmp, cache), axis=1)

with open('mapping.txt', 'a') as file:
    if str(cache) != "{}":
        file.write(f"Mapping created for {list(cache.keys())[-1]}'s District Names \n")
        file.write(str(cache[list(cache.keys())[-1]]))
        file.write("\n\n")


######################################################################################

# Function to get the best match with cache for Sub-District Names
with open('mapping.txt', 'a') as file:
    file.write("Step 3 started. Mapping Block Names \n\n")
    
def get_best_match_with_cache_subdistrict(row, fmp, cache, last_state):
    state = row['Matched State Name']
    district = row['Matched District name']
    sub_district = row['BlockName']
    
    if state != last_state[0]:
        cache.clear()  
        last_state[0] = state  
    
    fmp_state = fmp[fmp['State Name'] == state]
    fmp_district = fmp_state[fmp_state['d_name'] == district]
    
    if district not in cache:
        with open('mapping.txt', 'a') as file:
            if str(cache) != "{}":
                file.write(f"Mapping created for {list(cache.keys())[-1]}'s Block Names \n")
                file.write(str(cache[list(cache.keys())[-1]]))
                file.write("\n\n")
        cache[district] = {}

    if sub_district not in cache[district]:
        best_match = process.extractOne(sub_district, fmp_district['sd_name'].unique(), scorer=fuzz.token_sort_ratio)[0]
        cache[district][sub_district] = best_match

    return cache[district][sub_district]

cache = {}
last_state = [None]
concatenated_df['Matched SubDistrict name'] = concatenated_df.apply(lambda row: get_best_match_with_cache_subdistrict(row, fmp, cache, last_state), axis=1)

with open('mapping.txt', 'a') as file:
    if str(cache) != "{}":
        file.write(f"Mapping created for {list(cache.keys())[-1]}'s Block Names \n")
        file.write(str(cache[list(cache.keys())[-1]]))
        file.write("\n\n")
                
######################################################################################

# Function to get the best match with cache for Village Names
with open('mapping.txt', 'a') as file:
    file.write("Step 4 started. Mapping Villages Names \n\n")
    
def get_best_match_with_cache_village(row, fmp, cache, last_state):
    state = row['Matched State Name']
    district = row['Matched District name']
    village = row['VillageName']  
    
    if state != last_state[0]:
        cache.clear()
        last_state[0] = state  
    
    fmp_state = fmp[fmp['State Name'] == state]
    fmp_district = fmp_state[fmp_state['d_name'] == district]
    
    if district not in cache:
        with open('mapping.txt', 'a') as file:
            if str(cache) != "{}":
                file.write(f"Mapping created for {list(cache.keys())[-1]}'s Villages Names \n")
                file.write(str(cache[list(cache.keys())[-1]]))
                file.write("\n\n")
        
        cache[district] = {}
    
    if village not in cache[district]:
        best_match = process.extractOne(village, fmp_district['tv_name'].unique(), scorer=fuzz.token_sort_ratio)[0]
        cache[district][village] = best_match

    return cache[district][village]

cache = {}
last_state = [None]
concatenated_df['Matched Village name'] = concatenated_df.apply(lambda row: get_best_match_with_cache_village(row, fmp, cache, last_state), axis=1)

with open('mapping.txt', 'a') as file:
    if str(cache) != "{}":
        file.write(f"Mapping created for {list(cache.keys())[-1]}'s Villages Names \n")
        file.write(str(cache[list(cache.keys())[-1]]))
        file.write("\n\n")
                
######################################################################################

with open('mapping.txt', 'a') as file:
    file.write("Step 5 started. Merging \n\n")

# Rename columns to match FMP
concatenated_df = concatenated_df.rename(columns={
    'Matched State Name': 'State Name',
    'Matched District name': 'd_name',
    'Matched SubDistrict name': 'sd_name',
    'Matched Village name': 'tv_name'
})

# Merge concatenated_df with fmp
fmp_con = pd.merge(fmp, concatenated_df, on=['State Name', 'd_name', 'sd_name', 'tv_name'], how='inner')

with open('mapping.txt', 'a') as file:
    file.write("Step 6 started. Creating shrid column \n\n")

# Create shrid2 column
fmp_con['shrid2'] = fmp_con.apply(lambda row: f"11-{row['pc11_s_id']}-{row['pc11_d_id']}-0{row['pc11_sd_id']}-{row['pc11_tv_id']}", axis=1)

# Load Elevation data and merge with fmp_con
with open('mapping.txt', 'a') as file:
    file.write("Final Step started. Merging \n\n")
    
vcf = pd.read_csv("elevation_shrid.csv")
fmp_con = pd.merge(fmp_con, vcf, on='shrid2', how='inner')

# Save the final dataframe to CSV
output_csv_path = 'outputs/output.csv'
fmp_con.to_csv(output_csv_path, index=False)

with open('mapping.txt', 'w') as file:
    file.write("\n\n")
