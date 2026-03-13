"""
Tests for the filter_data() function in the helper_function module.

The function filter_data() is used to filter a dataframe for the @reactive.calc 
df_filtered_product which is used for the plots plot_sales_mix and plot_product_lines.

The following tests ensure that for every input (date range, aggregation method and range, 
comparison column, branch), the function filter_data() returns the correct output and 
filters the dataframe as expected.
"""
import pandas as pd
import pytest

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from helper_functions import filter_data


@pytest.fixture 
def sample_df():
    return pd.DataFrame(
        {
            "Date": [pd.Timestamp("2019-01-01"), pd.Timestamp("2019-02-01"), pd.Timestamp("2019-02-02"), pd.Timestamp("2019-03-31"),pd.Timestamp("2019-03-31")],
            "Branch": ['A', 'B', 'A', 'C','C'],
            "Total": [500, 232.23, 889.23, 976.30,100],
            "Product line": ["Health and beauty", "Sports and travel", "Home and lifestyle", "Health and beauty","Health and beauty"],
            "Payment": ["Ewallet", "Credit card", "Credit card", "Cash","Cash"],
            "Customer type": ["Member", "Member", "Normal", "Normal","Member"],
            "Gender": ['Male', 'Female', 'Female', 'Female','Male']
        }
    )

def tests_output_columns(sample_df):
    """Tests to ensure that the function returned has the expected columns"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-02-01'), 'all', 'Gender', 'day', 'mean')
    expected = ["time", "gender","total"]
    assert list(result.columns) == expected


def test_branch(sample_df):
    """Tests to ensure only the chosen branch is returned"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-03-31'), 'A', 'Gender', 'day', 'mean')
    expected = [pd.Timestamp("2019-01-01"),pd.Timestamp("2019-02-02")]
    assert list(result['time']) == expected

def test_date_range(sample_df):
    """Tests to ensure only rows within date range are returned"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-01-31'), 'all', 'Gender', 'day', 'mean')
    expected = [pd.Timestamp("2019-01-01")]
    assert list(result['time']) == expected


def test_sum_agg(sample_df):
    """Tests to ensure the sum aggregation works as expected"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-03-31'), 'all', 'Gender', 'week', 'sum')
    expected = [500.0, 232.23 + 889.23, 976.3, 100.0]
    assert list(result['total']) == expected

def test_mean_agg(sample_df):
    """Tests to ensure the mean aggregation works as expected"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-03-31'), 'all', 'Gender', 'week', 'mean')
    expected = [500, (232.23 + 889.23)/2, 976.3, 100]
    assert list(result['total']) == expected

def test_day_agg(sample_df):
    """Tests to ensure the daily aggregation works as expected"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-03-31'), 'all', 'Payment', 'day', 'sum')
    expected = [500, 232.23, 889.23, 976.30 + 100]
    assert list(result['total']) == expected

def test_day_agg(sample_df):
    """Tests to ensure the weekly aggregation works as expected"""
    result = filter_data(sample_df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-03-31'), 'all', 'Payment', 'week', 'sum')
    expected = [500, 232.23 + 889.23, 976.30 + 100]
    assert list(result['total']) == expected

