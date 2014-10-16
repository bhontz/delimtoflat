"""
    DelimitedToFlat.py
    
    Command line procedure for converting delimited files to flat files.
    
    Requires a Parameters.txt file to be passed as an argument.  This file can use any filename, but the structure specified below is required.
    
    Additional (optional) argument:
    -l CREATES the layout file.  You will need to use this argument when dealing with a new delimited file for the first time.
    
    Typically, you will modify the layout file in the following ways before running the script again to create your flat file:
        1) Any VERBATIM field should be identified by replacing the field width with a V
        2) You can reorder the fields any way you want to specify the layout of your flat file
        3) You can change the field widths any way you want, though note the fields widths provided by the -l argument are the maximum width found in the data
        4) You can remove fields you don't want in your flat file
        5) You can add a field with name P-A-D-D-I-N-G to add a "blank space" within your flat file.  Specify the field width you want for your padding.
        
    Structure of the Parameters.txt file:
        DELIMpathfn = e:/raw/myproject/some-delimited-file.txt
        LAYOUTpathfn = e:/raw/myproject/layout-of-delimited-file.csv   # note must be CSV -- will contain two fields, file name and field width
        CENDpathfn = e:/raw/myproject/closed-end-data.dat
        VERBpathfn = e:/raw/myproject/verbatim-data.dat   # note you don't need to specify this argument if your layout file doesn't include a V field width
        DELIMchar = [|]   # other options here would be for tab delimited [\t] or comma delimited [,]
        UIDfldname = RespondentID   # you will need to edit the some-delimited-file.txt and identify the unique respondent identifier field and designated it here
        
   Note that the layout of the VERBATIM file will be RespondentID  FieldName  Verbatim.  The width of the RespodentID field is determined in the layout file.
   The FieldName field with will be either 16, 24, 32, 48, 64, 128 (or wider) depending up the maximum field width of the fields in the layout file
   The VERBATIM file is written out as UTF-8 whereas the CEND file is written as a cp-1252 (ascii) code page file
        
"""
__version__ = "$Revision: 0.06 $"
__source__ = "$Header: \python27\DelimToFlat.py, v0.06 10/15/2014 $"

import os, sys, time, argparse
from DelimToFlatClass import DelimToFlat

def HandleCommandLineArguments():
   path, fn = os.path.split(sys.argv[0])
   if len(sys.argv) == 1:
      sys.stdout.write("C:\ScriptsFolder>python %s -h\n\tUse the -h argument after the module name to list the arguments required." % fn)
      sys.exit(1)
   
   strUsageMessage = \
   """
   %s converts a delimited text file to a flat file.  Will split a delimited file into CMR "closed end" and seperate "verbatim" filesets file.
   
   Example:
      C:\pythonscripts\python DelimitedToFlat.py [-l] parameters.txt
   """ % fn.upper()
   
   parser = argparse.ArgumentParser(description=strUsageMessage)
   parser.add_argument('strPARAMpathfn', action="store", type=str, help="Pathfilename of the required parameter file.  See the README for instructions.")
   parser.add_argument("-l", "--bCreateLayout", help="use -l to CREATE the layout file specified within parameters.txt", action="store_true")
   
   ns = parser.parse_args()
   
   return ns


def ParseParameterFile(fp):
    """
        This method parses the tab delimited parameter file and then returns the parameters as a dictionary
    """
    dictParameters = {}
    lstParams = fp.readlines()
    for row in lstParams:
        lstRow = row.split("=")
        k = lstRow[0].rstrip().lstrip()
        if not dictParameters.has_key(k):
            dictParameters[k] = str(lstRow[1]).rstrip().lstrip()
    fp.close()
    del fp
                            
    return dictParameters

if __name__ == '__main__':
    
    print "hello from DelimitedToFlat.py"
    
    argns = HandleCommandLineArguments()   # can comment this line out
 
    if os.path.exists(argns.strPARAMpathfn):
        try:
            fpPARAM = open(argns.strPARAMpathfn, "rt")
        except IOError, detail:
            sys.stdout.write("Unable to open file:%s for READ. Details:%s" % (argns.strPARApathfn, detail))
        else:
            dictParameters = ParseParameterFile(fpPARAM)
            fpPARAM.close()
                        
            sys.stdout.write("--------------------------------------------------------------\n")
            sys.stdout.write("Start of Process: %s\n\n" % time.strftime("%H:%M:%S", time.localtime()))
            
            obj = DelimToFlat(dictParameters)
            
            if argns.bCreateLayout:
                obj.CreateLayout()
            else:
                obj.Flatten()
                
            del obj

            sys.stdout.write("\n\nEnd of Process: %s\n" % time.strftime("%H:%M:%S", time.localtime()))
            sys.stdout.write("-------------------------------------------------------------\n")    
        
    else:
        print "Can't find parameter file pathfilename:%s.  Aborting." % argns.strPARAMpathfn