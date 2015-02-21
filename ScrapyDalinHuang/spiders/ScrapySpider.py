#!/usr/bin/python
#-*-coding:utf-8-*-

# import time
# import scrapy
# from pprint import pprint
# from scrapy.contrib.linkextractors import LinkExtractor
# from scrapy.spider import BaseSpider
# from scrapy.selector import HtmlXPathSelector
# from dirbot.items import VisionsCrawlerItem
# from dirbot.utils.select_result import clean_link


#  =========================== WORKING VERSION 001 =================================================================================




#  scrapy crawl dalin -o dainhuang.json -t json

# Feb 19, 2015. By: Dalin_Huang
from scrapy.spider import Spider
from scrapy.selector import Selector
from ScrapyDalinHuang.items import CategoryItem,ProductListItem,ProductItem,Dept,BundlesItem
from scrapy.http import Request
from scrapy.contrib.linkextractors import LinkExtractor

class DmozSpider(Spider):
    name = "dalin"
    # allowed_domains = ['visions.ca/']
    start_urls =  ['http://www.visions.ca',]
    

    # rules = (
    #         Rule(LinkExtractor(allow=('Catalogue/Bundles/',)), callback='parse_for_Bundles', dont_filter=True),


    #     )



    # TOP main menu with 13 departments (TV & VIDEO, HOME AUDIO etc...)
    def parse(self, response):
        res_sel = Selector(response)


        for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
            # department name and temp_url
            # item['Department_Name'] = Department_html.xpath('a/span/text()').extract()
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
                # item['Sub_Dept'] = Sub_Department_html.xpath('a/text()').extract()
                Sub_Dept_url = ('http://www.visions.ca/Catalogue/Category/'+temp_Sub_Dept_url)

                yield Request(url=Sub_Dept_url , callback=self.parse_Sub_Sub_Department)

        else:
            # else (this department do not have any sub department)
            # directly callback to parse_product_detail
            yield Request(url=thisURL, callback=self.parse_Product_Detail, dont_filter=True)


    def parse_Sub_Sub_Department(self, response):
        thisURL = response.url
        res_sel = Selector(response)

        Dept_links03 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
        
        # if this department have sub_sub_department
        if Dept_links03:
            for Sub_Sub_Department_html in Dept_links03:
                temp_Sub_Sub_Dept_url = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
                # item['Sub_Sub_Dept'] = Sub_Sub_Department_html.xpath('a/text()').extract()
                Sub_Sub_Dept_url = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Sub_Dept_url)

                yield Request(url=Sub_Sub_Dept_url, callback=self.parse_Product_Detail)

        else:
            # else (this department do not have any sub department)
            # directly callback to parse_product_detail
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

        product_list_html = res_sel.xpath('//div[@class="contentright"]')
        for product_html in product_list_html:
            p_item = ProductItem()

            p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
            p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
            # Sale_Price is the current price (could be sale or regular)
            p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
            try:
                p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
            except:
                p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0]
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


    # only for Bundles category
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

            b_item['BundlesTitle'] = bundle_html.xpath('tr[1]/td[2]/a/text()').extract()
            b_item['Bundles_SKU'] = bundle_html.xpath('tr[1]/td[1]/div[2]/text()').extract()[0].strip()
            # Sale_Price is the Current Price (hence this could be descripted as sale or regular price)
            try:
                b_item['Sale_Price'] = bundle_html.xpath('tr[1]/td[3]/span[3]/span//text()').extract()[0]
            except:
                b_item['Sale_Price'] = bundle_html.xpath('tr[1]/td[3]/span[1]/span//text()').extract()[0]
            try:
                b_item['Regular_Price'] = bundle_html.xpath('tr[1]/td[3]/span[1]/span//text()').extract()[0]
            except:
                b_item['Regular_Price'] = bundle_html.xpath('tr[1]/td[3]/span[3]/span//text()').extract()[0]
            # if this have the In_STORE_ONLY image, then it is not avaliable online
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







 # =========================== WORKING VERSION =================================================================================



#  =========================== WORKING VERSION 002 Full Category =================================================================================




