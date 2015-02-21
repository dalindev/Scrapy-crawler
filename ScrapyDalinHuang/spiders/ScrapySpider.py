#!/usr/bin/python
#-*-coding:utf-8-*-

# ***********************************************************
# * scrapy crawl dalin -o dainhuang.json -t json            *
# *                         Feb 19, 2015. By: Dalin_Huang   *
# ***********************************************************

from scrapy.spider import Spider
from scrapy.selector import Selector
from ScrapyDalinHuang.items import CategoryItem,ProductListItem,ProductItem,Dept,BundlesItem
from scrapy.http import Request
from scrapy.contrib.linkextractors import LinkExtractor


class DmozSpider(Spider):
    name = "dalin"
    # allowed_domains = ['visions.ca/']
    start_urls =  ['http://www.visions.ca',]
    
    # TOP main menu 'Home' (Department)
    def parse(self, response):
        res_sel = Selector(response)
        for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
            temp_Dept_url = Department_html.xpath('a/@href').extract()[0]
            # department full url
            Department_url = ('http://www.visions.ca'+temp_Dept_url)
            # since department 'Bundles' have a different form of pages (produced by JavaScript)
            # We need a special parse just for Bundles
            if 'Bundles' in Department_url:
                yield Request(url=Department_url, callback=self.parse_for_Bundles)
            else:
                yield Request(url=Department_url, callback=self.parse_Sub_Department)


    def parse_Sub_Department(self, response):
        thisURL = response.url
        res_sel = Selector(response)
        Dept_links02 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[1]/ul/li')
        #if this department have sub department
        if Dept_links02:
            for Sub_Department_html in Dept_links02: 
                temp_Sub_Dept_url = Sub_Department_html.xpath('a/@href').extract()[0]
                Sub_Dept_url = ('http://www.visions.ca/Catalogue/Category/'+temp_Sub_Dept_url)
                yield Request(url=Sub_Dept_url , callback=self.parse_Sub_Sub_Department)
            # else (this department do not have any sub department)
            # directly callback to parse_product_detail
        else:
            if 'categoryId=837&menu=741' in thisURL:
                thisURL = 'http://www.visions.ca/Catalogue/Category/ProductResults.aspx?categoryId=837&brandId=176'
            yield Request(url=thisURL, callback=self.parse_Before_Product_Detail, dont_filter=True)


    def parse_Sub_Sub_Department(self, response):
        thisURL = response.url
        res_sel = Selector(response)
        Dept_links03 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
        # if this department have sub_sub_department
        if Dept_links03:
            for Sub_Sub_Department_html in Dept_links03:
                temp_Sub_Sub_Dept_url = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
                Sub_Sub_Dept_url = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Sub_Dept_url)
                yield Request(url=Sub_Sub_Dept_url, callback=self.parse_Before_Product_Detail)
        else:
            # else (this department do not have any sub department)
            # directly callback to parse_Before_Product_Detail
            yield Request(url=thisURL, callback=self.parse_Before_Product_Detail, dont_filter=True)


    def parse_Before_Product_Detail(self, response):
        thisURL = response.url
        res_sel = Selector(response)
        # for there are next pages of list of products, yield request callback for new link
        try:
            next_link = res_sel.xpath(u'//*[@id="ctl00_ContentPlaceHolder1_lnkNextpage"]//@href').extract()[0]
            next_link = ('http://www.visions.ca'+next_link)
            yield Request(url=next_link, callback=self.parse_Before_Product_Detail)
        except:
            pass

        yield Request(url=thisURL, callback=self.parse_Product_Detail, dont_filter=True)


    def parse_Product_Detail(self, response):
        res_sel = Selector(response)
            # Category_Item include two things see below
            # 1.category path (Department >> Sub_Department >> Sub_Sub_Department >> this_category)
            # 2.detail product list for this_category
        Category_Item = CategoryItem()
        Category_Item['Category_and_Products'] = []

        # 1.category path
        Dept_List = Dept()

        # 2.detail product list
        Product_List_Item = ProductListItem()
        Product_List_Item['Product_List'] = []
            # the following is to get the categoies of this product list pages
            # each pages contain max 15 products with same category path and same 
            # basic information as single product page will shown.
            # this way saving a lot of request of go into page of each product
            # downloader/request_count': 1571, Product Collected: 6639, Time: 5mins
        categories = res_sel.xpath('//*[@id="ctl00_pnlBreadCrumbs"]/a//text()').extract()
        thiscategory = res_sel.xpath('//*[@id="ctl00_pnlBreadCrumbs"]/span//text()').extract()
        try:
            Dept_List['Department'] = categories[0]
        except:
            pass
        try:
            Dept_List['Sub_Department'] = categories[1]
        except:
            pass
        try:
            Dept_List['Sub_Sub_Department'] = categories[2]
        except:
            pass
        try:
            Dept_List['this_category'] = thiscategory[0]
        except:
            pass
        Category_Item['Category_and_Products'].append(Dept_List)
        # start deal with product info
        product_list_html = res_sel.xpath('//div[@class="contentright"]')
        for product_html in product_list_html:
            p_item = ProductItem()
            p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
            p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
            # Sale_Price is the current price (could be sale or regular)
            # some product does not have a price (mobiles etc...)
            # the price shown at right will always be the current price, hence the sale price
            p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0].strip()
            try:
                p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0].strip()
            except:
                p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0].strip()
            # if this have the In_STORE_ONLY image, then it is not avaliable online
            try:
                p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
                p_item['Availability'] = ('IN_STORE_ONLY')
            except: 
                p_item['Availability'] = ('AVALIABLE_ONLINE')
            # product_html links
            temp = product_html.xpath('h2/a/@href').extract()[0]
            p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)

            Product_List_Item['Product_List'].append(p_item)
        Category_Item['Category_and_Products'].append(Product_List_Item)

        return Category_Item


    # only for the Bundles category
    def parse_for_Bundles(self, response):
        res_sel = Selector(response)
        # parse_for_Bundles include Bundles titles
        # 2.detail product list for this_category
        Category_Item = CategoryItem()
        Category_Item['Category_and_Products'] = []

        # 1.category path
        Dept_List = Dept()

        # 2.detail product list
        Product_List_Item = ProductListItem()
        Product_List_Item['Product_List'] = []

        Dept_List['Department'] = ('Home')
        Dept_List['Sub_Department'] = ('Bundles')
        Category_Item['Category_and_Products'].append(Dept_List)

        bundle_list_html = res_sel.xpath('//table[@class="bundleItemTable"]')
        for bundle_html in bundle_list_html:
            b_item = BundlesItem()
            b_item['BundlesTitle'] = bundle_html.xpath('tr[1]/td[2]/a/text()').extract()[0]
            b_item['Bundles_SKU'] = bundle_html.xpath('tr[1]/td[1]/div[2]/text()').extract()[0].strip()
            # Sale_Price is the Current Price (hence this could be descripted as sale or regular price)
            # Since all bundles are on sale, do not have the knowledge of regular price only situations
            # assume the price will always at span[1] or span[3], then the following will cover all situations
            try:
                b_item['Sale_Price'] = bundle_html.xpath('tr[1]/td[3]/span[3]/span//text()').extract()[0]
            except:
                b_item['Sale_Price'] = bundle_html.xpath('tr[1]/td[3]/span[1]/span//text()').extract()[0]
            try:
                b_item['Regular_Price'] = bundle_html.xpath('tr[1]/td[3]/span[1]/span//text()').extract()[0]
            except:
                b_item['Regular_Price'] = bundle_html.xpath('tr[1]/td[3]/span[3]/span//text()').extract()[0]
            # if this product have the In_STORE_ONLY image, then it is not avaliable online
            # using CSS Selector
            try:
                b_item['Availability'] = bundle_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
                b_item['Availability'] = ('IN_STORE_ONLY')
            except: 
                b_item['Availability'] = ('AVALIABLE_ONLINE')
            # bundle_html links
            b_item['Bundles_url'] = ('http://www.visions.ca/Catalogue/Bundles/Default.aspx')
            # product list for this bundle
            b_item['Bundles_List_Item'] = bundle_html.xpath('tr[3]/td/ul/li//text()').extract()

            Product_List_Item['Product_List'].append(b_item)
        Category_Item['Category_and_Products'].append(Product_List_Item)

        return Category_Item




