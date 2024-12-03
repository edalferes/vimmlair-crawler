import asyncio
from dataclasses import asdict
from src.game_data_extractor import GameDataExtractor
from src.console_data_extractor import ConsoleDataExtractor


async def main():

    url_console = 'https://vimm.net/vault'
    crawler = ConsoleDataExtractor(url_console)
    consoles = await crawler.request_site()

    url_game = 'https://vimm.net/vault/8638'
    extractor = GameDataExtractor(url_game)
    game_data = await extractor.request_site()


if __name__ == '__main__':
    asyncio.run(main())
