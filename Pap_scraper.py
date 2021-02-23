import csv
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen


def get_page(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(url,headers=hdr)
    response = urlopen(req)
    soup = BeautifulSoup(response, 'lxml')
    #print(soup)
    return soup


def get_detail_data(soup):

    try:
        title_price = soup.find('h1', class_ = 'item-title').get_text().strip()
        title, price = title_price.split('				')
    except:
        title = ''
        price = ''
    print('Titre: ' ,title)
    print('Prix: ' ,price)

    try:
        refernce_date = soup.find('p', class_ = 'item-date').get_text().strip()
        reference, date = refernce_date.split(' /  ')
    except:
        reference = ''
        date = ''
    print('Reference: ' , reference)
    print('Date: ' , date)

    try:
        adresse_postal =  soup.find('h2', class_ = 'margin-bottom-8').get_text().strip()
    except:
        adresse_postal = ''
    print('Adresse postal: ' , adresse_postal)

    try:
        surf = soup.find('ul', class_ = 'item-tags margin-bottom-20').findAll('strong')
        if(len(surf) == 3):
            nb_pieces = surf[0].get_text().strip()
            nb_chambres = surf[1].get_text().strip()
            surface = surf[2].get_text().strip()
        else:
            nb_pieces = surf[0].get_text().strip()
            nb_chambres = ''
            surface = surf[1].get_text().strip()
    except:
        nb_pieces = ''
        nb_chambres = ''
        surface = ''
    print('nb pieces: ' , nb_pieces)
    print('nb chambres: ' , nb_chambres)
    print('Surface: ' , surface)

    try:
        description = soup.find('div', class_ = 'item-description margin-bottom-30').get_text().replace('\t','').strip().replace('\n','').split('\r')
        description = description[2]
    except:
        description = ''
    print('Description: ', description)
    
    try:
        stations = [station.get_text() for station in soup.find_all('span', class_ = 'label')]
         # supprimer la redundance des stations dans la description:
        for station in stations:
            description = description.replace(station,'').strip()
    except:
        stations = ''
    print('Stations', stations)

    try:
        garentie = description.split('Dépot de garantie :')[1]
        # supprimer le depot de garentie dans la description:
        description = description.replace('Dépot de garantie :' + garentie,'').strip()
        #print('Description: ', description)
    except:
        garentie = ''
    print('Garentie: ', garentie)

    try:
        tel_proprietaire = soup.find('p', class_ = 'h3 txt-indigo').get_text().strip()
        if(len(tel_proprietaire)> 14):
            # il existe 2 numero !
            tel_proprietaire = tel_proprietaire.replace(tel_proprietaire[13],tel_proprietaire[13] + ' ').strip()
    except:
        tel_proprietaire = ''
    print('Tel :', tel_proprietaire)

    data = {
        'titre' : title,
        'prix' : price,
        'date' : date,
        'adresse postal' : adresse_postal,
        'nb_pieces': nb_pieces,
        'nb_chambres' : nb_chambres,
        'surface' : surface,
        'stations' : stations,
        'garentie' : garentie,
        'telephone' : tel_proprietaire,
        'description' : description
    }

    return data


def get_index_data(soup):
    try:
        links = soup.findAll('a', class_ = 'item-title')
    except:
        links = []

    urls = [item.get('href') for item in links]
    #print(urls)

    # ajouter 'https://www.pap.fr/' aux liens commencant par '/annonces/...
    for i in range (0,len(urls)):
        if (urls[i][0:1] == '/'):
            urls[i] = 'https://www.pap.fr' + urls[i]
    print(urls)

    return urls


def write_en_tete_csv():
    with open('output.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        row = ['Titre','Loyer','Garentie','Date publication','Téléphone propriétaire','Adresse postale','Nombre de pièces','Nombre de chambres','Surface','Stations metro','Description','URL']
        writer.writerow(row)


def write_data_csv(data, url):
    with open('output.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        row = [data['titre'], data['prix'], data['garentie'], data['date'], data['telephone'], data['adresse postal'], data['nb_pieces'], data['nb_chambres'] ,data['surface'], data['stations'], data['description'], url]
        writer.writerow(row)


def main():
    url = 'https://www.pap.fr/annonce/location-appartement-maison-paris-9e-g37776-jusqu-a-800-euros'
    urls = get_index_data(get_page(url))
    write_en_tete_csv()
    # il existe 17 pages en tout
    for i in range(1,17):
        url = url + '-' + str(i)
        for url in urls:
            data = get_detail_data(get_page(url))
            write_data_csv(data,url)
        url = 'https://www.pap.fr/annonce/location-appartement-maison-paris-9e-g37776-jusqu-a-800-euros'

if __name__ == "__main__":
    main()