# #  scrapy crawl dalin -o dainhuang.json -t json

# # Feb 19, 2015. By: Dalin_Huang
# from scrapy.spider import Spider
# from scrapy.selector import Selector
# from dirbot.items import CategoryItem,ProductListItem,ProductItem,Dept
# from scrapy.http import Request
# from scrapy.contrib.linkextractors import LinkExtractor

# class DmozSpider(Spider):
#     name = "dalin"
#     # allowed_domains = ['visions.ca/']
#     start_urls =  ['http://www.visions.ca',]
    

#     rules = (
#             Rule(LinkExtractor(allow=('Catalogue/Bundles/',)), callback= ),




#         )



#     # TOP main menu with 13 departments (TV & VIDEO, HOME AUDIO etc...)
#     def parse(self, response):
#         res_sel = Selector(response)


#         for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
#             # department name and temp_url
#             # item['Department_Name'] = Department_html.xpath('a/span/text()').extract()
#             temp_Dept_url = Department_html.xpath('a/@href').extract()[0]
#             # department full url
#             Department_url = ('http://www.visions.ca'+temp_Dept_url)
#             yield Request(url=Department_url, callback=self.parse_Sub_Department)




#     def parse_Sub_Department(self, response):
#         thisURL = response.url
#         res_sel = Selector(response)
        

#         Dept_links02 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[1]/ul/li')
#         #if this department have sub department
#         if Dept_links02:
#             for Sub_Department_html in Dept_links02: 
#                 temp_Sub_Dept_url = Sub_Department_html.xpath('a/@href').extract()[0]
#                 # item['Sub_Dept'] = Sub_Department_html.xpath('a/text()').extract()
#                 Sub_Dept_url = ('http://www.visions.ca/Catalogue/Category/'+temp_Sub_Dept_url)

#                 yield Request(url=Sub_Dept_url , callback=self.parse_Sub_Sub_Department)

#         else:
#             # else (this department do not have any sub department)
#             # directly callback to parse_product_detail
#             yield Request(url=thisURL, callback=self.parse_Product_Detail,dont_filter=True)


#     def parse_Sub_Sub_Department(self, response):
#         thisURL = response.url
#         res_sel = Selector(response)

#         Dept_links03 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
        
#         # if this department have sub_sub_department
#         if Dept_links03:
#             for Sub_Sub_Department_html in Dept_links03:
#                 temp_Sub_Sub_Dept_url = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
#                 # item['Sub_Sub_Dept'] = Sub_Sub_Department_html.xpath('a/text()').extract()
#                 Sub_Sub_Dept_url = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Sub_Dept_url)

#                 yield Request(url=Sub_Sub_Dept_url, callback=self.parse_Product_Detail)

#         else:
#             # else (this department do not have any sub department)
#             # directly callback to parse_product_detail
#             yield Request(url=thisURL, callback=self.parse_Product_Detail,dont_filter=True)


#     def parse_Product_Detail(self, response):
#         res_sel = Selector(response)

#         # Category_Item include two things see below
#         # 1.category path (Department >> Sub_Department >> Sub_Sub_Department >> this_category)
#         # 2.detail product list for this_category
#         Category_Item = CategoryItem()
#         Category_Item['Category_and_Products'] = []

#         # 1.category path
#         Dept_List = Dept()

#         # 2.detail product list
#         Product_Lite_Item = ProductListItem()
#         Product_Lite_Item['Product_List'] = []

#         categories = res_sel.xpath('//*[@id="ctl00_pnlBreadCrumbs"]/a//text()').extract()
#         try:
#             Dept_List['Department'] = categories[0]
#         except:
#             pass
#         try:
#             Dept_List['Sub_Department'] = categories[1]
#         except:
#             pass
#         try:
#             Dept_List['Sub_Sub_Department'] = categories[2]
#         except:
#             pass
#         try:
#             Dept_List['this_category'] = res_sel.xpath('//*[@id="ctl00_pnlBreadCrumbs"]/span//text()').extract()[0]
#         except:
#             pass

#         Category_Item['Category_and_Products'].append(Dept_List)

