import aiohttp
from bs4 import BeautifulSoup
from mongoengine import Document, StringField, connect
from src.config import Config


class ConsoleDataDocument(Document):
    name = StringField(required=True)
    url = StringField(required=True)
    year = StringField(required=False)  # Ano do console
    type = StringField(required=True, choices=["Console", "Handheld"])

    meta = {
        'collection': 'consoles',
        'indexes': [
            'name',  # Garantir que o nome seja único
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
                # Salve os dados na coleção de consoles
                self.save_to_mongodb(consoles_data)
                return consoles_data

    def extract_data(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Encontrar as tabelas para Consoles e Handhelds
        tables = soup.find_all('table')
        consoles = self.extract_console_links(
            tables[0], "Console")  # A primeira tabela é de Consoles
        handhelds = self.extract_console_links(
            tables[1], "Handheld")  # A segunda tabela é de Handhelds

        return consoles, handhelds

    def extract_console_links(self, table, console_type):
        links = []
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 1:  # Verifica se a linha tem mais de uma célula
                link_tag = cols[0].find('a')
                if link_tag:
                    console_name = link_tag.text.strip()
                    console_url = link_tag['href']

                    # Tentando capturar o ano do console, caso esteja disponível
                    year_tag = cols[1].text.strip() if len(cols) > 1 else None

                    # Criando e salvando o documento do console no MongoDB
                    console = ConsoleDataDocument(
                        name=console_name,
                        url=f'https://vimm.net{console_url}',
                        year=year_tag,
                        type=console_type
                    )
                    console.save()
                    links.append({'name': console_name, 'url': console_url,
                                 'year': year_tag, 'type': console_type})

        return links

    def save_to_mongodb(self, consoles_data):
        """
        Save or update the extracted console data to MongoDB using the ConsoleDataDocument model.
        If a console with the same name already exists, it will be updated with the new data.
        """
        try:
            # Consoles são a primeira parte da tupla
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

            # Handhelds são a segunda parte da tupla
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
