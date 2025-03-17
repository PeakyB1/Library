import fb2reader
from bs4 import BeautifulSoup

 
if __name__ == "__main__":
    symbols = 1000
    file_path = 'media/books/Война и мир.fb2'
    with open('media/books/Война и мир.fb2', 'r', encoding='utf-8') as fb2_file:
        soup = BeautifulSoup(fb2_file, "xml")
    
    section = soup.find('section', id='id20160101081932_793')

    if section:
        print(section)  
    else:
        print("Секция не найдена")