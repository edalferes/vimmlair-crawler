import asyncio
import os
from pyppeteer import launch


class GameDownloader:
    def __init__(self, download_url, download_params=None):
        if download_url.startswith('//'):
            download_url = 'https:' + download_url
        self.download_url = download_url
        self.download_params = download_params if download_params is not None else {}

    async def download_game(self, download_path):
        browser = await launch(headless=True)
        page = await browser.newPage()

        await page._client.send('Page.setDownloadBehavior', {
            'behavior': 'allow',
            'downloadPath': download_path
        })

        await page.goto(self.download_url)

        # Esperar pelo formulário de download estar disponível
        try:
            await page.waitForSelector('form#dl_form', options={'timeout': 10000})
            # Agora, submeter o formulário
            await page.click('form#dl_form button[type="submit"]')
        except Exception as e:
            print(f"An error occurred: {e}")
            await browser.close()
            return

        await self.wait_for_download(download_path)
        await browser.close()

    async def wait_for_download(self, download_path):
        download_in_progress = True
        while download_in_progress:
            download_in_progress = any(
                fname.endswith('.crdownload') for fname in os.listdir(download_path)
            )
            if download_in_progress:
                await asyncio.sleep(1)
