from flask import Flask ,render_template, request, jsonify
import json
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask_sqlalchemy import SQLAlchemy
from datetime import date



app = Flask(__name__,instance_relative_config=False)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1 ,x_proto=1)
app.secret_key = os.urandom(30)
analyzer = SentimentIntensityAnalyzer()
db = SQLAlchemy()
uri = "postgresql://postgres:postgres@localhost/news"
app.config['SQLALCHEMY_DATABASE_URI'] = uri

class News(db.Model):
    __tablename__ = 'news_info'
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    link = db.Column(db.String(128),nullable=False,primary_key=True)
    img = db.Column(db.String(128),nullable=False)
    date_ = db.Column(db.Date,nullable=False)

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()
init_db()



def get_data():
    news_desc = [] 
    news_title = [] 
    img = []
    news_link = []
    parsed_news=[]
    for i in range(1,10):
        web_url = "https://www.ndtv.com/latest/page-"+str(i)
        req = requests.get(web_url,headers={'user_agent':'my-app/0.0.1'})   
        soup = BeautifulSoup(req.text,'html.parser')
        
        news_desc.append(soup.find_all(class_ = 'newsCont'))
        news_title.append(soup.find_all(class_ = 'newsHdng'))
        img.append(soup.select('.news_Itm-img img'))
        news_link.append(soup.select('.news_Itm-itm a'))

    new_desc=[]
    new_title=[]
    img_url=[]
    links = []
    for i in range(0,9):
        n = len(news_desc[i])
        for j in range(0,n):
            new_desc.append(news_desc[i][j].get_text())
            new_title.append(news_title[i][j].get_text())
            img_url.append(img[i][j]['src'])
            links.append(news_title[i][j])
    for i in range(len(new_desc)):
        parsed_news.append([new_title[i],new_desc[i],img_url[i],links[i]])

    return parsed_news
    

@app.route('/',methods=['GET','POST'])
def index():       
    return render_template('base.html')

@app.route('/getNews',methods=['GET','POST'])
def get_sentiment():
    parsed_news= get_data()
    df = pd.DataFrame(parsed_news,columns = ['title','desc','img','link'])
    df['link'] = df['link'].apply(lambda x: x.select('a')[0]['href'])
    df['score'] = df['desc'].apply(lambda x:analyzer.polarity_scores(x)['compound'])
    df = df[df['desc'].str.contains('positive')==False]
    df = df[df['desc'].str.contains('COVID-19   -',flags= re.IGNORECASE)==False]
    df = df[df.score > 0.2]
    df = df.reset_index(drop=True)
    for i in range(len(df['desc'])):
        try:
            info = News(title=df['title'][i],description=df['desc'][i],link=df['link'][i],img = df['img'][i],date_ = date.today())
            db.session.add(info)
            db.session.commit()
        except Exception as e:
            print(e)	       
    result = df.to_json(orient="columns")
    ans = json.loads(result)
    return ans


if __name__ == '__main__':
    app.run(debug=True)     