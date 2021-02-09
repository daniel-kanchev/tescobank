import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tescobank.items import Article


class TescoSpider(scrapy.Spider):
    name = 'tesco'
    start_urls = ['https://bank.tescoplc.com/media/features-and-blogs/']

    def parse(self, response):
        links = response.xpath('//li[@class="listing__item"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="nav-pagination__item"][last()]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        author = response.xpath('//div[@class="author__bio"]/strong/text()').get()
        date = response.xpath('//p[@class="article-date"]/text()').get().strip()
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//main//div[@class="rte-wrapper"]//p/text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)

        return item.load_item()