#         product_list_html = res_sel.xpath('//div[@class="contentright"]')
#         //*[@id="ctl00_tdMainPanel"]/div[2]
#         //*[@id="ctl00_tdMainPanel"]


#         for product_html in product_list_html:
#             p_item = ProductItem()

#             p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
#             p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
#             # Sale_Price is the current price (could be sale or regular)
#             p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
#             try:
#                 p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
#             except:
#                 p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0]





#             # if this have the In_STORE_ONLY image, then it is not avaliable online
#             try:
#                 p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
#                 p_item['Availability'] = ('IN_STORE_ONLY')
#             except: 
#                 p_item['Availability'] = ('AVALIABLE_ONLINE')
#             # product_html links
#             temp = product_html.xpath('h2/a/@href').extract()[0]
#             p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)



#             Product_Lite_Item['Product_List'].append(p_item)

#         Category_Item['Category_and_Products'].append(Product_Lite_Item)
#         return [Category_Item]


#         def parse_for_Bundles(self, response):

            


 # =========================== WORKING VERSION =================================================================================

















#  =========================== WORKING VERSION 00000 =================================================================================



# #  scrapy crawl dmoz -o dainhuang.json -t json

# # Feb 19, 2015. By: Dalin_Huang
# from scrapy.spider import Spider
# from scrapy.selector import Selector
# from dirbot.items import DeptRootItem,DeptItem,Sub_DeptItem,Sub_Sub_DeptItem,ProductItem
# from scrapy.http import Request


# class DmozSpider(Spider):
#     name = "dmoz"
#     # allowed_domains = ['visions.ca/']
#     start_urls =  ['http://www.visions.ca',]
#     # start_urls =  ['http://www.visions.ca/Catalogue/Category/ProductResults.aspx?categoryId=12&menu=14',]

#     # TOP main menu with 13 departments (TV & VIDEO, HOME AUDIO etc...)
#     def parse(self, response):
#         res_sel = Selector(response)

#         DeptRoot = DeptRootItem()
#         DeptRoot['Department_Root'] = []

#         for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
#             # department name and temp_url
#             Dept = DeptItem()
#             Dept['Departments'] = []
#             Dept['Dept_Name'] = Department_html.xpath('a/span/text()').extract()
#             temp_Dept_url = Department_html.xpath('a/@href').extract()[0]
#             # department full url
#             Dept['Dept_url'] = ('http://www.visions.ca'+temp_Dept_url)

#             request = Request(url=Dept['Dept_url'], callback=self.parse_Sub_Department)
#             request.meta['Dept'] = Dept

#             DeptRoot['Department_Root'].append(Dept)

#             yield request

#     # return item
#     # Sub menu for each of the 13 departments from TOP main menu
#     # Some of those depatments does not have a sub menu, just redirect to
#     # parse_Product_Detail
#     def parse_Sub_Department(self, response):   
#         thisURL = response.url
#         Dept = response.meta['Dept']

#         res_sel = Selector(response)
#         Dept_links02 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[1]/ul/li')
#         # if this department have sub department
#         if Dept_links02:
#             for Sub_Department_html in Dept_links02: 
                
#                 Sub_Dept = Sub_DeptItem()

#                 temp_Sub_Dept_url = Sub_Department_html.xpath('a/@href').extract()[0]
#                 Sub_Dept['Sub_Dept'] = Sub_Department_html.xpath('a/text()').extract()
#                 Sub_Dept['Sub_Dept_url'] = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Dept_url)
            
#                 request = Request(url=Sub_Dept['Sub_Dept_url'], callback=self.parse_Sub_Sub_Department)
#                 request.meta['Sub_Dept'] = Sub_Dept

#                 Dept.append(Sub_Dept)

#                 yield request
       
#         # else (this department do not have any sub department)
#         # directly callback to parse_product_detail
#         else:
#             request = Request(url=thisURL, callback=self.parse_Product_Detail)
#             request.meta['Dept'] = Dept
#             yield request


#     def parse_Sub_Sub_Department(self, response):
#         thisURL = response.url
#         Sub_Dept = response.meta['Sub_Dept']

