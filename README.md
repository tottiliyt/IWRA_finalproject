# IWRA finalproject Option 4b: MetaShopper

Option 4b: MetaShopper
Another useful thing that Web Agents can do is extract information from multiple sources
and condense it into a useful format. Examples of this would be MetaCrawler (http://www.metacrawler.com)
that searches a number of search engines, re-weights the results and returns you the answer,
BottomDollar (http://www.bottomdollar.com) that searches through many shopping sites
and returns you the best prices for the product(s) that you searched for.
Implementing something like BottomDollar isn’t very difficult. First visit all of the
shopping sites that you wish to support, download their pages, and look at the HTML
forms. Then you can find the fields that you will need to add to the HTTP::Request when
doing a POST to get the search results back.
Take the basic web robot and add:
(a) A configuration file with the URLs and fields that you need to post to for each store.
(b) Add an interface where the user can type in the queries that they want.
(c) For each query, visit all the services in your configuration file, and get the resulting
page.
(d) For each resulting page, use the Text Extraction methods from assignment #1 and
assignment #3 to pull out the information that you need to display the user (product
name, link to see the product, price) so that you have a common format for all services.
(e) Display the information to the user ranked by price.

Evaluation:
You can test the program by entering queries and then visiting the services that your web
robot is visiting and compare the results. Make sure that your Text Extraction methods
aren’t missing anything, and that your ranking of results is working properly. If you want,
you can also add some more advanced ranking by the search term vs. what was returned,
instead of just by price.

This is a metashopper that support these websites:

1. Amazon

2. Walmart

3. Bestbuy

4. Ebay

#### 1. Setup Virtual Environment
We recommend creating a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)
for running the API server. 
```
python -m venv metashopper-env
```

#### 2. Activate Virtual Environment
For Windows:
```
.\metashopper-env\scripts\activate
```

For Linux/MacOS
```
source metashopper-env/bin/activate
```

#### 3. Install Requirements
Then install the requirements (with your virtual environment activated)
```
pip install -r requirements.txt
```

#### 4. Running
Running Dev:
```
flask run
```

