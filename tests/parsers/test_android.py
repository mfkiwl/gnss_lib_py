"""Tests for Android raw data loaders.

"""

__authors__ = "Derek Knowles"
__date__ = "30 Oct 2023"

import os
import csv
import pathlib

import pytest
import numpy as np
import pandas as pd

from gnss_lib_py.parsers import android
from gnss_lib_py.parsers.google_decimeter import AndroidDerived2023
from gnss_lib_py.parsers.navdata import NavData

# pylint: disable=protected-access

@pytest.fixture(name="root_path")
def fixture_root_path():
    """Location of measurements for unit test

    Returns
    -------
    root_path : string
        Folder location containing measurements
    """
    root_path = os.path.dirname(
                os.path.dirname(
                os.path.dirname(
                os.path.realpath(__file__))))
    root_path = os.path.join(root_path, 'data/unit_test')
    return root_path

@pytest.fixture(name="android_raw_path")
def fixture_raw_path(root_path):
    """Filepath of Android Raw measurements

    Parameters
    ----------
    root_path : string
        Path of testing dataset root path

    Returns
    -------
    raw_path : string
        Location for text log file with Android Raw measurements

    Notes
    -----
    Test data is a subset of the Android Raw Measurement Dataset [2]_,
    particularly the train/2020-05-14-US-MTV-1/Pixel4 trace. The dataset
    was retrieved from
    https://www.kaggle.com/c/google-smartphone-decimeter-challenge/data

    References
    ----------
    .. [2] Fu, Guoyu Michael, Mohammed Khider, and Frank van Diggelen.
        "Android Raw GNSS Measurement Datasets for Precise Positioning."
        Proceedings of the 33rd International Technical Meeting of the
        Satellite Division of The Institute of Navigation (ION GNSS+
        2020). 2020.
    """
    raw_path = os.path.join(root_path, 'google_decimeter_2021',
                            'Pixel4_GnssLog.txt')
    return raw_path

@pytest.fixture(name="android_raw_2023_path")
def fixture_raw_2023_path(root_path):
    """Filepath of Android Raw measurements

    Parameters
    ----------
    root_path : string
        Path of testing dataset root path

    Returns
    -------
    raw_path : string
        Location for text log file with Android Raw measurements

    Notes
    -----
    Test data is a subset of the 2023 Google Challenge [3]_.

    References
    ----------
    .. [3] https://www.kaggle.com/competitions/smartphone-decimeter-2023/overview

    """
    raw_path = os.path.join(root_path, 'google_decimeter_2023',
                            '2023-09-07-18-59-us-ca',
                            'pixel7pro',
                            'gnss_log.txt')
    return raw_path

@pytest.fixture(name="android_derived_2023_path")
def fixture_derived_2023_path(root_path):
    """Filepath of Android derived measurements

    Parameters
    ----------
    root_path : string
        Path of testing dataset root path

    Returns
    -------
    raw_path : string
        Location for text log file with Android Raw measurements

    Notes
    -----
    Test data is a subset of the 2023 Google Challenge [4]_.

    References
    ----------
    .. [4] https://www.kaggle.com/competitions/smartphone-decimeter-2023/overview

    """
    raw_path = os.path.join(root_path, 'google_decimeter_2023',
                            '2023-09-07-18-59-us-ca',
                            'pixel7pro',
                            'device_gnss.csv')
    return raw_path

def test_imu_raw(android_raw_path):
    """Test that AndroidRawImu initialization

    Parameters
    ----------
    android_raw_path : pytest.fixture
        Path to Android Raw measurements text log file
    """
    test_imu = android.AndroidRawImu(android_raw_path)
    isinstance(test_imu, NavData)

    test_imu = android.AndroidRawImu(pathlib.Path(android_raw_path))
    isinstance(test_imu, NavData)

    # raises exception if not a file path
    with pytest.raises(FileNotFoundError):
        android.AndroidRawImu("not_a_file.txt")
    with pytest.raises(FileNotFoundError):
        android.AndroidRawImu(pathlib.Path("not_a_file.txt"))

    # raises exception if input not string or path-like
    with pytest.raises(TypeError):
        android.AndroidRawImu([])

def test_fix_raw(android_raw_path):
    """Test that AndroidRawFixes initialization

    Parameters
    ----------
    android_raw_path : pytest.fixture
        Path to Android Raw measurements text log file
    """
    test_fix = android.AndroidRawFixes(android_raw_path)
    isinstance(test_fix, NavData)

    test_fix = android.AndroidRawFixes(pathlib.Path(android_raw_path))
    isinstance(test_fix, NavData)

    # raises exception if not a file path
    with pytest.raises(FileNotFoundError):
        android.AndroidRawFixes("not_a_file.txt")
    with pytest.raises(FileNotFoundError):
        android.AndroidRawFixes(pathlib.Path("not_a_file.txt"))

    # raises exception if input not string or path-like
    with pytest.raises(TypeError):
        android.AndroidRawFixes([])

