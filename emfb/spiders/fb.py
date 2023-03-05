import scrapy
import uncurl, re, csv
from html import unescape

from scrapy.shell import inspect_response

class FbSpider(scrapy.Spider):
    name = 'fb'
    allowed_domains = ['facebook.com']
    start_urls = ['https://hu-hu.facebook.com/amiidonk/about']
    
    def __init__(self, csv=False, url=False, *args, **kwargs):   
        super(FbSpider, self).__init__(*args, **kwargs)         
        self.url = url
        self.csv = csv
    
    def start_requests(self):
        cu = self.settings.get('CU')
        cu = cu.replace('gzip, deflate, br', 'deflate')
        uc = uncurl.parse_context(cu)
        if self.csv:
            with open(self.csv) as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                for row in csv_reader:
                    if len(row["facebook"]) == 0:
                        self.logger.info('No Facebook site specified, so skipped (ID): %s' % row['id'])                    
                        continue            
                    yield scrapy.Request(
                        url = row['facebook'],
                        headers=uc.headers, 
                        cookies=uc.cookies,
                        meta={'id': row['id']}
                    )                                
        elif self.url:
            yield scrapy.Request(
                url = self.url,
                headers=uc.headers, 
                cookies=uc.cookies,
                meta={'id': 1}
            )                                
        else:
            yield scrapy.Request(
                url = self.start_urls[0],
                headers=uc.headers, 
                cookies=uc.cookies,
                meta={'id': 1}
            )                        

    def parse(self, response):
        print('Title: '+response.xpath('//title/text()').get())
        hasteJs = ""
        for haste in response.xpath('//script[contains(text(), "HasteSupportData")]' ):
            hasteJs += haste.get()
        source1 = unescape(hasteJs.replace("\\u0040", "@").replace('<em>', ''))
        mails = re.findall(r'[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}', source1)
        l = len(mails)        
        if l:
            yield  {
                'id': response.meta['id'],
                'email': mails[l-1]
            }
        
        #inspect_response(response, self)        
        #pass
