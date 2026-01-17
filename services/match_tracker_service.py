import json
import os
import logging

logger = logging.getLogger(__name__)

class MatchTrackerService:
    '''
    Serviço responsável por rastrear a última partida conhecida de cada usuário.
    '''
    
    DATA_FILE = 'data/last_matches.json'

    @staticmethod
    def _load_matches() -> dict:
        '''
        Carrega os últimos IDs de partidas do arquivo JSON.

        Returns:
            dict: Dicionário mapeando Discord ID para Match ID.
        '''
        if not os.path.exists(MatchTrackerService.DATA_FILE):
            return {}
        
        try:
            with open(MatchTrackerService.DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar matches: {e}")
            return {}

    @staticmethod
    def _save_matches(matches: dict):
        '''
        Salva o dicionário de matches no arquivo JSON.

        Args:
            matches (dict): Os dados a serem salvos.
        '''
        try:
            with open(MatchTrackerService.DATA_FILE, 'w') as f:
                json.dump(matches, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar matches: {e}")

    @staticmethod
    def get_last_match_id(discord_id: str) -> str:
        '''
        Recupera o ID da última partida conhecida de um usuário.

        Args:
            discord_id (str): ID do usuário no Discord.

        Returns:
            str: O Match ID ou None se não encontrado.
        '''
        matches = MatchTrackerService._load_matches()
        return matches.get(str(discord_id))

    @staticmethod
    def update_last_match(discord_id: str, match_id: str):
        '''
        Atualiza o ID da última partida de um usuário.

        Args:
            discord_id (str): ID do usuário no Discord.
            match_id (str): ID da última partida.
        '''
        matches = MatchTrackerService._load_matches()
        matches[str(discord_id)] = match_id
        MatchTrackerService._save_matches(matches)
        logger.info(f"Última partida de {discord_id} atualizada para {match_id}")