def make_csv(input_path, output_directory, field, show_path=False):
    """Write specific data types from a GNSS android log to a CSV.

    Parameters
    ----------
    input_path : string or path-like
        File location of data file to read.
    output_directory : string
        Directory where new csv file should be created
    fields : list of strings
        Type of data to extract. Valid options are either "Raw",
        "Accel", "Gyro", "Mag", or "Fix".

    Returns
    -------
    output_path : string
        New file location of the exported CSV.

    Notes
    -----
    Based off of MATLAB code from Google's gps-measurement-tools
    repository: https://github.com/google/gps-measurement-tools. Compare
    with MakeCsv() in opensource/ReadGnssLogger.m

    """
    if not os.path.isdir(output_directory): #pragma: no cover
        os.makedirs(output_directory)
    output_path = os.path.join(output_directory, field + ".csv")
    with open(output_path, 'w', encoding="utf8") as out_csv:
        writer = csv.writer(out_csv)

        if not isinstance(input_path, (str, os.PathLike)):
            raise TypeError("input_path must be string or path-like")
        if not os.path.exists(input_path):
            raise FileNotFoundError(input_path,"file not found")

        with open(input_path, 'r', encoding="utf8") as in_txt:
            for line in in_txt:
                # Comments in the log file
                if line[0] == '#':
                    # Remove initial '#', spaces, trailing newline
                    # and split using commas as delimiter
                    line_data = line[2:].rstrip('\n').replace(" ","").split(",")
                    if line_data[0] == field:
                        writer.writerow(line_data[1:])
                # Data in file
                else:
                    # Remove spaces, trailing newline and split using commas as delimiter
                    line_data = line.rstrip('\n').replace(" ","").split(",")
                    if line_data[0] == field:
                        writer.writerow(line_data[1:])
    if show_path: #pragma: no cover
        print(output_path)

    return output_path

@pytest.mark.parametrize('file_type',
                        ['Accel',
                        'Gyro',
                        'Fix'])
def test_csv_equivalence(android_raw_path, root_path, file_type):
    """Test equivalence of loaded measurements and data from split csv

    Parameters
    ----------
    android_raw_path : pytest.fixture
        Path to Android Raw measurements text log file

    root_path : pytest.fixture
        Path to location of all data for Android unit testing

    file_type : string
        Type of measurement to be extracted into csv files

    """
    #NOTE: Times for gyroscope measurements are overridden by accel times
    # and are not checked in this test for any measurement
    no_check = ['utcTimeMillis', 'elapsedRealtimeNanos']
    if file_type in ('Accel','Gyro'):
        test_measure = android.AndroidRawImu(android_raw_path)
    elif file_type=='Fix':
        test_measure = android.AndroidRawFixes(android_raw_path)
    output_directory = os.path.join(root_path, 'csv_test')
    csv_loc = make_csv(android_raw_path, output_directory,
                               file_type)
    test_df = pd.read_csv(csv_loc)
    test_measure = android.AndroidRawImu(android_raw_path)
    row_map = test_measure._row_map()
    for col_name in test_df.columns:
        if col_name in row_map:
            row_idx = row_map[col_name]
        else:
            row_idx = col_name
        if col_name in no_check or col_name :
            break
        measure_slice = test_measure[row_idx, :]
        df_slice = test_df[col_name].values
        np.testing.assert_almost_equal(measure_slice, df_slice)
    os.remove(csv_loc)
    for file in os.listdir(output_directory):
        os.remove(os.path.join(output_directory, file))
    os.rmdir(output_directory)

    # raises exception if not a file path
    with pytest.raises(FileNotFoundError):
        make_csv("", output_directory, file_type)

    # raises exception if input not string or path-like
    with pytest.raises(TypeError):
        make_csv([], output_directory, file_type)

def test_raw_load(android_raw_2023_path, android_derived_2023_path):
    """Test basic loading of android raw file.

    Parameters
    ----------
    android_raw_2023_path : string
        Location for text log file with Android Raw measurements.
    android_derived_2023_path : string
        Location for text log file with Android derived measurements.

    """
    # load derived data
    derived = AndroidDerived2023(input_path=android_derived_2023_path)

    # load raw data
    raw = android.AndroidRawGnss(input_path=android_raw_2023_path)

    # make sure the same data is contained in both
    assert len(derived) == len(raw)

    print(raw)

    print(derived.shape,"vs.",raw.shape)
