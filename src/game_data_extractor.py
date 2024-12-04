import aiohttp
import base64
from bs4 import BeautifulSoup
from mongoengine import connect, Document, StringField, FloatField, BooleanField, DictField, NotUniqueError
from src.config import Config


# Configuração para conexão com o banco de dados MongoDB
config = Config()
connect('game_database', host=config.database_url)


# Apenas a classe GameDataDocument, sem a necessidade de GameData (dataclass)
class GameDataDocument(Document):
    # Campos para representar os dados de jogos
    Region = StringField(required=False)
    Players = StringField(required=False)
    Year = StringField(required=False)
    Publisher = StringField(required=False)
    Serial = StringField(required=False)
    Graphics = FloatField(required=False)
    Sound = FloatField(required=False)
    Gameplay = FloatField(required=False)
    Format = StringField(required=False)
    Version = StringField(required=False)
    GameName = StringField(required=False, unique=True)
    Console = StringField(required=False)
    CanBeDownloaded = BooleanField(required=False, default=False)
    DownloadURL = StringField(required=False)
    DownloadParams = DictField(required=False)

    meta = {
        'collection': 'games',
        'indexes': [
            'GameName',  # Garantir que há um índice único em GameName
        ]
    }

    def to_dict(self):
        """
        Converte o documento para um dicionário.
        """
        return {
            "Region": self.Region,
            "Players": self.Players,
            "Year": self.Year,
            "Publisher": self.Publisher,
            "Serial": self.Serial,
            "Graphics": self.Graphics,
            "Sound": self.Sound,
            "Gameplay": self.Gameplay,
            "Format": self.Format,
            "Version": self.Version,
            "GameName": self.GameName,
            "Console": self.Console,
            "CanBeDownloaded": self.CanBeDownloaded,
            "DownloadURL": self.DownloadURL,
            "DownloadParams": self.DownloadParams
        }


class GameDataExtractor:
    def __init__(self, url):
        self.url = url

    async def request_site(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                content = await response.read()
                game_data = self.extract_data(content)
                # Salve os dados no MongoDB
                self.save_to_mongodb(game_data)
                return game_data

    def extract_data(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Extract game name and console name
        console = soup.find('div', {'class': 'sectionTitle'})
        game_name = None
        console_name = None
        if console:
            console_name = console.text.strip()
            canvas = console.find_next('canvas')
            if canvas:
                data_v_base64 = canvas['data-v']
                game_name = base64.b64decode(data_v_base64).decode('utf-8')

        # Verify if download is possible
        download_form = soup.find('form', id='dl_form')
        download_possible = bool(download_form)
        download_url = None
        download_params = {}
        if download_possible:
            download_url = download_form['action']
            # Check if download_url starts with "//" and add "https:"
            if download_url and download_url.startswith("//"):
                download_url = "https:" + download_url

            # Extract download form parameters
            for input_tag in download_form.find_all('input'):
                if input_tag.has_attr('name'):
                    download_params[input_tag['name']
                                    ] = input_tag.get('value', '')

        # Extract table data
        table_data = self.extract_table_data(soup)

        # Salve todos os dados no modelo GameDataDocument
        game_data = GameDataDocument(
            Region=table_data.get('Region'),
            Players=table_data.get('Players'),
            Year=table_data.get('Year'),
            Publisher=table_data.get('Publisher'),
            Serial=table_data.get('Serial'),
            Graphics=table_data.get('Graphics'),
            Sound=table_data.get('Sound'),
            Gameplay=table_data.get('Gameplay'),
            Format=table_data.get('Format'),
            Version=table_data.get('Version'),
            GameName=game_name,
            Console=console_name,
            CanBeDownloaded=download_possible,
            DownloadURL=download_url,
            DownloadParams=download_params
        )
        return game_data

    def extract_table_data(self, soup):
        table = soup.find('table', {'class': 'rounded cellpadding1'})
        data = {}

        if table:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 3:
                    key = cols[0].text.strip()
                    value = cols[2].text.strip()
                    if cols[2].find('img'):
                        value = cols[2].img['title']

                    key_map = {
                        'Region': 'Region',
                        'Players': 'Players',
                        'Year': 'Year',
                        'Publisher': 'Publisher',
                        'Serial #': 'Serial',
                        'Graphics': 'Graphics',
                        'Sound': 'Sound',
                        'Gameplay': 'Gameplay',
                        'Format': 'Format',
                        'Version': 'Version',
                    }

                    if key in key_map:
                        if key == 'Version':
                            value = value.split()[0]
                        data[key_map[key]] = value

                        if key in ['Graphics', 'Sound', 'Gameplay', 'Overall']:
                            try:
                                data[key_map[key]] = float(value.split()[0])
                            except ValueError:
                                pass  # Handle or log the error as necessary

        return data

    def save_to_mongodb(self, game_data):
        """
        Save or update the extracted game data to MongoDB using the GameDataDocument model.
        If a game with the same GameName already exists, it will be updated with the new data.
        """
        try:
            # Verifica se o GameName já existe
            existing_game = GameDataDocument.objects(
                GameName=game_data.GameName).first()

            if existing_game:
                # Atualiza o jogo com os novos dados
                existing_game.update(**game_data.to_dict())
                print(
                    f"Game data for '{game_data.GameName}' updated in MongoDB.")
            else:
                # Se não existe, cria e salva o documento
                game_doc = game_data
                game_doc.save()
                print(f"Game data saved to MongoDB: {game_data.GameName}")

        except NotUniqueError:
            print(
                f"Duplicate GameName found: {game_data.GameName}. Skipping insert.")
