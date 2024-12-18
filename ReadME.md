# `clean_date` `datetime_str` and `split_period`Function Documentation

## Overview

The `clean_date` function is designed to clean and standardize the `publishDate` column in a Pandas DataFrame. It adjusts dates expressed in relative terms (e.g., "Bugün" for "Today" and "Dün" for "Yesterday") to absolute dates, based on the reference date provided as `toDate`.
These two utility functions handle date and time-related operations.

1. **`datetime_str`:** Formats the current date and time into a string based on the specified case.
2. **`split_period`:** Generates a list of dates between two given dates, inclusive.

---

### **Function Signature**

````python
def clean_date(df, toDate):

```python
def datetime_str(case):

````
