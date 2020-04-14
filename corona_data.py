import camelot
import os, glob
import pathlib
import requests
import pandas as pd
import csv
from shutil import rmtree
import time

def createPath(s):
    try:  
        os.mkdir(s)
    except OSError:  
        assert False, "Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"
    return s

def deletePath(s): # Dangerous! Watch out!
    try:  
        rmtree(s,ignore_errors=False)
    except OSError:  
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

def pageNum(s):
	n = s.find("page")
	i = n + 5
	y = i + 1
	if s[y] != "-":
		y += 1
		return int(s[i:y])
	return int(s[i])

start_time = time.time()

#Get the PDF
url = "https://www.gob.mx/cms/uploads/attachment/file/546234/Tabla_casos_positivos_COVID-19_resultado_InDRE_2020.04.12.pdf"
file = requests.get(url).content

# #Create TEMP path
myPath = str(pathlib.Path(__file__).parent.absolute())
tempPath = createPath(myPath + "/TEMP")
tempPath = myPath + "/TEMP/"

# #Save PDF
with open(tempPath + "current.pdf", "wb") as f:
	f.write(file)

# PDF to CSV Files
# tables = camelot.read_pdf(tempPath + "current.pdf", pages="1-end", flavor="stream", edge_tol=50)
tables = camelot.read_pdf(tempPath + "current.pdf", pages="1-end")
tables.export(tempPath + "cases.csv", f='csv', compress=False)

# Collect and sort all CSV file names
all_files = glob.glob(os.path.join(tempPath, "cases-page-*-table-1.csv"))
all_files.sort(key=pageNum)

# Get the header of the table from the first file
with open(all_files[0], "r") as doc:
	read = csv.reader(doc)
	header = next(read)

#Reads the CSV files as a Pandas Data Frame
dfs = [pd.read_csv(f, sep=",") for f in all_files]

#Add the header to all the data frames
for i in dfs:
	i.columns = header

#Join the data frames and export as CSV
finaldf = pd.concat(dfs, axis=0, join="outer")
finaldf.to_csv( "merged.csv", index=False, encoding='utf-8-sig')

#Delete temp files
deletePath(myPath + "/TEMP")

print("--- %s seconds ---" % (time.time() - start_time))
