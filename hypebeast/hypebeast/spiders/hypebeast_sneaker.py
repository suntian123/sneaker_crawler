# -*- coding: utf-8 -*-
import scrapy
import os
from items import HypebeastItem
import datetime
import re
from sneakers import sneaker


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
                    pass
                    #if not(self.last_ids_reached['hype']):
                        #yield scrapy.Request(crawling_url, callback=self.parse_hype_pages)
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

        selector = scrapy.Selector(response)
        articles = selector.xpath('//div[contains(@class, "-post-box")]')
        title_div = articles.xpath('//div[contains(@class, "post-content")]')

        post_box = title_div[0]
        big_artical_url = post_box.xpath('//h2/a/@href').extract()
        article_url = big_artical_url + post_box.xpath('//h4/a/@href').extract()

        for url in article_url:
            if url == self.last_ids['snkr'].strip('\n'):
                self.last_ids_reached['snkr'] = 1
                return
            yield scrapy.Request(url, callback=self.process_snkr_page)

    def process_snkr_page(self, response):
        if str(response.url) == self.last_ids['hype'].strip('\n'):
            self.last_ids_reached['hype'] = 1
            return
        if (self.last_ids_reached['snkr']):
            return
        print("\n================================Getting SNKRS page:{}==========================\n".format(response.url))
        item = HypebeastItem()
        snkrs = ""
        time = response.url[24:34]
        if (self.is_today(time) and self.most_ids['snkr'] == '-1'):
            self.most_ids['snkr'] = response.url
            self.write_last_crawled(self.most_ids)
        selector = scrapy.Selector(response)
        title = selector.xpath('/html/body/div[1]/div[2]/div/div[1]/div[1]/h1/text()').extract_first()
        votes = selector.xpath('//div[@class = "vote-box"]/div[@class="post-ratings"]/span/i/text()').extract_first().strip(" ")
        votes = votes.strip("VOTES")
        print('-----------Titel = {}-----------\n'.format(title))
        print('-----------Votes = {}-----------\n'.format(votes))
        print('-----------Time = {}-----------\n'.format(time))
        release_divs = selector.xpath('//blockquote[@class = "releases"]/p')
        print('-----------Found {} Release Divs:{}\n'.format(len(release_divs), release_divs))
        for release_div in release_divs:
            snkr = sneaker()
            prize = "".join(release_div.xpath('text()').extract()).strip("\n$").strip(' ')
            print('-----------Prize = {}-----------\n'.format(prize))
            info = release_div.xpath('strong')
            if len(info) > 1:
                date = info[1].xpath('text()').extract()[0].strip("Release Date: ")
            else:
                date = "unknown"
            name = info[0].xpath('text()').extract()[0]
            info = release_div.xpath('//small/text()').extract()
            color = '-'
            code = '-'
            while(len(info)>0):
                if("Color: "in info[0]):
                    color = info[0].strip("Color: ")
                elif("Style Code: " in info[0]):
                    code = info[0].strip("Style Code: ")
                del(info[0])
            snkr.name(name)
            snkr.color(color)
            snkr.prize(prize)
            snkr.release(date)
            snkr.id(code)
            print(str(snkr))

            snkrs += snkr.snkr_name
            snkrs += ", "

        item['url'] = response.url
        item['time'] = time
        item['votes'] = votes
        item['title'] = title
        item['sneaker'] = str(snkrs)

        self.page_crawled += 1
        yield item

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

    def is_today(self, date):

        '''
        Check if the input date is the current date
        :param date: string e.g.: 2018/07/23
        :return: bool
        '''

        if(datetime.datetime.now().strftime("%Y/%m/%d") == date):
            return True
        else:
            return False

    def convert_hype_time(self, text_time):
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

    def get_inpage_sneaker(self, url):
        print("\n================================Getting Request From({})==========================\n".format(url))
        return scrapy.Request(url, callback=self.process_snkr_page)



