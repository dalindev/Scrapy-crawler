#!/usr/bin/python
#-*-coding:utf-8-*-

from scrapy.item import Item, Field

class CategoryItem(Item):
	Category_and_Products = Field()

class ProductListItem(Item):
	Product_List = Field()

class ProductItem(Item):
	Product_SKU = Field()
	Product_title = Field()
	Regular_Price = Field()
	Sale_Price = Field()
	Availability = Field()
	Product_url = Field()

class Dept(Item):

	Department = Field()
	# Department_url = Field()

	Sub_Department = Field()
	# Sub_Department_url = Field()

	Sub_Sub_Department = Field()
	# Sub_Sub_Department_url = Field()

	this_category = Field()

class BundlesItem(Item):
	BundlesTitle = Field()
	Regular_Price = Field()
	Sale_Price = Field()
	Availability = Field()
	Product_url = Field()
	Bundles_SKU = Field()

