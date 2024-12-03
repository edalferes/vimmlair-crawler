import asyncio
from src.data_extractor import GameDataExtractor
from src.downloader import GameDownloader


async def main():
    url = 'https://vimm.net/vault/7263'
    extractor = GameDataExtractor(url)
    game_data = await extractor.request_site()

    if game_data.CanBeDownloaded:
        downloader = GameDownloader(
            game_data.DownloadURL, game_data.DownloadParams)
        # certifique-se de que o caminho é acessível
        await downloader.download_game('./data')

if __name__ == '__main__':
    asyncio.run(main())
