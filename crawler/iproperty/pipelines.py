# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter

class IpropertyPipeline(object):

    def open_spider(self,spider):
        self.file = open("data/%s.csv"%spider.name, 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        if spider.name == 'house_cheap':
            item['prize_range'] = 'Low'
        elif spider.name == 'house_exp':
            item['prize_range'] = 'High'
        self.exporter.export_item(item)
        return item
