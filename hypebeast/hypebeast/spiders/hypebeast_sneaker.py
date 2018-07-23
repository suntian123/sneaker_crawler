# -*- coding: utf-8 -*-
import scrapy
import os
from items import HypebeastItem
import datetime
import re


class HypebeastSneakerSpider(scrapy.Spider):
    name = 'hypebeast_sneaker'
    page_crawled = 0
    # allowed_domains = ['https://hypebeast.com/footwear']
    start_urls = ['https://hypebeast.com/footwear/page/']
    urls = [('hypebeast','https://hypebeast.com/footwear/page/'), ('snkr_news','https://sneakernews.com/page/')]
    last_ids = {'hype': '-1', 'snkr': '-1','where2b': '-1'}
    last_ids_reached = {'hype': 0, 'snkr': 0, 'where2b': 0}
    most_ids = {'hype': '-1', 'snkr': '-1', 'where2b': '-1'}
    _Debug = False

    def parse(self, response):
        self.last_ids = self.get_last_crawled()
        for (site, url) in self.urls:
            for page_num in range(4,0,-1):
                crawling_url = url + str(page_num)
                if(site == 'hypebeast'):
                    if not(self.last_ids_reached['hype']):
                        yield scrapy.Request(crawling_url, callback=self.parse_hype_pages)
                else:
                    if not (self.last_ids_reached['snkr']):
                        yield scrapy.Request(crawling_url, callback=self.parse_snkr_pages)



    def parse_hype_pages(self, response):
        if(self.last_ids_reached['hype']):
            return
        item = HypebeastItem()
        selector = scrapy.Selector(response)
        articles = selector.xpath('//div[@class="post-box-content-container"]') ##找到每篇文章的div#
        for article in articles:

            title_div = article.xpath('div[@class="post-box-content-title"]')
            artical_mata = article.xpath('div[@class="post-box-content-meta"]')

            artical_url = title_div.xpath('a/@href').extract()[0]

            if str(artical_url) == self.last_ids['hype'].strip('\n'):
                self.last_ids_reached['hype'] = 1
                return

            if self.most_ids['hype'] == '-1':
                self.most_ids['hype'] = artical_url
            title_text = title_div.xpath('a/@title').extract()[0]

            artical_mata = artical_mata.xpath('div[@class="post-box-content-meta-time-info"]')[0]
            datetime = artical_mata.xpath('span[@class="time"]/time/text()').extract()[0]
            views = artical_mata.xpath('div[@class="post-box-stats"]/hype-count/span[@class="hype-count"]/text()').extract()[0]
            views = views.replace("\n", "")
            views = views.replace(" ", "")
            views = views.replace(",", "")
            views = views.strip('Hypes')
            views = int(views)

            self.page_crawled += 1

            item['url'] = artical_url
            item['title'] = title_text
            item['views'] = views
            item['time'] = self.convert_hype_time(datetime)

            yield item

    def parse_snkr_pages(self, response):
        if(self.last_ids_reached['snkr']):
            return
        item = HypebeastItem()
        selector = scrapy.Selector(response)
        articles = selector.xpath('//div[contains(@class, "-post-box")]')
        title_div = articles.xpath('//div[contains(@class, "post-content")]')

        post_box = title_div[0]
        big_artical_url = post_box.xpath('//h2/a/@href').extract()
        big_artical_tital = post_box.xpath('//h2/a/text()').extract()
        article_url = big_artical_url + post_box.xpath('//h4/a/@href').extract()
        title_text = big_artical_tital + post_box.xpath('//h4/a/text()').extract()

        for index in range(len(article_url)):
            if article_url[index] == self.last_ids['snkr'].strip('\n'):
                self.last_ids_reached['snkr'] = 1
                return
            item['url'] = article_url[index]
            time = article_url[index][24:34]
            item['time'] = time
            if(self.is_today(time) and self.most_ids['snkr'] == '-1'):
                self.most_ids['snkr'] = article_url[index]
                self.write_last_crawled(self.most_ids)
            item['title'] = title_text[index]
            yield item

            self.page_crawled += 1

    def get_last_crawled(self):
        last_doc = open("last_doc.txt",'r')
        result = {'hype': '', 'snkr': '', 'where2b': ''}

        if(os.stat('last_doc.txt').st_size==0):
            last_doc.close()
            return result
        for line in last_doc:
            id_entry = line.split(',')
            if id_entry[0] == 'where2b':
                result['where2b'] = id_entry[-1]
            elif id_entry[0] == 'snkr':
                result['snkr'] = id_entry[-1]
            elif id_entry[0] == 'hype':
                result['hype'] = id_entry[-1]

        last_doc.close()
        return result

    def write_last_crawled(self, last_crawled):
        last_doc = open("last_doc.txt",'w')
        for site,url in last_crawled.items():
            last_doc.write('{},{}\n'.format(site,url))
        last_doc.close()

    def is_today(self,date):

        '''
        Check if the input date is the current date
        :param date: string
        :return: bool
        '''

        if(datetime.datetime.now().strftime("%Y/%m/%d") == date):
            return True
        else:
            return False

    def convert_hype_time(self,text_time):
        result = ''
        if("ago" in text_time):
            reobject = re.match(r'^(\d+) ([\w]+) ago', text_time)
            if('Hr' in reobject.group(2) or 'Min' in reobject.group(2)):
                result = datetime.datetime.now().strftime("%Y/%m/%d")
            if ('day' in reobject.group(2)):
                time_obj = datetime.datetime.today() - datetime.timedelta(days=int(reobject.group(1)))
                result = time_obj.strftime("%Y/%m/%d")
        else:
            time_obj = datetime.datetime.strptime(text_time, '%b %d, %Y')
            result = time_obj.strftime("%Y/%m/%d")
        return result




