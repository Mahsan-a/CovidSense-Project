#!/usr/bin/env python

import os
import sys
import time
import collections
import json
import datetime

import numpy as np

import json
import csv
import pandas as pd
from fuzzywuzzy import fuzz, process

import matplotlib.pyplot as plt
import seaborn as sns

import psychometry

def pretty_print(infodict):
    '''
        Print a dictionary in a pretty manner
    '''
    for key in infodict:
        print('%s : %s'%(key, infodict[key]))
        
def cat_arrays(db_dict, key):
    '''
        Concatenate arrays for a given keyword in dictionary
        
        db_dict: dictionary with each entry having 'key' with at least
            length 0
        key: Keyword for which arrays need to be concatenated
    '''
    
    array = []
    
    for entry in db_dict:
        array += db_dict[entry][key]
        
    return array

def getall(db_dict, key):
    '''
        Get values for a given key in all entries of the dictionary
        
        db_dict: Dictionary with each entry having 'key'. If not found,
            'not supplied' is added as the entry
        key: Keyword for which values need to be concatenated
        
    '''
    array = []
    
    for entry in db_dict:
        try:
            val = db_dict[entry][key]
        except KeyError:
            val = 'not supplied'
        array.append(val)
        
    return array

def getqids(db_dict):
    '''
        Get QIDS time array and values
        
        Inputs:
            db_dict: Dictionary
        Outputs:
            time_array: Array with time stamps
            qids_array: Array with QIDS values
    '''
    time_array = []
    qids_array = []
    
    for key in db_dict:
        qids_entries = db_dict[key]['QIDS']
        qids_val = list(qids_entries.values())[0]
        qids_time = list(qids_entries.keys())[0]
        
        time_array.append(float(qids_time))
        qids_array.append(float(qids_val))
        #for qkey, qval in qids_entries.items():
        #    time_array.append(float(qkey))
        #    qids_array.append(qval)
            
    return np.array(time_array), np.array(qids_array)

def Counter(array, normalize=True):
    '''
        Similar to Python's inbuilt counter, but with option to normalize numbers w.r.t sum
    '''
    
    cntr = collections.Counter(array)
    maxval = sum(list(cntr.values()))
    
    for key in cntr:
        cntr[key] = cntr[key]*1.0/maxval
        
    return cntr

def loadtsv(filename):
    '''
        Load a tab separated value file and convert to dictionary

        Inputs:
            filename: tsv filename

        Outputs:
            data_dict: Dictionary with data
    '''
    tsv_data = open(filename, 'r', encoding='utf-8')
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

def convert2numeric(data_dict, rubrik, non_numeric_vars=None, convert_pd=False):
    '''
        Convert data loaded from TSV file to numbers and variables.

        Inputs:
            data_dict: tsv data dictionary
            rubrik: Rubrik used for converting data to numbers (if needed)
            non_numeric_vars: Do not convert these variables into numeric value
            convert_pd: If True, convert to Pandas dataframe
    '''
    time_format = '%Y-%m-%dT%H:%M:%SZ'
    numeric_dict = dict()

    for key in data_dict:
        rubrik_dict = rubrik[key]

        entry_type = rubrik_dict['type']
        answers = rubrik_dict['answers']
        varname = rubrik_dict['varname']

        if varname == 'ignore':
            continue

        numeric_dict[varname] = []

        if len(answers) > 0:
            answers_list = list(answers.keys())

        for entry in data_dict[key]:
            if entry_type == 'ID':
                numeric_dict[varname].append(int(entry))

            elif entry_type == 'timestamp':
                timestamp = datetime.datetime.strptime(entry, time_format)
                numeric_dict[varname].append(timestamp.timestamp())

            elif entry_type == 'MultipleChoice':
                if varname in non_numeric_vars:
                    val = entry
                else:
                    try:
                        val = answers[entry]
                    except KeyError:
                        qr = process.extractOne(entry, answers_list)
                        val = answers[qr[0]]

                numeric_dict[varname].append(val)
            elif entry_type == 'Checkbox':
                numeric_dict[varname].append(entry.split(';'))

            elif entry_type == 'IntegerChoice':
                numeric_dict[varname].append(int(entry))

            elif entry_type == 'TextLines':
                numeric_dict[varname].append(entry)

            else:
                raise KeyError('Data type not understood')

    if convert_pd:
        numeric_dict = pd.DataFrame.from_dict(numeric_dict)

    return numeric_dict

