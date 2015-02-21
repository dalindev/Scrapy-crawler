# -*- coding: utf-8 -*-

# Scrapy settings for ScrapyDalinHuang project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'ScrapyDalinHuang'

SPIDER_MODULES = ['ScrapyDalinHuang.spiders']
NEWSPIDER_MODULE = 'ScrapyDalinHuang.spiders'

# used 0.1 sec for fast scrapy (DalinHuang)
# most of the time should use 2-5 sec
DOWNLOAD_DELAY = 0.1
CONCURRENT_REQUESTS = 250


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ScrapyDalinHuang (+http://www.yourdomain.com)'
