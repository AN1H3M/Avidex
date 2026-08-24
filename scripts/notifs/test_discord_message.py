from scripts.notifs.discord_message import *

def main():
    send_discord_message("Test message.", username="Bird Scraper Test")

    print("Discord message sent")

if __name__ == "__main__":
    main()