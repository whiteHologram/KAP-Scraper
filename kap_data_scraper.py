import requests
from requests_html import *
import time as tm
from datetime import *
import pandas as pd
import json
import numpy as np
from sqlalchemy import *
import pyodbc 

def get_response(fromDate,toDate):

  url = "https://www.kap.org.tr/tr/api/memberDisclosureQuery" #bunusil

  payload = {
    "fromDate":fromDate,
    "toDate":toDate,
    "year":"",
    "prd":"",
    "term":"", 
    "ruleType":"",
    "bdkReview":"", 
    "disclosureClass":"",
    "index":"", 
    "market":"",
    "isLate":"", 
    "subjectList":[],
    "mkkMemberOidList":[], 
    "inactiveMkkMemberOidList":[],
    "bdkMemberOidList":[], 
    "mainSector":"",
    "sector":"", 
    "subSector":"",
    "memberType":"IGS", 
    "fromSrc":"N",
    "srcCategory":"", 
    "discIndex":[]
    }
  
  payload_json = json.dumps(payload)

  headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8,fr-FR;q=0.7,fr;q=0.6,es-ES;q=0.5,es;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://www.kap.org.tr',
    'Referer': 'https://www.kap.org.tr/tr/bildirim-sorgu',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
  }
  
  try:
    response = requests.request("POST", url, headers=headers, data=payload_json)
    print(f"status:{response.status_code}\n")
    tm.sleep(2)
    return response  
  
  except Exception as e:
    print(f"Request error: {e}\n")
    raise e

# parse_response calls get response and returns processed data in dataframe format as raw_df and final_df 
# final_df is for db table and excludes website parameters in raw data   
def  parse_response(fromDate,toDate):
  res = []
  response = get_response(fromDate,toDate)
  data = response.json()
  for p in data:
    res.append(p)
  df = pd.json_normalize(res)
  
  if not df.empty:

    clean_date(df,toDate)
    df['publishDate'] = pd.to_datetime(df['publishDate'], format='mixed')
    raw_df = df

    columns=['disclosureType','disclosureCategory','hasMultiLanguageSupport','attachmentCount','year', 'isModified']
    for column in columns:
      try: 
        df = df.drop(column)
      # print(df.info())
      except:
        print(column +  'does not exist')

    column_order = ['disclosureIndex', 'disclosureClass', 'publishDate', 'stockCodes', 'kapTitle', 'isOldKap', 'subject', 'summary', 'relatedStocks', 'ruleTypeTerm', 'isLate']
    
    for column in column_order:
      if column not in df.columns:
        df[column] = np.nan
    
    ordered_df = df[column_order]
    final_df = ordered_df.rename(columns={'disclosureIndex':'reportId',
                                        'disclosureClass':'reportClass',
                                        'publishDate':'createDat',
                                        'stockCodes':'firmStockCode', 
                                        'kapTitle':'firmName'
                                        })
    
    print(final_df.info())
    # print(final_df.head(50))
    print("raw_final_df.ok")

  else: 
    raw_df = pd.DataFrame()
    final_df = pd.DataFrame()

  return {'raw_df': raw_df, 'final_df': final_df}

