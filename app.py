from flask import Flask, request, render_template, session, redirect
from typing import Final
from markupsafe import escape
import numpy as np
import pandas as pd
from main import Secche, CIKNotFoundException

app = Flask(__name__)

@app.route('/')
def display_dataframebasic():
    return render_template('homepage.html')

@app.route('/<ticker>', methods=['GET', 'POST'])
def display_dataframe(ticker):
    # Pass DataFrame to the HTML template
    returned = Secche().query(ticker, "dataframe") 
    try:
        IncomeStatement, BalanceSheet, CashFlow, Ratios = returned
    except:
        return render_template('error.html', errorMessage = str(returned))
    return render_template(
        'index.html',ticker=ticker.upper(), 
        IncomeStatement=IncomeStatement.to_html(classes='data', header="true", float_format=lambda x: '{:,.0f}'.format(x)),
        BalanceSheet=BalanceSheet.to_html(classes='data', header="true", float_format=lambda x: '{:,.0f}'.format(x))
        )

