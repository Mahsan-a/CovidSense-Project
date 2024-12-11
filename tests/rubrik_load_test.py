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

import json

if __name__ == '__main__':
    # Loading folder
    rubriks_folder = '../CE-EmaResponseValidator/data/json'

    filenames = glob.glob('%s/*.json'%rubriks_folder)

    rubriks = dict()

    for filename in tqdm(filenames):
        name = os.path.split(filename)[-1].replace('.json', '')

        with open(filename, 'rb') as f:
            rubriks[name] = json.load(f)

