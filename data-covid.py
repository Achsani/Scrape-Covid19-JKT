from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime as DT
from requests_html import HTMLSession
from google_drive_downloader import GoogleDriveDownloader as gdd
import pandas as pd
import os


data = []
url = "https://riwayat-file-covid-19-dki-jakarta-jakartagis.hub.arcgis.com/"

session = HTMLSession()
r = session.get(url)
r.html.render(sleep=5)
res = BeautifulSoup(r.html.raw_html, "html.parser")

links = res.find_all("a")

for link in res.find_all('a', href=True):
    data.append(link)


# Yg tanggal terbaru di nomor 7
link = data[7]['href']
id_file = link[32:65]
judul = data[7].get_text()


destination = './' + judul + ".xlsx"
gdd.download_file_from_google_drive(file_id=id_file, dest_path=destination)
judul_excel = judul + ".xlsx"


today = DT.date.today()
date = today - DT.timedelta(days=1)
str_date = str(date)


cols_kecamatan = [0, 2, 3, 26, 27, 28, 29, 30]

kecamatan = pd.read_excel(judul_excel, header = 0,sheet_name="data_kecamatan", usecols=cols_kecamatan)
kecamatan.rename(columns={'Meninggal.1': 'Meninggal'}, inplace=True)
kecamatan = kecamatan.iloc[1:]
kecamatan['Kasus Aktif'] = kecamatan['Dirawat'] + kecamatan['Self Isolation']
kecamatan['Tanggal'] = date

cols_kelurahan = [0, 2, 3, 4, 27, 28, 29, 30, 31]

kelurahan = pd.read_excel(judul_excel, header = 0, sheet_name="data", usecols=cols_kelurahan)
kelurahan.rename(columns={'Meninggal.1': 'Meninggal'}, inplace=True)
kelurahan = kelurahan.iloc[1:]
kelurahan['Kasus Aktif'] = kelurahan['Dirawat'] + kelurahan['Self Isolation']
kelurahan['Tanggal'] = date

# print(kelurahan.head())
# print(link)
# print(judul)
# print(date)

destination_kecamatan = './Covid19-JKT-Kecamatan.csv'
destination_kelurahan = './Covid19-JKT-Kelurahan.csv'

past_kelurahan = pd.read_csv(destination_kelurahan)
past_kecamatan = pd.read_csv(destination_kecamatan)

# print(past_kelurahan.head())

past_kelurahan = past_kelurahan.append(kelurahan)
past_kecamatan = past_kecamatan.append(kecamatan)


os.remove(destination)
os.remove(destination_kecamatan)
os.remove(destination_kelurahan)

past_kecamatan.to_csv(destination_kecamatan,index=False)
past_kelurahan.to_csv(destination_kelurahan,index=False)


