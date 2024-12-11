#!/usr/bin/env python3

from __future__ import print_function, division
import datetime
import requests
import tqdm
import json

import numpy as np
import matplotlib.pyplot as plt

import xlrd

if __name__ == '__main__':
    # Constants
    url_root = 'https://dshs.texas.gov/coronavirus'
    filename = 'TexasCOVID19CaseCountData.xlsx'
    savename = 'data/Texas_cases.json'

    date_idx = 2
    total_idx = 257

    cleanup = lambda x : x.replace('\r', '').replace('Cases', '').replace('\n', '').replace('*', '').strip()
    s2d = lambda x : datetime.datetime.strptime(x + '-20', '%m-%d-%y').timestamp()

    # Download the data
    print('Downloading data')
    req = requests.get('%s/%s'%(url_root, filename), allow_redirects=True)
    open('data/%s'%filename, 'wb').write(req.content)

    # Extract fatalities info
    print('Extracting information')
    wb = xlrd.open_workbook('data/%s'%filename)
    sheet = wb.sheet_by_index(1)

    # We need to dynamically build the data
    dates = []
    cases = []
    deaths = []

    for idx in tqdm.tqdm(range(3, sheet.nrows)):
        date = xlrd.xldate_as_datetime(sheet.cell(idx, 1).value, wb.datemode)
        try:
            case = int(sheet.cell(idx, 4).value)
            death = int(sheet.cell(idx, 5).value)

            dates.append(date.timestamp())
            cases.append(case)
            deaths.append(death)
        except ValueError:
            break

    assert len(dates) == len(cases)
    assert len(dates) == len(deaths)

    print('Saving data')
    data_dict = {'timestamps': dates,
                 'cases': cases,
                 'deaths': deaths}

    with open(savename, 'w') as fname:
        json.dump(data_dict, fname)
