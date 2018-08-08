from project.apps.crime.models import Release
from time import sleep

file_location = "scraper/data/pdfs/crime_reports.csv"
with open(file_location, 'rU') as f:
    row_list = f.readlines()
counter = 0
brokens = []
for row in row_list[1:]:
    p = Release()
    length = p.check_pdf_length(row.strip())
    if not length:
        print("error")
        brokens.append(row)
    sleep(.5)
    counter+=1
print(counter)

