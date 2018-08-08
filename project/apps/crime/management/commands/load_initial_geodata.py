import os
import logging
import requests
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from project.apps.crime.models import County, State, City, Agency

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Load the state and county objects the first time."

    def open_state_file(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_location = BASE_DIR+ "/state_table.csv"
        with open(file_location, 'rU') as f:
            row_list = f.readlines()
        return row_list

    def create_state_objects(self, row_list):
        counter = 0
        row_list = row_list[1:]
        for row in row_list:
            items = row.strip().split(',')
            name = items[1]
            name = name.replace('"', '')
            abbrev = items[2]
            abbrev = abbrev.replace('"', '')
            fips = items[9]
            fips = fips.replace('"', '')
            assoc_press = items[10]
            assoc_press = assoc_press.replace('"', '')
            census_division_name = items[15]
            census_division_name = census_division_name.replace('"', '')
            standard_federal_region = items[11]
            standard_federal_region = standard_federal_region.replace('"', '')
            census_region_name = items[13]
            census_region_name = census_region_name.replace('"', '')
            census_region = items[12]
            census_region = census_region.replace('"', '')
            circuit_court = items[16]
            circuit_court = circuit_court.replace('"', '')
            census_division = items[14]
            census_division = census_division.replace('"', '')
            p = State(name=name, 
                abbrev = abbrev, 
                fips=fips,
                assoc_press = assoc_press, 
                census_division_name = census_division_name,
                standard_federal_region = standard_federal_region,
                census_region_name = census_region_name,
                census_region = census_region,
                circuit_court = circuit_court,
                census_division = census_division)
            p.save()
            counter+=1
        return counter

    def open_county_file(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_location = BASE_DIR+ "/national_county.txt"
        with open(file_location, 'rU') as f:
            row_list = f.readlines()
        addl_file_location = BASE_DIR+ "/MasterGeo.csv"
        with open(addl_file_location, 'rU') as g:
            addl_row_list = g.readlines()
        return row_list, addl_row_list

    def create_county_objects(self, row_list, addl_row_list):
        counter = 0
        for row in row_list:
            items = row.strip().split(',')
            state=items[0]
            territories = ("AS", "GU", "MP", "PR", "UM","VI")
            if state in territories:
                continue
            else:
                try:
                    state_obj = State.objects.get(abbrev=state)
                    fips = items[1] + items[2]
                    name = items[3]
                    p = County(name=name, state=state_obj, fips=fips)
                    p.save()
                    counter+=1
                except:
                    continue
        for row in addl_row_list:
            items = row.strip().split(',')
            if items[2].strip() != "County":
                continue
            else:
                fips = items[12]
                p = County.objects.get(fips=fips)
                p.GNIS = GNIS = items[-4]
                msa = items[88]
                if len(msa)==1:
                    msa = items[89]
                p.msa = msa
                p.save()
        return counter

    def open_muni_file(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_location = BASE_DIR+ "/MasterGeo.csv"
        with open(file_location, 'rU') as f:
            row_list = f.readlines()
        return row_list

    def create_muni_objects(self, row_list):
        counter = 0
        muni_types = ("borough", "city", "od city", "town", "township", "village")
        row_list = row_list[1:]
        for row in row_list:
            items = row.strip().split(',')
            fips = items[12]
            muni_type = items[2].strip()
            if muni_type not in muni_types:
                continue
            elif fips == "3402160915":
                print("Princeton township no longer exists.") 
                continue
            else:
                #TODO TROUBLESHOOT THESE ASSIGNMENTS
                county_fips = "34{0}".format(items[21].zfill(3))
                county = County.objects.get(fips=county_fips)
                name = items[0]
                fips = items[12]
                muni_type = items[2].strip()
                character = items[3]
                nj_muncode = items[23]
                msa = items[88]
                if len(msa)==1:
                    msa = items[89]
                state_code_1968 = items[16]
                Treasury_Taxation_code_03 = items[17] 
                Federal_code_03 = items[18]
                Alternate_County_Code_state = items[20]
                GNIS = items[-4]
                SSN = items[-3]
                OGIS_MUN_CODE = items[-2]
                p = City(name = name, 
                    county = county,
                    fips = fips,
                    muni_type = muni_type,
                    character = character,
                    nj_muncode = nj_muncode,
                    msa = msa,
                    state_code_1968 = state_code_1968,
                    Treasury_Taxation_code_03 = Treasury_Taxation_code_03,
                    Federal_code_03 = Federal_code_03,
                    Alternate_County_Code_state = Alternate_County_Code_state,
                    GNIS = GNIS,
                    SSN = SSN,
                    OGIS_MUN_CODE = OGIS_MUN_CODE)
                p.save()
                counter+=1
        return counter

    def load_njsp(self):
        state_name = State.objects.get(abbrev="NJ")
        counties = County.objects.filter(state=state_name)
        name = 'New Jersey State Police Headquarters'
        city = City.objects.filter(name__contains="Ewing").first()
        zip_code = "08628"
        website = "https://www.njsp.org/"
        agency_type="1"
        ori7 = "NJNSP00"
        ori9 = "NJNSP0000"
        p = Agency(name = name,
            state_name = state_name,
            city = city,
            zip_code = zip_code,
            website = website,
            agency_type="3",
            ori7 = ori7,
            ori9 = ori9)
        p.save()
        for county in counties:
            p.counties.add(county)
            p.save()
        return

    def update_site(self):
        p = Site.objects.first()
        p.domain = "crime.hackjersey.com"
        p.name = "crime.hackjersey.com"
        p.save()
        return

    def handle(self, *args, **options):
        """
        load all the preliminary geographical data
        """
        logger.debug("opening state list from the state_table.csv")
        state_list = self.open_state_file()
        counter = self.create_state_objects(state_list)
        logger.debug("Loaded {0} state records".format(counter))

        logger.debug("opening county list from the Census")
        county_list, geo_list = self.open_county_file()
        counter = self.create_county_objects(county_list, geo_list)
        logger.debug("Loaded {0} county records".format(counter))

        logger.debug("opening list of municipalities from the state")
        muni_list = self.open_muni_file()
        counter = self.create_muni_objects(muni_list)
        logger.debug("Loaded {0} municipal records".format(counter))

        self.load_njsp()

        logger.debug("updating site domain and name")
        self.update_site()
