#!/usr/bin/env python
# coding: utf-8

# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Set the executable path and initialize Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres": hemispheres(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data
def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    
    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()
        news_title

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

### JPL Space Images Featured Image
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

### Mars Facts
def mars_facts():
    # add try/except for error handling
    try:
        # use 'read_html' to scrape the facts table
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # convert dataframe to HTML, add bootstrap
    return df.to_html(classes="table table-striped")

# D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles
def hemispheres(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)
    
    # create a list
    hemisphere_image_urls = []

    # Code to retrieve the image urls and titles for each hemisphere.
    # Parse the html with soup
    html = browser.html
    main_page_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the number of pictures to scan
        pics_count = len(main_page_soup.select("div.item"))

        # for loop over the link of each sample picture
        for i in range(pics_count):
            # Create an empty dict to hold the search results
            results = {}
            # Find link to picture and open it
            link_image = main_page_soup.select("div.description a")[i].get('href')
            browser.visit(f'https://marshemispheres.com/{link_image}')
        
            # Parse the new html page with soup
            html = browser.html
            sample_image_soup = soup(html, 'html.parser')
            # Get the full image link
            img_url = sample_image_soup.select_one("div.downloads ul li a").get('href')
            # Get the full image title
            img_title = sample_image_soup.select_one("h2.title").get_text()
            # Add extracts to the results dict
            results = {
                'img_url': img_url,
                'title': img_title}
        
            # Append results dict to hemisphere image urls list
            hemisphere_image_urls.append(results)
        
            # Return to main page
            browser.back()

    except BaseException:
        return None
    
    # Return the list that holds the dictionary of each image url and title
    return hemisphere_image_urls    

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())