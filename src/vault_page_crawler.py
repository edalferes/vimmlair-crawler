import aiohttp
from bs4 import BeautifulSoup


import aiohttp
from bs4 import BeautifulSoup


class VaultPageCrawler:
    def __init__(self, url):
        self.url = url

    async def fetch_page(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                content = await response.text()
                return self.parse_page(content)

    def parse_page(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Encontrar as tabelas para Consoles e Handhelds
        tables = soup.find_all('table')
        consoles = self.extract_console_links(
            tables[0])  # A primeira tabela é de Consoles
        handhelds = self.extract_console_links(
            tables[1])  # A segunda tabela é de Handhelds

        return consoles, handhelds

    def extract_console_links(self, table):
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
                    links.append(
                        {'name': console_name, 'url': console_url, 'year': year_tag})

        return links
