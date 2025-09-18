# This script is designed to take in any form of order for GTC and process it into a single table fitting daily usecase

#------------------------------#
# TO DO:
# - Build a script to take in any csv files for GTC orders
# - Process the data into a pandas dataframe
# - Clean the data 
#    - Including dropping unneeded columns
#
# - Two options:
#       1. Store the data in a sqlite database (this is unnecessary due to output being multi index pivot table)
#           - Store the data in a temp sqlite table (table is dropped at start of process)
#           - Pull the data for daily use table
#           - export the retrieved data in a format that is easy to read
#           - Send the export file to email address
#       2. Transform pandas dataframe into a daily use table
#           - export the data in a format that is easy to read
#           - Send the export file to email address
#
# - Add logging to the process
# - Add error handling to the process
# - Automaticaly delete the csv files at the end of the process
#
# - Two options for automatization:
# -     1. Automat the process to run when new csv files are saved to input folder
# -     2. Automat the process to run when csv files are sent to email address
# - 
#------------------------------#
# OUTPUT: square data
# - Table to include:
#   - Item Name
#   - Item Modifiers
#   - Item Variation
#   - Order Name
#   - Item Price
#   - Item Quantity --> int
# - Table should be Orderd by Item Name
# - Table should include sub and grand totals 
# - - try to make the sub total values bold
# - File format: (these are options to be looked into)
#   - Excel
#------------------------------#
# OUTPUT: shopify data
# - Table to include:
#   - Lineitem name
#   - Shipping Name
#   - Lineitem price
#   - Lineitem quantity
# - Table should be Orderd by Item Name
# - Table should include sub and grand totals
# - - try to make the sub total values bold
# - File format: (these are options to be looked into)
#   - Excel
#------------------------------#
# OUTPUT TWO: (do not do this until boss gives express direction to do so)
# - Filter the data to output grouped by person
# - give the total nuumber of unieque people who ordered
#------------------------------#

# Importing necessary libraries

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import glob
import os
import re
import xlsxwriter as xw


# set pandas display for building purposes
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Optional: Show all columns
pd.set_option('display.width', None)  # Optional: Prevent line wrapping
pd.set_option('display.max_colwidth', None)  # Optional: Show full column content]
pd.set_option('display.float_format', '{:.6f}'.format)  # Optional: Format floats to 2 decimal places 


# Connection to sqlite database used for temp storage 
# This process may be redundant but allows for learning experience
sqlite_connection = sqlite3.connect(input('Enter the path for your sqlite db:'))
table = 'temp_table'

#------------------------------#
# log processing
#------------------------------#

log_file = input('Add your log file path here:')
global_log_file = input('Add your global log file path here if applicable:')

#writing both to daily log and global log
def log(message):
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a' )as log:
        log.write(f'{message}, {timestamp}\n')
    with open(global_log_file, 'a' )as log:
        log.write(f'{message}, {timestamp}\n')
    print(f'Log entry added: {message}, {timestamp}')

#------------------------------#
# Extracting data from csv files
#------------------------------#

# Path to input folder
csv_input_folder = input('Add your input folder path here:')
csv_files = glob.glob(csv_input_folder + '/*.csv')
csv_files

# Attribute lists related to input source

square_attribute_list = [
    'Order',
    'Order Name',
    'Order Date',
    'Currency',
    'Order Subtotal', 
    'Order Shipping Price',
    'Order Tax Total',
    'Order Total',
    'Order Refunded Amount',
    'Fulfillment Date',
    'Fulfillment Type',
    'Fulfillment Status',
    'Channels',
    'Fulfillment Location',
    'Fulfillment Notes',
    'Recipient Name',
    'Recipient Email',
    'Recipient Phone',
    'Recipient Address',
    'Recipient Address 2',
    'Recipient Postal Code',
    'Recipient City',
    'Recipient Region',
    'Recipient Country',
    'Item Quantity',
    'Item Name',
    'Item SKU',
    'Item Variation',
    'Item Modifiers',
    'Item Price',
    'Item Options Total Price',
    'Item Total Price'
]

