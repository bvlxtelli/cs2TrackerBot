import json
import os
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    '''
    Serviço responsável pelas configurações do bot.
    '''
    
    DATA_FILE = 'data/config.json'

    @staticmethod
    def _load_config() -> dict:
        '''
        Carrega as configurações do arquivo JSON.

        Returns:
            dict: Configurações do bot.
        '''
        if not os.path.exists(ConfigService.DATA_FILE):
            return {}
        
        try:
            with open(ConfigService.DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return {}

    @staticmethod
    def _save_config(config: dict):
        '''
        Salva as configurações no arquivo JSON.

        Args:
            config (dict): As configurações a serem salvas.
        '''
        try:
            with open(ConfigService.DATA_FILE, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar config: {e}")

    @staticmethod
    def get_notification_channel() -> int:
        '''
        Recupera o ID do canal de notificações.

        Returns:
            int: O channel ID ou None se não configurado.
        '''
        config = ConfigService._load_config()
        channel_id = config.get('notification_channel_id')
        return int(channel_id) if channel_id else None

    @staticmethod
    def set_notification_channel(channel_id: int):
        '''
        Define o canal de notificações.

        Args:
            channel_id (int): ID do canal do Discord.
        '''
        config = ConfigService._load_config()
        config['notification_channel_id'] = str(channel_id)
        ConfigService._save_config(config)
        logger.info(f"Canal de notificações configurado para {channel_id}")
