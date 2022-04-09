#import splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
def scrape_all(): 
    #initiate headless driver for deployment
    executable_path={'executable_path':ChromeDriverManager().install()}
    browser=Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph=mars_news(browser)

    #run all scraping functions and store results in dictionary
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image":featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    #stop webdriver an return data
    browser.quit()
    return data


def mars_news(browser):
    #visit mars nasa news site
    url='https://redplanetscience.com'
    browser.visit(url)

    html=browser.html
    news_soup=soup(html, 'html.parser')

    try:
        slide_elem=news_soup.select_one('div.list_text')
        # use parent element to find first 'a' tag and save to 'news_title'
        news_title=slide_elem.find('div', class_='content_title').get_text()
        # use parent element to find paragraph text
        news_p=slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p

# ### featured images
def featured_image(browser):
    # visit URL
    url= 'https://spaceimages-mars.com'
    browser.visit(url)

    # find and click full image button
    full_image_elem=browser.find_by_tag('button')[1]
    full_image_elem.click()

    # parse the resulting html with soup
    html=browser.html
    img_soup=soup(html, 'html.parser')
    
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    # use the base url to create an absolute url
    img_url=f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    
    try:
        df=pd.read_html('https://galaxyfacts-mars.com')[0]
        
    except BaseException:
        return None

    df.columns=['description','Mars','Earth']
    df.set_index('description', inplace=True)

    return df.to_html()


def hemisphere_facts(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    hemisphere_image_urls = []

    for hemisphere in range(4):
        browser.links.find_by_partial_text('Hemisphere')[hemisphere].click()
    
    html=browser.html
    hemisphere_soup=soup(html, 'html.parser')
    
    title=hemisphere_soup.find('h2', class_='title').text
    img_url= hemisphere_soup.find('li').a.get('href')
    
    hemispheres={}
    hemispheres['img_url']=f'https://marshemispheres.com/{img_url}'
    hemispheres['title']=title
    hemisphere_image_urls.append(hemispheres)
    
    browser.back()

    return hemisphere_image_urls

if __name__=="__main__":
    # if running as script, print scraped data
    print(scrape_all())



