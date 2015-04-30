#NJ Crime
This is a fledgling effort by a small group of New Jersey journalists to scrape, compile and publish monthly crime data in the Garden State.

In the initial phase, we've published Ruby scripts to convert the State Police crime data from PDFs into csvs for each police agency in the state.

Later, we plan to launch a web interface and API serving slices of the crime data. Ultimately, depending on the work it takes for the second phase, we hope to create a dashboard of visualizations for the data as well.

Got a question about the data or how to get involved? [File an issue](https://github.com/HackJersey/crime/issues) or contact one of the [core contributors](https://github.com/HackJersey/crime/blob/master/CONTRIBUTORS.md).

##Get Started
###Set the stage
These scripts use the tabula-extractor Ruby gem, which only runs in the [JRuby](http://jruby.org/) version of the language. Before you can do anything, you'll have to use a Ruby version manager like [rbenv](https://github.com/sstephenson/rbenv) or [RVM](https://rvm.io/) to install Ruby. You'll also need to have the [Bundler](http://bundler.io/) Ruby gem installed to set up the additional gems we use. If you are a seasoned Rubyist, you can skip to the next section. We'll also assume that you've used git before and have it installed on your command line. (These instructions have been tested on OS X. If you use a Windows machine, please adjust as necessary).

```
git clone git@github.com:HackJersey/crime.git   #clone this repo to your local machine
cd crime
rbenv install jruby-1.7.15   #install this or a newer version of JRuby
rbenv rehash
rbenv local jruby-1.7.15   #set JRuby as your current, local version of Ruby for this project
bundle install   #install the gems that we use and their dependencies
```

###Run the script
Now that you've got the right version of Ruby and the gems installed

Make certain you're in the project directory with the ```crimecsv.rb``` file.
This script can take a number of command line arguments for names of the crime report pdfs you want to scrape to CSVs. By default, this is set to ```20150327_crimetrend.pdf```, which was the report for January, 2015 crime stats released in March. To scrape a different report, just list its name after typing ```./crimecsv.rb```. So, if I wanted to scrape ```20150327_crimetrend.pdf``` and ```20150327_ucr_2014stats.pdf```, I'd type: 

```
./crimecsv.rb 20150327_crimetrend.pdf 20150327_ucr_2014stats.pdf
```

Then sit back and wait for the magic to happen.

###But what does it *do*?
This code takes each report you name, splits it into pieces and generates a single CSV for each department (or page) in the original.

It starts by looking for the pdf you name in the ```data/pdfs``` directory. If it's not there, it'll download it from the [State Police's website](http://www.njsp.org/info/ucr_currentdata1.html?agree=0). If it is there, it uses [tabula-extractor](https://github.com/tabulapdf/tabula-extractor) to pull out the data table from each page and spit it into its own csv. All of the csvs wind up in the aptly named ```data/csvs``` directory.

###Now I see a few hundred csv files. Which one do I want?
Each csv generated by the script follows a consistent naming convention.

YYYY-MM-DD-for-YYYY-MM-ID_NUMBER.csv

The first 10 characters are the date when the State Police posted this PDF report originally. The next 8 characters, starting with "-for-..." is the time period covered by the monthly report. The remaining characters before ".csv" are the unique ID number of the police agency that the stats cover. There is also one file that ends in "-state.csv", which are total numbers for all New Jersey agencies for that time period.

If you're looking for a CSV for a specific department, first find its ID number in ```lookup-agency.csv```. Beware of agencies with common names. For instance, there are 4 Washington Twp PDs, each in a different county. We'll soon provide more details on each agency in the lookup table, including home counties, to help deal with this. Find your police department and its nine-digit ID number, then look in ```data/csvs``` for any csv that ends with that ID.

The CSVs have the following columns.
* "crime" - the category label of the crime, along with overall totals and counts of index, violent and nonviolent crimes (which we will eventually remove from the CSVs)
* "month_last_yr" - the count for each crime from the time period covered, such as March, 2015, for instance.
* "month_this_yr" - the count for the same time period the previous year.
* "pct_chg" - the year-to-year percent change
* "ytd_last" - the cumulative count from January 1 of the year.
* "ytd_this_yr" - the same year-to-date count over the same time the previous year.
* "ytd_pct_chg" - the annual, year-to-date percent change.
* "cleared" - the number of crimes in this category cleared.
* "pct_cleared" - the percent of crimes cleared.
* "juvie_cleared" - the count of these crimes that were commited by juveniles and cleared.

##Additional options
We've added support for three optional command line arguments.

```
Usage: ./crimecsv.rb [options] [filename(s) to scrape]
    -o, --output [DIR]               Output directory
    -i, --ids [IDs]                  Provide a pipe-separated (|) list of unique agency IDs
    -l, --local                      Only parse local copy, if it exists.
```
If you use the ID flag, you must give it the agency's unique ID, from the ```lookup-agency.csv```. If you want reports for more than one agency, you must separate the IDs with a comma and no spaces, like ```NJ101010,NJ202020```. If you only want the statewide overview, you can use the id ```state```.

##What next?
Right now, these script provide an easier tabular format for dealing with the data than the massive, monthly State Police PDFs. In short order, we hope to start ingesting these into a database to provide programmatic access to these numbers, along with historic data. So stay tuned.

##Help us make this better.
This is an early, pre-alpha release. There will be bugs and mistakes in here. Anything you spot that seems odd, please let us know, ideally by [filing an issue](https://github.com/HackJersey/crime/issues) for us. If you have questions or suggestions for features you'd like to see, we want to hear that too. If, for some reason, you don't want to submit an issue, please feel free to also reach out to any of the [core contributors](https://github.com/HackJersey/crime/blob/master/CONTRIBUTORS.md) at any time. With your help, we can make this better and easier to use.