#!/usr/bin/env ruby
# encoding: utf-8

require_relative './lib/csver.rb'

if __FILE__ == $0
	options = Optparser.parse(ARGV)

    if ARGV.length > 0
        ARGV.each do |argv|
        	ucr_pdf_parser = UCRPDFParser.new(argv, options.output, local=options.local, id=options.ids)
            ucr_pdf_parser.scrape()
        end
    else
        abort("You must list at least one file to scrape.")
    end
end