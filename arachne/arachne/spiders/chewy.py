# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import pandas as pd
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from .. import items


class ChewySpider(CrawlSpider):
    name = 'chewy'
    allowed_domains = ['chewy.com']
    start_urls = [
        'https://www.chewy.com/b/wet-food-389/' # Wet Cat Food
    ]

    rules = (
        Rule(LinkExtractor(allow=r'.*s\?rh=c%.+&page=.*'), follow=True), # Go to next page
        Rule(LinkExtractor(allow=r'.*\/dp\/.*'), callback='parse_item', follow=False) # View each food page
    )

    def score_food(self, protein, fat, carbs, moisture):
        avg_protein = 45
        avg_fat = 20
        avg_carbs = 30
        dry_protein = (protein * (100 / (100 - moisture)))
        dry_fat = (fat * (100 / (100 - moisture)))
        dry_carbs = (carbs * (100 / (100 - moisture)))

        # Perfect score = 3
        return (((dry_protein - avg_protein) / avg_protein) + 
                ((avg_carbs - dry_carbs) / avg_carbs) + 
                ((avg_fat - abs(avg_fat - dry_fat)) / avg_fat))

    def parse_item(self, response):
        item = items.PetFood()
        title = response.css("#product-title > h1::text").extract_first().strip().rsplit(',', 2)
        serving_selector = response.css('.cw-btn--soft--active.selected > span::text').extract_first()

        numeric = r'\d*\.\d+|\d+'
        prot_r = re.compile('^.*Protein.*$', re.I)
        fat_r = re.compile('^.*fat.*$', re.I)
        mois_r = re.compile('^.*moisture.*$', re.I)

        item['name'] = title[0].strip()

        # SERVING
        if(serving_selector == None):
            # No selector for size, can be found in title
            item['weight'] = float(re.findall(numeric, title[1].strip())[0])
            item['cans'] = int(re.findall(numeric, title[2].strip())[0])
        else:
            serving = serving_selector.split(',')
            item['weight'] = float(re.findall(numeric, serving[0].strip())[0])
            item['cans'] = int(re.findall(numeric, serving[1].strip())[0])

        # NUTRITION
        nutrition = [tuple(row.css('td::text').extract()) for row in  response.css('#Nutritional-Info > section.cw-tabs__content--right > div > table > tbody > tr')]
        percentages = [(row[0], float(re.findall(numeric, row[1].strip())[0])) for row in nutrition]
        df = pd.DataFrame(percentages, columns = ['name', 'percent'])
        agg_pct = [tuple(x) for x in df.groupby('name').mean().reset_index().values]

        protein = [pct[1] for pct in agg_pct if prot_r.match(pct[0])][0]
        fat = [pct[1] for pct in agg_pct if fat_r.match(pct[0])][0]
        moisture = [pct[1] for pct in agg_pct if mois_r.match(pct[0])][0]

        carbs = 100
        for pct in agg_pct:
            carbs -= pct[1]
        carbs = max(carbs, 0)

        item['protein'] = protein
        item['fat'] = fat
        item['moisture'] = moisture
        item['carbs'] = carbs
        item['score'] = self.score_food(protein, fat, carbs, moisture)

        # ID
        item['price'] = float(response.css(".ga-eec__price::text").extract_first().strip()[1:])
        item['price_per_oz'] = item['price'] / (item['cans'] * item['weight'])
        item['url'] = response.url

        return item