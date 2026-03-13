"""
Tests for the filter_data() function in the helper_function module.

The function filter_data() is used to filter a dataframe using given inputs.
"""
import pandas as pd
import pytest

@pytest.fixture 
def sample_df():
    return pd.DataFrame(
        {
            "Date": [pd.Timestamp("2019-01-01"), pd.Timestamp("2019-03-05"), pd.Timestamp("2019-02-02"), pd.Timestamp("2019-03-31")],
            "Branch": ['A', 'B', 'A', 'C'],
            "Total": [500, 232.23, 889.23, 976.30],
            "Product line": ["Health and beauty", "Sports and travel", "Home and lifestyle", "Health and beauty"],
            "Payment": ["Ewallet", "Cash", "Credit card", "Cash"],
            "Customer type": ["Member", "Member", "Normal", "Normal"],
            "Gender": ['Female', 'Male', 'Female', 'Female']
        }
    )

def tests_df():
    """Tests to ensure that the function works as expected"""
    pass

def test_chosen_comp_col():
    """Tests to ensure the chosen comparison column is returned"""
    pass

def test_date_range():
    """Tests to ensure only rows within date range are returned"""
    pass

def test_agg_type():
    """Tests to ensure the aggregation works as expected"""
    pass