shopify_attribute_list = [
    'Name',
    'Email',
    'Financial Status',
    'Paid at',
    'Fulfillment Status',
    'Fulfilled at',
    'Accepts Marketing',
    'Currency',
    'Subtotal',
    'Shipping',
    'Taxes',
    'Total',
    'Discount Code',
    'Discount Amount',
    'Shipping Method',
    'Created at',
    'Lineitem quantity',
    'Lineitem name',
    'Lineitem price',
    'Lineitem compare at price',
    'Lineitem sku',
    'Lineitem requires shipping',
    'Lineitem taxable',
    'Lineitem fulfillment status',
    'Billing Name',
    'Billing Street',
    'Billing Address1',
    'Billing Address2',
    'Billing Company',
    'Billing City',
    'Billing Zip',
    'Billing Province',
    'Billing Country',
    'Billing Phone',
    'Shipping Name',
    'Shipping Street',
    'Shipping Address1',
    'Shipping Address2',
    'Shipping Company',
    'Shipping City',
    'Shipping Zip',
    'Shipping Province',
    'Shipping Country',
    'Shipping Phone',
    'Notes',
    'Note Attributes',
    'Cancelled at',
    'Payment Method',
    'Payment Reference',
    'Refunded Amount',
    'Vendor',
    'Outstanding Balance',
    'Employee',
    'Location',
    'Device ID',
    'Id',
    'Tags',
    'Risk Level',
    'Source',
    'Lineitem discount',
    'Tax 1 Name',
    'Tax 1 Value',
    'Tax 2 Name',
    'Tax 2 Value',
    'Tax 3 Name',
    'Tax 3 Value',
    'Tax 4 Name',
    'Tax 4 Value',
    'Tax 5 Name',
    'Tax 5 Value',
    'Phone',
    'Receipt Number',
    'Duties',
    'Billing Province Name',
    'Shipping Province Name',
    'Payment ID',
    'Payment Terms Name',
    'Next Payment Due At',
    'Payment References'
]

#------------------------------#
# Function to process input csv files into dataframe
#------------------------------#

# this will only work if all the csv files come from the same source
def csv_to_dataframe(files):
    
    # identifying the source of files
    square_csv_pattern = r'.*orders-.*'
    square_csv_files = [file for file in files if re.search(square_csv_pattern, file)]
    shopify_csv_pattern = r'orders_.*'
    shopify_csv_files = [file for file in files if re.search(shopify_csv_pattern, file)]
    
        #processing the files into a single dataframe
        #use error handeling to catch any errors
    try:
        if len(square_csv_files) > 0:
            log(f'square csv files found: {square_csv_files}')
            # processing the square files
            square_df = pd.DataFrame(columns=square_attribute_list)
            for file in square_csv_files:
                temp_df = pd.read_csv(file)
                square_df = pd.concat([square_df, temp_df], ignore_index=True)
                log(f'square dataframe created')
            return square_df
        
        if len(shopify_csv_files) > 0:
            log(f'Shopify csv files found: {shopify_csv_files}')    
            # processing the shopify files
            shopify_df = pd.DataFrame(columns=shopify_attribute_list)
            #This may be redundant as there only might be one file for this export location
            for file in shopify_csv_files:
                temp_df = pd.read_csv(file)
                shopify_df = pd.concat([shopify_df, temp_df], ignore_index=True)
                log(f'Shopify dataframe created')
            return shopify_df
        
        if len(square_csv_files) == 0 and len(shopify_csv_files) == 0:
            log('No recognizable csv files found')
            print('No recognizable csv files found')
            return ImportError
        
        if len(square_csv_files) > 0 and len(shopify_csv_files) > 0:
            log('Both square and shopify csv files found')
            print('Both square and shopify csv files found, please only input one source at a time')
            return ImportError
        
    except Exception as e:
        log(f'Error in csv_to_dataframe function: {e}')
        print(f'Error in csv_to_dataframe function: {e}')
        return e

#------------------------------#   
# Function to clean the input data
#------------------------------#

