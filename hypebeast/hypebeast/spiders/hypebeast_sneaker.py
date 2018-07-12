# -*- coding: utf-8 -*-
import scrapy
import os
from items import HypebeastItem

class HypebeastSneakerSpider(scrapy.Spider):

    name = 'hypebeast_sneaker'
    page_crawled = 0
    #allowed_domains = ['https://hypebeast.com/footwear']
    start_urls = ['https://hypebeast.com/footwear/page/']
    urls = [('hypebeast','https://hypebeast.com/footwear/page/'), ('snkr_news','https://sneakernews.com/page/')]
    last_ids = {'hype': '-1', 'snkr':'-1','where2b':'-1'}
    last_ids_reached = {'hype': 0, 'snkr': 0, 'where2b': 0}
    most_ids = {'hype': '-1', 'snkr': '-1', 'where2b': '-1'}
    _Debug = True

    def parse(self, response):
        self.last_ids = self.get_last_crawled()
        for (site, url) in self.urls:
            for page_num in range(1,5,1):
                crawling_url = url + str(page_num)
                if(site == 'hypebeast'):
                    if not(self.last_ids_reached['hype']):
                        yield scrapy.Request(crawling_url, callback=self.parse_hype_pages)
                #else:
                #    pass
                #    yield scrapy.Request(crawling_url, callback=self.parse_snkr_pages)




    def parse_hype_pages(self, response):
        if(self.last_ids_reached['hype']):
            print('\n===============================Last Reached Should Stop==================================\n')
            return
        item = HypebeastItem()
        selector = scrapy.Selector(response)
        articals = selector.xpath('//div[@class="post-box-content-container"]') ##找到每篇文章的div#
        for artical in articals:

            title_div = artical.xpath('div[@class="post-box-content-title"]')
            artical_mata = artical.xpath('div[@class="post-box-content-meta"]')

            artical_url = title_div.xpath('a/@href').extract()[0]

            if (self._Debug):
                print('========================Comparing URLS======================')
                print('{}\n::VS::\n{}'.format(artical_url,self.last_ids['hype'].strip('\n')))

            if str(artical_url) == self.last_ids['hype'].strip('\n'):
                self.last_ids_reached['hype'] = 1
                if (self._Debug):
                    print('\n=========================================Should Stop==================================\n')
                    print("Total Crawled" + str(self.page_crawled) + '\n')
                return

            if self.most_ids['hype'] == '-1':
                self.most_ids['hype'] = artical_url
                self.write_last_crawled('hype',artical_url)
            title_text = title_div.xpath('a/@title').extract()[0]

            artical_mata = artical_mata.xpath('div[@class="post-box-content-meta-time-info"]')[0]
            datetime = artical_mata.xpath('span[@class="time"]/time').extract()[0]
            views = artical_mata.xpath('div[@class="post-box-stats"]/hype-count/span[@class="hype-count"]/text()').extract()[0]
            views = views.replace("\n", "")
            views = views.replace(" ", "")
            views = views.replace(",", "")
            views = views.strip('Hypes')
            views = int(views)

            self.page_crawled += 1
            if(self._Debug):                                     #####Debug
                print('\n===============================================Title==================================\n')
                print('URL:'+artical_url+'\n')
                print('Title:' + title_text + '\n')
                # print("ID:"+str(post_id))
                print(title_div)
                # print(artical_mata)
                print("Time:"+datetime+'\n')
                print('Views:' + str(views) + '\n')
                print("Total Crawled" + str(self.page_crawled)+'\n')



            item['url'] = artical_url
            item['title'] = title_text
            item['views'] = views
            item['time'] = datetime

            yield item

    def parse_snkr_pages(self, response):
        item = HypebeastItem()
        selector = scrapy.Selector(response)
        articals = selector.xpath('//div[@class="post-box-content-container"]') ##正则表达式找到每篇文章的div#
        for artical in articals:
            # post_id = artical.xpath('@id').extract()[0]
            # post_id = int(post_id.strip("post-"))
            title_div = artical.xpath('div[@class="post-box-content-title"]')
            artical_mata = artical.xpath('div[@class="post-box-content-meta"]')

            artical_url = title_div.xpath('a/@href').extract()[0]
            title_text = title_div.xpath('a/@title').extract()[0]
            # print('URL:'+artical_url+'\n')
            # print('Title:' + title_text + '\n')
            artical_mata = artical_mata.xpath('div[@class="post-box-content-meta-time-info"]')[0]
            datetime = artical_mata.xpath('span[@class="time"]/time').extract()[0]
            views = artical_mata.xpath('div[@class="post-box-stats"]/hype-count/span[@class="hype-count"]/text()').extract()[0]
            views = views.replace("\n","")
            views = views.replace(" ", "")
            views = views.replace(",", "")
            views = views.strip('Hypes')
            views = int(views)


            self.page_crawled += 1;
            if(self._Debug):
                print('\n===============================================Title==================================\n')
                #print("ID:"+str(post_id))
                print(title_div)
                #print(artical_mata)
                print("Time:"+datetime+'\n')
                print('Views:' + str(views) + '\n')
                print("Total Crawled" + str(self.page_crawled)+'\n')



            item['url'] = artical_url
            item['title'] = title_text
            item['views'] = views
            item['time'] = datetime

            yield item

    def get_last_crawled(self):
        last_doc = open("last_doc.txt",'r')
        result = {'hype':'', 'snkr':'','where2b':''}
        if(self._Debug):
            print('======reading last_doc=====\n')
        if(os.stat('last_doc.txt').st_size==0):
            if (self._Debug):
                print('Last doc is Empty!\n')
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
        if (self._Debug):
            print('Got Last Doc:\nwhere2buy:{}\nsnkr:{}\nhype:{}'.format(result['where2b'],result['snkr'],result['hype']))
            print('===========Finishing==========\n')
        last_doc.close()
        return result

    def write_last_crawled(self,site,url):
        last_doc = open("last_doc.txt",'w')
        if(self._Debug):
            print('======Writing last_doc=====\n')
        last_doc.write('{},{}\n'.format(site,url))
        if (self._Debug):
            print('Got Last Doc:\n {},{}'.format(site,url))
            print('===========Finishing==========\n')
        last_doc.close()









