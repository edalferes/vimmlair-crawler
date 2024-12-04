import requests
import os
from mongoengine import connect
from src.config import Config
from tqdm import tqdm

config = Config()
connect('game_database', host=config.database_url)


class GameDownloadChecker:
    def __init__(self, console_data):
        """
        Initializes the GameDownloadChecker object with the console data.
        """
        self.console_data = console_data

    async def check_downloadable_games(self):
        """
        Search for downloadable games for the console.
        """
        console_name = self.console_data['name']

        print(
            f"Checking downloadable games for console: {console_name}")

        games = self.get_games_from_console(console_name)

        for game in games:
            print(f"Checking game: {game['GameName']}")

            if self.can_download_game(game):
                print(f"Game {game['GameName']} is downloadable.")
                self.download_game(game)
            else:
                print(f"Game {game['GameName']} is NOT downloadable.")

    def get_games_from_console(self, console_name):
        """
        Get games for the console from the database.
        """
        from src.game_data_extractor import GameDataDocument

        games = GameDataDocument.objects(Console=console_name)

        return [game.to_dict() for game in games]

    def can_download_game(self, game):
        """
        Check if the game is downloadable.
        """
        if game.get('DownloadURL') and game.get('CanBeDownloaded'):
            return True
        return False

    def download_game(self, game):
        """
        Download the game from the download URL.
        """
        media_id = game.get('DownloadParams', {}).get('mediaId')
        download_url = f"https://download2.vimm.net/?mediaId={media_id}"

        if not media_id:
            print(
                f"Not possible to download {game['GameName']}. Missing mediaId.")
            return

        filename = f"{game['GameName']}.zip"

        console_directory = os.path.join('roms', game['Console'])
        if not os.path.exists(console_directory):
            os.makedirs(console_directory)

        save_path = os.path.join(console_directory, filename)

        if os.path.exists(save_path):
            print(f"Arquivo {filename} já existe. Pulando download.")
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': f'https://vimm.net/vault/{game["Console"]}',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
            'Connection': 'keep-alive',
        }

        try:
            print(f"Iniciando download de {filename}...")

            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            with open(save_path, 'wb') as file:
                for chunk in tqdm(response.iter_content(chunk_size=8192),
                                  desc=f"Donwloading: {filename}",
                                  total=total_size // 8192,
                                  unit="KB",
                                  ncols=100):
                    if chunk:
                        file.write(chunk)

            print(f"Download the {filename} completed successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {filename}: {e}")
