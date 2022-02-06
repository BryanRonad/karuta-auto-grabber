from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import cv2
import numpy
import requests
import io
import PIL.Image

#Function to find card pattern in image and return index
def card_index(src):
    #Get image from url
    response = requests.get(src)
    image_bytes = io.BytesIO(response.content)
    pil_image = PIL.Image.open(image_bytes).convert('RGB') 
    open_cv_image = numpy.array(pil_image) 
    open_cv_image = open_cv_image[:, :, ::-1].copy() 
    height, width, dimensions = open_cv_image.shape

    #Finding number of cards in image    
    canvas = numpy.zeros(open_cv_image.shape, numpy.uint8)
    img2gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cont in contours:
        cv2.drawContours(canvas, cont, -1, (0, 255, 0), 3)
    # cv2.imwrite('thresh.png', thresh)
    # cv2.imwrite('test.png', canvas)
    cards_in_image = (len(contours))
    if(int(cards_in_image%3)==0 and int(cards_in_image/3)>1):
        cards_in_image=3
    elif(int(cards_in_image%3)==1):
        cards_in_image=4
    print(f"There are {cards_in_image} cards in this picture.")

    #Template matching
    threshold = 0.85
    #Common cards count
    template = cv2.imread('ed3.png')
    h, w = template.shape[:-1]
    res = cv2.matchTemplate(open_cv_image, template, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(res >= threshold)
    # Switch collumns and rows
    card_index = 0
    # for pt in zip(*loc[::-1]):
    pt = zip(*loc[::-1]) 
    pt = list(pt)[0]
    cv2.rectangle(open_cv_image, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    cv2.imwrite('result.png', open_cv_image)
    card_index = int(pt[0]/(width/cards_in_image))
    if card_index+1>0:
        return card_index
    return 'null'


PATH = r"C:\Users\bryan\OneDrive\Documents\Practice\Selenium\chromedriver.exe"
driver = webdriver.Chrome(PATH)

driver.get("server channel url")

#Login to discord
email = driver.find_element(By.NAME, "email")
password = driver.find_element(By.NAME, "password")
email.send_keys("email")
password.send_keys("password")
password.send_keys(Keys.RETURN)
wait = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.TAG_NAME, 'li')))

#Last message loop
last_message_id = ""
while True:
    try:
        #Checking if message is new
        message = driver.find_elements(By.TAG_NAME, "li")[-1]
        message_id = message.get_property('id')        
        if(last_message_id == message_id):
            continue
        else:
            # print(message_id)
            last_message_id = message_id
            #Getting message innerHTML
            message_content = message.find_element(By.ID, str(message_id).replace("chat-messages-", "message-content-"))
            # print(str(message_content.get_property("innerHTML")))  
            if('@username</span>, you must' in str(message_content.get_property("innerHTML"))):
                print("Waiting for 15 seconds...")
                time.sleep(15) 
            if('@username</span> took' in str(message_content.get_property("innerHTML")) or '@username</span> fought' in str(message_content.get_property("innerHTML"))):
            # if('@username' in str(message_content.get_property("innerHTML"))):
                print("Hit")
                if('fought off "<span class="mention wrapper-1ZcZW- mention interactive" aria-controls="popout_196" aria-expanded="false" tabindex="0" role="button">@username' not in str(message_content.get_property("innerHTML"))):
                    print("Waiting for 10.5 minutes...")
                    time.sleep(630)
            try:
                #Getting message image
                accessories = str(message_id).replace("chat-messages-", "message-accessories-")   
                image = driver.find_element(By.XPATH, f"//div[@id='{accessories}']/div[@class='messageAttachment-CZp8Iv']/a")
                print('Image found', image.get_property('href'))
                cindex = card_index(image.get_property('href'))
                print(f"Rare card at {cindex+1} index")

                #Find appropriate reaction
                reaction = driver.find_elements(By.XPATH, f"//div[@id='{accessories}']/div[@class='container-3Sqbyb']/div/div/button")
                print(f"Clicking the button!")
                time.sleep(1.1)
                click = list(reaction)[cindex].click()

            except:
                print("No image")
    except:
        continue