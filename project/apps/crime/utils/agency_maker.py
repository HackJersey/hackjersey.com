import csv

import pandas as pd

old_file = 'lookup_agency_2015.csv'
newer_file = 'lookup_agency_new.csv'

base_dict = {}
with open(old_file, "rU") as file:
    csv_data = csv.reader(file)
    next(csv_data)
    for agency in csv_data:
        base_dict[agency[0]]=agency[1].strip()

with open(newer_file, "r") as file:
    csv_data = csv.reader(file)
    next(csv_data)
    for agency in csv_data:
        if agency[0] in base_dict.keys():
            #only add it if it has a different name for the same key
            if agency[1].strip() != base_dict[agency[0]].strip():
                base_dict["{0}new".format(agency[0])] = agency[1].strip()
        else:
            base_dict[agency[0]] = agency[1].strip()
#now up to 555 items
#TODO check and vet the duplicates in our list

#create a pandas dataframe for them
new_list = []
for item in base_dict.keys():
    new_list.append([item, base_dict[item]])

njsp = pd.DataFrame(new_list)
njsp.rename(index=str, inplace=True, columns={0:"ORI9", 1:"Name"})

#then open up the lear and see how many are there (and how many aren't)
lear = pd.read_csv('36697-0001-Data.tsv', sep="\t")
nj_lear = lear[lear.STATE=="NJ"]

#then open up the leiac and fill in the blanks.
leaic = pd.read_csv('35158-0001-Data.tsv', sep="\t")
nj_leaic = leaic[leaic.FIPS_ST==34]


fed_data = pd.merge(nj_leaic, nj_lear, on="ORI9",  how = "outer")

shorts = njsp[njsp.ORI9.str.len()<9]
njsp = njsp[njsp.ORI9.str.len()>8]

short_merge = pd.merge(shorts, fed_data, left_on='ORI9', right_on='ORI7_x', how="left")
all_agencies = pd.merge(njsp, fed_data, on='ORI9', how="outer")

all_agencies = short_merge.append(all_agencies)d

all_agencies.to_csv('all_agencies.csv')

'''
take that last dataframe and output it to a csv to examine the gaps
and load it into our models.
'''