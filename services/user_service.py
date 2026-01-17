import json
import os
import logging

logger = logging.getLogger(__name__)

class UserService:
    '''
    Serviço responsável pelo gerenciamento de usuários e seus IDs da Steam.
    '''
    
    DATA_FILE = 'data/users.json'

    @staticmethod
    def _load_users() -> dict:
        '''
        Carrega os usuários do arquivo JSON.

        Returns:
            dict: Dicionário mapeando Discord ID para Steam ID.
        '''
        if not os.path.exists(UserService.DATA_FILE):
            return {}
        
        try:
            with open(UserService.DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {e}")
            return {}

    @staticmethod
    def _save_users(users: dict):
        '''
        Salva o dicionário de usuários no arquivo JSON.

        Args:
            users (dict): Os dados a serem salvos.
        '''
        try:
            with open(UserService.DATA_FILE, 'w') as f:
                json.dump(users, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar usuários: {e}")

    @staticmethod
    def register_user(discord_id: str, steam_id: str):
        '''
        Registra ou atualiza o Steam ID de um usuário do Discord.

        Args:
            discord_id (str): ID do usuário no Discord.
            steam_id (str): Steam ID 64 do usuário.
        '''
        users = UserService._load_users()
        users[str(discord_id)] = steam_id
        UserService._save_users(users)
        logger.info(f"Usuário {discord_id} vinculado ao Steam ID {steam_id}")

    @staticmethod
    def get_steam_id(discord_id: str) -> str:
        '''
        Recupera o Steam ID vinculado a um usuário do Discord.

        Args:
            discord_id (str): ID do usuário no Discord.

        Returns:
            str: O Steam ID vinculado ou None se não encontrado.
        '''
        users = UserService._load_users()
        return users.get(str(discord_id))
