# `clean_date` `datetime_str` and `split_period`

## Overview

The `clean_date` function is designed to clean and standardize the `publishDate` column in a Pandas DataFrame. It adjusts dates expressed in relative terms (e.g., "Bugün" for "Today" and "Dün" for "Yesterday") to absolute dates, based on the reference date provided as `toDate`.  


### `datetime_str`

Formats the current date and time into a string based on the specified case.


### `split_period`

* description:  
 Generates a list of dates between two given dates, inclusive.

* Parameters:  
fromDate (String)
toDate (String)

* Returns:  
List of Strings: A list of dates in the format YYYY-MM-DD, spanning from fromDate to toDate (inclusive).

* Behavior:  
Parses the input date strings into datetime objects.  
Iterates through each day from fromDate to toDate (inclusive) and appends the corresponding date string to a list.  
Returns the list of dates.  
   

---



---
# `get response` and `parse_response`
## Overview
### `get response` 
* Description:  
Sends a POST request to the KAP API to retrieve disclosure data between specified dates.

* Parameters:  
fromDate (String): The starting date of the query in YYYY-MM-DD format.  
toDate (String): The ending date of the query in YYYY-MM-DD format.  
* Returns  
Response Object: The raw response from the KAP API.

### `parse_response` 
* Description:  
Calls get_response to fetch data for a given date range and processes the response into two dataframes:  
raw_df: A raw dataframe containing all data from the API response.  
final_df: A cleaned dataframe with selected columns for database insertion.  

* Parameters:  
  fromDate (String): The starting date of the query in YYYY-MM-DD format.  
  toDate (String): The ending date of the query in YYYY-MM-DD format.  

* Returns:  
Dictionary:  
{'raw_df': raw_df, 'final_df': final_df}

* Processing Steps:  
  Calls get_response to fetch data.  
  Normalizes the JSON response into a dataframe.  
  Cleans and reorders the dataframe for further processing.  

---
# `long_period_parser` and `db_jobs`
## Overview
### `long_period_parser`
*Description:  
Handles queries for date ranges exceeding the API's 2000-record limit by splitting the date range into individual days and querying the API day by day.

* Parameters:  
  fromDate (String): Starting date in YYYY-MM-DD format.  
  toDate (String): Ending date in YYYY-MM-DD format.  
  final_temp (String): Path for saving the temporary "final" Excel file.  
  detailed_temp (String): Path for saving the temporary "detailed" Excel file.  
  final_full (String): Path for saving the full "final" Excel file.  
  detailed_full (String): Path for saving the full "detailed" Excel file.  

*Returns
None

### `db_jobs`
* Description:  
Processes an Excel file, consolidates data across sheets, and updates a database table with the results.

* Parameters:  
path (String): Path to the Excel file containing the data to process.

* Steps:  
  Reads all sheets from the Excel file into a single dataframe.  
  Cleans and prepares the dataframe:  
  Removes duplicate rows based on reportId.  
  Fills NaN values in boolean columns (isOldKap and isLate) and converts them to integers.  
  Escapes problematic characters  
