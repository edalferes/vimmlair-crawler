import requests
import os
import time
from urllib.parse import urlparse
from mongoengine import connect
from src.config import Config
from tqdm import tqdm  # Adicionando tqdm para a barra de progresso

# Configuração de conexão com o banco
config = Config()
connect('game_database', host=config.database_url)


class GameDownloadChecker:
    def __init__(self, console_data):
        """
        Inicializa a classe com os dados do console.
        """
        self.console_data = console_data

    async def check_downloadable_games(self):
        """
        Percorre todos os jogos associados ao console e verifica se são possíveis de baixar.
        """
        console_name = self.console_data['name']
        console_url = self.console_data['url']

        print(
            f"Checking downloadable games for console: {console_name} at {console_url}")

        # Recupera os jogos para o console. Isso pode ser feito diretamente no banco de dados ou por scraping.
        # Para simplificar, vamos buscar os jogos que já foram salvos no banco
        games = self.get_games_from_console(console_name)

        for game in games:
            print(f"Checking game: {game['GameName']}")

            # Simula a verificação se o jogo pode ser baixado
            if self.can_download_game(game):
                print(f"Game {game['GameName']} is downloadable.")
                # Aqui é onde você colocaria o código para baixar o jogo
                self.download_game(game)
            else:
                print(f"Game {game['GameName']} is NOT downloadable.")

    def get_games_from_console(self, console_name):
        """
        Recupera os jogos associados ao console do banco de dados.
        Este método pode ser ajustado para buscar os dados de acordo com a sua implementação.
        """
        from src.game_data_extractor import GameDataDocument

        # Busca jogos para o console no banco de dados
        games = GameDataDocument.objects(Console=console_name)

        return [game.to_dict() for game in games]

    def can_download_game(self, game):
        """
        Verifica se o jogo pode ser baixado.
        Este é apenas um boilerplate, você pode personalizar a lógica de verificação.
        """
        # Lógica simplificada de verificação de jogo para download.
        # Por exemplo, vamos verificar se o campo `DownloadURL` está presente e se o jogo tem a flag de "baixável".
        if game.get('DownloadURL') and game.get('CanBeDownloaded'):
            return True
        return False

    def download_game(self, game):
        """
        Baixa o jogo do Vimm's Lair, usando o mediaId armazenado no banco de dados.
        """
        # Obtém o mediaId e DownloadURL armazenados no banco
        media_id = game.get('DownloadParams', {}).get('mediaId')
        download_url = f"https://download2.vimm.net/?mediaId={media_id}"

        if not media_id:
            print(
                f"Não foi possível encontrar o mediaId para o jogo {game['GameName']}.")
            return

        # Obtém o nome do arquivo a partir do nome do jogo
        filename = f"{game['GameName']}.zip"  # Ou o formato que você preferir

        # Diretório onde a ROM será salva, agora organizando por console
        console_directory = os.path.join('roms', game['Console'])
        if not os.path.exists(console_directory):
            os.makedirs(console_directory)

        save_path = os.path.join(console_directory, filename)

        # Verifica se o arquivo já existe
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
            'Cookie': 'your_cookies_here',  # Adicione os cookies apropriados, se necessário
        }

        try:
            print(f"Iniciando download de {filename}...")

            # Realiza o download diretamente do link
            response = requests.get(download_url, headers=headers, stream=True)
            response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

            # Cria a barra de progresso com tqdm
            total_size = int(response.headers.get('content-length', 0))
            with open(save_path, 'wb') as file:
                for chunk in tqdm(response.iter_content(chunk_size=8192),
                                  desc=f"Baixando {filename}",
                                  total=total_size // 8192,
                                  unit="KB",
                                  ncols=100):
                    if chunk:
                        file.write(chunk)

            print(f"Download de {filename} concluído e salvo em {save_path}.")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar {game['GameName']}: {e}")
