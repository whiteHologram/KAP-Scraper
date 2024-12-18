# `clean_date` `datetime_str` and `split_period`

## Overview

The `clean_date` function is designed to clean and standardize the `publishDate` column in a Pandas DataFrame. It adjusts dates expressed in relative terms (e.g., "Bugün" for "Today" and "Dün" for "Yesterday") to absolute dates, based on the reference date provided as `toDate`.
These two utility functions handle date and time-related operations.

1. **`datetime_str`:** Formats the current date and time into a string based on the specified case.
2. **`split_period`:** Generates a list of dates between two given dates, inclusive.

---



---
# `get response` and `parse_response`
## Overview
### `get response` 
* Description
Sends a POST request to the KAP API to retrieve disclosure data between specified dates.

* Parameters
fromDate (String): The starting date of the query in YYYY-MM-DD format.
toDate (String): The ending date of the query in YYYY-MM-DD format.
* Returns
Response Object: The raw response from the KAP API.

### `parse_response` 
* Description
Calls get_response to fetch data for a given date range and processes the response into two dataframes:
raw_df: A raw dataframe containing all data from the API response.
final_df: A cleaned dataframe with selected columns for database insertion.

* Parameters
1- fromDate (String): The starting date of the query in YYYY-MM-DD format.
2- toDate (String): The ending date of the query in YYYY-MM-DD format.

* Returns
Dictionary:
{'raw_df': raw_df, 'final_df': final_df}

---
# `long_period_parser` and `db_jobs`
## Overview
### `long_period_parser`
*Description
Handles queries for date ranges exceeding the API's 2000-record limit by splitting the date range into individual days and querying the API day by day.

*Parameters
1- fromDate (String): Starting date in YYYY-MM-DD format.
1- toDate (String): Ending date in YYYY-MM-DD format.
3- final_temp (String): Path for saving the temporary "final" Excel file.
4- detailed_temp (String): Path for saving the temporary "detailed" Excel file.
5- final_full (String): Path for saving the full "final" Excel file.
6- detailed_full (String): Path for saving the full "detailed" Excel file.

*Returns
None

### `db_jobs`
* Description
Processes an Excel file, consolidates data across sheets, and updates a database table with the results.

* Parameters
path (String): Path to the Excel file containing the data to process.

* Steps
1- Reads all sheets from the Excel file into a single dataframe.
2- Cleans and prepares the dataframe:
3- Removes duplicate rows based on reportId.
4- Fills NaN values in boolean columns (isOldKap and isLate) and converts them to integers.
5- Escapes problematic characters
