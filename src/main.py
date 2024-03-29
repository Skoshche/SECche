# Import Statements
# First party
from os import getcwd
from csv import reader
from json import loads
import requests
from typing import Final
from datetime import datetime, date
import re

# Second party

# Third party
from requests import get, Response
from pandas import read_csv, DataFrame, ExcelWriter

# File Docstring
# --------------------------------
#
# Authors: @Skoshche <https:www.github.com/Skoshche>                  || Owner
#          @MaxineToTheStars <https:www.github.com/MaxineToTheStars>  || Contributor
# ----------------------------------------------------------------


# Class Definitions
class CIKNotFoundException(Exception):
    # Enums

    # Interfaces

    # Constants

    # Public Variables

    # Private Variables
    _exceptionMessage: Final[str] = None

    # Constructor
    def __init__(self, message: str):
        """
        Constructs a new ``CIKNotFoundException`` instance.

        @return ``CIKNotFoundException`` - ``CIKNotFoundException`` instance
        """
        # Instance the base Exception
        super().__init__(message)

        # Set the exception message
        self._exceptionMessage = message

    # Public Static Methods

    # Public Inherited Methods
    def getMessage(self) -> str:
        """
        Returns the exception message.

        @return ``str`` - The exception message
        """
        return "ERROR MESSAGE"
        #return self._exceptionMessage

    # Private Static Methods

    # Private Inherited Methods


