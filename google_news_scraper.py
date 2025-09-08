import feedparser
from newspaper import Article
import requests
from playwright.sync_api import sync_playwright
import json
from bs4 import BeautifulSoup
from summary_agent import summarize_article
from email_news import build_email_body, send_email
import argparse

#import nltk
#nltk.download('punkt_tab')

def extract_direct_article_url(google_news_url):
    try:
        # Step 1: Fetch the redirect/intermediate page
        resp = requests.get(google_news_url)
        if resp.status_code != 200:
            raise Exception("Failed to load page")

        # Step 2: Parse page and extract the data-p attribute
        soup = BeautifulSoup(resp.text, 'html.parser')
        c_wiz = soup.select_one('c-wiz[data-p]')
        if not c_wiz:
            raise Exception("data-p not found in page")

        raw_data = c_wiz.get('data-p')

        # Step 3: Fix the malformed JSON
        cleaned_data = raw_data.replace('%.@.', '["garturlreq",')
        obj = json.loads(cleaned_data)

        # Step 4: Prepare payload for internal Google endpoint
        f_req_payload = json.dumps([[['Fbv4je', json.dumps(obj[:-6] + obj[-2:]), 'null', 'generic']]])

        headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        }

        url = "https://news.google.com/_/DotsSplashUi/data/batchexecute"
        post_resp = requests.post(url, headers=headers, data={'f.req': f_req_payload})
        if post_resp.status_code != 200:
            raise Exception("Failed to get article from batch API")

        # Step 5: Extract real URL from the response
        cleaned = post_resp.text.replace(")]}'", "")
        array_string = json.loads(cleaned)[0][2]
        article_url = json.loads(array_string)[1]

        return article_url

    except Exception as e:
        return f"Error: {e}"

print("Entered The Script")
# Google News RSS feed for Top Stories

parser = argparse.ArgumentParser(description="Run News Agent in different modes.")
parser.add_argument('--mode', type=str, choices=['general', 'law'], required=True,
                    help='Choose mode to run: general or law')
args = parser.parse_args()

if args.mode == 'law':
    rss_url = 'https://news.google.com/rss/search?q=employment+and+labor+law'
else:
    rss_url = 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en'

# Parse the RSS feed
feed = feedparser.parse(rss_url)
articles = []
max_articles = 7

for entry in feed.entries:
    if len(articles) >= max_articles:
        break

    try:
        final_url = extract_direct_article_url(entry.link)

        article = Article(url=final_url)
        article.download()
        article.parse()

        article_text = article.text
        article_summary = "summary"
        #article_summary = summarize_article(article_text)

        articles.append({
            "title": entry.title,
            "published": entry.published,
            "link": final_url,
            "summary": article_summary
        })

    except Exception as e:
        # Optional: log the error
        print(f"Skipping article due to error: {e}")
        continue

email_body = build_email_body(articles, args.mode)
print("Email Written")
#Call Send Email With your email here
#send_email(html_content=email_body, receiver_email=<your_email>, mode=args.mode)
print("Email Sent")