#         res_sel = Selector(response)
#         Dept_links03 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
#         if Dept_links03:
#             for Sub_Sub_Department_html in Dept_links03:
                    
#                     Sub_Sub_Dept = Sub_Sub_DeptItem()

#                     temp_Sub_Sub_Dept_url = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
#                     Sub_Sub_Dept['Sub_Sub_Dept'] = Sub_Sub_Department_html.xpath('a/text()').extract()
#                     Sub_Sub_Dept['Sub_Sub_Dept_url'] = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Sub_Dept_url)

#                     request = Request(url=Sub_Sub_Dept['Sub_Sub_Dept_url'], callback=self.parse_Product_Detail)    
#                     request.meta['Dept_Item'] = Dept_Item
                    
#                     Sub_Dept.append(Sub_Sub_Dept)

#                     yield request
#         # No sub_sub_category for this sub category, directly goto parse_product_detail
#         else:
#             request = Request(url=thisURL, callback=self.parse_Product_Detail)
#             request.meta['DeptRoot'] = DeptRoot
#             yield request


#     def parse_Product_Detail(self, response):
#         DeptRoot = response.meta['DeptRoot']

#         # Dept_Item['Product_List'] = []
#         res_sel = Selector(response)
#         product_list_html = res_sel.xpath('//div[@class="contentright"]')
#         # items = []

#         for product_html in product_list_html[0:3]:
#             p_item = ProductItem()

#             p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
#             p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
#             # Sale_Price is the current price (could be sale or regular)
#             p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
#             try:
#                 p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
#             except:
#                 p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0]
#             # if this have the In_STORE_ONLY image, then it is not avaliable online
#             # 
#             try:
#                 p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
#                 p_item['Availability'] = ('IN_STORE_ONLY')
#             except: 
#                 p_item['Availability'] = ('AVALIABLE_ONLINE')
#             # product_html links
#             temp = product_html.xpath('h2/a/@href').extract()[0]
#             p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)

#             DeptRoot['Department_Root'].append(p_item)

#         return DeptRoot



    # def parse_Product_Detail_000(self, response):
    #     Dept_Item = response.meta['Dept_Item']

    #     Dept_Item['Product_List'] = []
    #     res_sel = Selector(response)
    #     product_list_html = res_sel.xpath('//div[@class="contentright"]')
    #     # items = []

    #     for product_html in product_list_html[0:3]:
    #         p_item = ProductItem()

    #         p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
    #         p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
    #         # Sale_Price is the current price (could be sale or regular)
    #         p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
    #         try:
    #             p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
    #         except:
    #             p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0]
    #         # if this have the In_STORE_ONLY image, then it is not avaliable online
    #         # 
    #         try:
    #             p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
    #             p_item['Availability'] = ('IN_STORE_ONLY')
    #         except: 
    #             p_item['Availability'] = ('AVALIABLE_ONLINE')
    #         # product_html links
    #         temp = product_html.xpath('h2/a/@href').extract()[0]
    #         p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)

    #         Dept_Item['Product_List'].append(p_item)

    #     Dept_Item['Departments'].append(Dept_Item['Product_List'])


    #     return Dept_Item



    # def parse_Product_Detail_111(self, response):
    #     Dept_Item = response.meta['Dept_Item']

    #     Dept_Item['Product_List'] = []
    #     res_sel = Selector(response)
    #     product_list_html = res_sel.xpath('//div[@class="contentright"]')
    #     # items = []

    #     for product_html in product_list_html[0:3]:
    #         p_item = ProductItem()

    #         p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
    #         p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
    #         # Sale_Price is the current price (could be sale or regular)
    #         p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
    #         try:
    #             p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
    #         except:
    #             p_item['Regular_Price'] = product_html.xpath('div/div//text()').extract()[0]
    #         # if this have the In_STORE_ONLY image, then it is not avaliable online
    #         # 
    #         try:
    #             p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
    #             p_item['Availability'] = ('IN_STORE_ONLY')
    #         except: 
    #             p_item['Availability'] = ('AVALIABLE_ONLINE')
    #         # product_html links
    #         temp = product_html.xpath('h2/a/@href').extract()[0]
    #         p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)
            
    #         Dept_Item['Product_List'].append(p_item)

    #     Dept_Item['Sub_Dept_List'].append('Product_List')

    #     return Dept_Item



