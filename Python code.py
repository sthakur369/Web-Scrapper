# Imports

import requests
from bs4 import BeautifulSoup
import pandas as pd
import bs4 as bs
import re
import math
import os
import sqlite3




# Get City Nammes::

# def get_city_names():
#     global city_names
#     url = 'https://www.makaan.com/price-trends'
#     data = requests.get(url).text
#     response = requests.get(url)
#     city_names = []
#     city_names.clear()

#     # Create a BeautifulSoup object to parse the HTML content
#     soup = BeautifulSoup(data, 'html.parser')
#     table = soup.find('table', {'class': 'tbl', 'data-trend-type': 'apartment'})

#     if table:
#         for row in table.tbody.find_all('tr'):
#             columns = row.find_all('td')
#             first_column = columns[0].get_text(strip=True)
#             city_names.append(first_column)


# Get URLs

# Make a GET request to the webpage
def get_urls():
    global city_names
    urls = []
    urls.clear()

    base_url = 'https://www.makaan.com/price-trends'
    city_names = ['Chennai', 'Mumbai', 'Pune', 'Puri', 'Bangalore']

    for i in range(0,len(city_names)):
        urls.append(base_url + '/property-rates-for-buy-in-' + city_names[i])
    return urls



# Get Table object

def get_table(url, trend):
    global table
    global soup
    data = requests.get(url).text
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML content
    soup = BeautifulSoup(data, 'html.parser')

    table = soup.find('table', {'class': 'tbl', 'data-trend-type': trend})



# Scrape the Data

def get_data(url, trend):
    global locality_name
    global price_range_per_sq_ft
    global avg_price_per_sq_ft
    global price_rise
    global city
    global city_url
    global page_numbers
    global page_links
    global total_pages
    
    locality_name = []
    price_range_per_sq_ft = []
    avg_price_per_sq_ft = []
    price_rise = []
    city = []
    city_url = []
    page_numbers = []


    page = 1
    while True:
        response = requests.get(url + f"?page={page}")
        soup = BeautifulSoup(response.content, 'html.parser')
        

        table = soup.find('table', {'class': 'tbl', 'data-trend-type': trend})
        if table:
            for row in table.tbody.find_all('tr'):
                columns = row.find_all('td')
                if len(columns) > 4:
                    first_column = columns[0].get_text(strip=True)
                    locality_name.append(first_column)

                    second_column = columns[1].get_text(strip=True)
                    price_range_per_sq_ft.append(second_column)

                    third_column = columns[2].get_text(strip=True)
                    avg_price_per_sq_ft.append(third_column)

                    fourth_column = columns[3].get_text(strip=True)
                    price_rise.append(fourth_column)

                    city_element = soup.find('h1', {'class': 'page-hdng'})
                    city_name = city_element.text.strip()
                    city_name = city_name.split(' in ')[-1].split(' - ')[0]

                    city.append(city_name)
                    city_url.append(url)
                    page_numbers.append(page)

            pagination = soup.find('div', class_='pagination')
            
            if not pagination:
                total_pages = 1
                break

            page_links = pagination.find_all('a')
            if len(page_links) < 2:
                break

            last_page_link = page_links[-2].get('href')
            if last_page_link is None:
                total_pages = 1
                break
                
            total_pages = int(last_page_link.split('=')[-1])+1
            if page >= total_pages:
                break

            page += 1
        else:
            break





# Clean the Data

def clean_data():
    global FLOAT_avg_price_per_sq_ft
    global INT_price_rise
    global converted_data
    
    FLOAT_avg_price_per_sq_ft = []
    INT_price_rise = []
    converted_data = []

    FLOAT_avg_price_per_sq_ft.clear()
    INT_price_rise.clear()
    converted_data.clear()


    #1
    for price in avg_price_per_sq_ft:
        if price == '-':
            FLOAT_avg_price_per_sq_ft.append(None)
        else:
            cleaned_price = re.sub(r'[^\d.]', '', price)
            FLOAT_avg_price_per_sq_ft.append(float(cleaned_price) if cleaned_price else None)


    #2        
    for data in price_rise:
        if data == '-':
            INT_price_rise.append(None)
        else:
            cleaned_data = re.sub(r'[^-?\d.]', '', data)
            if cleaned_data:
                rounded_value = math.copysign(round(abs(float(cleaned_data))), float(cleaned_data))
                INT_price_rise.append(rounded_value)
            else:
                INT_price_rise.append(None)
    

    #3
    for data in price_range_per_sq_ft:
        range_match = re.search(r'(\d+(?:,\d+)?)(?:-(\d+(?:,\d+)?))?', data)
        if range_match:
            min_value = int(range_match.group(1).replace(',', ''))
            max_value = int(range_match.group(2).replace(',', '')) if range_match.group(2) else min_value
            #converted_data.append((min_value, max_value))
            converted_data.append(f"{min_value}-{max_value}")
        else:
            converted_data.append(None)
            




# Format the data

def extract_data(i):
    global df
    global INT_price_rise2
    INT_price_rise2 = [int(x) if x is not None else None for x in INT_price_rise]    
    
    df_name = f"df{i}"  # Generate the variable name
    globals()[df_name] = pd.DataFrame({'city_name': city, 'city_url': city_url,'locality_name': locality_name, 'price_range_per_sq_ft': converted_data, 'avg_price_per_sq_ft': FLOAT_avg_price_per_sq_ft, 'price_rise': INT_price_rise2, 'page_number': page_numbers})  
    
    return globals()[df_name]




# Calling the functions

trend = ['apartment', 'builderfloor', 'villa', 'plot']
urls = get_urls()

# Create an empty list to store the DataFrames
df_list = []
total_pages_ls = []
locality_name_len = []

df_list.clear()
total_pages_ls.clear()
locality_name_len.clear()

# creating connection with SQLLite
conn = sqlite3.connect('makaan_locality_prices.db')

for tr in trend:
    print(tr)
    df_list.clear()
    for i, url in enumerate(urls):
        print(url)
        
        get_table(url, tr)
        get_data(url, tr)
        clean_data()
        
        #df = df.iloc[0:0]
        df = extract_data(i+1)
        df_list.append(df)
        
        if tr == 'apartment':
            total_pages_ls.append(total_pages)
            locality_name_len.append(len(locality_name))   
        
    new_df = pd.concat(df_list)
    new_df['price_rise'] = new_df['price_rise'].astype('Int64')
    
    # insert column using insert(position,column_name,first_column) function
    first_column = new_df.pop('page_number')
    new_df.insert(0, 'page_number', first_column)
    
    new_df.to_sql(tr, conn, if_exists='replace', index=False)
    
    # Generating our main file
    if os.path.isfile('makaan_locality_prices.xlsx'):
        with pd.ExcelWriter('makaan_locality_prices.xlsx', mode='a', engine='openpyxl', if_sheet_exists="replace") as writer:
            new_df.to_excel(writer, index=False, sheet_name=tr)
        
    else:   
        new_df.to_excel('makaan_locality_prices.xlsx', index=False, sheet_name=tr)
        
conn.close()



# Generating 'makaan_localities.csv'

dk = pd.DataFrame({'city_name': city_names, 'city_url': urls,'total_pages': total_pages_ls, 'total_localities': locality_name_len})
dk.to_csv('makaan_localities.csv', index=False)