def process_burnout(data_dict):
    '''
        Create burnout scores from K-panel regression
        
        Inputs:
            data_dict: K-panel responses
        
        Outputs:
            burnout_risk: Risk factor for burnout
            burnout_protective: Protective factor for burnout
    '''
    away_dict = {'feel like my normal self': 1,
                'am more stressed than usual': -1,
                'feel isolated': -1,
                'feel I have family support': 1,
                'feel I have social support': 1,
                'am worried about my work-related exposure to Corona/COVID-19': -1,
                'am still taking extra precautions around others': -1,
                '(empty)': 0}
    burnout_risk = 0
    burnout_protective = 0
    for var in data_dict:
        if 'timestamp' in var or 'ID' in var or 'note' in var:
            continue
        elif 'away_from_work' in var:
            entries = data_dict[var]
            for entry in entries:
                if away_dict[entry] > 0:
                    burnout_protective += 1
                elif away_dict[entry] < 0:
                    burnout_risk += 1
        else:
            val = data_dict[var]
            try:
                if val < 0:
                    burnout_risk += 1
                else:
                    burnout_protective += 1
            except TypeError as err:
                print(err)
                print(val)
    
    return burnout_risk, burnout_protective

def process_psychometry(data_dict, varname):
    '''
        Function to convert individual scores for psychometric tests to a
        processed result.

        Inputs:
            data_dict: Dictionary or Pandas dataframe with data from S or A
                panels
            varname: 'qids', 'camsr', or 'ipip'
    '''
    qname_dict = {'qids': 14,
                  'camsr': 10,
                  'ipip': 20}
    qname_func = {'qids': psychometry.QIDS,
                  'camsr': psychometry.CAMS_R,
                  'ipip': psychometry.IPIP}

    fields = ['%s%d'%(varname, idx) for idx in range(1, qname_dict[varname]+1)]

    data_dict[varname] = []

    scores_list = [data_dict[field] for field in fields]

    for idx in range(len(data_dict['ID'])):
        scores = [scores_list[k][idx] for k in range(qname_dict[varname])]

        data_dict[varname].append(qname_func[varname](scores))

    # Delete the other fields
    for field in fields:
        del data_dict[field]

    return data_dict

def plot_timeseries(data_pd, varname, winsize=5, fig=None, ax=None, palette='deep',
                    linestyle='-', label=None):
    '''
        Plot timeseries by aggregating data and doing a time-average
        
        Inputs:
            data_pd: Pandas dataframe with three main variables:
                varname: Name of variable of interest
                timestamps: Timestamps where varname were recorded
                nresponses: Number of respones for each entry of varname
                winsize: Size of window for averaging
                fig, ax: Optional figure handles
                palette: Seaborn color palette
                linestyle: linestyle for the line. Default is '-'
                label: Legend name (optional)
                
        Outputs:
            fig, ax: Figure and axes handle
    '''
    d2s = lambda x : datetime.datetime.fromtimestamp(x/1000.0).strftime('%m %d')
    d2s2 = lambda x : datetime.datetime.fromtimestamp(x/1000.0).strftime('%B %d')
    
    colors = sns.color_palette(palette, 3)
    
    data_pd_dict = pd.DataFrame.to_dict(data_pd[[varname, 'timestamp', 'nresponses']])
    
    timestamp_array = np.array(list(data_pd_dict['timestamp'].values()))
    timestamps = np.unique(timestamp_array)
    
    data_pd_agg = data_pd[[varname, 'timestamp', 'nresponses']].groupby(by='timestamp').agg({varname: 'median', 'nresponses': 'sum'})
    data_pd_std = data_pd[[varname, 'timestamp', 'nresponses']].groupby(by='timestamp').agg({varname: 'std'})
    
    qids_array = np.array(list(pd.DataFrame.to_dict(data_pd_agg)[varname].values()))
    qids_std_array = np.array(list(pd.DataFrame.to_dict(data_pd_std)[varname].values()))
    nresponses_array = np.array(list(pd.DataFrame.to_dict(data_pd_agg)['nresponses'].values()))

    if fig is None:
        fig, ax = plt.subplots(dpi=150, figsize=[12, 4])
        
    qids_vals = np.array(list(data_pd_dict[varname].values())) + np.random.randn(len(timestamp_array))/10
    
    #ax.scatter(timestamp_array, qids_vals, marker='o', 
    #            edgecolors=colors[1], facecolors=colors[1], alpha=0.2, s=20)
    
    if label:
        ax.plot(timestamps, qids_array, linestyle=linestyle, color=colors[2], label=label)
    else:
        ax.plot(timestamps, qids_array, linestyle=linestyle, color=colors[2])

    ax.fill_between(timestamps, qids_array - qids_std_array, qids_array + qids_std_array, alpha=0.2, color=colors[1])
    _ = plt.xticks(timestamps, labels=[d2s2(x*1000) for x in timestamps], rotation='vertical', fontsize=10)
    _ = plt.yticks(fontsize=10)

    return fig, ax, timestamps[0]
    