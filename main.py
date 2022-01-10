import csv
from io import StringIO

import requests
from flask import Flask, jsonify
from flask import Response

import config

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return "Hello to Crypto API ! <br> Try these endpoints : /csv , /currency/currency_name"


@app.route("/csv", methods=['GET'])
def generate_csv():
    currency_data = get_price_data()
    return csv_response(currency_data)


@app.route("/currency/<currencyType>/", methods=['GET'])
def get_price(currencyType):
    if not currencyType or currencyType.upper() not in config.CURRENCIES:
        return "Not a valid Currency !"

    # Uppercase
    currencyType = currencyType.upper()
    currency_data = get_price_data()
    return jsonify({'price': currency_data[currencyType]})


def get_price_data():
    data = requests.get(config.BITCOIN_PRICE_URL).json()
    return parse_currency(data)


def parse_currency(jsonData):
    currency_data = {};
    for currency in config.CURRENCIES:
        currency_data[currency] = float(jsonData['bpi'][currency]['rate'].replace(',', ''))
    return currency_data;


def iter_csv(data):
    line = StringIO()
    writer = csv.writer(line)

    # Write headers
    writer.writerow(config.CSV_HEADERS)
    yield line.read()

    for itr in data:
        writer.writerow([itr, str(data[itr])])
        line.seek(0)
        yield line.read()
        line.truncate(0)
        line.seek(0)


def csv_response(data):
    response = Response(iter_csv(data), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8080)
