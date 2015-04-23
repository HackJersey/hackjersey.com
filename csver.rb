#!/usr/bin/env jruby
# encoding: utf-8

require 'rubygems'
require 'date'
require 'fileutils'
require 'tabula'
require 'httparty'

def scrape(file_name, csvs_output)
    local_dir = "data/pdfs/"
    grab(file_name, local_dir)
    puts "Processing "+file_name
    FileUtils.mkdir_p(csvs_output)
    peel(file_name, csvs_output)
end

def grab(file_name, local_dir)
    if Dir.entries(local_dir).include?file_name
        puts file_name + " found on local machine."
    else
        retrieve(file_name, local_dir)
    end
end

def retrieve(file_name, local_dir)
    remote_dir="http://www.njsp.org/info/pdf/ucr/current/"
    puts remote_dir+file_name
    remotes = HTTParty.get(remote_dir+file_name)
    case remotes.code
    when 404
        abort(file_name + " not found on State Police website.")
    when 500..600
        abort("some other error happening with web request")
    when 200 
        File.open(local_dir+file_name, 'wb') do |f|
            puts "downloaded " + file_name
            f.write remotes.parsed_response
        end
    end
end

def peel(file_name, csvs_output)
    pdfs_dir = 'data/pdfs/'
    counter = 0
    page_area = [97.55,11.19,573.48,778.62]
    extractor = Tabula::Extraction::ObjectExtractor.new(pdfs_dir+file_name, :all)
    extractor.extract.each_with_index do |pdf_page, page_index|
        first_csv = pdf_page.get_table.to_csv
        my_csv = CSV.parse(first_csv)
        #TODO make this a function
        if my_csv[0][-1]!= ""
            date = my_csv[0][-1]
        else
            date = my_csv[1][-1]
        end
        coverage = my_csv[4][-1].split('-')[1]
        pattern = /^(N.+)\s+Total/
        id = pattern.match(first_csv)[1].strip
        if id.downcase == "new jersey"
            id = "state"
        end

        release_date = Date.parse date
        covers = Date.parse coverage


        #TODO make this a function
        year_pattern = /.*(201\d)/
        if file_name.end_with?('stats.pdf')
            outfile = csvs_output + release_date.to_s + "-for-" + id + "-" + year_pattern.match(file_name)[1] + "annual.csv"
        else
            outfile = csvs_output + release_date.to_s + "-for-" + covers.to_s[0..-4] + "-" + id +".csv"
        end

        table_area = pdf_page.get_area(page_area).get_table.to_csv
        #TODO Make this a function
        table_csv = CSV.parse(table_area)

        heds = ["crime", "month_last_yr", "month_this_yr", "ytd_last", "ytd_this_yr", "cleared", "juvie_cleared"]
        CSV.open(outfile,"wb") do |csv|
            csv << heds
            table_csv.each do |row|
                #TODO make this a function
                next if row[0].strip.end_with?("Total:")
                next if row[0].strip.end_with?("Index")
                next if row[0].strip.end_with?("Crime")
                if row[-1] != ""
                    if row.length>10
                        row = row.values_at(0,2,3,5,6,8,10)
                    else
                        row = row.values_at(0,1,2,4,5,7,9)
                    end
                    csv << row
                end
            end
        end
        counter += 1
    end
    extractor.close!    
    puts counter.to_s + " pages from " + file_name + " converted to CSVs."
end

csvs_output="data/csvs/"
file_name = "20150327_crimetrend.pdf"
if ARGV.length > 0
    ARGV.each do |argv|
        scrape(argv, csvs_output)
    end
else
    scrape(file_name, csvs_output)
end