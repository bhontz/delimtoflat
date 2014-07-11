"""
    DelimToFlat.py
    
    A class that supports converting delimited files to flat files.
    
    Class includes the following methods:
    
    CreateLayout() - Determines the maximum field widths of each field within the delimited file, producing a CSV file of the field names and widths
    
    Flatten() - Takes the layout (presumably modified) file created by CreateLayout() and uses the layout to create a flat file from the delimited file.
    "Presumably modified" means that the layout.csv file can be modified in terms of changing the field ordering, removing fields, designating field widths
    as V which means the data from these fields will be written into a verbatim file, and adding fields(s) with field name P-A-D-D-I-N-G to force deliberate
    spacing within the fixed file output.    
"""
__version__ = "$Revision: 0.05 $"
__source__ = "$Header: \python27\DelimToFlat.py, v0.05 7/8/2014 $"

import sys, unicodecsv, csv, time, codecs, unicodedata

class DelimToFlat():
    """
        manages the FTP process and returns a list of validated files pulled
        from the project's FTP folder
    """
    def __init__(self, dictParameters):
        if dictParameters.has_key("DELIMpathfn"):
            self.strDELIMpathfn = dictParameters["DELIMpathfn"]
        if dictParameters.has_key("LAYOUTpathfn"):
            self.strLAYOUTpathfn = dictParameters["LAYOUTpathfn"]
        if dictParameters.has_key("CENDpathfn"):
            self.strCENDpathfn = dictParameters["CENDpathfn"]
        if dictParameters.has_key("VERBpathfn"):
            self.strVERBpathfn = dictParameters["VERBpathfn"]
        if dictParameters.has_key("DELIMchar"):
            self.strDELIMchar = self.__CleanDelimChar(dictParameters["DELIMchar"])  # assumes dictionary contains brackets around delimiter like [\t]
        if dictParameters.has_key("UIDfldname"):
            self.strUIDfldname = dictParameters["UIDfldname"].upper()  # user needs to identify the respondent UID fieldname
        return
    
    def __del__(self):
        return
    
    def PrintParameters(self):
        print self.strDELIMpathfn
        print "(%s)" % self.strDELIMchar
        return
    
    def CreateLayout(self):
        """
            CreateLayout() - method used to create a LAYOUT file (csv) representing the maximum field width of each field in the delimited file
        """
        bHasBOM, nLenBOM = self.__HasBOM(self.strDELIMpathfn)
            
        try:
            fDelim = open(self.strDELIMpathfn,'rb')
        except IOError, detail:
            print "unable to open file %s for READ - details:%s" % (self.strDELIMpathfn, detail)
            sys.exit(-1)
            
        if bHasBOM:
            fDelim.seek(long(nLenBOM))   # move past the BOM marker if there is one
            
        try:
            fControl = open(self.strLAYOUTpathfn, 'wt')
        except IOError, detail:
            print "unable to open file - details:%s" % detail
            sys.exit(-1)
        
        reader = unicodecsv.reader(fDelim, delimiter=self.strDELIMchar, encoding='UTF-8', errors='ignore')   
        lstHeaderRecord = reader.next()   # capture the header record of the delimited file     
                    
        dictMaxFieldLns = self.__InitializeDictionary(lstHeaderRecord)
        
        for row in reader:
            for i, col in enumerate(lstHeaderRecord):
                nLen = len(row[i])
                if dictMaxFieldLns[col] < nLen:
                    dictMaxFieldLns[col] = nLen
    
        # now that dictMaxFieldLns is populated with the max field width per field, write out the control file                
        fControl.write("FieldName,MaxFldWidth\n")  # write a header record...
        for col in lstHeaderRecord:
            v = dictMaxFieldLns[col]
            fControl.write("%s,%d\n" % (col, v))
                       
        fControl.close()
        fDelim.close()        
        
        return
        
    def Flatten(self):
        """
            Takes a two field CSV control file containing a header record.  Fields are FieldName and MaxFldWidth.  The MaxFldWidth column can contain
            a value of V which will write the delimited file content for this field to the VERBATIM file.   A FieldName value of P-A-D-D-I-N-G will be accepted
            and will create a blank field of the width specified.  Output file has codepage cp-1252 (aka ASCII).  If a VERBATIM file is specified and created
            it will be created in using a UTF-8 code page with field values of UID, fieldname and verbatim field value.
        """
        bHasVerbatim = False
        
        try:
            fControl = open(self.strLAYOUTpathfn, 'rt')
        except IOError, detail:
            print "unable to open file LAYOUT file for read: %s - details:%s" % (self.strLAYOUTpathfn, detail)
            sys.exit(1)
        else:
            reader = csv.reader(fControl, delimiter=',')   # control file uses comma delimiter
            reader.next() # skip header record
            lstControl = list(reader)
            for l in lstControl:
                l[0] = str(l[0].upper())   # ucase the fieldname to facilitate matchbacks
                if l[1] == 'V' or l[1] == 'v':   # we know we will need the VERBpathfn
                    bHasVerbatim = True
            del reader
            fControl.close()
            del fControl
     
            try:
                fout = codecs.open(self.strCENDpathfn, encoding='cp1252', mode='w', errors='ignore')
            except IOError, detail:
                print "unable to open file CEND OUTPUT FILE:%s for WRITE - details:%s" % (self.strCENDpathfn, detail)
                sys.exit(1)
            
            if bHasVerbatim:
                try:
                    fFileSet = codecs.open(self.strVERBpathfn, encoding='UTF-8', mode='w', errors='ignore')
                except IOError, detail:
                    print "unable to open VERBATIM OUTPUT file %s for WRITE - details:%s" % (self.strVERBpathfn, detail)
                    sys.exit(1)
    
            bHasBOM, nLenBOM = self.__HasBOM(self.strDELIMpathfn)
    
            try:
                fDelim = open(self.strDELIMpathfn, 'rb')
            except IOError, detail:
                print "unable to open DELIMITED file %s for READ - details:%s" % (self.strDELIMpathfn, detail)
                sys.exit(1)
            else:
                
                if bHasBOM:   # push past the BOM marker if one is found
                    fDelim.seek(long(nLenBOM))
        
                reader = unicodecsv.reader(fDelim, delimiter=self.strDELIMchar, encoding='UTF-8', errors='ignore')
                lstHeaderRecord = reader.next()
                lstHeaderRecord = list(str(l.upper()) for l in lstHeaderRecord)
                
                # build up a dictionary with keys of field labels and values of the field column ordering (0,1,2...)
                nMaxFldNameWidth = 0
                dictHeaderRecord = {}
                for i, col in enumerate(lstHeaderRecord):
                    if len(col) > nMaxFldNameWidth:
                        nMaxFldNameWidth = len(col)
                    dictHeaderRecord[col] = i
                    
                nMaxFldNameWidth = self.__VERBFldNameWidth(nMaxFldNameWidth)
                
                nUID = lstHeaderRecord.index(self.strUIDfldname)  # column of the record UID
                lRec = 1L                
                for row in reader:
                    for r in lstControl:
                        if r[0] == "P-A-D-D-I-N-G":   # this field can be inserted into the layout to insert blank spaces
                            nWidth = int(r[1])
                            fout.write("%s" % ''.center(nWidth))
                        else:
                            if r[0] == self.strUIDfldname:
                                nUIDWidth = int(r[1])   # capture this field width in for the VERBpathfn layout
                                
                            nCol = dictHeaderRecord[r[0]]
                            if r[1] == 'V' or r[1] == 'v':
                                strVerbatim = row[nCol].rstrip().lstrip()
                                if strVerbatim != "":
                                    fFileSet.write("%-*.*s%-*.*s%s\n" % (nUIDWidth,  nUIDWidth, row[nUID], nMaxFldNameWidth, nMaxFldNameWidth, r[0], strVerbatim))
                            else:
                                nWidth = int(r[1])
                                strValue = ""
                                if dictHeaderRecord.has_key(r[0]):
                                    strValue = self.__strip_accents(unicode(row[nCol]))
                                fout.write("%-*.*s" % (nWidth,nWidth,strValue))

                    if (lRec % 1000L) == 0:
                        sys.stdout.write("\r\trecords processed:%12ld" % lRec)
                        sys.stdout.flush()
                    lRec += 1L
                                
                    fout.write('\n')
                
                fout.close()
                if bHasVerbatim:
                    fFileSet.close()
                    
                sys.stdout.write("\t\n\nCompleted. Total number of records processed:%12ld " % lRec)
                        
        return
        
    def __HasBOM(self, strPathfn):
        """
            Looks at a file passed by pathfile name and determines if the file contains a BOM character or not (returns true/false)
        """
        bHasBOM = False
        nLenBOM = 0  # can be different lengths, returns 0 if bHasBOM = False
        
        lstBOMAlternatives = [codecs.BOM_UTF32, codecs.BOM_UTF16, codecs.BOM_UTF8]
    
        try:
            fp = open(strPathfn,'rb')
        except IOError, detail:
            print "unable to open file %s for READ - details:%s" % (strPathfn, detail)
            sys.exit(-1)
        else:
            header = fp.read(4)  # just need the first four bytes of the file to determine if a BOM exists
            fp.close()
            
            for l in lstBOMAlternatives:
                if header.find(l) == 0:
                    bHasBOM = True
                    nLenBOM = len(l)
                    break
                
        return bHasBOM, nLenBOM
    
    def __InitializeDictionary(self, lstHeader):
        """
            Initializes a dictionary which will contain keys of the fields in the delimited file
            and values of the max widths of the fields within the delimited file
        """
        d = {}
        for l in lstHeader:
            if d.has_key(l):
                print "Fatal error - file contains replicated field name:%s.  Fatal, aborting."
                sys.exit(-1)
            else:
                d[l] = 0
        return d
    

    def __strip_accents(self, s):
        return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore')
        
        
    def __CleanDelimChar(self, s):
        """
            assumes strDelimiter is passed with square brackets like [|] or [\t].
            Returns the single character that would be used by methods requiring a delimiter character
        """
        if s.find('[') != -1 and s.find(']') > 0:
            s = s.replace('[', '').replace(']', '')
            if s == '\\t':
                s = '\t'
        else:
            print "Invalid delimiter specified within the parameters dictionary:%s" % s
            s = None   # this will cause a fail somewhere down the road
                
        return s
    
    def __VERBFldNameWidth(self, nMaxWidth):
        """
            In an effort to keep a consistent field width between very similar projects, this project returns
            widths of 16, 24, 32, 48, 64 or 128 dependent upon the nMaxWidth argument.  Realize this doesn't work
            if the widths are close to the list parameters below.
            Will return the nMaxWidth passed argument if nMaxWidth exceeds 128
        """
        lstLen = [16, 24, 32, 48, 64, 128]
        for v in lstLen:
            if v > nMaxWidth:
                nMaxWidth = v
                break
            
        return nMaxWidth  

if __name__ == '__main__':
    dictNew = {"DELIMpathfn": "/users/brad/my projects/raw/Nissan_Sales_20140520.txt", "DELIMchar": "[|]", \
               "LAYOUTpathfn": "/users/brad/my projects/raw/Nissan_Sales_20140520_LAYOUT.csv", \
               "CENDpathfn" : "/users/brad/my projects/raw/BradRules.dat", "UIDfldname": "SampleID", \
               "VERBpathfn" : "/users/brad/my projects/raw/BradRulesVERB.dat"}
    obj = DelimToFlat(dictNew)
    ###obj.CreateLayout()
    obj.Flatten()
    del obj
    