# web site doesn't support more than 2000 results per page
# there isn't any other page so long period parser divides date range to days and pulls data day by day
def long_period_parser(fromDate,toDate, final_temp, detailed_temp, final_full, detailed_full):

  date_list = split_period(fromDate, toDate)
  dfs = []
  concat_detail_df = pd.DataFrame()
  concat_final_df = pd.DataFrame()
  for date in date_list:
    try:
      dfs = parse_response(date,date)
      write_log_file('Kap_log.txt','parser',date=date)
      
      concat_detail_df = pd.concat([dfs['raw_df'], concat_detail_df]).drop_duplicates()
      concat_final_df = pd.concat([dfs['final_df'],concat_final_df]).drop_duplicates()
      
      # print(concat_full_df.head())
      print(concat_detail_df.info())
      # print(concat_db_df.head())
      print(concat_final_df.info())

      print(date + " data.ok")

      concat_final_df.to_excel(final_temp, sheet_name= datetime_str(2), index = False)
      concat_detail_df.to_excel(detailed_temp, sheet_name= datetime_str(2), index = False)
      
      write_log_file('Kap_log.txt','temp_excel')
      print("temp_excel.ok")
      tm.sleep(5) 

    except Exception as e:
      
      with pd.ExcelWriter(final_full, engine= 'openpyxl', mode= 'a', if_sheet_exists= 'replace') as writer:
        concat_final_df.to_excel(writer, sheet_name= datetime_str(2), index = False)
      with pd.ExcelWriter(detailed_full, engine= 'openpyxl', mode= 'a', if_sheet_exists= 'replace') as writer:
        concat_detail_df.to_excel(writer, sheet_name= datetime_str(2), index = False)

      print("for " + str(e) + "300 seconds waiting for recall of long_period_parser from where it left")
      write_log_file('Kap_log.txt','unfinished_excel')
      print("unfinished_final_excel.ok")
      tm.sleep(300)
      print("recalling long_period_parser")
      long_period_parser(fromDate, toDate)

  with pd.ExcelWriter(final_full, engine= 'openpyxl', mode= 'a', if_sheet_exists= 'replace') as writer:
    concat_final_df.to_excel(writer, sheet_name= datetime_str(2), index = False)
  with pd.ExcelWriter(detailed_full, engine= 'openpyxl', mode= 'a', if_sheet_exists= 'replace') as writer:
    concat_detail_df.to_excel(writer, sheet_name= datetime_str(2), index = False)

  write_log_file('Kap_log.txt','final_excel')
  print("fully_final_excel.ok")

def db_jobs(path):

  odbc_string = " "
  db_string = " " + odbc_string
  engine = create_engine(db_string)

  path = path
  dfs = pd.read_excel(path, sheet_name=None)
  keys = dfs.keys()
  df_concat = pd.DataFrame()
  for key in keys:
    df_concat = pd.concat([df_concat, dfs[key]]).drop_duplicates()
  df_concat = df_concat.drop_duplicates(subset=['reportId'])

  df_concat = df_concat[df_concat['firmStockCode'].notna()]
  df_concat['isOldKap'] = df_concat['isOldKap'].map({True: 1, False: 0}) 
  df_concat['isOldKap'] = df_concat['isOldKap'].fillna(0).astype(int)
  df_concat['isLate'] = df_concat['isLate'].map({True: 1, False: 0}).fillna(0).astype(int)
  df_concat['summary'] = df_concat['summary'].str.replace("'","''").str.replace(":"," ")
  df_concat['subject'] = df_concat['subject'].str.replace("'","''").str.replace(":"," ")



  print(df_concat.info())
  # print(df_concat.head(30))
  with engine.connect() as con:

    # your table name
    select_query = "SELECT ReportId FROM <your_table_name>"
    existent_ids_df = pd.read_sql(select_query, con)
    existent_ids = existent_ids_df['ReportId'].to_list()

    for index, row in df_concat.iterrows():
      ReportId = row['reportId']
      ReportClass = row['reportClass']
      CreateDat = row['createDat']
      FirmStockCode = row['firmStockCode']
      FirmName = row['firmName']
      IsOldKap = row['isOldKap']
      Subject = row['subject']
      Summary = row['summary']
      RelatedStocks = row['relatedStocks']
      RuleTypeTerm = row['ruleTypeTerm']
      IsLate = row['isLate']
      Status = 0

      if ReportId not in existent_ids:
        con.execute(text("""INSERT INTO KAPDB.dbo.KapFirms_test
                        (ReportId,ReportClass,CreateDat,FirmStockCode,FirmName,IsOldKap,
                        Subject,Summary,RelatedStocks,RuleTypeTerm,IsLate,Status) 
                        VALUES ({ReportId}, '{ReportClass}', '{CreateDat}', '{FirmStockCode}', '{FirmName}', {IsOldKap},
                        '{Subject}', '{Summary}', '{RelatedStocks}', '{RuleTypeTerm}', {IsLate}, {Status});""".format(ReportId=ReportId,
                                                                                                              ReportClass=ReportClass,
                                                                                                              CreateDat=CreateDat, 
                                                                                                              FirmStockCode=FirmStockCode, 
                                                                                                              FirmName=FirmName,
                                                                                                              IsOldKap=IsOldKap,
                                                                                                              Subject=Subject,
                                                                                                              Summary=Summary,
                                                                                                              RelatedStocks=RelatedStocks,
                                                                                                              RuleTypeTerm=RuleTypeTerm,
                                                                                                              IsLate=IsLate,
                                                                                                              Status=Status)))
        print(ReportId, CreateDat, FirmStockCode, FirmName,"ok")
        con.commit()
  write_log_file('kap_log.txt','db_update')
  print("db updated")

