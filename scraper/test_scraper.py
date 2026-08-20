from bird_scraper import *

birds = [("Bald Eagle","Haliaeetus leucocephalus"), ("American Crow", "Corvus brachyrhynchos")]

def main():
    try: 
        search_for_birds(birds,"https://birdsoftheworld.org/bow/home")

    except Exception as error:
        print("Scraping failed:")
        print(error)
if __name__ == "__main__":
    main()