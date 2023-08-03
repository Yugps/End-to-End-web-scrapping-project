from bs4 import BeautifulSoup as bs 
from flask import Flask,render_template,request,jsonify 
from flask_cors import CORS,cross_origin
from urllib.request import urlopen 
import logging
import pymongo

logging.basicConfig(filename='project.log',level=logging.DEBUG,format='%(asctime)s %(name)s %(levelname)s %(message)s')

app=Flask(__name__)
@app.route('/',methods=['GET'])
@cross_origin() # This will make sure that server can be accessed in any region globally
def home_page():
    logging.info(msg='home page has been rendered')
    return render_template('index.html')

@app.route('/review',methods=['POST'])
@cross_origin() # This will make sure that server can be accessed in any region globally
def main_function():
    if request.method=='POST':
        Product=request.form['content'].replace(' ','')
        logging.info(msg='search string has been obtained')
        flipkart_url='https://www.flipkart.com/search?q='+Product
        flipkart_page=urlopen(flipkart_url)
        flipkart_html=bs(flipkart_page,'html.parser')
        big_boxes=flipkart_html.find_all('div',{'class':"_1AtVbE col-12-12"})
        del big_boxes[0:3]
        productlink='https://www.flipkart.com'+big_boxes[0].div.div.div.a['href']
        product_page=urlopen(productlink)
        product_html=bs(product_page,'html.parser')
        commenter_remarks=product_html.find_all('div',{'class':'_16PBlm'})
        try:
            commenter_remarks_text=[]
            for i in commenter_remarks:
                commenter_remarks_text.append(str(i.div.div.div.p.text))
            logging.info(msg='comment headers done')
        except Exception as e:
            logging.error(msg='error handled for nonetype object')
        commenter_names=product_html.find_all('div',{'class':'row _3n8db9'})
        commenter_names_text=[]
        for i in commenter_names:
            commenter_names_text.append(i.div.p.text)
        logging.info(msg='Name of the reviewers done')
        comments=product_html.find_all('div',{'class':'t-ZTKy'})
        comments_text=[]
        for i in comments:
            comments_text.append(i.div.div.text)
        logging.info(msg='comments done')
        ratings=product_html.find_all('div',{'class':'_16PBlm'})
        ratings_text=[]
        try:
            for i in ratings:
                ratings_text.append(i.div.div.div.div.text)
            logging.info('ratings being done')
        except Exception as e:
            logging.error(msg='NoneType error handled perfectly')
        reviews=[]
        for j,k,l,m in zip(commenter_names_text,ratings_text,commenter_remarks_text,comments_text):
            my_dict={'Product':Product,'Name':j,'Rating':k,'CommentHead':l,'Comment':m,'Comment':m}
            reviews.append(my_dict)
        logging.info(msg='seperate dictionaries have been created for all the headers')
        review={'Product':Product,
               'Name':commenter_names_text,
               'Rating':ratings_text,
               'CommentHead':commenter_remarks_text,
                'Comment':comments_text}
    client=pymongo.MongoClient("mongodb+srv://yugpratapsingh:313ycd014916@cluster0.25gtiu5.mongodb.net/?retryWrites=true&w=majority")
    db=client['webScrappingFlipkart']
    collection=db['search data on reviews']
    collection.insert_many(reviews)
    
    return render_template('result.html',reviews= reviews)
    logging.info(msg='result template has been rendered')

    # Here we enter all the data into our mongo db database
    
if __name__=='__main__':
    app.run(host='0.0.0.0')

