import asyncio
from dataclasses import asdict
from src.data_extractor import GameDataExtractor
from src.vault_page_crawler import VaultPageCrawler


async def main():
    # url = 'https://vimm.net/vault/7461'
    # extractor = GameDataExtractor(url)
    # game_data = await extractor.request_site()

    url = 'https://vimm.net/vault'
    crawler = VaultPageCrawler(url)
    consoles, handhelds = await crawler.fetch_page()

    print("Consoles:")
    for console in consoles:
        print(f"{console['name']} ({console['year']}): {console['url']}")

    print("\nHandhelds:")
    for handheld in handhelds:
        print(f"{handheld['name']} ({handheld['year']}): {handheld['url']}")

if __name__ == '__main__':
    asyncio.run(main())
