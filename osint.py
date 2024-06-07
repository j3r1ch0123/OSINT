#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
import requests
import re
import time
import threading
import urllib.parse
from bs4 import BeautifulSoup

# Helper function to validate and get URL content
def get_url_content(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

# define function for finding email addresses
def find_emails(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    emails = set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text))
    return emails

# define function for finding phone numbers
def find_phone_numbers(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    phone_numbers = set(re.findall(r"\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", text))
    return phone_numbers

# define function for finding IP addresses
def find_ip_addresses(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    ip_addresses = set(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text))
    return ip_addresses

# define function for finding names
def find_names(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    names = set(re.findall(r"\b[A-Z][a-z]+\b", text))
    return names

# define function for finding links
def find_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = set(a.get('href') for a in soup.find_all('a', href=True))
    return links

# define function for finding social media profiles
def find_social_media_profiles(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    social_media_profiles = set(re.findall(r"(https?://\S+)", text))
    return social_media_profiles

# define function to save images
def save_images(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    images = set(img['src'] for img in soup.find_all('img', src=True))
    for image_url in images:
        image_url = urllib.parse.urljoin(base_url, image_url)
        image_name = image_url.split("/")[-1]
        try:
            urllib.request.urlretrieve(image_url, image_name)
            print("Image saved as", image_name)
            time.sleep(1)
        except Exception as e:
            print(f"Error saving image {image_url}: {e}")
    return images

# define the main scraping function
def run(url, base_url):
    html = get_url_content(url)
    if html:
        emails = find_emails(html)
        print("Email addresses:", emails)
        phone_numbers = find_phone_numbers(html)
        print("Phone numbers:", phone_numbers)
        ip_addresses = find_ip_addresses(html)
        print("IP addresses:", ip_addresses)
        social_media_profiles = find_social_media_profiles(html)
        print("Social media profiles:", social_media_profiles)
        names = find_names(html)
        print("Names:", names)
        links = find_links(html)
        print("Links:", links)
        images = save_images(html, base_url)
        print("Images:", images)
        with open("outfile.txt", "a") as thefile:
            thefile.write("URL: " + url + "\n")
            thefile.write("Emails: " + str(emails) + "\n")
            thefile.write("Phone numbers: " + str(phone_numbers) + "\n")
            thefile.write("IP addresses: " + str(ip_addresses) + "\n")
            thefile.write("Social media profiles: " + str(social_media_profiles) + "\n")
            thefile.write("Names: " + str(names) + "\n")
            thefile.write("Links: " + str(links) + "\n")
        return links  # return the links for further processing
    return []

# define main function
def main():
    base_url = input("Enter the base URL you'd like to scrape: ")
    to_scrape = [base_url]
    scraped = set()

    while to_scrape:
        url = to_scrape.pop(0)
        if url not in scraped:
            scraped.add(url)
            links = run(url, base_url)
            for link in links:
                # Resolve relative links
                full_link = urllib.parse.urljoin(base_url, link)
                if full_link not in scraped:
                    to_scrape.append(full_link)

# call main function
if __name__ == "__main__":
    # use threads to scrape multiple URLs in parallel
    threads = []
    for i in range(20):
        thread = threading.Thread(target=main)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