def datetime_str(case):

  dt = datetime.now()
  if case == 1:
    dt_str = dt.strftime("%Y-%m-%d, %H:%M:%S")
    return dt_str
  # case 2 is for excel
  if case == 2:
    dt_str = dt.strftime("%Y-%m-%d, %H-%M-%S")
    return dt_str

def split_period(fromDate,toDate):

  date_list = []
  start_date = datetime.strptime(fromDate, '%Y-%m-%d')
  end_date = datetime.strptime(toDate,'%Y-%m-%d')

  current_date = start_date
  while current_date <= end_date:
    date_list.append(current_date.strftime('%Y-%m-%d'))
    current_date += timedelta(days=1)
  
  return date_list

def clean_date(df,toDate):

  for index, row in df.iterrows():
    if "Bugün" in str(row["publishDate"]):
      splitdate = row['publishDate'].split(" ")
      df.at[index, "publishDate"] = toDate + " " + splitdate[1]
      # print(row['publishDate'])
      # print(toDate + " " + splitdate[1])

    if "Dün" in str(row["publishDate"]):
      splitdate = row['publishDate'].split(" ")
      today = datetime.strptime(toDate,'%Y-%m-%d')
      yesterday = today - timedelta(days=1)
      df.at[index, "publishDate"] = yesterday.strftime('%Y-%m-%d') + " " + splitdate[1]
      # print(row['publishDate'])
      # print(yesterday.strftime('%Y-%m-%d') + " " + splitdate[1])

def write_log_file(filename, summary, fromDate="", toDate="", date=""):
  today = datetime_str(1)

  summaries = {
    'log_entry': 'log of ' + today + '\t: process for ' + str(fromDate) + ' to ' + str(toDate) + ' time interval started\n',
    'parser': '\t' + datetime_str(1) + '\t:' + ' parsing ' + date + ' completed successfully...\n',
    'temp_excel': '\t' + datetime_str(1) + '\t: last updated data exported to temp excel successfully...\n',
    'final_excel': '\t' + datetime_str(1) + '\t: all data exported to final excel successfully...\n',
    'unfinished_excel': '\t' + datetime_str(1) + '\t: an exception occurred during data pulling long_period_parser will be recalled in 5 minutes, fetched data exported to final excel destination...\n',
    'db_update': '\t' + datetime_str(1) + '\t: database update completed successfully...\n',
    'log_end': 'log of ' + today + '\t: data scraping for ' + str(fromDate) + ' to ' + str(toDate) + ' time interval ended at ' + datetime_str(1) + '\n\n'
  }

  with open(filename, 'a') as file: 
    if summary == 'log_entry':
      file.write(summaries[summary])
    elif summary == 'parser':
      file.write(summaries[summary])
    elif summary == 'temp_excel':
      file.write(summaries[summary])
    elif summary == 'final_excel':
      file.write(summaries[summary])
    elif summary == 'db_update':
      file.write(summaries[summary])
    elif summary == 'log_end':
      file.write(summaries[summary])
    else:
      print("keyword for summary isn't recognized try one of those: \n 'log_entry' or 'parser' or 'temp_excel' or 'final_excel' or 'unfinished_excel' or 'db_update' or 'log_end' \n")
    

if __name__ == "__main__":
  # those are for final results and have multiple sheets, each for one scraping session
  # data is recorded in those if either scraping is complete or in case of a connection loss
  full_final_excel = r"path\kap_data_new.xlsx"
  full_detailed_excel = r"path\kap_detailed.xlsx" 
  # those have only one sheet and are for backup. for each export, file is overwritten
  # while pulling data day by day last concatenated data instantly recorded to those files
  temp_final_excel = r"path\kapData_temp.xlsx"
  temp_detailed_excel = r"path\kapDetailed_temp.xlsx"

  fromDate = "2024-10-10"
  toDate = "2024-10-15"
  write_log_file('Kap_log.txt','log_entry',fromDate=fromDate,toDate=toDate)
  # use long_period_parser, parse_response just parses the response returns a df, and never exports it to excel
  long_period_parser(fromDate,toDate,temp_final_excel,temp_detailed_excel,full_final_excel,full_detailed_excel)
  # db_jobs(full_final_excel)
  write_log_file('Kap_log.txt','log_end',fromDate=fromDate,toDate=toDate)

  