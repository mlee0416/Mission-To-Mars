# Dependencies
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pandas as pd


def init_browser():
    """Create browser session from splinter"""
    # Chromedriver path
    executable_path = {"executable_path": "webdriver/chromedriver.exe"}

    return Browser("chrome", **executable_path, headless=True)


def mars_news():
    """Extract latest Mars news title and description"""
    with init_browser() as browser:

        # Mars exploration program url
        news_url = "https://mars.nasa.gov/news/"
        browser.visit(news_url)

        # Maximize window
        browser.driver.maximize_window()

        # Latest news container
        news_container = browser.find_by_css('div[class="list_text"]').first

        # Grab news title
        news_title = news_container.find_by_css("a").text.strip()

        # Grab news title description
        news_p = news_container.find_by_css('div[class="article_teaser_body"]').text.strip()

    return news_title, news_p


def feat_img():
    """Extract featured image from JPL Mars Space Images"""
    # Create browser instance with context manager
    with init_browser() as browser:

        # Visit JPL Mars space images url
        mars_imgs_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
        browser.visit(mars_imgs_url)

        # Maximize window
        browser.driver.maximize_window()

        # Latest image container xpath and click
        browser.find_by_xpath("//*[@id=\"page\"]/section[3]/div/ul/li[1]/a/div").click()

        # Retrieve featured image url
        featured_img_url = browser.find_by_css('img[class="fancybox-image"]')["src"]

    return featured_img_url


def mars_weather():
    """Extract Mars weather from twitter account"""
    # Mars weather twitter account url
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"

    # Retrieve page with the requests module
    response = requests.get(mars_weather_url)

    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')

    # Retrieve all tweets
    results = soup.find_all(
        "p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text")

    # Grab latest Mars weather
    for result in results:

        # Grab tweet
        mars_weather_tweet = result.get_text().strip()

        # Only get the first tweet that has Mars weather
        if mars_weather_tweet[:3] == "Sol":
            break

    return mars_weather_tweet


def mars_facts():
    """Extract Mars facts table from Mars facts webpage"""
    # Mars facts url
    mars_facts_url = "https://space-facts.com/mars/"

    # Read html to get tables
    tables = pd.read_html(mars_facts_url)

    # Grab mars facts table and create df
    df = tables[0]
    df.columns = ["Description", "Value"]

    # Set description as index
    df = df.set_index(["Description"])

    # Convert to html string
    html_table = df.to_html(classes="table table-bordered table-sm table-hover")

    # Strip newlines
    html_table = html_table.replace('\n', '')

    return html_table


def mars_hemispheres():
    """Extract Mars hemispheres images from the USGS Astrogeology site"""
    # List to hold hemisphere titles and urls
    hemisphere_image_urls = []

    # Creat browser instance with context manager
    with init_browser() as browser:

        # Visit Mars hemispheres url
        mars_hemis_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        browser.visit(mars_hemis_url)

        # Maximize window
        browser.driver.maximize_window()

        # Find all image thumbnail imgs for loop
        thumbnails = len(browser.find_by_css('img[class="thumb"]'))

        for i in range(thumbnails):

            # Click image thumbnail
            browser.find_by_css('img[class="thumb"]')[i].click()

            # Dictionary to hold image title and url
            hemis = {}

            # Retrieve image title and add to dicitonary
            title = browser.find_by_css('h2[class="title"]').first.text.strip()
            hemis["title"] = title

            # Retrieve full resolution image url and add to dicitonary
            img_url = browser.find_by_css('img[class="wide-image"]')["src"]
            hemis["image_url"] = img_url

            # Append dictionary to hemis image urls list
            hemisphere_image_urls.append(hemis)

            # Go back to mars hemis url
            browser.back()

    return hemisphere_image_urls


def scrape():
    """Master function to scrape all Mars data"""
    # Create mars_data dict to insert into mongo
    mars_data = {}

    # Call mars_news function to grab latest news title and description
    news_title, news_p = mars_news()

    # Call feat_img function to grab Mars featured image url
    featured_img_url = feat_img()

    # Call mars_weather to grab latest Mars weather tweet
    mars_weather_tweet = mars_weather()

    # Call mars_facts function to grab html table
    html_table = mars_facts()

    # Call mars_hemispheres function to grab Mars hemisphere dictionary
    hemisphere_image_urls = mars_hemispheres()

    # Add all Mars data into mars_data dict
    mars_data["news_title"] = news_title
    mars_data["news_p"] = news_p
    mars_data["featured_img_url"] = featured_img_url
    mars_data["mars_weather_tweet"] = mars_weather_tweet
    mars_data["html_table"] = html_table
    mars_data["hemisphere_image_urls"] = hemisphere_image_urls

    return mars_data


if __name__ == '__main__':
    scrape()