#  =========================== WORKING VERSION 000 =================================================================================





# #  =========================== WORKING VERSION =================================================================================




# #  scrapy crawl dmoz -o dainhuang.json -t json

# # Feb 19, 2015. By: Dalin_Huang
# from scrapy.spider import Spider
# from scrapy.selector import Selector
# from dirbot.items import Dept,ProductItem
# from scrapy.http import Request


# class DmozSpider(Spider):
#     name = "dmoz"
#     # allowed_domains = ['visions.ca/']
#     start_urls =  ['http://www.visions.ca',]
#     # start_urls =  ['http://www.visions.ca/Catalogue/Category/ProductResults.aspx?categoryId=12&menu=14',]

#     # TOP main menu with 13 departments (TV & VIDEO, HOME AUDIO etc...)
#     def parse(self, response):
#         res_sel = Selector(response)

#         # items = []

#         for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
#             item = Dept()
#             # department name and temp_url
#             item['Department_Name'] = Department_html.xpath('a/span/text()').extract()
#             temp_Dept_url = Department_html.xpath('a/@href').extract()[0]
#             # department full url
#             item['Department_url'] = ('http://www.visions.ca'+temp_Dept_url)

#             request = Request(url=item['Department_url'], callback=self.parse_Sub_Department)
#             request.meta['item'] = item
#             yield request

#     # return item
#     # Sub menu for each of the 13 departments from TOP main menu
#     # Some of those depatments does not have a sub menu, just redirect to
#     # parse_Product_Detail
#     def parse_Sub_Department(self, response):
#         thisURL = response.url
#         item = response.meta['item']

#         res_sel = Selector(response)
#         Dept_links02 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[1]/ul/li')
#         # if this department have sub department
#         if Dept_links02:
#             for Sub_Department_html in Dept_links02: 
#                 temp_Sub_Dept_url = Sub_Department_html.xpath('a/@href').extract()[0]
#                 item['Sub_Dept'] = Sub_Department_html.xpath('a/text()').extract()
#                 item['Sub_Dept_url'] = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Dept_url)
               
#                 request = Request(url=item['Sub_Dept_url'], callback=self.parse_Sub_Sub_Department)
#                 request.meta['item'] = item
#                 yield request
       
#         # else (this department do not have any sub department)
#         # directly callback to parse_product_detail
#         else:

#             print ('33333333 No More Sub Dept links !!!!!!!!!!!!!!!!!!!!!!!!!!')

#             request = Request(url=thisURL, callback=self.parse_Product_Detail)
#             request.meta['item'] = item
#             yield request

#     def parse_Sub_Sub_Department(self, response):
#         thisURL = response.url
#         item = response.meta['item']

#         res_sel = Selector(response)
#         Dept_links03 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
#         if Dept_links03:
#             for Sub_Sub_Department_html in Dept_links03:
#                     temp_Sub_Sub_Dept_url = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
#                     item['Sub_Sub_Dept'] = Sub_Sub_Department_html.xpath('a/text()').extract()
#                     item['Sub_Sub_Dept_url'] = ("http://www.visions.ca/Catalogue/Category/"+temp_Sub_Sub_Dept_url)

#                     request = Request(url=item['Sub_Sub_Dept_url'], callback=self.parse_Product_Detail)
#                     request.meta['item'] = item
#                     yield request
#         else:
#             # No sub_sub_category for this sub category, directly goto parse_product_detail
#             print ('55555555555 No More Sub Sub Dept !==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

#             request = Request(url=thisURL, callback=self.parse_Product_Detail)
#             request.meta['item'] = item
#             yield request


#     def parse_Product_Detail(self, response):
#         item = response.meta['item']

#         item['Product_List'] = []
#         res_sel = Selector(response)
#         product_list_html = res_sel.xpath('//div[@class="contentright"]')
#         # items = []

