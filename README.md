# ScrapyDalinHuang
<br><br>
Used:  Python 2.79, scrapy, Git
System: OS X (10.x)
<br><br>
How to run it:<br>
scrapy crawl dalin -o dainhuang.json -t json
<br><br>

Category path:<br>
	Department >> Sub_Department >> Sub_Sub_Department >> this_category<br>
(example):  Home  >>  TV & Video  >>  Televisions  >>  25 - 31" Televisions<br>
	

Features:<br>
	• Fast speed with 6639 Products retrieved in 5mins (DOWNLOAD_DELAY = 0.01), 7mins (DOWNLOAD_DELAY = 0.01)<br>
	• No wasted request, spider is guided through categories<br>
	• Sub_Departments Gift Card and Bundles are special treated since page formates are different<br>
	
Known Issues:<br>
	• Output Data Scructures (Json) are not well formated, sacrificed for fast running speed (currently)<br>
	• Some of the Category names shown in http://www.visions.ca/ home page are different inside sub categories<br>
 	 	 		[ I used categoies path shown in the product page ]
 	 	 		
 	 	 		
<br><br><br>
REQUIREMENT:

A simple tool that will scrape product information from http://www.visions.ca/, returning at a
minimum the following information:<br>
    • The product categories available on the website<br>
	• At least one product per category<br>
Each product returned should have the following information:<br>
	• Product title<br>
	• Product sale or regular price where applicable<br>
	• Product availability<br>
As a bonus (but not doing this will not count against you), you may want to use the following
your solution:<br>
	• Python<br>
	• The scrapy, lxml, or requests python libraries<br>
	• Xpaths or CSS selectors<br><br>



