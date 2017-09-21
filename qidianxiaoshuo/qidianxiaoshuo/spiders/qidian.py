# -*- coding: utf-8 -*-
import scrapy
from qidianxiaoshuo.items import QidianxiaoshuoItem
from scrapy.http import Request


class QidianSpider(scrapy.Spider):
    name = "qidian"
    allowed_domains = ["qidian.org"]
    #我这里是下载起点玄幻类的完本小说, 所以通过for来创建每一个页面的url, 因为每一个只是page不同而已, 而page是根据全部的本数 / 页数而来

    start_urls = [
        "http://fin.qidian.com/?chanId=21&action=hidden&orderId=&page=1&style=1&pageSize=20&siteid=1&hiddenField=" + str(
            page) + "&month=-1&style=1&vip=-1" for page in range(1, 2)
    ]

    def parse(self, response):
        #获取每一个书的url
        bookurls = response.xpath('//div[@class="book-mid-info"]/h4/a//@href').extract()
        for bookurl in bookurls:
            #根据获取到的书本url跳转到每本书的页面
            yield Request('http:' + bookurl, self.parseBook, dont_filter=True)

    def parseBook(self, response):
        #获取免费阅读的url
        charterurls = response.xpath('//div[@class="book-info "]/p/a[@class="red-btn J-getJumpUrl "]/@href').extract()
        #每一本书都创建一个item
        item = QidianxiaoshuoItem()
        #通过免费阅读的url进入书的第一章
        for url in charterurls:
            yield Request(('http:'+ url),meta={'item':item},callback=self.parseCharter, dont_filter=True)

    def parseCharter(self,response):
        #获取小说名字
        names = response.xpath('//div[@class="act"]/text()').extract()
        item = response.meta['item']
        for name in names:
            names = item.get('bookName')
            if names == None:
                item['bookName'] = name
        #获取章节名
        biaoti = response.xpath('//h3[@class="j_chapterName"]/text()').extract()
        content = ''
        for bt in biaoti:
            content = content + bt + '\n'
        # 获取每一章的内容
        d = response.xpath('//div[@class="read-content j_readContent"]//p/text()').extract()
        for str in d:
            # 拼接章节名和内容
            content = content + str

        detail = item.get('detail')
        if None == detail:
            item['detail'] = content
        else:
            item['detail'] = detail + content
        if content == '':
            yield item


        # 获取下一章的内容
        chapters = response.xpath('//div[@class="chapter-control dib-wrap"]/a[@id="j_chapterNext"]//@href').extract()
        for chapter in chapters:
            # 组成新的url
            yield Request("http:" + chapter, meta={'item': item}, callback=self.parseCharter, dont_filter=True)
