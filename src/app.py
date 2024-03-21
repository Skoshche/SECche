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
        IncomeStatement=IncomeStatement.to_html(classes='data', header="true", float_format=lambda x: '{:,.0f}'.format(x)),
        BalanceSheet=BalanceSheet.to_html(classes='data', header="true", float_format=lambda x: '{:,.0f}'.format(x)),
        CashFlow=CashFlow.to_html(classes='data', header="true", float_format=lambda x: '{:,.0f}'.format(x)),
        )

