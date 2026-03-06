from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from iproperty.spiders.house import HouseSpider, HouseSpiderExp
from configparser import ConfigParser 
from datetime import datetime
import pandas as pd
import folium
import re
import os

global timestamp
timestamp = datetime.today().date().isoformat().replace('-','')

def facilities(x):
	try:
		return x.replace('Bedroom(s)','Room').replace('Bathroom(s)','Bath').replace('Parking Bay(s)','Park')
	except:
		pass

def add_frame(index,name,price,size,facilities,link,**kwargs):
	html="""
<pre>
{0}
Name      : {1}
Price     : {2}
Amenities : {3}
sq. ft    : {4}
link      : {5}
</pre>
	"""
	return folium.IFrame(html= html.format(index+1,name,price,facilities,size,link), width=400, height=100)

def plot_map(df,house_conf):

	def getHTML(house_conf):
		global timestamp
		html_name = '{0}/{1}_{2}'.format(house_conf['Map']['folder'],\
										  house_conf['Map']['filename'],\
										  timestamp)
		lat_lon = house_conf['MyHouse'] if 'MyHouse' in house_conf.keys() else None
		return html_name, lat_lon

	html_name, lat_lon = getHTML(house_conf)

	color_group = {'High':'red','Low':'blue'}

	m = folium.Map(location=[3.139, 101.6869], zoom_start = 10)

	for row in df.to_dict(orient='records'):
		iframe = add_frame(**row)
		popup = folium.Popup(iframe, max_width=2650)
		folium.Marker([row['lat'], row['lon']], popup=popup, icon=folium.Icon(color=color_group[row['prize_range']])).add_to(m)

	if lat_lon: folium.Marker([float(lat_lon['lat']),float(lat_lon['lng'])],\
								popup='MyHome', icon=folium.Icon(color='green')).add_to(m)
	m.save('{}.html'.format(html_name))

def process_result():
	global timestamp
	df1 = pd.read_csv('data/house_cheap.csv')
	df2 = pd.read_csv('data/house_exp.csv')
	os.rename('data/house_cheap.csv','data/house_cheap_{}.csv'.format(timestamp))
	os.rename('data/house_exp.csv','data/house_exp_{}.csv'.format(timestamp))
	df = df1.append(df2, ignore_index=True)
	df['facilities'] = df['amenities'].map(facilities)
	df = df[df['lat'].notnull()]
	return df.reset_index(drop=True).reset_index()

def get_conf(config_path):
	house_conf = ConfigParser()
	house_conf.read(config_path)
	return house_conf

def crawling(house_conf):
	process = CrawlerProcess(get_project_settings())
	process.crawl(HouseSpider,**dict(house_conf['Low']))
	process.crawl(HouseSpiderExp,**dict(house_conf['High']))
	process.start()

def process_plot(house_conf):
	df = process_result()
	plot_map(df,house_conf)

def crawl_plot(config_path):
	house_conf = get_conf(config_path)
	crawling(house_conf)
	process_plot(house_conf)

############################################################################################################
if __name__ == '__main__':
	crawl_plot('house_conf.ini')
