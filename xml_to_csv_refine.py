from lxml import etree
from collections import OrderedDict
import os
import csv
# <--pprint is useful for debugging-->
# import pprint
# pp = pprint.PrettyPrinter(indent=4)

xpathTargets = [
    ("series_ordinal_qualifier(P1545)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/serinfo[1]/issue[1]"),
    ("Label/title(P1476)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/title"),
    ("creator(P170)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/origin"),
    ("edition(P393)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/edition[1]"),
    ("coordinates(P1334)", "/metadata/idinfo[1]/spdom[1]/bounding[1]/eastbc[1]"),
    ("coordinates(P1332)", "/metadata/idinfo[1]/spdom[1]/bounding[1]/northbc[1]"),
    ("coordinates(P1333)","/metadata/idinfo[1]/spdom[1]/bounding[1]/southbc[1]"),
    ("coordinates(P1335)","/metadata/idinfo[1]/spdom[1]/bounding[1]/westbc[1]"),
    ("publisher(123)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/pubinfo[1]/publish[1]"),
    ("place_of_publication(P291)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/pubinfo[1]/pubplace[1]"),
    ("depicts(P180)", "/metadata/idinfo[1]/keywords[1]/place[1]/placekey"),
    ("publication_date(P577)","/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/pubdate[1]"),
    ("date_depicted(P2913)", "/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srctime[1]/timeinfo[1]/sngdate[1]/caldate[1]")
]

#Columns with static values
additionalHeaders = [
    ("Instance_of(P31)", "Map Edition"),
    ("scale(P1752)", "250000"),
    ("language_of_work_or_name(P407)", "English"),
    ("height(P2048)", "47cm"),
    ("width(P2049)", "66cm"),
    ("described_at_URL(P973)","http://id.lib.harvard.edu/alma/990094028280203941/catalog"),
    ("location(P276)","Harvard Library" ),
    ("Harvard_Library_system_number(P5199)","990094028280203000")    
]


#XML files to be parse should be at relative path in folder named in 'folderpath'
folderpath = "ChinaMaps"

# Create list of XML file names found in 'folderpath'
xmlfiles = []
fdir = os.listdir(folderpath)

for f in fdir:
    if f.endswith(".xml"):
        xmlfiles.append(os.path.join(folderpath,f))

# Create list of header-names for table columns, based on values in each tuple in 'xpathTargets' and 'additionalHeaders'
headers = []
addlValues = [] #non-xpath(hardcoded)column values

#xpath headers
for xt in xpathTargets:
    headers.append(str(xt[0])) #header label corresponding to Wikidata label from tuple

#non-xpath headers
for ah in additionalHeaders:
    headers.append(str(ah[0])) #headers for hard-coded column values
    addlValues.append(str(ah[1])) #hard-coded column values

#Add 'Description' header
headers.append("Description")


#parse XML and create data for conversion to CSV format

joinToken = "; " # use when joining multi-values into single cell (e.g. 'depicts(P180) values')
CSV_write_file = "china_maps_wikidata.csv"


with open(CSV_write_file, 'w', newline = '') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    #print("Wrote row", headers)
    
    for file in xmlfiles:
        resultRow=[]
        tree = etree.parse(file)
        for x in xpathTargets: #for each name/xpath tuple:
            x_key  = x[0] #name
            x_path = x[1] #xpath
            result = tree.xpath(x_path) #returns list of element objects
            # want a list of the text values from each 'result' object
            tagValue = [] 
            for r in result:
                tagValue.append((r.text).strip())
            resultString = joinToken.join(tagValue) #final yield is delimited string
            #print("ResultString", resultString)
            resultRow.append(resultString)
        for av in addlValues:
            resultRow.append(av)
        
        #Finally, tack on the concatenated description string
        #"1:250,000 China  topographic series map (L500 "+ordinal number+") produced by the Army Map Service,"+published date
        desc_ord_num = tree.xpath("/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/serinfo[1]/issue[1]")[0].text
        desc_pub_date = tree.xpath("/metadata/dataqual[1]/lineage[1]/srcinfo[1]/srccite[1]/citeinfo[1]/pubdate[1]")[0].text
        
        #re-format date string if possible.
        if len(desc_pub_date)==6:
            desc_pub_dateY = desc_pub_date[0:4]
            desc_pub_dateM = desc_pub_date[4:]
            desc_pub_date = str(desc_pub_dateM + "/" + desc_pub_dateY)
        
        descriptionString = "1:250,000 China  topographic series map (L500 _ORDNUM_) produced by the Army Map Service, _PUBDATE_".replace("_ORDNUM_", desc_ord_num).replace("_PUBDATE_", desc_pub_date)
        resultRow.append(descriptionString)
        
        #Write the full resultRow to the CSV file
        writer.writerow(resultRow)
        print("Parsed XML in", file, "--- appended row to", CSV_write_file)