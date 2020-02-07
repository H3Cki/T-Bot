from bs4 import BeautifulSoup
import requests
import json

def get_google_img(query):
    return "https://thenypost.files.wordpress.com/2019/12/dinosaur-feature.jpg"
    url = "https://www.google.com/search?q=" + str(query) + "&source=lnms&tbm=isch"
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    try:
        html = requests.get(url, headers=headers).text
    except requests.ConnectionError:
        print("couldn't reach google")
        return None

    soup = BeautifulSoup(html, 'html.parser')
    image = soup.find("div",{"class":"rg_meta"})

    try:
        link = json.loads(image.text)["ou"]
        return link
    except AttributeError:
        print("     couldn't find any images")
        return None
    except ValueError:
        print("ill formated json")
        return None
    

if __name__ == '__main__':
    query = input("search term\n")
    print(get_google_img(query))