#         for product_html in product_list_html:
#             p_item = ProductItem()

#             p_item['Product_title'] = product_html.xpath('h2/a//text()').extract()[0]
#             p_item['Product_SKU'] = product_html.xpath('h2/a//text()').extract()[2]
#             # Sale_Price is the current price (could be sale or regular)
#             p_item['Sale_Price'] = product_html.xpath('div/div//text()').extract()[0]
#             p_item['Regular_Price'] = product_html.xpath('div/div[2]//text()').extract()[0]
#             # if this have the In_STORE_ONLY image, then it is not avaliable online
#             # 
#             try:
#                 p_item['Availability'] = product_html.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
#                 p_item['Availability'] = ('IN_STORE_ONLY')
#             except: 
#                 p_item['Availability'] = ('AVALIABLE_ONLINE')
#             # product_html links
#             temp = product_html.xpath('h2/a/@href').extract()[0]
#             p_item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)

#             item['Product_List'].append(p_item)

#         return item







#  =========================== WORKING VERSION =================================================================================

            # req = Request(url=item['Dept_links'], callback=self.parseDepartment)
            # req.meta['item'] = item
        # return item

        # yield req



            # if Department_link:
            # Department_link = ('http://www.visions.ca'+Department_link)
            # print ('11111 Department is========'+Department_link)
            # yield Request(url=Department_link, callback=self.parse)

        # for product_info in res_sel.xpath(u'//*[@id="ctl00_ContentPlaceHolder1_lnkNextpage"]//@href').extract():
        #     print ('111 next product is========='+product_info)   
        #     if product_info:
        #         product_info = ('http://www.visions.ca/Catalogue/Category/'+product_info)
        #         print ('222 next product is=========='+product_info) 
        #         yield Request(url=product_info, callback=self.parse_detail)


    # def parse_detail(self, response):

    #     res_sel = Selector(response)
    #     sites = res_sel.xpath('//*[@id="ctl00_tdMainPanel"]/div/div/div[3]')
    #     items = []

    #     for site in sites:
    #         item = Website()

    #         item['url'] = site.xpath('h2/a/@href').extract()
    #         item['productname'] = site.xpath('h2//text()').extract()[1]
    #         # item['description'] = site.xpath('p/text()').extract()[0].strip()

    #         items.append(item)

    #     return items

# # =================== feb 18, 1:20 PM ================================
#     # get url productname descriptin from web list
#     # "http://www.visions.ca/Catalogue/Category/ProductResults.aspx?categoryId=8&menu=11"
 
#     def parse(self, response):

#         res_sel = Selector(response)
#         next_link = res_sel.xpath(u'//*[@id="ctl00_ContentPlaceHolder1_lnkNextpage"]//@href').extract()[0]
#         if next_link:
#              next_link = ('http://www.visions.ca'+next_link)
#              print ('000 next_Page is========'+next_link)
#              yield Request(url=next_link, callback=self.parse)
        
#         for detail_link in res_sel.xpath(u'//*[@id="ctl00_tdMainPanel"]/div/div/div[3]/h2//@href').extract():
#             print ('111 next product is========='+detail_link)   
#             if detail_link:
#                 detail_link = ('http://www.visions.ca/Catalogue/Category/'+detail_link)
#                 print ('222 next product is=========='+detail_link) 
#                 yield Request(url=detail_link, callback=self.parse_detail)

#     def parse_detail(self, response):
#             item = Website()
#             res_sel = Selector(response)

#             item['Product_title'] = res_sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lblProdTitle"]/span/text()').extract()[0]
            
#              #  Using try/except allowed to check if there is a sale price (if not then pass)
#              #  Also allowed the situation of there is only SALE price provided
#             try:  
#                 item['Regular_Price'] = res_sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lblRegprice"]//text()').extract()[0]
#             except:
#                 pass

#             try:    
#                 item['Sale_Price'] = res_sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lblSaleprice"]/font/text()').extract()[0]
#             except:
#                 pass
                
