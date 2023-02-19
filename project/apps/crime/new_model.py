    name = models.CharField(max_length=200)
    street_number = models.CharField(null=True, blank=True, max_length=50)
    street_name = models.CharField(null=True, blank=True, max_length=200)
    room = models.CharField(null=True, blank=True, max_length=50)
    city = models.ForeignKey(City, null=True, blank=True, related_name='agency', on_delete=models.SET_NULL)
    state_name = models.ForeignKey(State, related_name='agency2', verbose_name="state", on_delete=models.PROTECT)
    zip_code = models.CharField(null=True, blank=True, max_length=30, verbose_name="zip")
    website = URLOrRelativeURLField(null=True, blank=True)
    agency_notes = models.TextField(blank=True, null=True, verbose_name = "Notes about agency")
    agency_type = models.CharField(choices=AGENCY_CHOICES, max_length=10, blank=False, default="1")
    cities = models.ManyToManyField(City, related_name='cities_covered', verbose_name="cities in jurisdiction")
    counties = models.ManyToManyField(County, related_name = 'counties_covered', verbose_name="counties covered")
    ori7 = models.CharField(max_length=20, null=True, blank=True, help_text="Federal ORI ID number for the jurisdiciton")
    ori9 = models.CharField(max_length=20, null=True, blank=True, help_text="Federal ORI ID number for the jurisdiciton")


make our name NJSP_name
from lear

LEAR_ORI9    <- to ori9
LEAR_ORI7    <- to ori9
LEAR_STREET_ADDRESS < - convert to street_number street_name 
LEAR_CITY    <- look up city by name and convert to city
LEAR_FIPS    <- make this its own field, but also split it to add counties and state

LEAR_ID 
LEAR_NAME    
LEAR_ZIP 
LEAR_CSLLEA08_ID 
LEAR_SAMPTYPE    LEAR agency type
LEAR_PE14_DIVISION_REGION    
LEAR_PE14_MSA    
LEAR_PE14_POPULATION 
LEAR_PE14_MALE_OFFICERS  
LEAR_PE14_MALE_CIVILIANS 
LEAR_PE14_MALE_TOTAL 
LEAR_PE14_FEMALE_OFFICERS    
LEAR_PE14_FEMALE_CIVILIANS   
LEAR_PE14_FEMALE_TOTAL   
LEAR_PE14_TOTAL_EMPLOYEES

from leaic


LEAIC_FPLACE FIPS PLACE CODE
LEAIC_ORI9 ORIGINATING AGENCY IDENTIFIER (9 CHARACTERS) FROM UCR AND NCIC FILES
LEAIC_ORI7 ORIGINATING AGENCY IDENTIFIER (7 CHARACTERS) FROM UCR FILES
LEAIC_NAME
LEAIC_UA URBAN AREA/URBAN CLUSTER CODE (AS OF 2010)
LEAIC_UANAME URBAN AREA/URBAN CLUSTER NAME (AS OF 2010)
LEAIC_PARTOF AGENCY/ORI IS PART OF LARGER PARENT AGENCY
LEAIC_AGCYTYPE AGENCY TYPE
LEAIC_SUBTYPE1 AGENCY SUB-TYPE 1
LEAIC_SUBTYPE2 AGENCY SUB-TYPE 2
LEAIC_GOVID CENSUS GOVERNMENT ID (AS OF 2012)
LEAIC_LG_NAME CENSUS GOVERNMENT NAME (AS OF 2012)
LEAIC_ADDRESS_NAME ADDRESS - NAME
LEAIC_ADDRESS_STR1 ADDRESS - STREET LINE 1
LEAIC_ADDRESS_STR2 ADDRESS - STREET LINE 2
LEAIC_ADDRESS_CITY ADDRESS - CITY
LEAIC_ADDRESS_STATE ADDRESS - STATE
LEAIC_ADDRESS_ZIP ADDRESS - ZIP CODE
LEAIC_REPORT_FLAG ORI REPORTED 1 OR MORE OFFENSES 1985 - 2012
LEAIC_CSLLEA08_ID CSLLEA 2008 AGENCY IDENTIFIER (#TODO does this match LEAR?)
LEAIC_LEMAS_ID LEMAS FILES ID
LEAIC_U_STATENO UCR NUMERIC STATE CODE (UCR CODING)
LEAIC_U_CNTY UCR COUNTY (UCR CODING)
LEAIC_U_POPGRP GROUP NUMBER (AS OF 2012)
LEAIC_U_TPOP UCR TOTAL POPULATION (AS OF 2012)
LEAIC_LG_POPULATION CENSUS POPULATION (AS OF 2010)
LEAIC_COMMENT COMMENTS - TYPICALLY LISTING INFORMATION ON MULTI-JURISDICTION AGENCIES
LEAIC_CONGDIST1 CONGRESSIONAL DISTRICT 1 (AS OF 2010)
LEAIC_CONGDIST2_18 CONGRESSIONAL DISTRICTS 2 THROUGH 18 (AS OF 2010)
LEAIC_DISTNAME FEDERAL JUDICIAL DISTRICT NAME