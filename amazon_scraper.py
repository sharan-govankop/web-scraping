import requests
from bs4 import BeautifulSoup
import csv

def get_product_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    product_list = []

    for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
        product_url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal'})['href']
        product_name = product.find('span', {'class': 'a-size-medium'}).text.strip()
        product_price = product.find('span', {'class': 'a-offscreen'}).text.strip()
        rating = product.find('span', {'class': 'a-icon-alt'})
        if rating:
            rating = rating.text.split()[0]
        else:
            rating = 'Not available'
        num_reviews = product.find('span', {'class': 'a-size-base'}).text.strip()
        product_list.append([product_url, product_name, product_price, rating, num_reviews])

    return product_list

def get_additional_info(product_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize the variables with default values
    description = 'Not available'
    asin = 'Not available'
    product_description = 'Not available'
    manufacturer = 'Not available'

    # Update the variables only if the elements are found
    description_element = soup.find('meta', {'name': 'description'})
    if description_element:
        description = description_element.get('content', 'Not available')

    asin_element = soup.find('th', {'class': 'prodDetAttr'})
    if asin_element:
        asin = asin_element.text.strip()

    product_description_element = soup.find('span', {'class': 'a-list-item'})
    if product_description_element:
        product_description = product_description_element.text.strip()

    manufacturer_element = soup.find('a', {'id': 'bylineInfo'})
    if manufacturer_element:
        manufacturer = manufacturer_element.text.strip()

    return [description, asin, product_description, manufacturer]


def main():
    base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"
    num_pages = 20

    # Part 1: Scrape product info
    all_products = []
    for page in range(1, num_pages + 1):
        url = base_url.format(page)
        products = get_product_info(url)
        all_products.extend(products)

    # Part 2: Fetch additional info
    for product in all_products:
        product_url = product[0]
        additional_info = get_additional_info(product_url)
        product.extend(additional_info)

    # Save data to CSV
    with open('amazon_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews',
                         'Description', 'ASIN', 'Product Description', 'Manufacturer'])
        writer.writerows(all_products)

if __name__ == "__main__":
    main()
