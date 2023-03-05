# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EmfbPipeline:
    def process_item(self, item, spider):
        return item
        
from scrapy.exceptions import DropItem

class DuplicatesPipeline:

    def __init__(self):
        self.id_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['id'] in self.id_seen:
            raise DropItem(f"Duplicate item found! id = {item['id']!r}")
        else:
            self.id_seen.add(adapter['id'])
            return item           