#               #  Could assume default value of item['Availability'] is IN_STORE_ONLY
#               #  But I tried to check on both '...imgInstoreonly' and '...lnkAddCart'
#             try:
#                 item['Availability'] = res_sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_imgInstoreonly"]/img/@src').extract()
#                 item['Availability'] = ('IN_STORE_ONLY')
#             except:
#                 pass  

#             try:
#                 item['Availability'] = res_sel.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lnkAddCart"]//text()').extract()[0]
#                 item['Availability'] = ('AVALIABLE_ONLINE')
#             except:
#                 pass  

#             return item
#         # yield item
# # =================== feb 18, 1:20 PM ================================
    # rules = (
    #     # Extract links matching 'category.php' (but not matching 'subsection.php')
    #     # and follow links from them (since no callback means follow=True by default).

    #     # Rule(LinkExtractor(restrict_xpaths=('//*[@id="mastermenu-startbtn"]', ))),
    #     # Rule(LinkExtractor(allow=('.*/catalogue/category/.*',), )),

    #     # Extract links matching 'sku=' and parse them with the spider's method parse_item
    #     Rule(LinkExtractor(restrict_xpaths=('//*[@id="mastermenu-startbtn"//a/@href]', ))),
    #     Rule(LinkExtractor(allow=('sku=', )), callback='parse_item'),
    # )


    # get url productname descriptin from web list
    # "http://www.visions.ca/Catalogue/Category/ProductResults.aspx?categoryId=8&menu=11"

    # def parse(self, response):

    #     sel = Selector(response)
    #     sites = sel.xpath('//*[@id="ctl00_tdMainPanel"]/div/div/div[3]')
    #     items = []

    #     for site in sites:
    #         item = Website()

    #         item['url'] = site.xpath('h2/a/@href').extract()
    #         item['productname'] = site.xpath('h2//text()').extract()[1]
    #         # item['description'] = site.xpath('p/text()').extract()[0].strip()


    #         items.append(item)

    #     return items




# # ======================================  Product Scrapy Ready  ========================================================================
#     def parse_item(self, response):

#         sel = Selector(response)
#         sites = sel.xpath('//*[@id="productdetail-container"]/div[2]/div[2]')
#         items = []

#         for site in sites:
#             item = Website()

#             item['Product_title'] = site.xpath('h1/span/text()').extract()[0]
            
#              #  Using try/except allowed to check if there is a sale price (if not then pass)
#              #  Also allowed the situation of there is only SALE price provided
#             try:  
#                 item['Regular_Price'] = site.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lblRegprice"]//text()').extract()[0]
#             except: pass

#             try:    
#                 item['Sale_Price'] = site.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lblSaleprice"]/font/text()').extract()[0]
#             except: pass
                
#               #  Could assume default value of item['Availability'] is IN_STORE_ONLY
#               #  But I tried to check on both '...imgInstoreonly' and '...lnkAddCart'
#             try:
#                 item['Availability'] = site.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_imgInstoreonly"]/img/@src').extract()
#                 item['Availability'] = ('IN_STORE_ONLY')
#             except: pass  

#             try:
#                 item['Availability'] = site.xpath('//*[@id="ctl00_ContentPlaceHolder1_ctrlProdDetailUC_lnkAddCart"]//text()').extract()[0]
#                 item['Availability'] = ('AVALIABLE_ONLINE')
#             except: pass  

#             items.append(item)
#             yield item
#         return items
# # ======================================  Product Scrapy Ready  ========================================================================







# # ==================================== almost Final Version =====================================

#  # old one yoyoyoy
# from scrapy.spider import Spider
# from scrapy.selector import Selector
# from dirbot.items import Dept,ProductItem
# from scrapy.http import Request


# class DmozSpider(Spider):
#     name = "dmoz"
#     # allowed_domains = ['visions.ca/']
#     start_urls =  ['http://www.visions.ca',]


#     # TOP main menu with 13 departments (TV & VIDEO, HOME AUDIO etc...)
#     def parse(self, response):
#         res_sel = Selector(response)
#         items = []
#         for Department_html in res_sel.xpath('//*[@id="mastermenu-dropdown"]/li')[0:13]:
#             item = Dept()
#             # department name and url
#             item['Department_Name'] = Department_html.xpath('a/span/text()').extract()
#             item['Dept_url'] = Department_html.xpath('a/@href').extract()[0]
#             print (item['Department_Name'])

