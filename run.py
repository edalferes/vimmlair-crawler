import asyncio
from dataclasses import asdict
from src.data_extractor import GameDataExtractor


async def main():
    url = 'https://vimm.net/vault/15704'
    extractor = GameDataExtractor(url)
    game_data = await extractor.request_site()

    # Print game data dict dataclass
    print(asdict(game_data))

if __name__ == '__main__':
    asyncio.run(main())