def clean_input_data(df):
    
    #cleaning square data
    if len(square_attribute_list) == len(df.columns):
        log('square database detected')
        
        #drop unneeded columns
        df = df.drop(columns=['Order',
        'Order Date',
        'Currency',
        'Order Subtotal', 
        'Order Shipping Price',
        'Order Tax Total',
        'Order Total',
        'Order Refunded Amount',
        'Fulfillment Date',
        'Fulfillment Type',
        'Fulfillment Status',
        'Channels',
        'Fulfillment Location',
        'Fulfillment Notes',
        'Recipient Name',
        'Recipient Email',
        'Recipient Phone',
        'Recipient Address',
        'Recipient Address 2',
        'Recipient Postal Code',
        'Recipient City',
        'Recipient Region',
        'Recipient Country',
        'Item SKU',
        'Item Options Total Price',
        'Item Total Price'])
        
        #formating columns 
        df['Item Quantity'] = df['Item Quantity'].astype(int)
        df = df.replace({np.nan: 'None'})
        log('square dataframe cleaned')
        return df
    
    
    if len(shopify_attribute_list) == len(df.columns):
        log('shopify database detected')
        
        #drop unneeded columns
        df = df.drop(columns=['Name',
    'Email',
    'Financial Status',
    'Paid at',
    'Fulfillment Status',
    'Fulfilled at',
    'Accepts Marketing',
    'Currency',
    'Subtotal',
    'Shipping',
    'Taxes',
    'Total',
    'Discount Code',
    'Discount Amount',
    'Shipping Method',
    'Created at',
    'Lineitem compare at price',
    'Lineitem sku',
    'Lineitem requires shipping',
    'Lineitem taxable',
    'Lineitem fulfillment status',
    'Billing Name',
    'Billing Street',
    'Billing Address1',
    'Billing Address2',
    'Billing Company',
    'Billing City',
    'Billing Zip',
    'Billing Province',
    'Billing Country',
    'Billing Phone',
    'Shipping Street',
    'Shipping Address1',
    'Shipping Address2',
    'Shipping Company',
    'Shipping City',
    'Shipping Zip',
    'Shipping Province',
    'Shipping Country',
    'Shipping Phone',
    'Notes',
    'Note Attributes',
    'Cancelled at',
    'Payment Method',
    'Payment Reference',
    'Refunded Amount',
    'Vendor',
    'Outstanding Balance',
    'Employee',
    'Location',
    'Device ID',
    'Id',
    'Tags',
    'Risk Level',
    'Source',
    'Lineitem discount',
    'Tax 1 Name',
    'Tax 1 Value',
    'Tax 2 Name',
    'Tax 2 Value',
    'Tax 3 Name',
    'Tax 3 Value',
    'Tax 4 Name',
    'Tax 4 Value',
    'Tax 5 Name',
    'Tax 5 Value',
    'Phone',
    'Receipt Number',
    'Duties',
    'Billing Province Name',
    'Shipping Province Name',
    'Payment ID',
    'Payment Terms Name',
    'Next Payment Due At',
    'Payment References'])
    
        #formatting columns
        df = df.replace({np.nan: 'None'})
        log('shopify dataframe cleaned')
        return df
    
    else:
        log('unrecognizable database detected')
        print('unrecognizable database detected')
        return None

#------------------------------#
# Function to Upload dataframe to sqlite db
#------------------------------#

def df_to_sqlite(df, table_name):
    df.to_sql(table_name, sqlite_connection, if_exists='replace', index=False)
    print(f'Table {table_name} created in SQLite database.')
    log(f'Table {table_name} created in SQLite database.')

#------------------------------#
# Function to retrieve data from sqlite db
#------------------------------#

def query_sqlite(query):
    try:
        log(f'Query executed: {query}')
        result_df = pd.read_sql_query(query, sqlite_connection)
        print(f'Query: {query}')
        print(f'Result:\n{result_df}')
        log(f'Query returned with no errors')
        log
        return result_df
    except Exception as e:
        log(f'Error querying SQLite database: {e}')
        print(f'Error querying SQLite database: {e}')
        return None

#------------------------------#
# Function to create pivot table 
#------------------------------#

