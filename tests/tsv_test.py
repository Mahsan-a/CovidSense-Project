#!/usr/bin/env python

'''
Description of files goes here.
'''

# System imports
import os
import sys
import time
from tqdm import tqdm
import glob

# Scientific computing
import numpy as np
import scipy.linalg as lin
from scipy import io

# Plotting
import matplotlib.pyplot as plt

import csv
import pandas as pd

if __name__ == '__main__':
    filename = '../data/ema-responses/A_6.tsv'

    tsv_data = open(filename, 'r')
    data = csv.DictReader(tsv_data, delimiter='\t')

    data_dict = dict()

    for row in data:
        for key, val in row.items():
            try:
                data_dict[key].append(val)
            except KeyError:
                data_dict[key] = []
                data_dict[key].append(val)

    data_pd = pd.DataFrame.from_dict(data_dict)