#             if item['Dept_url']:
#                 Dept_links01 = ('http://www.visions.ca'+item['Dept_url'])
#                 print ('00000 Department_html is======== ', Dept_links01)
#                 request = Request(url=item['Dept_url'], callback=self.parse_Sub_Department)
#                 request.meta['item'] = item
#                 yield request


#     # return item
#     # Sub menu for each of the 13 departments from TOP main menu
#     # Some of those depatments does not have a sub menu, just redirect to
#     # parse_Product_Detail
#     def parse_Sub_Department(self, response):
#         res_sel = Selector(response)
#         Dept_links02 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[1]/ul/li')
#         if Dept_links02:
#             for Sub_Department_html in Dept_links02: 
#                     delinks02 = Sub_Department_html.xpath('a/@href').extract()[0]
#                     sub_dept_name = Sub_Department_html.xpath('a/text()').extract()
#                     print ('11111 Sub_Department_html is======== ', delinks02)
#                     print ('22222 Sub_Department_html is======== ', sub_dept_name)
#                     if delinks02:
#                         Dept_links03 = ("http://www.visions.ca/Catalogue/Category/"+delinks02)
#                         yield Request(url=Dept_links03, callback=self.parse_Sub_Sub_Department)
#         else:
#             # No sub category for this Department, directly goto parse_product_detail
#             print ('33333333 No More Sub Dept links !!!!!!!!!!!!!!!!!!!!!!!!!!')

#     def parse_Sub_Sub_Department(self, response):
#         res_sel = Selector(response)
#         Dept_links04 = res_sel.xpath('//*[@id="subcatemenu-container"]/div[2]/ul/li/div/div[1]')
#         if Dept_links04:
#             for Sub_Sub_Department_html in Dept_links04:
#                     delinks03 = Sub_Sub_Department_html.xpath('a/@href').extract()[0]
#                     sub_dept_name2 = Sub_Sub_Department_html.xpath('a/text()').extract()
#                     print ('333333 Sub_Sub_Department_html is======== ', delinks03)
#                     print ('444444 Sub_Sub_Department_html is======== ', sub_dept_name2)
#                     if delinks03:
#                         Dept_links05 = ("http://www.visions.ca/Catalogue/Category/"+delinks03)
#                         yield Request(url=Dept_links05, callback=self.parse_Product_Detail)
#         else:
#             # No sub_sub_category for this sub category, directly goto parse_product_detail
#             print ('55555555555 No More parse_Sub_Department !==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')

#     def parse_Product_Detail(self, response):
#         print ('NOT DEFINED YET parse_Product_Detail ******************************* ')
#         return 



# # ==================================== almost Final Version =====================================



# # ===============works alone ============================

#     def parse_Product_Detail(self, response):

#         res_sel = Selector(response)
#         sites = res_sel.xpath('//div[@class="contentright"]')
#         items = []

#         for site in sites:
#             item = ProductItem()


#             item['Product_title'] = site.xpath('h2/a//text()').extract()[0]
#             item['Product_SKU'] = site.xpath('h2/a//text()').extract()[2]
#             # Sale_Price is the current price (could be sale or regular)
#             item['Sale_Price'] = site.xpath('div/div//text()').extract()[0]
#             item['Regular_Price'] = site.xpath('div/div[2]//text()').extract()[0]
#             # if this have the In_STORE_ONLY image, then it is not avaliable online
#             # 
#             try:
#                 item['Availability'] = site.css('a[href*=StoreLocator] img::attr(src)').extract()[0]
#                 item['Availability'] = ('IN_STORE_ONLY')
#             except: 
#                 item['Availability'] = ('AVALIABLE_ONLINE')
#             # product links
#             temp = site.xpath('h2/a/@href').extract()[0]
#             item['Product_url'] = ('http://www.visions.ca/Catalogue/Category/'+temp)

#             items.append(item)

#         return items

# # ===============works alone ============================





