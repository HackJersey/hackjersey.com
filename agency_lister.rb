require 'rubygems'
require 'date'
require 'fileutils'
require 'tabula'

def peel(file_name)
    pdfs_dir = "data/burstpdfs/"
    big_array = []
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

        if my_csv[6][0]!=""
        	dept = my_csv[6][0]
        end
        pattern = /^(N.+)\s+Total/
        id = pattern.match(first_csv)[1].strip
        next if id.downcase == "new jersey"
        kv = [id, dept]
        big_array << kv
    end

    outfile = 'agency_lookup.csv'
    heds = ['id', 'dept_name']
    CSV.open(outfile,"wb") do |csv|
            csv << heds
            big_array.each do |row|
            	csv << row
            end
        end
#        end
    extractor.close!
    end
#    counter += 1
end
#puts counter.to_s + " pages from " + file_name + " converted to CSVs."


file_name = "20150327_crimetrend.pdf"
peel(file_name)