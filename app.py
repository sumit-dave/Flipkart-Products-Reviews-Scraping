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
            product_page = requests.get(url)  # Pulled out code of webpage in object format
            page_code = bs(product_page.text,"html.parser")  # retrieved object data and beautified in perfect understandable HTML code
            products = page_code.find_all("div", {"class": "_1AtVbE col-12-12"})
            # retrieved all the products div call and saved in products
            del products[0:2]  # deleted some starting line due to error in some poducts

            product_link = products[0].div.div.div.a['href']  # Choosen 2nd product of every search we do and pulled out the ref. link

            product = "https://www.flipkart.com" + product_link  # link gentrated to reach that individual product
            product_obj = requests.get(product)  # again pulled out code of webpage in object format
            product_code = bs(product_obj.text,"html.parser")  # again retrieved object data and beautified in perfect understandable HTML code
            product_code1_page1 = product_code.find("div", {"class": "_1YokD2 _3Mn1Gg"})
            product_code2_page1 = product_code1_page1.find("div", {"class": "col JOpGWq"})
            product_review_page_link = product_code2_page1.find_all("a", {"class": ""})[10]["href"]
            ## Till here we have pulled out review page link of all reviews.

            product_review_page_code1 = "https://www.flipkart.com" + product_review_page_link
            product_review_page_code2 = requests.get(product_review_page_code1)
            product_review_page_code2.encoding = "utf-8"
            product_review_page_code3 = bs(product_review_page_code2.text, "html.parser")
            product_review_page_code4 = product_review_page_code3.find_all("div", {"class": "_1YokD2 _3Mn1Gg col-9-12"})
            product_review_pages_links = product_review_page_code4[0].find_all("a", {"class": "ge-49M"})
            ## Now we have retrieved all pages links of review

            # for testing purpose
            ##review_date=all_review_data[0].find_all("p",{"class":"_2sc7ZR"})[1].text
            ##review_name=all_review_data[0].find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
            ##review_comment_header = product_all_reviews_box[0].find_all("div", {"class": "_2sc7ZR"}).text
            ##review_comment=all_review_data[0].find_all("div",{"class":"t-ZTKy"})[0].div.div.text
            ##review_rating=all_review_data[0].find_all("div",{"class":"_3LWZlK _1BLPMq"})[0].text

            ## Here we have retrieved and appended all data in json format under single veriable

            data_new = []
            for j in range(len(product_review_pages_links)):
                link = product_review_pages_links[j]["href"]
                review_pages_data_link = "https://www.flipkart.com" + link
                retrieve_page = requests.get(review_pages_data_link)
                retrieve_page.encoding = "utf-8"
                bs_retrieve_page = bs(retrieve_page.text, "html.parser")
                bs_retrieve_page_code1 = bs_retrieve_page.find_all("div", {"class": "_1YokD2 _3Mn1Gg col-9-12"})
                product_all_reviews_box = bs_retrieve_page_code1[0].find_all("div", {"class": "_27M-vq"})

                # till here we have retrieve each review box, now at last we have to retrieve data from each box

                for i in range(len(product_all_reviews_box)):
                    date_elem = product_all_reviews_box[i].find_all("p", {
                        "class": "_2sc7ZR"})  # Use find() instead of find_all()
                    if date_elem:
                        date = date_elem[1].text
                    else:
                        date = "No Date"

                    name_elem = product_all_reviews_box[i].find("p", {"class": "_2sc7ZR _2V5EHH"})
                    if name_elem:
                        name = name_elem.text
                    else:
                        name = "No Name"

                    comm_had_elem = product_all_reviews_box[i].find("p", {"class": "_2-N8zT"})
                    if comm_had_elem:
                        comm_had = comm_had_elem.text
                    else:
                        comm_had = "NO Comment Head"

                    comm_elem = product_all_reviews_box[i].find("div", {"class": "t-ZTKy"}).div.div
                    if comm_elem:
                        comm = comm_elem.text
                    else:
                        comm = "NO Comment"

                    rating_elem = product_all_reviews_box[i].find("div", {"class": "_3LWZlK _1BLPMq"})
                    if rating_elem:
                        rating = rating_elem.text
                    else:
                        rating = "No Ratings"

                    review_data = {
                        "Date": date,
                        "Name": name,
                        "Comment Header": comm_had,
                        "Comment": comm,
                        "Ratings": rating
                    }
                    data_new.append(review_data)
            df = pd.DataFrame(data_new)  # data_new converted in data frame and saved as json file
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