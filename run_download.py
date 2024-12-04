
from src.game_download_checker import GameDownloadChecker


async def main():
    # Aqui você passa os dados do console, que podem vir de um banco de dados ou de algum scraping anterior
    console_data = {
        'name': 'PlayStation',
        'url': 'https://vimm.net/vault/PS1',
        'year': '1994',
        'type': 'Console'
    }

    # Criando uma instância de GameDownloadChecker
    download_checker = GameDownloadChecker(console_data)

    # Verificando os jogos para o console e se podem ser baixados
    await download_checker.check_downloadable_games()


if __name__ == '__main__':
    # Rodando a verificação de jogos
    import asyncio
    asyncio.run(main())
