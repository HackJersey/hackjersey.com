#!/usr/bin/env jruby
# encoding: utf-8

require 'rubygems'
require 'date'
require 'fileutils'
require 'docsplit'
require 'tabula'
require 'httparty'

#require 'tmpdir'

def scrape(file_name, csvs_output)
    puts "Processing "+file_name
    local_dir = "data/pdfs/"
    grab(file_name, local_dir)
    FileUtils.mkdir_p(csvs_output)

    peel(file_name, csvs_output)
end

def grab(file_name, local_dir)
    pdfs_output = "data/burstpdfs/"

    if Dir.entries(local_dir).include?file_name
        Docsplit.extract_pages(local_dir+"/"+file_name, :output=>pdfs_output)
    else
        retrieve(file_name, local_dir, remote_dir)
    end
end

def retreive(file_name, local_dir, remote_dir)
    remote_dir = "http://www.njsp.org/info/pdf/ucr/current/"
	File.open(local_dir+file_name, 'wb') do |f|
		f.write HTTParty.get(remote_dir+file_name).parsed_response
    end
end

def peel(file_name, csvs_output)
    pdfs_dir = "data/burstpdfs/"
    counter = 0
    Dir.foreach(pdfs_dir) do |item|
        num_chars = file_name[0..-5].length
	    page_area = [97.55,11.19,573.48,778.62]
	    next if item.start_with?('.')
	    next if item.end_with?('.txt')
        next if item[0..num_chars-1]!=file_name[0..num_chars-1]
        
        extractor = Tabula::Extraction::ObjectExtractor.new(pdfs_dir+item, :all )
        extractor.extract.each_with_index do |pdf_page, page_index|
        
        first_csv = pdf_page.get_table.to_csv
        my_csv = CSV.parse(first_csv)
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

        year_pattern = /.*(201\d)/
        if file_name.end_with?('stats.pdf')
            outfile = csvs_output + release_date.to_s + "-for-" + id + "-" + year_pattern.match(file_name)[1] + "annual.csv"
        else
            outfile = csvs_output + release_date.to_s + "-for-" + covers.to_s[0..-4] + "-" + id +".csv"
        end

        table_area = pdf_page.get_area(page_area).get_table.to_csv
        table_csv = CSV.parse(table_area)

        heds = ["crime", "month_last_yr", "month_this_yr", "pct_chg", "ytd_last", "ytd_this_yr", "ytd_pct_chg", "cleared", "pct_cleared", "juvie_cleared"]
        CSV.open(outfile,"wb") do |csv|
            csv << heds
            table_csv.each do |row|
                next if row[0].start_with?("Total")
                if row[-1] != ""
                    csv << row
                end
            end
        end
    extractor.close!
    end
    counter += 1
end
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