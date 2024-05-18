import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

with open("data.json", "w") as f:
    json.dump([], f)

def write_json(new_data, filename='data.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

browser = webdriver.Chrome()
browser.get('https://www.lazada.co.th/shop-mobiles/?spm=a2o4m.searchlist.breadcrumb.3.61182d53HVAT55')

isNextDisabled = False

while not isNextDisabled:
    try:
        element = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#root > div > div.ant-row.FrEdP.css-17lv24q.app > div:nth-child(1) > div > div.ant-col.ant-col-20.ant-col-push-4.Jv5R8.css-17lv24q.app > div._17mcb')))
        
        category = element.find_element(By.XPATH, '//*[@id="J_breadcrumb"]/li[2]').text
        sub_category = element.find_element(By.XPATH, '//*[@id="J_breadcrumb"]/li[3]').text
        page = element.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div[1]/div[3]/div/ul/li[8]').text
        
        print(page, "Page")
        print(category, "Category")
        print(sub_category, "Sub Category")
        
        page = int(page)
        
        for i in range(1, page):
            items = element.find_elements(By.XPATH, '//div[@data-qa-locator="product-item"]')
            for item in items:
                title = item.find_element(By.CSS_SELECTOR, 'div.RfADt').text
                price = item.find_element(By.CSS_SELECTOR, 'div.aBrP0 > span').text
                img = item.find_element(By.TAG_NAME, 'img').get_attribute('src')
                print("Title: " + title)
                print("Price: " + price)
                # print("Image: " + img)
                
            print(i, "Page")
            browser.get(f'https://www.lazada.co.th/shop-mobiles/?page={i}')

            print("Next Clicked")
    except Exception as e:
        print(e, "Main Error")
        isNextDisabled = True
        break

# while not isNextDisabled:
#     try:
#         element = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
#             (By.XPATH, '/html/body/div[3]/div/div[2]/div[1]/div/div[1]/div[2]')))

#         print(element)
#         elem_list = browser.find_element(
#             By.CSS_SELECTOR, "div.s-main-slot.s-result-list.s-search-results.sg-row")

#         items = elem_list.find_elements(
#             By.XPATH, '//div[@data-component-type="s-search-result"]')

#         for item in items:
#             title = item.find_element(By.TAG_NAME, 'h2').text
#             price = "No Price Found"
#             img = "No Image Found"
#             link = item.find_element(
#                 By.CLASS_NAME, 'a-link-normal').get_attribute('href')

#             try:
#                 price = item.find_element(
#                     By.CSS_SELECTOR, '.a-price').text.replace("\n", ".")
#             except:
#                 pass

#             try:
#                 img = item.find_element(
#                     By.CSS_SELECTOR, '.s-image').get_attribute("src")
#             except:
#                 pass

#             print("Title: " + title)
#             print("Price: " + price)
#             print("Image: " + img)
#             print("Link: " + link + "\n")

#             write_json({
#                 "title": title,
#                 "price": price,
#                 "image": img,
#                 "link": link
#             })


#         next_btn = WebDriverWait(browser, 10).until(EC.presence_of_element_located(
#             (By.CLASS_NAME, 's-pagination-next')))

#         next_class = next_btn.get_attribute('class')

#         if "disabled" in next_class:
#             isNextDisabled = True
#         else:
#             browser.find_element(By.CLASS_NAME, 's-pagination-next').click()

#     except Exception as e:
#         print(e, "Main Error")
#         isNextDisabled = True
