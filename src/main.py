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
# Authors: @Skoshche <https:#github.com/Skoshche>                  || Owner
#          @MaxineToTheStars <https:#github.com/MaxineToTheStars>  || Contributor
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
    _VERSION_NUMBER: Final[str] = "beta-v1.0.0"
    _API_QUERY_URL_: Final[str] = "https://data.sec.gov/api/xbrl/companyfacts/CIK{centralIndexKey}.json"
    _OUTPUT_FILENAME: Final[str] = "{ticker}_financial_data.xlsx"
    _API_QUERY_HEADERS: Final[dict] = {"User-Agent": "SECche"}
    _CENTRAL_INDEX_KEY_FULL_PATH: Final[str] = getcwd().replace("/src", "/data/centralIndexKey.csv")
    _FINANCIAL_METRIC_OPTIONS_FULL_PATH: Final[str] = getcwd().replace("/src", "/data/financialMetricOptions.csv")

    # Public Variables

    # Private Variables
    _outputData: Final[dict] = None
    _financialMetricOptions: Final[dict] = None
    _centralIndexKeyDataFrame: Final[DataFrame] = None

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
                optionValue: Final[str] = optionRow[1].strip()

                # Store
                self._financialMetricOptions[optionKey] = optionValue

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
            self._API_QUERY_URL_.format(centralIndexKey=centralIndexKey),
            headers=self._API_QUERY_HEADERS,
        )

        # Get the response JSON
        responseJSON: Final[dict] = loads(apiResponse.text)

        # Parse and store data
        for metricOption in self._financialMetricOptions:
            self._parseAndStoreFinancialData(metricOption, responseJSON)

        # Create a new spreadsheet and dump the data
        self._createAndStoreFromData(ticker)

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

    def _parseAndStoreFinancialData(self, metricOption: str, rawJSONData: dict) -> None:
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

        # Iterate
        for data in optionData:
            # Get the form type
            formType: Final[str] = data["form"]

            # Skip forms that aren't 10-K
            if formType != "10-K":
                # Next iteration
                continue

            # Retrieve the end date and year
            endDate: Final[str] = data["end"]
            endYear: Final[int] = endDate[0:4]

            # TODO: This is very fucked

            # Create a new entry if specified year is not yet a key
            if endYear not in self._outputData.keys():
                self._outputData[endYear] = {}

            if self._financialMetricOptions[metricOption] not in self._outputData[endYear].keys():
                self._outputData[endYear][self._financialMetricOptions[metricOption]] = []

            # Populate
            self._outputData[endYear][self._financialMetricOptions[metricOption]].append(data["val"])

    def _createAndStoreFromData(self, ticker: str) -> None:
        # Create a new data frame
        dataFrame: Final[DataFrame] = DataFrame().from_dict(
            orient="index",
            data=self._outputData,
            columns=self._outputData.keys(),
        )

        # Instance the data
        dataFrame.transpose()

        # Re-index the data frame
        dataFrame = dataFrame.reindex(sorted(dataFrame.columns, reverse=True))

        # Create a new spreadsheet writer
        spreadSheetWriter = ExcelWriter(
            self._OUTPUT_FILENAME.format(ticker=ticker),
            engine="xlsxwriter",
        )

        # Convert the data frame to an excel sheet
        dataFrame.to_excel(
            spreadSheetWriter,
            index=True,
            sheet_name="generated-report",
        )

        # Set the zoom level
        spreadSheetWriter.sheets["generated-report"].set_zoom(100)

        # Add number format
        numberFormat: Final[any] = spreadSheetWriter.book.add_format({"num_format": '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'})

        # Format cells
        spreadSheetWriter.sheets["generated-report"].set_column(f"B:{chr(len(self._outputData) + 65)}", 12, numberFormat)

        # Format
        spreadSheetWriter.sheets["generated-report"].autofit()

        # Close the spreadsheet
        spreadSheetWriter.close()


# Run
if __name__ == "__main__":
    Secche().query("aapl")