#Secche!!
class Secche:
    # Enums

    # Interfaces

    # Constants
    _API_QUERY_URL: Final[str] = "https://data.sec.gov/api/xbrl/companyfacts/CIK{centralIndexKey}.json"
    _EDGAR_URL_FORMAT: Final[str] = "https://www.sec.gov/edgar/browse/?CIK={centralIndexKey}"
    _VERSION_NUMBER: Final[str] = "beta-v1.0.0"
    _OUTPUT_FILENAME: Final[str] = "{ticker}_financial_data.xlsx"
    _API_QUERY_HEADERS: Final[dict] = {"User-Agent": "secche@skoshche.com","Accept-Encoding": "gzip,deflate", "Host": "data.sec.gov"}
    _CIK_QUERY_HEADERS: Final[dict] = {"User-Agent": "secche@skoshche.com","Accept-Encoding": "gzip,deflate", "Host": "www.sec.gov"}
    _FINANCIAL_METRIC_OPTIONS_FULL_PATH: Final[str] = getcwd().replace("/src", "/src/data/financialMetricOptions.csv")
    _COMPANYNAME: Final[str] = None
    _multiple = 0

    # Public Variables

    # Private Variables
    _outputData: Final[dict] = None
    _outputDateTime: Final[dict] = None
    _financialMetricOptions: Final[dict] = None
    _centralIndexKeyDataFrame: Final[DataFrame] = None
    
    #Results for dataframe output
    _IncomeStatement: Final[any] = 0
    _BalanceSheet: Final[any]  = 0
    _CashFlow: Final[any]  = 0
    _Ratios: Final[any]  = 0
    _URL = 0
    _EDGAR_URL = 0
    
    #Printout
    _Result = 0

    # Constructor
    def __init__(self) -> None:
        """
        Constructs a new ``Secche`` instance.

        @return ``Secche`` - ``Secche`` instance
        """

        # Read the CSV and store the data


        # Instance a new dictionary object
        self._outputData = {}
        self._outputDateTime = {}
        self._financialMetricOptions = {}

        # Read the metric options
        with open(self._FINANCIAL_METRIC_OPTIONS_FULL_PATH, "r") as file:
            # Create a CSV reader
            fileReader: Final[any] = reader(file)

            # Skip the header if it exists
            next(fileReader, None)

            # Iterate
            for optionRow in fileReader:
                # Index is a tuple
                optionKey: Final[str] = optionRow[0].strip()
                # SEC code
                optionValue: Final[str] = optionRow[1].strip()
                # Code name
                optionSheet: Final[str] = optionRow[2].strip()
                # What sheet its on

                # Create 3 dictionaries, Balance Sheet, Income Statement, Cash FLow (depending on FMO.csv)
                if optionSheet not in self._financialMetricOptions:
                    self._financialMetricOptions[optionSheet] = {}
                
                #Save each key inside the dictionary it belongs to
                self._financialMetricOptions[optionSheet][optionKey] = optionValue
                

        # Debugging
        # print('Un-Padded CIK of "AAPL" ->', self._centralIndexKeyDataFrame.loc["AAPL".lower(), "CIK"])

    #Go through structure
    def query(self, ticker: str, filetype: str):
        """
        Queries a given ticker for data and outputs it as a spreadsheet.

        @param ticker - The specified ticker
        @return None
        """

        # Get the specified CIK
        centralIndexKey: Final[str] = self._getCIK(ticker)

        # Check if the CIK is valid
        if centralIndexKey == None:
            ticker = ticker.upper()
            return CIKNotFoundException(f"Central Index Key for ticker {ticker} was not found!")

        # Send the request
        try:
            apiResponse: Final[Response] = get(
                self._API_QUERY_URL.format(centralIndexKey=centralIndexKey),
                headers=self._API_QUERY_HEADERS,
            )
        except:
            return("Cannot connect to SEC API")
        
        self._URL = self._API_QUERY_URL.format(centralIndexKey=centralIndexKey)
        self._EDGAR_URL = self._EDGAR_URL_FORMAT.format(centralIndexKey=centralIndexKey)
        print(f"The URL used: {self._URL}")
        
        # Get the response JSON
        responseJSON: Final[dict] = loads(apiResponse.text)

        self._COMPANYNAME = responseJSON["entityName"]

        # Parse and store data
        #For Balance Sheet and Income Statement
        amountBooks = len(self._financialMetricOptions)

        timesRan = 0

        for book in self._financialMetricOptions:
            #For each value in Balance Sheet or Income statement


        
            for metricOption in self._financialMetricOptions[book]:
                self._parseAndStoreFinancialData(metricOption, responseJSON, book)

            # Create a new spreadsheet and dump the data
            timesRan += 1
            final = False
            if timesRan == amountBooks:
                final = True

            self._createAndStoreFromData(ticker, book, final, filetype)
        
        #What gets returned 
        if filetype == "dataframe":
            return (self._IncomeStatement, self._BalanceSheet, self._CashFlow, self._Ratios, self._URL, self._COMPANYNAME, self._EDGAR_URL)

    #Obtain the CIK value for a given ticker
    def _getCIK(self, ticker: str) -> str:
        """
        Retrieves a CIK from the given ticker.

        @param ticker - The supplied ticker
        @return centralIndexKey - A padded CIK
        """

        response: Final[Response] = requests.get("https://www.sec.gov/files/company_tickers.json", headers=self._CIK_QUERY_HEADERS)
        tickers = response.json()
        for i in tickers:
            if ticker.upper() == (tickers[i]["ticker"]):
                return ((10 - len(str(tickers[i]["cik_str"]))) * "0") + str(tickers[i]["cik_str"])

    #Parse financial data from SEC api and store as dictionary to outputdata
    def _parseAndStoreFinancialData(self, metricOption: str, rawJSONData: dict, book):
        """
        Parses the return JSON data and stores the specified financial metric option.

        @param metricOption - The metric option to look for
        @param rawJSONData - The return JSON from the API
        @return None
        """
        # Declare option data array
        optionData: Final[list] = None

        if book != "Ratios":

            # Try to fetch the specified option
            try:
                # Set option data

                if "shares" in rawJSONData["facts"]["us-gaap"][metricOption]["units"].keys():
                    print(rawJSONData["facts"]["us-gaap"][metricOption]["units"]["shares"])
                    optionData = rawJSONData["facts"]["us-gaap"][metricOption]["units"]["shares"]
                elif "USD" in rawJSONData["facts"]["us-gaap"][metricOption]["units"].keys():
                    optionData = rawJSONData["facts"]["us-gaap"][metricOption]["units"]["USD"]
            except Exception:
                # Option not found, return
                return

            # Check if no entries are available
            if len(optionData) == 0:
                # No entries, return
                return
            
            # print("KEYSSSSS", self._outputData.keys())
            # Iterate
            # The 0,1,2,3,4 etc under a specific option data
            for data in optionData:
                # Get the form type

                formType: Final[str] = data["form"]
                metricRename = self._financialMetricOptions[book][metricOption]

                try:
                    value = int(data["val"])
                except:
                    value = "BROKE BITCH"

                # Retrieve the end date and year
                endDate: Final[str] = data["end"]
                endYear: Final[int] = endDate[0:4]
                endMonth: Final[int] = endDate[5:7]
                try:
                    startDate: Final[str] = data["start"]
                    startMonth: Final[int] = startDate[5:7]
                except:
                    startMonth: Final[int] = endMonth

                filingDate = datetime.strptime(data["filed"], "%Y-%m-%d")

                # Skip forms that aren't 10-K or 10-K/A
                if (formType == "10-Q") or (abs((int(startMonth) - int(endMonth))) in range(2,11)):
                    # Next iteration
                    continue

                if book not in self._outputData.keys():
                    self._outputData[book] = {}
                    self._outputDateTime[book] = {}

                # Create a new entry if specified year is not yet a key
                if endYear not in self._outputData[book].keys():
                    self._outputData[book][endYear] = {}
                    self._outputDateTime[book][endYear] = {}

                if metricRename not in self._outputData[book][endYear].keys():
                    self._outputData[book][endYear][metricRename] = {}
                    self._outputDateTime[book][endYear][metricRename] = {}

                # Populate the grid
                
                try:
                    oldDateString = self._outputDateTime[book][endYear][metricRename]  
                    if filingDate > oldDateString:
                        #set DateTime to filing date, Data to value
                        self._outputDateTime[book][endYear][metricRename] = filingDate
                        self._outputData[book][endYear][metricRename] = float(value)

                        #print values of both
                    else:
                        continue
                except Exception as error:
                    #set DateTime to filing date, Data to value
                    self._outputDateTime[book][endYear][metricRename] = filingDate
                    self._outputData[book][endYear][metricRename] = float(value)

                    #print values of both
        else:
            if book not in self._outputData.keys():
                    self._outputData[book] = {}
                    self._outputDateTime[book] = {}
            
            metricRename = self._financialMetricOptions[book][metricOption]
            for year in self._outputData["Income Statement"].keys():
                if year not in self._outputData[book].keys():
                    self._outputData[book][year] = {}
                    self._outputDateTime[book][year] = {}
                try:
                    EPS = ((int(self._outputData["Income Statement"][year]["Net Income"]) / int(self._outputData["Balance Sheet"][year]["Basic Average Shares"])))
                    self._outputData[book][year][metricRename] = EPS
                except:
                    self._outputData[book][year][metricRename] = "N/A"


                




    #Store the data in dataframes self._(name of book)
    def _createAndStoreFromData(self, ticker: str, book, final, filetype):
        # Create a new data frame
        custom_order = []
        
        dataFrame = (book.replace(" ", "") + "_dataframe")

        dataFrame: Final[DataFrame] = DataFrame().from_dict(
            orient="index",
            data=self._outputData[book],
        )

        # Flip the row and columns
        dataFrame = dataFrame.transpose()

        for i in self._financialMetricOptions[book].values():
            if i not in custom_order:
                custom_order.append(i)

        # Re-index the data
        present_categories = [category for category in custom_order if category in dataFrame.index]
        dataFrame = dataFrame.reindex(columns=sorted(dataFrame.columns, reverse=True))
        dataFrame = dataFrame.reindex(index=present_categories)

        output = (self._OUTPUT_FILENAME, book)
        # Create a new spreadsheet writer

        #Save balance sheet and income statement as two seperate dataframes
        #Can change this to be a dynamic variable
        if book == "Balance Sheet":
            self._BalanceSheet = dataFrame

        elif book == "Income Statement":
            self._IncomeStatement = dataFrame
        
        elif book == "Cash Flow":
            self._CashFlow = dataFrame
        
        elif book == "Ratios":
            self._Ratios = dataFrame

        startRow = 0
        # Convert the data frame to an excel sheet once all variables are set
        if final == True:
            match(filetype.lower()):
                case "excel":
                    self._ExcelFormatting(ticker)
                case _:
                    self._Result = "invalid format"

    #Format for excel (Only if query is Excel output)
    def _ExcelFormatting(self, ticker):
        row = 0

        spreadSheetWriter = ExcelWriter(
            engine="xlsxwriter",
            path=self._OUTPUT_FILENAME.format(ticker=ticker.upper()),
        )

        # Add number format
        numberFormat: Final[any] = spreadSheetWriter.book.add_format({"num_format": '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'})
        bold: Final[any] = spreadSheetWriter.book.add_format({'bold': True})

        for i in (dict.keys(self._financialMetricOptions)):
            variable_name = "_" + i.replace(" ", "")
            variable = getattr(self, variable_name)
            try:
                variable.to_excel(
                        index=True,
                        sheet_name="Data",
                        excel_writer=spreadSheetWriter,
                        startrow=row
                    )
                
                spreadSheetWriter.sheets["Data"].write(row, 0, (i + ' Data provided by SECche: ' + ticker.upper()), bold)

                row += (variable.shape[0] +2)

            except:
                (i, " not added")

        # Set the zoom level
        spreadSheetWriter.sheets["Data"].set_zoom(100)

            # Format cells
        
        spreadSheetWriter.sheets["Data"].set_column(f"B:{chr(self._IncomeStatement.shape[1] + 65)}", 12, numberFormat)

            # Format
        spreadSheetWriter.sheets["Data"].autofit()

        spreadSheetWriter.sheets["Data"].write(0, 0, "Balance Sheet" + ' Data provided by SECche: ' + ticker.upper(), bold)
        spreadSheetWriter.close()
        # Close the spreadsheet




# Run
if __name__ == "__main__":

    # Test case
    Secche().query(input("Enter ticker: "),"excel")
