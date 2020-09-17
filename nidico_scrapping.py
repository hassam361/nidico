from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import datetime
print("The script is about to start, first urls will be scraped, then products will be scraped.")

requests.packages.urllib3.disable_warnings()
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options,executable_path="./geckodriver.exe")

driver.maximize_window()
driver.get('https://www.nidico.com/shop?page=14')
# click load more button
load_b=True
while(load_b):
    try:
        driver.find_element_by_class_name('dn9KO').click()
    except:
        load_b=False
        
body=driver.find_element_by_class_name('_3_X2Q')
products_li=body.find_elements_by_tag_name('li')
prod_links=[]
for li in products_li:
    try:
        a=li.find_element_by_tag_name('a')
        prod_links.append(a.get_attribute('href'))
        print(a.get_attribute('href'))
    except:
        pass
    

def get_item_details(url):
    page= requests.get(url, verify=False)
    soup = BeautifulSoup(page.content, 'html.parser')
    body=soup.find(class_='_-6UNl')
    
    sku=body.find(class_='_2qrJF igTU-').text
    item['sku']=sku

    p_li=body.find(class_='_28cEs')
    title=p_li.find('strong').text
    title=title.replace('\xa0', ' ')
    item['post_title']=title
    
    
    p_li=p_li.find_all('p')
    
    new_st=[]
    found=False
    for i,p in enumerate(p_li):
       
        if str(p).find('strong') >-1:
            found=True
        if found==True:
            
            new_st.append(p.text+"\n")
            
    new_st=new_st[1:]
    
    new_st=' '.join(new_st)
    item['post_excerpt']=new_st
    


    pr_cl=body.find(class_='_2sFaY')
    price=pr_cl.find(attrs={'data-hook': 'formatted-primary-price'}).text
    item['sale_price']=price

    
    avail=False
    try:
        buy_now=body.find(attrs={'data-hook': 'buy-now-button'}).text
        
        if buy_now=='Buy Now':
            
            item['stock_status']='instock'
            avail=True
    except:
        pass
    if avail == False:
        try:
            out_of_st=body.find(attrs={'class': '_3j0qu fggS- cell'}).text
            item['stock_status']='outofstock'
        except:
            pass
    img_link='https://www.livingfashions.com/wp-content/uploads/products/'+sku.lower()+'.jpg'
    item['img_link']=img_link
    
    
    # save image to file 
    body=soup.find(class_='main-media-image-wrapper-hook')
    orig_img_link=body.div.get('href')
    image_name=sku.lower()+'.jpg'
    file_name= "Images"
    with open(file_name+'\\'+image_name, 'wb') as handler:
        img_data = requests.get(orig_img_link,verify=False).content
        handler.write(img_data)
    
    global page_df
    dFrame=pd.DataFrame.from_dict(item,orient='index')
    df=dFrame.T
    page_df=page_df.append(df,ignore_index=True)
    
    return page_df

item={
    'sku' :"",
    'post_title':"",
    'post_excerpt':"",
    'sale_price':"",
    'stock_status':"",
    'img_link':""
    
}
page_df=pd.DataFrame.from_dict(item,orient='index')
page_df=page_df.T
page_df=page_df[1:]
print('There are total '+str(len(prod_links)) +' products on this website')
for i in range(len(prod_links)):
    get_item_details(prod_links[i])
    print('product-'+str(i+1)+' done..')
time_now=datetime.now().strftime("%Y_%m_%d")
page_df.to_csv('product_import_'+time_now+'.csv',index=False,header=False,encoding='utf-8-sig')
driver.close()
print("All products have been scraped successfully, you may close the exe file ")