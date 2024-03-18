# Import Statements
# First party
from os import getcwd
from csv import reader
from json import loads
from typing import Final

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
    def __init__(self, message: str, *args: object) -> None:
        """
        Constructs a new ``CIKNotFoundException`` instance.

        @return ``CIKNotFoundException`` - ``CIKNotFoundException`` instance
        """
        # Instance the base Exception
        super().__init__(*args)

        # Set the exception message
        self._exceptionMessage = message

    # Public Static Methods

    # Public Inherited Methods
    def getMessage(self) -> str:
        """
        Returns the exception message.

        @return ``str`` - The exception message
        """
        return self._exceptionMessage

    # Private Static Methods

    # Private Inherited Methods


class Secche:
    # Enums

    # Interfaces

    # Constants
    _API_QUERY_URL: Final[str] = "https://data.sec.gov/api/xbrl/companyfacts/CIK{centralIndexKey}.json"
    _VERSION_NUMBER: Final[str] = "beta-v1.0.0"
    _OUTPUT_FILENAME: Final[str] = "{ticker}_financial_data.xlsx"
    _API_QUERY_HEADERS: Final[dict] = {"User-Agent": "SECche"}
    _CENTRAL_INDEX_KEY_FULL_PATH: Final[str] = getcwd().replace("/src", "/data/centralIndexKey.csv")
    _FINANCIAL_METRIC_OPTIONS_FULL_PATH: Final[str] = getcwd().replace("/src", "/data/financialMetricOptions.csv")

    # Public Variables

    # Private Variables
    _outputData: Final[dict] = None
    _financialMetricOptions: Final[dict] = None
    _centralIndexKeyDataFrame: Final[DataFrame] = None
    
    _dataFrame1 = 0
    _dataFrame2 = 0

    # Constructor
    def __init__(self) -> None:
        """
        Constructs a new ``Secche`` instance.

        @return ``Secche`` - ``Secche`` instance
        """

        # Read the CSV and store the data
        self._centralIndexKeyDataFrame = read_csv(
            self._CENTRAL_INDEX_KEY_FULL_PATH,
            index_col=0,
        )

        # Instance a new dictionary object
        self._outputData = {}
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

    # Public Static Methods

    # Public Inherited Methods
    def query(self, ticker: str) -> None:
        """
        Queries a given ticker for data and outputs it as a spreadsheet.

        @param ticker - The specified ticker
        @return None
        """

        # Get the specified CIK
        centralIndexKey: Final[str] = self._getCIK(ticker)

        # Check if the CIK is valid
        if centralIndexKey == None:
            raise CIKNotFoundException(f"Central Index Key({ticker}) was not found!")

        # Send the request
        apiResponse: Final[Response] = get(
            self._API_QUERY_URL.format(centralIndexKey=centralIndexKey),
            headers=self._API_QUERY_HEADERS,
        )
        print("The URL used:", self._API_QUERY_URL.format(centralIndexKey=centralIndexKey))
        # Get the response JSON
        responseJSON: Final[dict] = loads(apiResponse.text)

        # Parse and store data
        #WORKING
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
            self._createAndStoreFromData(ticker, book, final)
    # Private Static Methods

    # Private Inherited Methods
    def _padCIK(self, centralIndexKey: str) -> str:
        """
        Returns a padded CIK that matches the 10 digit standard.

        @param centralIndexKey - The supplied CIK
        @return paddedCentralIndexKey - A padded CIK
        """

        # Welcome to funky town
        return ((10 - len(centralIndexKey)) * "0") + centralIndexKey

    def _getCIK(self, ticker: str) -> str:
        """
        Retrieves a CIK from the given ticker.

        @param ticker - The supplied ticker
        @return centralIndexKey - A padded CIK
        """

        # Try to return the CIK from the given ticker
        try:
            # Retrieve the CIK from the data frame, pad it, and return it
            return self._padCIK(str(self._centralIndexKeyDataFrame.loc[ticker.lower(), "CIK"]))
        except Exception as ex:
            # CIK was not found for the ticker, return None
            return None

    def _parseAndStoreFinancialData(self, metricOption: str, rawJSONData: dict, book) -> None:
        """
        Parses the return JSON data and stores the specified financial metric option.

        @param metricOption - The metric option to look for
        @param rawJSONData - The return JSON from the API
        @return None
        """
        # Declare option data array
        optionData: Final[list] = None

        # Try to fetch the specified option
        try:
            # Set option data
            optionData = rawJSONData["facts"]["us-gaap"][metricOption]["units"]["USD"]
        except Exception:
            # Option not found, return
            return

        # Check if no entries are available
        if len(optionData) == 0:
            # No entries, return
            return
        #12:56 AM getting stuck here i want to kill myself holy shit
        
        # Iterate
        for data in optionData:
            # Get the form type
            formType: Final[str] = data["form"]
            try:
                startDate: Final[str] = data["start"]
                startMonth: Final[int] = startDate[5:7]
            except:
                startMonth: Final[int] = 9

            # Retrieve the end date and year
            endDate: Final[str] = data["end"]
            endYear: Final[int] = endDate[0:4]
            endMonth: Final[int] = endDate[5:7]

            # Skip forms that aren't 10-K
            if (formType != "10-K") or ((int(endMonth) - int(startMonth)) > 1):
                # Next iteration
                continue

            if book not in self._outputData.keys():
                self._outputData[book] = {}
    
            # Create a new entry if specified year is not yet a key
            if endYear not in self._outputData[book].keys():
                self._outputData[book][endYear] = {}

            # Populate the grid
            self._outputData[book][endYear][self._financialMetricOptions[book][metricOption]] = data["val"]

    def _createAndStoreFromData(self, ticker: str, book, final) -> None:
        # Create a new data frame
        dataFrame = (book.replace(" ", "") + "_dataframe")
        #print(dataFrame)
        #print(dataFrame)
        #print(book, "\n", self._outputData[book], "\n")

        dataFrame: Final[DataFrame] = DataFrame().from_dict(
            orient="index",
            data=self._outputData[book],
        )
        #print(self._outputData.keys())

        # Flip the row and columns
        dataFrame = dataFrame.transpose()

        # Re-index the data frame
        dataFrame = dataFrame.reindex(columns=sorted(dataFrame.columns, reverse=True))

        output = (self._OUTPUT_FILENAME, book)
        # Create a new spreadsheet writer
        spreadSheetWriter = ExcelWriter(
            engine="xlsxwriter",
            path=self._OUTPUT_FILENAME.format(ticker=ticker.upper()),
        )

        if book == "Balance Sheet":
            self._dataFrame1 = dataFrame
            print("doing the first")

        elif book == "Income Statement":
            self._dataFrame2 = dataFrame
            print("Doing the else")


        # Convert the data frame to an excel sheet

        if final == True:
            self._dataFrame1.to_excel(
                index=True,
                sheet_name="Data",
                excel_writer=spreadSheetWriter,
                startrow=self._dataFrame1.shape[0] + 5
            )
            self._dataFrame2.to_excel(
                index=True,
                sheet_name="Data",
                excel_writer=spreadSheetWriter,
            )

            # Set the zoom level
            spreadSheetWriter.sheets["Data"].set_zoom(100)

            # Add number format
            numberFormat: Final[any] = spreadSheetWriter.book.add_format({"num_format": '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'})
            bold: Final[any] = spreadSheetWriter.book.add_format({'bold': True})
            # Format cells
            spreadSheetWriter.sheets["Data"].set_column(f"B:{chr(self._dataFrame2.shape[1] + 65)}", 12, numberFormat)

            # Format
            spreadSheetWriter.sheets["Data"].autofit()

            spreadSheetWriter.sheets["Data"].write(0, 0, "Income Statement" + ' Data provided by SECche: ' + ticker.upper(), bold)
            spreadSheetWriter.sheets["Data"].write(self._dataFrame1.shape[0] + 5, 0, "Balance Sheet" + ' Data provided by SECche: ' + ticker.upper(), bold)
            print("Closed")
            spreadSheetWriter.close()
        # Close the spreadsheet
    


# Run
if __name__ == "__main__":
    # Test case
    Secche().query(input("Enter ticker: "))
