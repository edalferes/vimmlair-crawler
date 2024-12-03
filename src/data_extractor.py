
import aiohttp
from bs4 import BeautifulSoup
import base64
from src.game_data import GameData


class GameDataExtractor:
    def __init__(self, url):
        self.url = url

    async def request_site(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                content = await response.read()
                return self.extract_data(content)

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
            # Extract download form parameters
            for input_tag in download_form.find_all('input'):
                if input_tag.has_attr('name'):
                    download_params[input_tag['name']
                                    ] = input_tag.get('value', '')

        # Extract table data
        table_data = self.extract_table_data(soup)

        # Join all data
        game_data = GameData(**table_data, GameName=game_name, Console=console_name,
                             CanBeDownloaded=download_possible, DownloadURL=download_url,
                             DownloadParams=download_params)
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
                        # Clean up the value if it's the Version to ensure no redundant or newline characters
                        if key == 'Version':
                            # This assumes the version is always followed by spaces and newline, keeping the first part only
                            # Adjust based on actual content observed
                            value = value.split()[0]
                        data[key_map[key]] = value

                        if key in ['Graphics', 'Sound', 'Gameplay', 'Overall']:
                            # Convert these values to float, handle exceptions if conversion is not possible
                            try:
                                data[key_map[key]] = float(value.split()[0])
                            except ValueError:
                                pass  # Handle or log the error as necessary

        return data
