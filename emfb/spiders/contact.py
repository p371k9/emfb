import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from html import unescape
import re,csv
from scrapy.utils.project import get_project_settings


#https://stackoverflow.com/questions/56995150/how-to-use-meta-in-scrapy-rule
def my_request_processor(request, response):
    request.meta['id'] = response.meta['id']
    return request

class ContactSpider(CrawlSpider):
    name = 'contact'
    allowed_domains = []    #['danubiushotels.com']
    start_urls = ['https://www.danubiushotels.com']
    custom_settings = {
        'ITEM_PIPELINES': {
            'emfb.pipelines.DuplicatesPipeline': 300,
        },
        'DOWNLOAD_DELAY': 3,
    }

    def __init__(self, csv=False, url=False, *args, **kwargs):   
        settings=get_project_settings()
        
        self.rules = (
            Rule(
                LinkExtractor(allow=settings.get('LEA')), # self.settings.get('LEA')
                process_request=my_request_processor,
                callback='parse_item', follow=True
            ),
        )  
        super(ContactSpider, self).__init__(*args, **kwargs)         
        self.url = url
        self.csv = csv
        
    def start_requests(self):
        if self.csv:
            id = self.settings.get('ID')
            with open(self.csv) as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:
                    if len(row["website"]) == 0:
                        self.logger.info('No website specified, so skipped (ID): %s' % row[id])                    
                        continue            
                    yield scrapy.Request(url=row["website"], meta={'id': row[id]})                            
        elif self.url:
            yield scrapy.Request(self.url, meta={'id': 1})
        else:
            yield scrapy.Request(self.start_urls[0], meta={'id': 1})

    def parse_item(self, response):
        item = {}
        item['id'] = response.meta['id']
        source1 = unescape(response.text).replace('<em>', '').replace('%20', " ").replace('u003e', ' ')
        mails = re.findall(r'[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', source1)        
        email = ''; more = ''
        szamlalo = 0
        for m in list(set(mails)):
            if szamlalo == 0:
                email = m
            else:
                more += m + " " 
            szamlalo += 1            
        item['email'] = email
        item['more'] = more     # more emails
        item['facebook'] = response.xpath("//a/@href[contains(.,'facebook.com')]").extract_first()
        if szamlalo or item['facebook']:
            return item
