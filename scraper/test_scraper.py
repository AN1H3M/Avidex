from bird_scraper import *

birds = [("Bald Eagle","Haliaeetus leucocephalus"), ("American Crow", "Corvus brachyrhynchos")]

def main():
    try: 
        search_for_birds(birds)

    except Exception as error:
        print("Scraping failed:")
        print(error)
if __name__ == "__main__":
    main()