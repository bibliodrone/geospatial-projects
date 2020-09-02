# extractImageData.py
# Gerald Walden
# China maps project
# 8/26/2020

# Harvard University\Scanned Maps in Wikimedia Commons and Wikidata Project - General\China maps project files\China map image lists and downloads from DRS\ExtractedImageFilesXML
# This code illustrates how to use lxml etree with XML namespaces

# xmlns:premis = "info:lc/xmlns/premis-v2" ==> premis:objectIdentifierValue
# xmlns:hulDrsAdmin = "http://hul.harvard.edu/ois/xml/ns/hulDrsAdmin" ==> hulDrsAdmin:uriValue

# xpath1 = "mets/amdSec/techMD/mdWrap/xmlData/object/objectIdentifierType"
# xpath2 = "mets/amdSec/techMD/mdWrap/xmlData/object/objectIdentifierType/objectIdentifierValue"

from lxml import etree
import os
import csv
	
# create a list of files to iterate over for lxml parsing.
xmlfiles = []

# update hardcoded path to image xml files, to reflect relative path from this script's working directory
folderpath="ExtractedImageFilesXML"

# assemble list of xml files
fdir = os.listdir(folderpath)
for f in fdir:
    if f.endswith(".xml"):
        xmlfiles.append(os.path.join(folderpath,f))
        #print(folderpath, f)

# loop thru xml files, read each and extract target data

results=[["HUL_DRS_DESCRIPTOR_ORACLE","uri_type_IDS", "HUL_DRS_FILE_ORACLE"]]
for fx in xmlfiles:
    output = [] # "row"
    hul_desc = [] # "cell"
    urn3 = [] # "cell"
    hul_file = [] # "cell"
    
    tree = etree.parse(fx)
    
    # To print all elements, which is useful for initial testing --> print(elem.tag, " @", elem.attrib, elem.text)
        # Targeting of element data is here based on the text of its preceding sibling.
        # ...thus it is the elem.getnext().text that is returned.
    
	# note the syntax for indentifying a tag which includes a namespace --- "{namespaceURL}tag"
    for elem in tree.getiterator():       
        if elem.tag == "{info:lc/xmlns/premis-v2}objectIdentifierType":
            if elem.text=="HUL_DRS_DESCRIPTOR_ORACLE":
                hul_desc.append(elem.getnext().text)
            elif elem.text=="HUL_DRS_FILE_ORACLE":
                hul_file.append(elem.getnext().text)
        elif elem.tag == "{http://hul.harvard.edu/ois/xml/ns/hulDrsAdmin}uriType":
            if elem.text=="IDS":
                urn3.append(elem.getnext().text)
    
    # add "cells" to output "row"
    output.append(",".join(hul_desc)) 
    output.append(",".join(urn3))
    output.append(";".join(hul_file))
    print(output)
    
    results.append(output) #append "row" to "table" 

# will save .csv file to same folder as this script
with open('extracted_image_xml_metadata.csv', newline='', mode='w') as outfile:
    filewriter = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    for row in results:
        filewriter.writerow(row)