def create_pivot_table(df):
    #check which df it is
    #square df
    if len(df.columns) == 6:
        log('square database detected for pivot table creation')
        ptable = df.pivot_table(
        index=['Item Name', 'Item Modifiers', 'Item Variation','Order Name'], 
        values=['Item Quantity', 'Item Price'], 
        aggfunc={'Item Quantity': 'sum', 'Item Price': 'first'}).sort_index()
        log('pivot table created from square dataframe')
        return ptable

    #shopify df
    if len(df.columns) == 4:
        log('shopify database detected for pivot table creation')
        ptable = df.pivot_table(
        index=['Lineitem name', 'Shipping Name'], 
        values=['Lineitem quantity', 'Lineitem price'], 
        aggfunc={'Lineitem quantity': 'sum', 'Lineitem price': 'first'}).sort_index()
        log('pivot table created from shopify dataframe')
        return ptable

#------------------------------#
# Function to add subtotals and grand totals
#------------------------------#

def add_subtotals_totals(ptable):
    # check which pivot table it is
    #square ptable
    
    # this could potentially be refactored to go baised off of the length of the index
    
    if len(ptable.index.names) == 4:
        log('square pivot table detected\n Adding in subtotals and grand totals')
        total_items_sold = ptable['Item Quantity'].values.sum()
        total_price_sold = (ptable['Item Price'].values * ptable['Item Quantity'].values).sum()
        
        # sub totals of item quantity based on item name
        sub = ptable.groupby(level = 'Item Name')[['Item Quantity']].sum()
        # setting up a multi index for sub totals to be in the correct place on the pivot table
        sub.index = pd.MultiIndex.from_frame(
            sub.index.to_frame().assign(
                **{
                    'Item Modifiers': 'SubTotal',
                    'Item Variation': '',
                    'Order Name': ''
                }
            )
        )
        # adding in the sub totals to the end pivot table 
        # they are not in the correct location yet
        out = pd.concat([ptable, sub],axis = 0)
        
        # ordering the pivot table to have subtotals in the correct location
        keys = out.index.to_frame(index=False)
        keys['__is_sub__'] = keys['Item Modifiers'] == 'SubTotal'

        orderer = keys.sort_values(
            ['Item Name', '__is_sub__', 'Item Modifiers', 'Item Variation', 'Order Name'],
        ).index

        out = out.iloc[orderer]
        log('subtotals added')
        
        # adding the grand total to the end of the table
        grand_index = pd.MultiIndex.from_tuples(
            [('Grand Total', '', '', '')],
            names=ptable.index.names
        )
        grand_total = pd.DataFrame(
            {"Item Quantity": [total_items_sold],
            "Item Price": [total_price_sold]},
            index=grand_index   
        )
        
        out = pd.concat([out, grand_total], axis=0)
        log('grand total added')
        return out
    
    #shopify ptable
    # this needs to be done
    if len(ptable.index.names) == 2:
        log('shopify pivot table detected\n Adding in subtotals and grand totals')
        total_iteams = ptable['Lineitem quantity'].values.sum()
        total_price = (ptable['Lineitem price'].values * ptable['Lineitem quantity'].values).sum()
    
        sub = ptable.groupby(level = 'Lineitem name')[['Lineitem quantity']].sum()
        
        sub.index = pd.MultiIndex.from_frame(
            sub.index.to_frame().assign(
                **{
                    'Shipping Name': 'SubTotal'
                }
            )
        )
        
        out = pd.concat([ptable, sub],axis = 0)
        
        keys = out.index.to_frame(index=False)
        keys['__is_sub__'] = keys['Shipping Name'] == 'SubTotal'
        orderer = keys.sort_values(
            ['Lineitem name', '__is_sub__', 'Shipping Name'],
        ).index
        
        out = out.iloc[orderer]
        log('subtotals added')
        
        grand_index = pd.MultiIndex.from_tuples(
            [('Grand Total', '')],
            names=ptable.index.names
        )
        
        grand_total = pd.DataFrame(
            {"Lineitem quantity": [total_iteams],
            "Lineitem price": [total_price]},
            index=grand_index
        )
        
        out = pd.concat([out, grand_total], axis=0)
        log('grand total added')
        return out

#------------------------------#
# All functions are working up to this point
#------------------------------#


input = csv_to_dataframe(csv_files)
cleaned = clean_input_data(input)
cleaned
ptable = create_pivot_table(cleaned)
ptable
output = add_subtotals_totals(ptable)
print(output)
output




def excel_export(ptable):
    ptable.to_excel('test.xlsx', engine='xlsxwriter')


excel_export(output)

