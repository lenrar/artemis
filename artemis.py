import pandas as pd
import os
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from arachne.spiders.chewy import ChewySpider
from datetime import datetime
from scrapy.utils.project import get_project_settings

def crawl_chewy():
    print("Crawling chewy.com, this may take a few minutes...")
    process = CrawlerProcess(get_project_settings())
    process.crawl(ChewySpider)
    process.start()

def main():
    numeric = r'\d*\.\d+|\d+'
    data_path = 'chewy.csv'

    if(os.path.isfile(data_path)):
        modified_ts = os.path.getmtime(data_path)
        date = datetime.utcfromtimestamp(modified_ts).strftime('%Y-%m-%d %H:%M:%S')
        if 'y' in input("Chewy data was last crawled at %s UTC, would you like to re-crawl? " % date):
            os.remove(data_path)
            crawl_chewy()
    else:
        if 'y' in  input("Chewy data does not exist. Would you like to generate it? "):
            crawl_chewy()
        else:
            print("Can not proceed.")
            quit()

    df = pd.read_csv(data_path)

    pet = input("What type of pet do you have (cat/dog)? ").strip().lower()
    df = df[df['animal_type'].str.lower() == pet]

    food_type = input("What type of food are you looking for (dry/wet)? ").strip().lower()
    df = df[df['food_type'].str.contains(food_type, case=False)]

    name_filter = input("Provide a comma separated list of filters for the name or press enter for no name filtering. ").strip().lower()
    if(name_filter != ''):
        filters = [re.escape(f.strip()) for f in name_filter.split(',')]
        pattern = '|'.join(filters)
        df = df[df['name'].str.contains(pattern, case=False)]

    if(len(df) == 0):
        print('No %s food found for %ss containing \'%s\'.' % (food_type, pet, name_filter))
        quit()

    budget = float(re.findall(numeric, input("What is your monthly budget in dollars? "))[0])
    consumption = float(re.findall(numeric, input("How many ounces of food does your %s eat a day? " % pet))[0])
    df['monthly_cost'] = df['price_per_oz'] * consumption * 30


    affordable_food = df[df.monthly_cost <= budget]
    if(len(affordable_food) > 0):
        best_food =  affordable_food.loc[affordable_food['score'].idxmax()]
        print("The best food for your %s is:" % pet)
        print()
        print("Name:", best_food['name'])
        print("Monthly Cost: $ %.2f" % (best_food['monthly_cost']))
        print("URL:", best_food['url'])
    else:
        cheapest = df.loc[df['monthly_cost'].idxmin()]
        print("There are no foods in your price range. The cheapest %s food for your %s is:" % (food_type, pet))
        print()
        print("Name:", cheapest['name'])
        print("Monthly Cost: $ %.2f" % (cheapest['monthly_cost']))
        print("URL:", cheapest['url'])

  
if __name__== "__main__":
    main()