
import pandas as pd
import json
import requests
import csv
import xlsxwriter
from datetime import datetime


data = {}



headersM = {
    'User-Agent': 'SECche',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'data.sec.gov',
}
# Headers for SEC Api
cikDir = 'cik.csv'

#read cik.csv as a pandas DataFrame
ciksDF = pd.read_csv(cikDir, delimiter='\t', header=None)
#set the column with all the tickers as the index
ciksDF = ciksDF.set_index(0)


financial_metrics = {}

with open('metrics.csv', 'r') as file:
    csv_reader = csv.reader(file)
    # Skip the header if exists
    next(csv_reader, None)  # Skip the header row
    # Create an empty dictionary
    financial_metrics = {}
    # Iterate over each row in the CSV file
    for row in csv_reader:
        key, value = row
        financial_metrics[key.strip()] = value.strip()

def make10(number):
    return '{:0>10}'.format(number)
# Make the CIK 10 digits

def getCIK(ticker):
    #return CIK if it exists, with the format CIK0000000000
    try:
        return ("CIK" + make10(int(ciksDF.loc[ticker.lower(), 1])))

    #return None there's no CIK for the ticker
    except:
        return "not"
        exit()
# Get the CIK from cik.csv

def search(query):
    try:
        unit = [i for i in response_json['facts']['us-gaap'][query]['units']][0]
        results = response_json['facts']['us-gaap'][query]['units'][unit]
    except:
        results = 0
    if results == 0:
        return("0")
    else:
        for i in results:
            if i['form'] == "10-K":
                end_date = datetime.strptime(i["end"], "%Y-%m-%d")
                end_year = end_date.year
                if end_year not in data:
                    data[end_year] = {}
                data[end_year][financial_metrics[query]] = i["val"]
# Search 


Ticker = input("Input Ticker: ")
CIK = getCIK(Ticker)
if CIK == "not":
    exit("Ticker not found! Sorry")
# Get the ticker and convert into a CIK string for URL. 
# If the ticker is not found in cik.csv, return not found. 

generalURL = f"https://data.sec.gov/api/xbrl/companyfacts/{CIK}.json"
print("URL used to access data: " +generalURL)
# Get the URL for the information

response = requests.get(generalURL,headers=headersM)
# Get the JSON from URL
response_json = json.loads(response.text)
# Convert json string to python 

for i in financial_metrics:
    search(i)


df = pd.DataFrame.from_dict(data, orient='index')
df = df.transpose()

sorted_years = sorted(df.columns, reverse=True)
df_sorted = df.reindex(columns=sorted_years)
output_file = (Ticker +'_financial_data.xlsx')

writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
df_sorted.to_excel(writer, index=True, sheet_name='report')
workbook = writer.book
worksheet = writer.sheets['report']
worksheet.set_zoom(100)
accformat = workbook.add_format({'num_format': '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'})
columns = f"B:{chr(len(data) + 65)}"
worksheet.set_column(columns, 12, accformat)
worksheet.autofit()
writer.close()


print("Data exported to:", output_file)

