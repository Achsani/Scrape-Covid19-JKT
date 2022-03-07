from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as DT
from requests_html import HTMLSession
from google_drive_downloader import GoogleDriveDownloader as gdd
import pandas as pd
import os
from selenium import webdriver
import time

# List for all href scraped 
data = []

# url that we want to scrape
url = "https://riwayat-file-covid-19-dki-jakarta-jakartagis.hub.arcgis.com/"

# Run HTMLSession to scrape dynamic page
session = HTMLSession()
r = session.get(url)
r.html.render(sleep=10, timeout = 25)
res = BeautifulSoup(r.html.raw_html, "html.parser")

# Get all href data and insert it to data list
for link in res.find_all('a', href=True):
    data.append(link)

# Getting google drive id for newest data
# Missing data on date 31 Januari  
# 1 Januari 2021 = 339
# 7 April 2020 = 607
# Newest date on number 7
link = data[7]['href']
id_file = link[32:65]
judul = data[7].get_text()


# Download excel data using google drive id
destination = 'C:/Users/Farhan Achsani/Desktop/Kodingan/Scrape-Covid19-JKT/' + judul + ".xlsx"
gdd.download_file_from_google_drive(file_id=id_file, dest_path=destination)
judul_excel = judul + ".xlsx"

# Get yesterday's date to be included in covid data
# 1 Januari 2021 = 333
# 7 Arpil 2020 = 601
# Newest date on 1
today = DT.date.today()
# date = today
date = today - DT.timedelta(days=1)
str_date = str(date)

# column used for date 1 Jan 2021 - 18 Jan 2021
# (0 = A, ID Kel) (2 = C, nama_kota) (3 = D, nama_kecamatan) (25 = Z, POSITIF) (26 = AA, Dirawat) (27 = AB, Sembuh) (28 = AC, Meninggal) (29 = AD, Self Isolation)
# cols_kecamatan = [0, 2, 3, 25, 26, 27, 28, 29]

# Column used for date 19 Jan 2021 - Now
# # (0 = A, ID Kel) (2 = C, nama_kota) (3 = D, nama_kecamatan) (26 = AA, POSITIF) (27 = AB, Dirawat) (28 = AC, Sembuh) (29 = AD, Meninggal) (30 = AE, Self Isolation)
cols_kecamatan = [0, 2, 3, 26, 27, 28, 29, 30]

# Read downloaded data and exctract column that's needed
kecamatan = pd.read_excel(destination, header = 0,sheet_name="data_kecamatan", usecols=cols_kecamatan)
kecamatan.rename(columns={'Meninggal.1': 'Meninggal', 'Self Isolation':'Self_Isolation', 'Kasus Aktif':'Kasus_Aktif'}, inplace=True)
kecamatan = kecamatan.iloc[1:]
# kecamatan = kecamatan.iloc[:-1]
kecamatan['Kasus_Aktif'] = kecamatan['Dirawat'] + kecamatan['Self_Isolation']
kecamatan['Tanggal'] = date
# kecamatan = kecamatan[kecamatan["ID_KEC"] != 'LUAR DKI JAKARTA']
# kecamatan = kecamatan[kecamatan["ID_KEC"] != 'PROSES UPDATE DATA'] 
kecamatan['ID_KEC'] = kecamatan['ID_KEC'].replace(['LUAR DKI JAKARTA', 'PROSES UPDATE DATA'],111111)

# Column used for date 1 Jan 2021 - 18 Jan 2021
# (0 = A, ID Kel) (2 = C, nama_kota) (3 = D, nama_kecamatan) (4 = E, nama_kelurahan) (26 = AA, POSITIF) (27 = AB, Dirawat) (28 = AC, Sembuh) (29 = AD, Meninggal) (30 = AE, Self Isolation)
# cols_kelurahan = [0, 2, 3, 4, 26, 27, 28, 29, 30]

# Column used for date 19 Jan 2021 - Now
# # (0 = A, ID Kel) (2 = C, nama_kota) (3 = D, nama_kecamatan) (4 = E, nama_kelurahan) (27 = AB, POSITIF) (28 = AC, Dirawat) (29 = AD, Sembuh) (30 = AE, Meninggal) (31 = AF, Self Isolation)
cols_kelurahan = [0, 2, 3, 4, 27, 28, 29, 30, 31]

# Read downloaded data and extract column that's needed
kelurahan = pd.read_excel(destination, header = 0, sheet_name="data", usecols=cols_kelurahan)
kelurahan.rename(columns={'Meninggal.1': 'Meninggal'}, inplace=True)
kelurahan = kelurahan.iloc[1:]
kelurahan['Kasus Aktif'] = kelurahan['Dirawat'] + kelurahan['Self Isolation']
kelurahan['Tanggal'] = date
#kelurahan = kelurahan[kelurahan["ID_KEL"] != 'LUAR DKI JAKARTA']
#kelurahan = kelurahan[kelurahan["ID_KEL"] != 'PROSES UPDATE DATA'] 
kelurahan['ID_KEL'] = kelurahan['ID_KEL'].replace(['LUAR DKI JAKARTA', 'PROSES UPDATE DATA'],111111)

# Print downloaded data and date
print(judul_excel)
print(date)

# Location of old data that we want to append
destination_kecamatan = 'C:/Users/Farhan Achsani/Desktop/Kodingan/Scrape-Covid19-JKT/Covid19-JKT-2021-Kecamatan.csv'
destination_kelurahan = 'C:/Users/Farhan Achsani/Desktop/Kodingan/Scrape-Covid19-JKT/Covid19-JKT-2021-Kelurahan.csv'

#Read past data
past_kelurahan = pd.read_csv(destination_kelurahan)
past_kecamatan = pd.read_csv(destination_kecamatan)

# Append past data with new data
past_kelurahan = past_kelurahan.append(kelurahan)
past_kecamatan = past_kecamatan.append(kecamatan)

# Remove old and downloaded file
os.remove(destination)
os.remove(destination_kecamatan)
os.remove(destination_kelurahan)

# Export newest data on dataframe to CSV
# For iteration other than the first time
past_kecamatan.to_csv(destination_kecamatan,index=False)
past_kelurahan.to_csv(destination_kelurahan,index=False)