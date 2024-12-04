import asyncio
from dataclasses import asdict
from src.game_data_extractor import GameDataExtractor
from src.console_data_extractor import ConsoleDataExtractor


async def main():

    url_console = 'https://vimm.net/vault'
    crawler = ConsoleDataExtractor(url_console)
    await crawler.request_site()


if __name__ == '__main__':
    asyncio.run(main())
