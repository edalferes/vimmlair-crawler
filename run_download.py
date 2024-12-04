import asyncio
from src.game_download_checker import GameDownloadChecker


async def main():

    # Console data this time is a dictionary with the name of the console
    console_data = {'name': 'GameCube'}

    # Creating the GameDownloadChecker object
    download_checker = GameDownloadChecker(console_data)

    # Veryfing if the games are downloadable
    await download_checker.check_downloadable_games()


if __name__ == '__main__':
    asyncio.run(main())
