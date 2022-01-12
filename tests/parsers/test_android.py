"""Tests for Android data loaders.

"""

__authors__ = "Ashwin Kanhere"
__date__ = "10 Nov 2021"

import os

import numpy as np
import pandas as pd
import pytest

from gnss_lib_py.parsers.android import AndroidDerived, AndroidRawFixes, AndroidRawImu
from gnss_lib_py.parsers.measurement import Measurement


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
    return root_path


@pytest.fixture(name="derived_path")
def fixture_derived_path(root_path):
    """Filepath of Android Derived measurements

    Returns
    -------
    derived_path : string
        Location for the unit_test Android derived measurements
    """
    derived_path = os.path.join(root_path, 'data/unit_test/Pixel4_derived.csv')
    return derived_path


@pytest.fixture(name="android_raw_path")
def fixture_imu_path(root_path):
    """Filepath of Android IMU measurements

    Returns
    -------
    raw_path : string
        Location for text log file with Android IMU measurements
    """
    raw_path = os.path.join(root_path, 'data/unit_test/Pixel4_GnssLog.txt')
    return raw_path


@pytest.fixture(name="pd_df")
def fixture_pd_df(derived_path):
    """Load Android derived measurements into dataframe

    Parameters
    ----------
    derived_path : pytest.fixture
        String with filepath to derived measurement file

    Returns
    -------
    derived_df : pd.DataFrame
        Dataframe with Android Derived measurements
    """
    derived_df = pd.read_csv(derived_path)
    return derived_df


@pytest.fixture(name="derived_col_map")
def fixture_inverse_col_map():
    """Map from standard names to derived column names

    Returns
    -------
    inverse_col_map : Dict
        Column names for inverse map of form {standard_name : derived_name}
    """
    inverse_col_map = {'toeMillis' : 'millisSinceGpsEpoch',
                        'PRN' : 'svid',
                        'x_sat_m' : 'xSatPosM',
                        'y_sat_m' : 'ySatPosM',
                        'z_sat_m' : 'zSatPosM',
                        'vx_sat_mps' : 'xSatVelMps',
                        'vy_sat_mps' : 'ySatVelMps',
                        'vz_sat_mps' : 'zSatVelMps',
                        'b_sat_m' : 'satClkBiasM',
                        'b_dot_sat_mps' : 'satClkDriftMps'
                    }
    return inverse_col_map


@pytest.fixture(name="derived")
def fixture_load_derived(derived_path):
    """Load instance of AndroidDerived

    Parameters
    ----------
    derived_path : pytest.fixture
        String with location of Android derived measurement file

    Returns
    -------
    derived : AndroidDerived
        Instance of AndroidDerived for testing
    """
    derived = AndroidDerived(derived_path)
    return derived


def test_derived_df_equivalence(derived, pd_df, derived_col_map):
    """Test if naive dataframe and AndroidDerived contain same data

    Parameters
    ----------
    derived : pytest.fixture
        Instance of AndroidDerived for testing

    pd_df : pytest.fixture
        pd.DataFrame for testing measurements

    derived_col_map : pytest.fixture
        Column map to convert standard to original derived column names

    """
    # Also tests if strings are being converted back correctly
    measure_df = derived.pandas_df()
    measure_df.rename(columns=derived_col_map, inplace=True)
    measure_df = measure_df.drop(columns='pseudo')
    pd.testing.assert_frame_equal(pd_df, measure_df, check_dtype=False)


@pytest.mark.parametrize('row_name, index, value',
                        [('collectionName', 0, '2020-05-14-US-MTV-1'),
                         ('phoneName', 1, 'Pixel4'),
                         ('vy_sat_mps', 7, 411.162),
                         ('b_dot_sat_mps', 41, -0.003),
                         ('signalType', 6, 'GLO_G1')]
                        )
def test_derived_value_check(derived, row_name, index, value):
    """Check AndroidDerived entries against known values using test matrix

    Parameters
    ----------
    derived : pytest.fixture
        Instance of AndroidDerived for testing

    row_name : string
        Row key for test example

    index : int
        Column number for test example

    value : float or string
        Known value to be checked against

    """
    # Testing stored values vs their known counterparts
    # String maps have been converted to equivalent integers
    if isinstance(value, str):
        value_str = derived.str_map[row_name][int(derived[row_name, index])]
        assert value == value_str
    else:
        np.testing.assert_equal(derived[row_name, index], value)


def test_get_and_set_num(derived):
    """Testing __getitem__ and __setitem__ methods for numerical values

    Parameters
    ----------
    derived : pytest.fixture
        Instance of AndroidDerived for testing
    """
    key = 'testing123'
    value = np.zeros(len(derived))
    derived[key] = value
    np.testing.assert_equal(derived[key, :], np.reshape(value, [1, -1]))


def test_get_and_set_str(derived):
    """Testing __getitem__ and __setitem__ methods for string values

    Parameters
    ----------
    derived : pytest.fixture
        Instance of AndroidDerived for testing
    """
    key = 'testing123_string'
    value = ['word']*len(derived)
    derived[key] = value
    np.testing.assert_equal(derived[key, :], np.zeros([1, len(derived)]))


def test_set_all(derived):
    """Testing __setitem__ method for all rows simultaneously

    Parameters
    ----------
    derived : pytest.fixture
        Instance of AndroidDerivevd for testing
    """
    assign_vals = np.zeros(len(derived))
    assign_vals[int(len(derived)/2):] = 1
    num_ones = np.sum(assign_vals==1)

    # choose_rows = [0, 2, 3, 5, 6]
    old_vals = derived.array[:, assign_vals==1]
    derived['all'] = derived['all', assign_vals==1]
    np.testing.assert_equal(len(derived), num_ones)
    np.testing.assert_equal(derived.array[:, :], old_vals)


def test_imu_raw(android_raw_path):
    """Test that AndroidRawImu initialization
    """
    _ = AndroidRawImu(android_raw_path)


def test_fix_raw(android_raw_path):
    """Test that AndroidRawImu initialization
    """
    _ = AndroidRawFixes(android_raw_path)


def test_measurement_type(derived):
    """Test that AndroidDerived is a subclass of Measurement
    """
    isinstance(derived, Measurement)
    isinstance(derived, AndroidDerived)
