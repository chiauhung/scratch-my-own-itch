from flaskapp import app
from flask import render_template, request, url_for, redirect, session
from datetime import datetime
import subprocess
import sys
import os

import pandas as pd
import requests
import folium
import json
import re

@app.before_first_request
def set_work_dir():
	global crawldir
	global flaskdir
	flaskdir = os.getcwd()
	crawldir = flaskdir+'\\iproperty'

@app.route('/result', methods=['GET','POST'])
def result():
	min_price = request.args.get('min_price')
	max_price = request.args.get('max_price')

	if request.method == 'POST':
		if request.form['displayType']=='OK':
			threshold = request.form['threshold']
			return redirect(url_for('map_plot', threshold=threshold))
		else:
			return redirect(url_for('table'))
	return render_template('displayType.html', min_price=int(min_price), max_price = int(max_price))

@app.route('/table')
def table():
	fname = session.get('data_filename')
	data = retrieve_data(fname)
	cols = ['name', 'tenure', 'price', 'size','amenities', 'address', 'link']
	return render_template('table.html', resp_json=data, columns=cols)

@app.route('/map')
def map_plot():
	threshold = request.args.get('threshold')	
	fname = session.get('data_filename')
	data = retrieve_data(fname)
	df = process_data(data,threshold)	
	plot_map(df)
	return render_template("map/house_prop.html")

@app.route('/', methods=['GET','POST'])
def set_up_crawl():
	print(os.getcwd())
	if request.method == "POST":
		if request.form['submit'] == 'View History':
			return redirect(url_for('result'))
		else:
			result = request.form
			state = result.get('state') or 'kuala-lumpur'
			min_price = result.get('min_price') or '280'
			max_price = result.get('max_price') or '350'
			user = result.get('user') or 'Unknown'
			fname = 'item2'
			session['data_filename'] = fname
			# crawl_data(state,min_price,max_price,fname)
			return redirect(url_for('result', min_price=int(min_price)*1000, max_price=int(max_price)*1000))


	states=['Johor',
			'Kedah',
			'Kelantan',
			'Labuan',
			'Kuala Lumpur',
			'Melaka',
			'Negeri Sembilan',
			'Pahang',
			'Perak',
			'Pulau Pinang',
			'Putrajaya',
			'Sabah',
			'Sarawak',
			'Selangor',
			'Terengganu']
	state_dict = {i.lower().replace(' ','-'):i for i in states}
	tenure =['Freehold','Leasehold','Any']

	return render_template('form.html', states=state_dict, tenure=tenure)
###################################################################################################

def change_work_space(t):
	global crawldir
	global flaskdir
	if t == 'flask':
		os.chdir(flaskdir)
	elif t == 'crawl':
		os.chdir(crawldir)

def crawl_data(state,min_price,max_price,fname,crawl_method='subprocess'):
	if crawl_method == 'rt':
		scrapyrt_url = 'http://localhost:9080/crawl.json?spider_name=house_exp&url='
		req_url = 'https://www.iproperty.com.my/buy/{0}/?mp={1},000&xp={2},000&ht=F'.format(state,min_price,max_price)
		resp = requests.get(scrapyrt_url+req_url)
		json.dump(json.loads(resp.text)['items'],open('data/{}.js'.format(fname),'w'))	
	elif crawl_method == 'subprocess':
		change_work_space('crawl')
		subprocess.call(['scrapy','crawl','houseprop','-a','state={}'.format(state),\
							'-a','min_price={}'.format(min_price),\
							'-a','max_price={}'.format(max_price),\
							'-o','data/{}.json'.format(fname)])

def retrieve_data(filename):
	change_work_space('crawl')
	with open('data/{}.json'.format(filename),'r') as data_file:    
		data = json.load(data_file)
	return data

def process_data(data, threshold):
	def facilities(x):
		try:
			return x.replace('Bedroom(s)','Room').replace('Bathroom(s)','Bath').replace('Parking Bay(s)','Park')
		except:
			pass
	print(threshold)
	threshold = int(threshold)
	df = pd.DataFrame.from_records(data)
	df['facilities'] = df['amenities'].map(facilities)
	df = df[df['lat'].notnull()]
	df['price_num'] = df['price'].map(lambda x: int(x.replace('RM ','').replace(',','')))
	df['prize_range'] = df['price_num'].map(lambda x: 'High' if x>threshold else 'Low')
	df = df.reset_index(drop=True).reset_index()
	return df

def plot_map(df,house_conf=None):
	def add_frame(index,name,price,size,facilities,link,**kwargs):
		html="""
<pre>
<a target="_blank" href="{5}">{0}</a>
Name      : {1}
Price     : {2}
Amenities : {3}
sq. ft    : {4}    
</pre>
		    """
		return folium.IFrame(html= html.format(index+1,name,price,facilities,size,link), width=400, height=100)

	# def getHTML(house_conf=None):
	# 	global timestamp
	# 	html_name = '{0}/{1}_{2}'.format(house_conf['Map']['folder'],\
	# 									  house_conf['Map']['filename'],\
	# 									  timestamp)
	# 	lat_lon = house_conf['MyHouse'] if 'MyHouse' in house_conf.keys() else None
	# 	return html_name, lat_lon

	# html_name, lat_lon = getHTML(house_conf)
	html_name = 'house_prop'
	lat_lon = None

	color_group = {'High':'red','Low':'blue'}


	m = folium.Map(location=[3.139, 101.6869], zoom_start = 10)

	for row in df.to_dict(orient='records'):
		iframe = add_frame(**row)
		popup = folium.Popup(iframe, max_width=2650)
		folium.Marker([row['lat'], row['lon']], popup=popup, icon=folium.Icon(color=color_group[row['prize_range']])).add_to(m)

	if lat_lon: folium.Marker([float(lat_lon['lat']),float(lat_lon['lng'])],\
								popup='MyHome', icon=folium.Icon(color='green')).add_to(m)
	change_work_space('flask')
	m.save('flaskapp/templates/map/{}.html'.format(html_name))