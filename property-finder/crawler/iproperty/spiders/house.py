# -*- coding: utf-8 -*-
import scrapy
from iproperty.items import IpropertyItem
from scrapy.http import Request
import re
class HouseSpider(scrapy.Spider):
	name = "house_cheap"
	allowed_domains = ["www.iproperty.com.my"]
	xpath_dict = {'main_list' :'//li[contains(@class,"listing")]',
				'check_price':'.//div[@class="price-margin"]/h2/text()',
				'name'		 :'.//div[@class="left"]/a/h2/text()',
				'amenities'	 :'.//div[@class="room-amenities"]//span[@class="no"]/@title',
				'link'		 :'.//div[contains(@class,"headers")]/div[@class="left"]/a/@href',
				'address'	 :'//div[@class="building-info-one"]/h2/text()',
				'prize_size' :'//div[@class="building-info-two"]/h2/text()',
				'next_page'  :'//li[@class="button"]/a[contains(text(),"Next")]/@href',
				'tenure'	 :'//ul[@class="infos"]/li[contains(text(),"Tenure")]/text()'}

	def __init__(self,state = 'pulau-pinang', min_price = None, max_price='280',):
		self.start_urls = ['https://www.iproperty.com.my/buy/{0}/?xp={1},000&ht=F'.\
										format(s,max_price.replace('k','')) for s in state.split(',')]

	def parse(self, response):
		xpath_dict = self.xpath_dict
		page = response.meta.get('pg') or 1

		house_list = response.xpath(xpath_dict['main_list'])

		for h in house_list:
			h_item = IpropertyItem()
			check_price			= h.xpath(xpath_dict['check_price']).extract_first()
			h_item['name'] 		= h.xpath(xpath_dict['name']).extract_first()
			h_item['amenities'] = h.xpath(xpath_dict['amenities']).extract()
			h_item['link'] 		= response.urljoin(h.xpath(xpath_dict['link']).extract_first())

			if check_price == 'Call for price' or (check_price and len(check_price)<=8):
				pass
			else:
				yield Request(h_item['link'], callback=self.details, meta={'item':h_item})

		next_page = response.xpath(xpath_dict['next_page']).extract_first()
		if next_page and page<50:
			yield Request(response.urljoin(next_page), callback = self.parse, meta = {'pg':page+1})

	def details(self, response):
		xpath_dict = self.xpath_dict
		h_item = response.meta['item']

		h_item['price'] 	 = response.xpath(xpath_dict['prize_size']).extract_first()
		h_item['address']	 = response.xpath(xpath_dict['address']).extract_first()
		h_item['tenure']	 = response.xpath(xpath_dict['tenure']).extract_first().replace('Tenure : ','').replace('\xa0','')
		size 				 = response.xpath(xpath_dict['prize_size']).extract()[-1]
		h_item['size'] = re.search('(.+)sq. ft.',size).group()

		for s in response.xpath('//script/text()').extract():
			if 'Google_Tag_Manager' in s:
				h_item['lat'] = re.search('mapLat: "(.+)"',s).group(1)
				h_item['lon'] = re.search('mapLon: "(.+)"',s).group(1)
				break

		return h_item


class HouseSpiderExp(HouseSpider):

	name = 'house_exp'

	def __init__(self,state = 'pulau-pinang', min_price = '280', max_price = '350'):
		self.start_urls = ['https://www.iproperty.com.my/buy/{0}/?mp={1},000&xp={2},000&ht=F'\
							.format(s,min_price.replace('k',''),max_price.replace('k','')) for s in state.split(',')]