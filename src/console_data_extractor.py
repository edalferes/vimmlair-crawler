from src.game_data_extractor import GameDataExtractor
import aiohttp
from bs4 import BeautifulSoup
from mongoengine import Document, StringField, connect
from src.config import Config


class ConsoleDataDocument(Document):
    name = StringField(required=True)
    url = StringField(required=True)
    year = StringField(required=False)
    type = StringField(required=True, choices=["Console", "Handheld"])

    meta = {
        'collection': 'consoles',
        'indexes': [
            'name',
        ]
    }


config = Config()
connect('game_database', host=config.database_url)


class ConsoleDataExtractor:
    def __init__(self, url):
        self.url = url

    async def request_site(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                content = await response.read()
                consoles_data = self.extract_data(content)
                # Save the extracted data to MongoDB
                self.save_to_mongodb(consoles_data)

                # Process the console games
                await self.process_console_games(consoles_data)

                return consoles_data

    def extract_data(self, content):
        """
        Extract the console and handheld data from the given HTML content.
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Search for the tables containing the console and handheld data
        tables = soup.find_all('table')
        consoles = self.extract_console_links(
            tables[0], "Console")
        handhelds = self.extract_console_links(
            tables[1], "Handheld")

        return consoles, handhelds

    def extract_console_links(self, table, console_type):
        """
        Extract the console or handheld links from the given table.
        """
        links = []
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:
                link_tag = cols[0].find('a')
                if link_tag:
                    console_name = link_tag.text.strip()
                    console_url = link_tag['href']

                    # Update the console URL if it's a relative URL
                    if console_url.startswith("/"):
                        console_url = f'https://vimm.net{console_url}'

                    # Try to extract the year tag if it exists
                    year_tag = cols[1].text.strip() if len(cols) > 1 else None

                    # Create a ConsoleDataDocument object and save it to MongoDB
                    console = ConsoleDataDocument(
                        name=console_name,
                        url=console_url,
                        year=year_tag,
                        type=console_type
                    )
                    console.save()
                    links.append({'name': console_name, 'url': console_url,
                                 'year': year_tag, 'type': console_type})

        return links

    async def process_console_games(self, consoles_data):
        """
        Process the games for each console and handheld by visiting the console's or handheld's page
        and extracting game data.
        """
        # Process consoles
        for console_data in consoles_data[0]:  # Consoles
            console_url = console_data['url']
            console_name = console_data['name']
            print(
                f"Processing games for console: {console_name} at {console_url}")

            # Extract the games from the console page
            await self.extract_games_from_page(console_url)

            # Extract the games from the console page by letter
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                page_url = f'{console_url}/{letter}'
                await self.extract_games_from_page(page_url)

        # Process handhelds
        for handheld_data in consoles_data[1]:  # Handhelds
            handheld_url = handheld_data['url']
            handheld_name = handheld_data['name']
            print(
                f"Processing games for handheld: {handheld_name} at {handheld_url}")

            # Extract the games from the handheld page
            await self.extract_games_from_page(handheld_url)

            # Extract the games from the handheld page by letter
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                page_url = f'{handheld_url}/{letter}'
                await self.extract_games_from_page(page_url)

    async def extract_games_from_page(self, page_url):
        """
        Extract the games from the given page URL.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url) as response:
                content = await response.read()
                soup = BeautifulSoup(content, 'html.parser')

                # Search for the game links on the page
                game_links = self.extract_game_links(soup)

                for game_link in game_links:
                    game_url = f'https://vimm.net{game_link["url"]}'
                    # Call the GameDataExtractor to extract the game data
                    game_data_extractor = GameDataExtractor(game_url)
                    await game_data_extractor.request_site()

    def extract_game_links(self, soup):
        """
        Extract the links for all games on the console page.
        """
        game_links = []
        game_table = soup.find(
            'table', {'class': 'rounded centered cellpadding1 hovertable striped'})
        if game_table:
            rows = game_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 1:
                    link_tag = cols[0].find('a')
                    if link_tag:
                        game_name = link_tag.text.strip()
                        game_url = link_tag['href']
                        game_links.append({'name': game_name, 'url': game_url})

        return game_links

    def save_to_mongodb(self, consoles_data):
        """
        Save or update the extracted console data to MongoDB using the ConsoleDataDocument model.
        If a console with the same name already exists, it will be updated with the new data.
        """
        try:
            # Consoles If the console already exists in the database, update the data
            for console_data in consoles_data[0]:
                existing_console = ConsoleDataDocument.objects(
                    name=console_data['name']).first()

                if existing_console:
                    existing_console.update(**console_data)
                    print(
                        f"Console data for '{console_data['name']}' updated in MongoDB.")
                else:
                    console_doc = ConsoleDataDocument(**console_data)
                    console_doc.save()
                    print(
                        f"Console data saved to MongoDB: {console_data['name']}")

            # Handhelds If the handheld already exists in the database, update the data
            for handheld_data in consoles_data[1]:
                existing_handheld = ConsoleDataDocument.objects(
                    name=handheld_data['name']).first()

                if existing_handheld:
                    existing_handheld.update(**handheld_data)
                    print(
                        f"Handheld data for '{handheld_data['name']}' updated in MongoDB.")
                else:
                    handheld_doc = ConsoleDataDocument(**handheld_data)
                    handheld_doc.save()
                    print(
                        f"Handheld data saved to MongoDB: {handheld_data['name']}")

        except Exception as e:
            print(f"Error saving console data: {e}")
