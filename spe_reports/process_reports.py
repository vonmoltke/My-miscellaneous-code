#!/usr/bin/python

# Copyright 2012  Wayne Krug

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This is a short-ish data parsing and formatting routine I wrote to extract
# data from some ugly text dumps generated from PDF files

import sys, csv, re

# Set up an empty data dictionary
section_data = {}

# Min and maxy years
min_year = 9999
max_year = 0

# Get files from the command line and process them
for filename in sys.argv[1:]:
    # Parse each line, pulling the current and previous year totals for each 
    # section and inserting them into the section's dictionary.  If the section
    # has no entries, create a new dictionary.
    
    # The filename must be of the form YYYY.txt, as the name will be used to set
    # the current and previous years for the data processing.

    # Open the filename
    filedata = open(filename)
    
    # Get the year out of the name
    data_year = int(filename.split(".")[0])
    
    if data_year > max_year: max_year = data_year
    if (data_year - 1) < min_year: min_year = data_year - 1
    
    # The 2007 dump has a missing column.  Change the prior year index for this
    # dataset
    current_index = 4
    prior_index = 13
    if data_year == 2007: prior_index = 12
    
    # Read the file in, parsing the section data from each line
    for line in filedata:
        section = ""
        try:
            section = re.split("(^.+\(\d+)", line)[1]
            data = re.split("(^.+\(\d+)", line)[2]
        except IndexError:
            print "Error splitting line:"
            print line
            continue
        # end if split fails
        
        # Remove the section number from the key
        section = section.split(" (")[0]
        
        # Check section_data for this key.  If the key is not there, create
        # a new dictionary
        if section not in section_data: section_data[section] = {}
            
        # Clean up the line by removing the trailing parenthesis from the
        # section number, if there, and split into separate values.
        data = re.sub("\)", "", data)
        values = data.split()
            
        # Check the length and determine if data is missing.  Every section
        # has current year data, and this value is always in the same place.
        # Some sections do not have prior year data; these lines will be
        # shorter because the dump leaves these entries blank.            
            
        # Current year number
        section_data[section][data_year] = values[current_index]
            
        # Prior year number, if the section has it
        if len(values) > 11:
            section_data[section][data_year-1] = values[prior_index]
        # end if section has prior year numbers
    # end for each line in the file
    
    filedata.close()
# end for each file on the command line

# Dump the data to a CSV file containing each section encountered and the number
# of paid members for each year from min_year to max_year.  If the section has
# no entry for a given year, insert 0.

# Build a header row for output
header = ['section']
for i in range(min_year, max_year+1): header.append(str(i))
header_row = {}
for key in header: header_row[key] = key

# Create the output file
outfile = open("output.csv", "w")
outwriter = csv.DictWriter(outfile, header, restval='0')
outwriter.writerow(header_row)

# Write out the data
for section in section_data:
    row = {}
    row['section'] = section
    
    for year in section_data[section]:
        row[str(year)] = section_data[section][year]
    # end for each year in the section data
    
    outwriter.writerow(row)
# end for each section

outfile.close()
