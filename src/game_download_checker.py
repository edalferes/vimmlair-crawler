import requests
import os
from urllib.parse import urlparse
from mongoengine import connect
from src.config import Config

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
                # Aqui é onde você colocaria o código para baixar o jogo, que será deixado como boilerplate
                self.download_game(game)
            else:
                print(f"Game {game['GameName']} is NOT downloadable.")

    def get_games_from_console(self, console_name):
        """
        Recupera os jogos associados ao console do banco de dados.
        Este método pode ser ajustado para buscar os dados do banco de dados MongoDB ou outro meio.
        """
        # Este é apenas um exemplo de como recuperar os dados de jogos
        # Você deve ajustar este método para obter os dados de acordo com a sua implementação
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
        download_url = game.get('DownloadURL')

        if not media_id or not download_url:
            print(
                f"Não foi possível encontrar o mediaId ou a URL de download para o jogo {game['GameName']}.")
            return

        # Usa o nome do jogo como o nome do arquivo
        game_name = game.get('GameName')
        # Ajuste a extensão conforme necessário (ex: .iso, .zip, .rom, etc.)
        filename = f"{game_name}.zip"

        # Diretório onde a ROM será salva
        save_directory = 'roms'  # Altere para o diretório desejado
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        save_path = os.path.join(save_directory, filename)

        # Verifica se o arquivo já existe
        if os.path.exists(save_path):
            print(f"Arquivo {filename} já existe. Pulando download.")
            return

        try:
            print(f"Iniciando download de {filename}...")

            # Envia a requisição POST para o servidor de download
            post_url = "https://download2.vimm.net/"
            post_data = {
                'mediaId': media_id,
                'alt': '0',  # Alt flag, conforme observado no código HTML
            }

            print(f"Enviando requisição de download para {filename}...")
            post_response = requests.post(
                post_url, data=post_data, stream=True)
            post_response.raise_for_status()

            # Salva o arquivo no diretório
            with open(save_path, 'wb') as file:
                for chunk in post_response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(
                f"Download de {filename} concluído e salvo em {save_path}.")

        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar {filename}: {e}")
