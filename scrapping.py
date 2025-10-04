import requests
from bs4 import BeautifulSoup
import os

def scrape_paris_fashion_houses():
    url="https://www.fhcm.paris/en/paris-fashion-week/maisons"

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        fashion_houses = []
        house_links = soup.find_all('a', class_='house offscreen')
        
        # Each house is like this:
        # <a href="/fr/maison/anrealage" class="house shown" data-img="https://www.fhcm.paris/sites/default/files/styles/hlarge/public/houses/83af052f3535-morinaga_color_1_.jpg?itok=C4_Xi4Vp" data-emerg="0" data-hc="0" data-hj="0" data-ww="3" data-mw="0" style="transition-delay: 0.493902s;">ANREALAGE</a>

        for div in house_links:
            name = div.text.strip()
            fashion_houses.append(name)

        if fashion_houses:
            return fashion_houses
        return []
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def save_houses_to_file(houses, filename="paris_fashion_houses.csv"):
    try:
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        with open(filepath, 'w') as f:
            for house in houses:
                f.write(f"{house}\n")
        print(f"Saved {len(houses)} fashion houses to {filepath}")

    except Exception as e:
        print(f"Error saving to file: {e}")
    
def main():
    print("Scraping Paris Fashion Houses...")
    houses = scrape_paris_fashion_houses()
    if houses:
        print(f"Found {len(houses)} fashion houses:")
        for house in houses:
            print(f"- {house}")
    else:
        print("No fashion houses found.")

    save_houses_to_file(houses)
    
if __name__ == "__main__":
    main()


    
            
        