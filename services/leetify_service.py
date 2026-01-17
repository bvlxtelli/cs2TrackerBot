import requests
import os
import logging

logger = logging.getLogger(__name__)

class LeetifyService:
    '''
    Serviço responsável pela comunicação com a API do Leetify.
    '''
    
    BASE_URL = "https://api-public.cs-prod.leetify.com"

    @staticmethod
    def get_headers() -> dict:
        '''
        Retorna os headers necessários para a autenticação.

        Returns:
            dict: Headers com o token de autenticação.
        '''
        token = os.getenv("LEETIFY_TOKEN")
        if not token:
            logger.error("Token do Leetify não encontrado no ambiente.")
            return {}
        return {"_leetify_key": token}

    @staticmethod
    def get_recent_matches(steam_id: str) -> list:
        '''
        Busca os jogos recentes de um usuário usando a API v3/profile/matches.

        Args:
            steam_id (str): Steam ID 64 do usuário.

        Returns:
            list: Lista de jogos recentes ou lista vazia em caso de erro.
        '''
        url = f"{LeetifyService.BASE_URL}/v3/profile/matches"
        params = {"steam64_id": steam_id}
        try:
            response = requests.get(url, headers=LeetifyService.get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # A API v3 retorna uma lista diretamente
                return data if isinstance(data, list) else []
            else:
                logger.error(f"Erro na API Leetify: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Erro ao buscar partidas no Leetify: {e}")
            return []
    
    @staticmethod
    def get_player_stats(steam_id: str):
        '''
        Busca estatísticas gerais do jogador usando os matches recentes.
        
        Args:
            steam_id (str): Steam ID 64 do usuário.
            
        Returns:
            list: Lista de matches do jogador.
        '''
        return LeetifyService.get_recent_matches(steam_id)
    
    @staticmethod
    def get_match_details(match_id: str) -> dict:
        '''
        Busca detalhes de uma partida específica usando o ID da partida.
        
        Args:
            match_id (str): ID da partida retornado pela API.
            
        Returns:
            dict: Detalhes da partida ou dicionário vazio em caso de erro.
        '''
        url = f"{LeetifyService.BASE_URL}/v2/matches/{match_id}"
        try:
            response = requests.get(url, headers=LeetifyService.get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao buscar partida {match_id}: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes da partida: {e}")
            return {}
    
    @staticmethod
    def get_user_profile(steam_id: str) -> dict:
        '''
        Busca perfil completo do usuário com ranks, stats gerais e recent_teammates.
        
        Args:
            steam_id (str): Steam ID 64 do usuário.
            
        Returns:
            dict: Dados completos do perfil ou dicionário vazio em caso de erro.
        '''
        url = f"{LeetifyService.BASE_URL}/v3/profile"
        params = {"steam64_id": steam_id}
        try:
            response = requests.get(url, headers=LeetifyService.get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao buscar perfil {steam_id}: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Erro ao buscar perfil do usuário: {e}")
            return {}
