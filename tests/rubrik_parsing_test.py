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
import pprint
import datetime
import importlib

# Scientific computing
import numpy as np
import scipy.linalg as lin
from scipy import io

# Plotting
import matplotlib.pyplot as plt

import json
import csv
import pandas as pd
from fuzzywuzzy import fuzz, process

sys.path.append('../')
import utils
utils = importlib.reload(utils)

if __name__ == '__main__':
    time_format = '%Y-%m-%dT%H:%M:%SZ'

    panels_folder = '../data/ema-rubriks';
    panel_names = glob.glob('%s/*.json'%panels_folder)

    panel_names = ['../data/ema-rubriks/K_3.json']

    non_numeric_vars = ['gender', 'healthcare_risk_exposure',
                        'healthcare_job_change', 'healthcare_redeployed',
                        'healthcare_workload', 'healthcare_worker', 
                        'healthcare_speciality',
                        'healthcare_extra_compensation']
    qids_vars = ['qids%d'%idx for idx in range(1, 15)]
    ipip_vars = ['ipip%d'%idx for idx in range(1, 21)]
    camsr_vars = ['camsr%d'%idx for idx in range(1, 11)]

    for panel_name_full in panel_names:
        print('Parsing %s'%panel_name_full)
        
        panel_name = os.path.split(panel_name_full)[1].replace('.json', '')

        # Load rubrik
        with open('../data/ema-rubriks/%s.json'%panel_name, 'rb') as f:
            rubrik = json.load(f)

        # Load tsv file
        data_raw = utils.loadtsv('../data/ema-responses/%s.tsv'%panel_name)

        data_dict = utils.convert2numeric(data_raw, rubrik,
                                          non_numeric_vars)

        varnames = [rubrik[var]['varname'] for var in rubrik]

        # Process psychometry questions
        if 'qids1' in data_dict:
            data_dict = utils.process_psychometry(data_dict, 'qids')

        if 'camsr1' in data_dict:
            data_dict = utils.process_psychometry(data_dict, 'camsr')

        if 'ipip1' in data_dict:
            data_dict = utils.process_psychometry(data_dict, 'ipip')


