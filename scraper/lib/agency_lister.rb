#!/usr/bin/env ruby
# encoding: utf-8

require_relative './csver.rb'

def write_to_csv(big_array)   
    outfile = '../lookup_agency_new.csv'
    heds = ['id', 'dept_name']
    CSV.open(outfile,"wb") do |csv|
        csv << heds
        big_array.each do |row|
            csv << row
        end
    end
end

def peel(pdfs_dir='../data/pdfs/')
    big_array = []
    Dir.foreach(pdfs_dir) do |item|
	    page_area = [97.55,11.19,573.48,778.62]
	    next if item.start_with?('.')
	    next if item.end_with?('.txt')
        next if item.end_with?('.csv')
        puts 'Extracting IDs from ' + item
        extractor = Tabula::Extraction::ObjectExtractor.new(pdfs_dir+item, :all )
        extractor.extract.each_with_index do |pdf_page, page_index|
            first_csv = pdf_page.get_table.to_csv
            my_csv = CSV.parse(first_csv)
            id = id_namer(first_csv)
            next if not id
            next if id.downcase == "new jersey"
            if my_csv[5][0]!=""
                dept = my_csv[5][0] #this format changed from earlier editions
                if dept.include? id and my_csv[6][0]!=""
                    dept = my_csv[6][0]
                end
            end

            kv = [id, dept]
            next if big_array.include?kv
            big_array << kv
        end

        extractor.close!
    end
    puts 'Writing ' + big_array.length.to_s + ' agencies to lookup_agency.csv'

    write_to_csv(big_array)
end

if __FILE__ == $0
    peel() #only declare the directory if different
end