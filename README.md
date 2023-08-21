# Web-Scrapper

1. Code is provided in both python file and jupyter notebook file.


Scrapped data from this link:
https://www.makaan.com/price-trends


2. scrapped_data.xlsx: This is our main scrapped data file.
> NOTE: I saved this file as .xlsx instead of .csv because for each city we have localities data w.r.t. ('Apartment', 'Builder Floor', 'Villa', and 'Plot'). In order to organize the data properly, I created separate sub-sheets within the .xlsx file for each section, as, Python does not support creating sub-sheets in CSV format, which is why I chose the .xlsx format.


3. scrapped_data.db: This is an SQLLite DB file that contains all the scraped data.
> NOTE: I have created four tables within the database, each representing one of the sections ('Apartment', 'Builder Floor', 'Villa', and 'Plot'). The data for each section is saved in a separate table.