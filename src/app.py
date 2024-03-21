from flask import Flask, request, render_template, session, redirect
from typing import Final
from markupsafe import escape
import numpy as np
import pandas as pd
from main import Secche, CIKNotFoundException
from logging import FileHandler,WARNING

app = Flask(__name__)
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

import pandas as pd

# Define custom formatting function
def custom_format(x):
    if x < 0:
        return '({:,.0f})'.format(abs(x))
    else:
        return '{:,.0f}'.format(x)

# Example DataFrame
data = {'A': [-1000, 2000, -3000, 4000]}
df = pd.DataFrame(data)

# Convert DataFrame to HTML with custom formatting
html_table = df.to_html(float_format=custom_format, classes='content-table', header=True)

print(html_table)


@app.route('/')
def display_dataframebasic():
    return render_template('homepage.html')

@app.route('/<ticker>', methods=['GET', 'POST'])
def display_dataframe(ticker):
    # Pass DataFrame to the HTML template
    returned = Secche().query(ticker, "dataframe") 
    try:
        IncomeStatement, BalanceSheet, CashFlow, Ratios, URL, CompanyName, Edgar = returned
    except:
        return render_template('error.html', errorMessage = str(returned))
    return render_template(
        'index.html',ticker=ticker.upper(), URL=URL, CompanyName=CompanyName, Edgar=Edgar,
        IncomeStatement=IncomeStatement.to_html(classes='content-table', header="true", float_format=custom_format,border="0"),
        BalanceSheet=BalanceSheet.to_html(classes='content-table', header="true", float_format=custom_format,border="0"),
        CashFlow=CashFlow.to_html(classes='content-table', header="true", float_format=custom_format,border="0"),
        )

