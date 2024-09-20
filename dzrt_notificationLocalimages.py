import os
import json
import requests
from bs4 import BeautifulSoup
import time

# Global list to store product names that are successfully sent
sent_products = []
# Dictionary to store the time each product was last sent
product_send_times = {}
# List of products that have special handling
special_products = ["بيربل مست", "هايلاند بيريز", "سبايسي زيست", "هيلة", "تمرة", "جاردن منت", "إيدجي منت", "سمرة", "ايسي رش", "سي سايد فروست", "منت فيوجن", ""]
# List of products to exclude from sending
excluded_products = []
# Variable to store the time of the last clearing of the sent_products list
last_clear_time = time.time()

# Function to fetch URL content with retries
def fetch_url_with_retry(url, max_retries=7, delay=1):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
        retries += 1
        time.sleep(delay)
    print(f"Max retries reached for URL: {url}")
    return None

# Function to send product data to Telegram
def send_product_data_to_telegram():
    global sent_products, last_clear_time, product_send_times
    url = "https://www.dzrt.com/ar-sa/products"
    html_content = fetch_url_with_retry(url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        product_divs = soup.find_all("div", class_="relative bg-white px-2.5 pb-3 pt-6")
        product_data_list = []
        for product_div in product_divs:
            product_name = product_div.find("span", class_="text-3.5 font-bold leading-5 text-custom-black-900").text.strip()
            add_to_cart_button = product_div.find("button", class_="inline-flex w-full items-center justify-center whitespace-nowrap shadow-xs rounded-0.5 font-semibold ring-offset-white transition-colors focus-visible:outline-none disabled:pointer-events-none dark:ring-offset-gray-950 dark:focus-visible:ring-gray-300 bg-custom-black-900 !text-custom-neutral-200 hover:bg-black-900/90 dark:bg-black-50 dark:text-black-900 dark:hover:bg-black-50/90 disabled:bg-custom-gray-400 focus-visible:ring-3 focus-visible:ring-purple-400 focus-visible:ring-opacity-25 focus-visible:ring-offset-0 h-11 px-4 py-2.5 text-4 mt-2.5 rounded-0.5 disabled:!bg-custom-black-900 disabled:!text-custom-gray-600")
            product_status = "متوفر" if not add_to_cart_button.has_attr('disabled') else "غير متوفر"

            # Construct the image file path relative to the script's location
            script_dir = os.path.dirname(__file__)
            image_file_path = os.path.join(script_dir, f"{product_name}.png")  # Assuming images are .png

            product_url = product_div.find("a")['href']
            if product_name and product_status:
                product_info = {
                    "name": product_name,
                    "status": product_status,
                    "image_file_path": image_file_path,
                    "url": f"https://www.dzrt.com{product_url}"
                }
                product_data_list.append(product_info)
                print(f"Product Name: {product_name}")
                print(f"Product Status: {product_status}")
                print(f"Image File Path: {image_file_path}")
                print("-" * 50)

        bot_token = "6958486146:AAFtYb_TaInJtSSFevXDn39BCssCzj4inV4"
        chat_id = "-1002411379455"
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

        for product_data in product_data_list:
            product_name = product_data.get("name", "")
            product_status = product_data.get("status", "")
            product_url = product_data.get("url", "")
            image_file_path = product_data.get("image_file_path", "")

            if product_status == "غير متوفر" and product_name not in excluded_products:
                current_time = time.time()
                if product_name in special_products:
                    if (product_name not in sent_products) or (current_time - product_send_times.get(product_name, 0) >= (3 * 600)):
                        message_text = f"✅ ** المنتج متاح ** ✅: {product_name}"
                        reply_markup = {
                            "inline_keyboard": [
                                [{"text": "🔍 عرض المنتج", "url": product_url}, {"text": "🛒 عرض السلة", "url": "https://www.dzrt.com/ar/checkout/cart"}],
                                [{"text": "🔐 تسجيل الدخول", "url": "https://www.dzrt.com/ar/customer/account/login/"}, {"text": "💳 الانتقال إلى رابط الدفع النهائي", "url": "https://www.dzrt.com/ar/onestepcheckout.html"}]
                            ]
                        }
                        if os.path.exists(image_file_path):
                            with open(image_file_path, 'rb') as image_file:
                                files = {'photo': image_file}
                                params = {
                                    "chat_id": chat_id,
                                    "caption": message_text,
                                    "reply_markup": json.dumps(reply_markup)
                                }
                                response = requests.post(telegram_api_url, data=params, files=files)
                                if response.status_code == 200:
                                    print(f"Product data sent successfully for {product_name}")
                                    sent_products.append(product_name)
                                    product_send_times[product_name] = current_time
                                else:
                                    print(f"Failed to send product data for {product_name}. Status code: {response.status_code}")
                        else:
                            print(f"Image file not found for {product_name}")
                else:
                    if product_name not in sent_products:
                        message_text = f"✅ ** المنتج متاح ** ✅: {product_name}"
                        reply_markup = {
                            "inline_keyboard": [
                                [{"text": "🔍 عرض المنتج", "url": product_url}, {"text": "🛒 عرض السلة", "url": "https://www.dzrt.com/ar/checkout/cart"}],
                                [{"text": "🔐 تسجيل الدخول", "url": "https://www.dzrt.com/ar/customer/account/login/"}, {"text": "💳 الانتقال إلى رابط الدفع النهائي", "url": "https://www.dzrt.com/ar/onestepcheckout.html"}]
                            ]
                        }
                        if os.path.exists(image_file_path):
                            with open(image_file_path, 'rb') as image_file:
                                files = {'photo': image_file}
                                params = {
                                    "chat_id": chat_id,
                                    "caption": message_text,
                                    "reply_markup": json.dumps(reply_markup)
                                }
                                response = requests.post(telegram_api_url, data=params, files=files)
                                if response.status_code == 200:
                                    print(f"Product data sent successfully for {product_name}")
                                    sent_products.append(product_name)
                                else:
                                    print(f"Failed to send product data for {product_name}. Status code: {response.status_code}")
                        else:
                            print(f"Image file not found for {product_name}")

        if time.time() - last_clear_time >= 60:
            sent_products = [product for product in sent_products if product in special_products]
            last_clear_time = time.time()

# Main loop to run the code every minute
while True:
    send_product_data_to_telegram()
    time.sleep(10)
