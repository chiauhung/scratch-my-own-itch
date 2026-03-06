# House Property Finder (2017)

Built this to help me buy my current house in KL. Scraped property listings from iproperty.com.my, filtered by budget and area, and plotted them on an interactive map so I could compare options visually.

It worked. I bought the house.

> **Note:** This code is not maintained. The crawler will no longer run — iproperty.com.my has changed significantly since 2017. The Flask app and the crawled data from back then are preserved as-is.

---

## What It Did

1. **Crawler** — Scrapy spider crawled iproperty.com.my for listings matching your budget and area (configured via `house_conf.ini`). Two spiders ran concurrently for low and high budget ranges. Results saved to CSV.

2. **Web App** — Flask app read the CSVs and plotted listings on a Folium map with price, size, location, and a link back to the listing page.

## Structure

```
crawler/    — Scrapy project (spider, pipeline, settings, config)
webapp/     — Flask app (map visualisation, table view)
data/       — Actual crawled CSVs from August 2017
```

## Stack

`Python` · `Scrapy` · `Flask` · `Folium` · `Pandas` · `ConfigParser`
