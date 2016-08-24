!README - DelimitedToFlat.py - see version history at bottom of this document

DelimitedToFlat.py - Command line procedure for converting delimited files to flat files.

Requires a Parameters.txt file to be passed as an argument.  This file can utilize any filename, but the structure specified below is required.

Additional (optional) argument:
-l CREATES the layout file (only).  You will need to use this argument when dealing with a new delimited file for the first time.

Typically, you will modify the layout file in the following ways before running the script a second time to create your flat file:
    1) Any VERBATIM field should be identified by replacing the field width with a V
    2) You can reorder the fields any way you want to specify the layout of your flat file
    3) You can change the field widths any way you want, though note the fields widths provided by the -l argument are the maximum width found in the data.
        Normally you will want to INCREASE the size of the field widths provided by the -l argument.
    4) You can remove fields you don't want in your flat file (e.g. empty fields)
    5) You can add a field with name P-A-D-D-I-N-G to add a "blank space" within your flat file.  Specify the field width you want for your padding.
    
Structure of the Parameters.txt file:
    DELIMpathfn = e:/raw/myproject/some-delimited-file.txt
    LAYOUTpathfn = e:/raw/myproject/layout-of-delimited-file.csv   # note must be CSV -- will contain two fields, file name and field width
    CENDpathfn = e:/raw/myproject/closed-end-data.dat
    VERBpathfn = e:/raw/myproject/verbatim-data.dat   # note you don't need to specify this argument if your layout file doesn't include a V field width
    DELIMchar = [|]   # other options here would be for tab delimited [\t] or comma delimited [,]
    TEXTqualifier = ["]   Text qualifier is the character that surrounds a delimiter that is found WITHIN a field. Options here are typically ", ' or empty
    If you leave this empty (e.g. []) then your indicating that you DON'T WANT a text qualifier, meaning your fields can contain " or ' chars.
    UIDfldname = RespondentID   # you will need to edit the some-delimited-file.txt and identify the unique respondent identifier field and designated it here
    
Note that the layout of the VERBATIM file will be RespondentID  FieldName  Verbatim.  The width of the RespodentID field is determined in the layout file.
The FieldName field with will be either 16, 24, 32, 48, 64, 128 (or wider) wide, depending up the maximum field width of the fields in the layout file
The VERBATIM file is written out as UTF-8 whereas the CEND file is written as a cp-1252 (ascii) code page file

Example usage:

c:\pythonscripts\python delimitedtoflat.py -l myparameters.txt   # this would create the LAYOUT file specified as LAYOUTpathfn in the myparameters.txt file

c:\pythonscripts\python delimitedtoflat.py myparameters.txt  # this would create the CEND (and potentially) VERB files from the revised LAYOUT file

Version History:
v.03 - updated 5/29/2014 - added record counter to show progress during long conversions

v.04 - updated 7/8/2014 - corrected record counter (was showing # fields * # records) and added display of a final record count tally

v.05 - updated 7/11/2014 - added "errors='ignore' parameter to the unicodereader() method as noted that non-UTF-8 characters provided in the feed.

v.06 - updated 8/26/2014 - added the TEXTqualifier parameter to support a problematic project file within which the verbatim fields contain double quotes that weren't meant to be used as a text qualifier.

