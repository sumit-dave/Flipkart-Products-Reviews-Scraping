from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import logging
logging.basicConfig(filename="Scrapping_status.log", level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
app=Flask(__name__)


## assigned route to Home page of Website
@app.route("/", methods=["GET"])
@cross_origin()
def homepage():
    return render_template("index.html")

## '/review' route will get hit after click on submit button
@app.route('/review', methods=["GET","POST"])
@cross_origin()
def reviews():
    if request.method=="POST":
        try:
            query = request.form['content'].replace(" ","")     # search content assigned as query
            url = f"https://www.flipkart.com/search?q={query}"  # created URL to reach serched content webpage
            product_page = requests.get(url)                    # Pulled out code of webpage in object format
            page_code = bs(product_page.text, "html.parser")    # retrived object data and beautified in perfect understandable HTML code
            products = page_code.find_all("div", {"class": "_1AtVbE col-12-12"})
                                                                # retrived all the products div call and saved in products
            del products[0:4]           # deleted some starting line due to error in some poducts

            product1_link = products[0].div.div.div.a['href']   # Choosen 5th product of every search we do and pulled out the ref. link
            product1 = "https://www.flipkart.com" + product1_link   #link gentrated to reach that individual product
            product1_obj = requests.get(product1)        # again pulled out code of webpage in object format
            product1_code = bs(product1_obj.text, "html.parser")  #again retrived object data and beautified in perfect understandable HTML code
            product1_reviews = product1_code.find_all("div", {"class": "_16PBlm"})

            ## Till here we have pulled out product5 all reviews.
            ## Now time to retrive required data.

            #for testing purpose
            ##review_date = product1_reviews[0].find_all("p", {"class": "_2sc7ZR"})[1].text
            ##review_name = product1_reviews[0].find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text
            ##review_comment_header = product1_reviews[0].find_all("div", {"class": "_2sc7ZR"}).text
            ##review_comment = product1_reviews[0].div.find_all("div", {"class": ""})[1].text
            ##review_rating = product1_reviews[0].div.div.div.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text

            ## Here we have retrived and appended all data in json format under single veriable
            data_new = []
            for i in range(len(product1_reviews)):
                date_elem = product1_reviews[i].find_all("p", {"class": "_2sc7ZR"})  # Use find() instead of find_all()
                if date_elem:
                    date=date_elem[1].text
                else:
                    date="No Date"

                name_elem = product1_reviews[i].find("p", {"class": "_2sc7ZR _2V5EHH"})
                if name_elem:
                    name=name_elem.text
                else:
                    name="No Name"

                comm_had_elem = product1_reviews[i].find("p", {"class": "_2-N8zT"})
                if comm_had_elem:
                    comm_had=comm_had_elem.text
                else:
                    comm_had="No Comment Header"

                comm_elem = product1_reviews[i].find_all("div", {"class":""})
                if comm_elem:
                    comm=comm_elem[1].text
                else:
                    comm="No Comments"

                rating_elem = product1_reviews[i].find("div", {"class": "_3LWZlK _1BLPMq"})
                if rating_elem:
                    rating=rating_elem.text
                else:
                    rating="No ratings"

                data = {
                    "Date": date,
                    "Name": name,
                    "Comment Header": comm_had,
                    "Comment": comm,
                    "Ratings": rating
                }
                data_new.append(data)


            df = pd.DataFrame(data_new)    #data_new converted in data frame and saved as json file
            df.to_json(r"C:\Users\sumit\OneDrive\Desktop\Data Science Folder\Projects_Tasks\Flipkart_Products-info_scraping\{}.json".format(query))

            logging.info( "Scraping completed successfully")  # indication to confirm creating file task

            # here new webpage will get hit and will show all data in table format
            return render_template('results.html', data_subset=data_new[0:-1])


        except Exception as e:
            logging.exception(e)
            return "Something is wrong"

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)