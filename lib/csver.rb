#!/usr/bin/env ruby
# encoding: utf-8

require 'optparse'
require 'ostruct'
require 'date'
require 'fileutils'

require 'rubygems'
require 'tabula'
require 'httparty'

class Optparser
    def self.parse(args)
        options = OpenStruct.new
        options.output = 'data/csvs/'
        options.local = false
        options.ids = []


        opt_parser = OptionParser.new do |opts|
            opts.banner = "Usage: ./crimecsv.rb [options] [filename(s) to scrape]"
            
            #a single string of output directory
            opts.on("-o", "--output [DIR]", String, "Output directory") do |o|  
                if o
                    options.output = o
                else
                    options.output=options.output
                end
            end

            #Array of IDs to parse
            opts.on("-i", "--ids [IDs]", "Provide a comma-separated (unspaced) list of unique agency IDs") do |i|
                if i
                    i.split(',').each do |it|
                        options.ids << it
                    end
                else
                    options.ids = nil
                end             
            end

            #Boolean to use local copy or fetch remote copy
            opts.on("-l", "--local", "Only parse local copy, if it exists.") do |l|
                options.local = l
            end

        end

        begin
            opt_parser.parse! 
            options
        rescue
            OptionParser::MissingArgument
            puts $!.to_s + " must add an argument with the flag"
            puts opt_parser
            exit
        end
    end
end

def id_namer(csv)
    pattern = /^(N.+)\s+Total/
    id = pattern.match(csv)[1].strip
    return id            
end

class UCRPDFParser    
    def initialize(file_name, csvs_output, local=false, id=false)
        @file_name = file_name
        @csvs_output = csvs_output
        @local = local
        @id_list = id
        @local_dir = "data/pdfs"
    end

    def output_dir(output)
        if output[-1]=='/'
            return output
        else
            output = output+"/"
        end
    end

    def scrape()
        local_dir = @local_dir
        csvs_output = output_dir(@csvs_output)
        if @local
            if Dir.entries(local_dir).include?@file_name
                puts @file_name + " found on local machine."
                puts "Processing "+@file_name
            else
                abort("File not found. Try running the script without the local flag to retrieve from the web.")
            end
        else
            if Dir.entries(local_dir).include?@file_name
                puts @file_name + " found on local machine."
                puts "Processing "+@file_name
            else
                retrieve(@file_name, local_dir)
            end
        end
        FileUtils.mkdir_p(csvs_output)
        peel(@file_name, csvs_output, @id_list)
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

    def filenamer(id, covers, release_date, csvs_output)
        year_pattern = /.*(201\d)/
        if @file_name.end_with?('stats.pdf')
            outfile = csvs_output + release_date.to_s + "-for-" + id + "-" + year_pattern.match(@file_name)[1] + "annual.csv"
        else
            outfile = csvs_output + release_date.to_s + "-for-" + covers.to_s[0..-4] + "-" + id + ".csv"
        end
    end

    def dateify(csv)
        if csv[0][-1]!= ""
            date = csv[0][-1]
        else
            date = csv[1][-1]
        end
        return date
    end

    def write_csv(table_area, outfile)
        table_csv = CSV.parse(table_area)

        heds = ["crime", "month_last_yr", "month_this_yr", "ytd_last", "ytd_this_yr", "cleared", "juvie_cleared"]
        CSV.open(outfile,"wb") do |csv|
            csv << heds
            table_csv.each do |row|
                next if row[0].strip.end_with?("Total:","Index","Crime")
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
    end

    def peel(file_name, csvs_output, id_list=false)
        pdfs_dir = 'data/pdfs/'
        counter = 0
        page_area = [97.55,11.19,573.48,778.62]
        extractor = Tabula::Extraction::ObjectExtractor.new(pdfs_dir+file_name, :all)
        extractor.extract.each_with_index do |pdf_page, page_index|
            first_csv = pdf_page.get_table.to_csv
            my_csv = CSV.parse(first_csv)
            date = dateify(my_csv)
            coverage = my_csv[4][-1].split('-')[1]
            id = id_namer(first_csv)
            if id.downcase == "new jersey"
                id = "state"
            end
            if @id_list.length>0
                next unless @id_list.include?(id)
            end
            release_date = Date.parse date
            covers = Date.parse coverage
            outfile = filenamer(id, covers, release_date, csvs_output)

            table_area = pdf_page.get_area(page_area).get_table.to_csv
            write_csv(table_area, outfile)
            counter += 1
        end
        extractor.close!    
        puts counter.to_s + " pages from " + file_name + " converted to CSVs."
    end
end