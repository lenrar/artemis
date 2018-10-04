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

    pet = input("What type of pet do you have (cat/dog)? ").lower()
    budget = float(re.findall(numeric, input("What is your monthly budget in dollars? "))[0])
    consumption = float(re.findall(numeric, input("How many ounces of food does your %s eat a day? " % pet))[0])

    df = pd.read_csv(data_path)
    df = df[df['animal_type'].str.lower() == pet]
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
        cheapest = df.loc[df['monthly_cost'].idxmin()]['monthly_cost']
        print("There are no foods in your price range. The cheapest food for your %s is $ %.2f a month." % (pet, cheapest))

  
if __name__== "__main__":
    main()