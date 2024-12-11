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

def tsv2dict(filename):
    '''
        Load a tsv file and convert to dictionary
    '''
    tsv_data = open(filename, 'r')
    data_reader = csv.DictReader(tsv_data, delimiter='\t')

    data_dict = dict()

    for row in data_reader:
        for key, val in row.items():
            try:
                data_dict[key].append(val)
            except KeyError:
                data_dict[key] = []
                data_dict[key].append(val)

    return data_dict

if __name__ == '__main__':
    panel_name = 'S_4_1'
    time_format = '%Y-%m-%dT%H:%M:%SZ'

    # We need to create prototype list and compare all other files against these
    # prototypes
    prototypes = {'A_6': ['A_1', 'A_2', 'A_3', 'A_4', 'A_5', 'A_7'],
                  'B_1': [],
                  'C_1': [],
                  'D_1': [],
                  'E_1': [],
                  'G_4': ['G_2'],
                  'H_3': ['H_1', 'H_2'],
                  'I_5': ['I_1', 'I_2', 'I_3'],
                  'K_3': ['K_1', 'K_2'],
                  'M_3': ['M_1', 'M_2'],
                  'N_3': ['N_1', 'N_2'],
                  'P_1': [],
                  'Q_5': [],
                  'R_3': [],
                  'V_1': [],
                  'X_3': ['X_2'],
                  'S_7_8': ['S_1_2', 'S_1_3', 'S_1_4',
                            'S_2_1', 'S_2_3', 'S_2_4', 'S_2_5', 'S_2_6', 'S_2_7',
                            'S_3_1', 'S_3_2', 'S_3_3', 'S_3_4', 'S_3_5', 'S_3_6',
                            'S_4_1', 'S_4_2', 'S_4_3', 'S_4_4', 'S_4_5',
                            'S_6_1', 'S_6_2', 'S_6_3', 'S_6_4', 'S_6_5', 'S_6_6',
                            'S_6_7', 'S_6_8',
                            'S_7_1', 'S_7_2', 'S_7_3', 'S_7_4', 'S_7_5', 'S_7_6',
                            'S_7_7']}

    panels_folder = '../data/ema-rubriks';

    for prototype, panels_list in prototypes.items():
        print('Parsing %s'%prototype)

        # Load rubrik
        with open('../data/ema-rubriks/%s.json'%prototype, 'rb') as f:
            prototype_rubrik = json.load(f)
            prototype_questions = list(prototype_rubrik.keys())

        # Now load other files
        for panel in panels_list:
            print('\tParsing %s'%panel)
            with open('../data/ema-rubriks/%s.json'%panel, 'rb') as f:
                panel_rubrik = json.load(f)

            # Find common questions, make sure the options match, and store
            # any extra questions in a separate list
            panel_questions = list(panel_rubrik.keys())

            # We need to rely on fuzzy processing
            for question in panel_questions:
                qr = process.extractOne(question, prototype_questions)

                if qr[1] < 90:
                    #print('\t\tP: %s'%question)
                    #print('\t\tR: %s'%qr[0])
                    #print('\t\t\tQuestion not in prototype? (Score: %d)'%qr[1])
                    panel_rubrik[question]['err_mesg'] = 'Question not in prototype'
                else:
                    prototype_options = prototype_rubrik[qr[0]]['answers']
                    panel_options = panel_rubrik[question]['answers']
                    
                    if panel_options == '':
                        del panel_rubrik[question]
                        continue

                    if all([v == 0 for v in list(panel_options.values())]) and\
                       not all([v == 0 for v in list(prototype_options.values())]):
                        print('\t\t%s'%question)
                        print('\t\t\tUngraded question?')
                        panel_rubrik[question]['err_msg'] = 'Ungraded question'
                    else:
                        del panel_rubrik[question]

            # Dump this file
            with open('diff_dump/%s.json'%panel, 'w') as f:
                json.dump(panel_rubrik, f, indent=4)
