import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class StatsService:
    '''
    Serviço responsável pelo cálculo e processamento de estatísticas.
    Implementa SRP separando a lógica de negócio da camada de apresentação/comando.
    '''

    @staticmethod
    def calculate_average_stats(matches: List[Dict], steam_id: str) -> Optional[Dict]:
        '''
        Calcula as médias de estatísticas para uma lista de partidas.
        
        Args:
            matches: Lista de partidas.
            steam_id: Steam ID do jogador.
            
        Returns:
            Dict com as médias calculadas ou None se não houver dados suficientes.
        '''
        if not matches:
            return None

        total_kills = 0
        total_deaths = 0
        total_kd = 0.0
        total_hs_pct = 0.0
        total_rating = 0.0
        wins = 0
        matches_with_data = 0

        for match in matches:
            player_stats = StatsService.extract_player_stats(match, steam_id)
            if player_stats:
                matches_with_data += 1
                total_kills += player_stats.get('total_kills', 0)
                total_deaths += player_stats.get('total_deaths', 0)
                total_kd += player_stats.get('kd_ratio', 0)
                total_rating += player_stats.get('leetify_rating', 0)
                
                # Calcular HS%
                if player_stats.get('total_kills', 0) > 0:
                    total_hs_pct += (player_stats.get('total_hs_kills', 0) / player_stats.get('total_kills', 1)) * 100
                
                # Verificar vitória
                player_team = player_stats.get('initial_team_number')
                if match.get('winner_team_number') == player_team:
                    wins += 1

        if matches_with_data == 0:
            return None

        return {
            'matches_count': matches_with_data,
            'avg_kd': total_kd / matches_with_data,
            'avg_hs_pct': total_hs_pct / matches_with_data,
            'avg_rating': total_rating / matches_with_data,
            'win_rate': (wins / matches_with_data) * 100,
            'wins': wins,
            'losses': matches_with_data - wins,
            'total_kills': total_kills,
            'total_deaths': total_deaths
        }

    @staticmethod
    def extract_player_stats(match: Dict, steam_id: str) -> Optional[Dict]:
        '''
        Extrai as estatísticas de um jogador específico de uma partida.
        '''
        return next((s for s in match.get('stats', []) if s['steam64_id'] == steam_id), None)

    @staticmethod
    def analyze_cheaters(matches: List[Dict]) -> Dict:
        '''
        Analisa a presença de cheaters nas partidas.
        '''
        cheater_matches = []
        for match in matches:
            if match.get('has_banned_player', False):
                cheater_matches.append({
                    'id': match.get('id'),
                    'map': match.get('map_name', 'unknown'),
                    'date': match.get('finished_at', 'N/A')
                })
        
        return {
            'total': len(cheater_matches),
            'percentage': (len(cheater_matches) / len(matches)) * 100 if matches else 0,
            'matches': cheater_matches
        }

    @staticmethod
    def get_mvp_teammates(matches: List[Dict], user_steam_id: str, limit: int = 5) -> List[Dict]:
        '''
        Identifica os companheiros de equipe mais frequentes.
        Nota: Idealmente usar o endpoint /profile, mas este serve como fallback ou análise mais profunda.
        '''
        teammates = {}
        total_matches_analyzed = 0

        for match in matches:
            try:
                user_stats = StatsService.extract_player_stats(match, user_steam_id)
                if not user_stats:
                    continue

                total_matches_analyzed += 1
                user_team = user_stats.get('initial_team_number')

                for stat in match.get('stats', []):
                    teammate_id = stat['steam64_id']
                    if teammate_id != user_steam_id and stat.get('initial_team_number') == user_team:
                        if teammate_id not in teammates:
                            teammates[teammate_id] = {
                                'steam_id': teammate_id,
                                'name': stat.get('name', 'Unknown'),
                                'count': 0
                            }
                        teammates[teammate_id]['count'] += 1
            except Exception as e:
                logger.error(f"Erro ao processar teammates na partida {match.get('id')}: {e}")
                continue

        sorted_teammates = sorted(teammates.values(), key=lambda x: x['count'], reverse=True)[:limit]
        return {
            'matches_analyzed': total_matches_analyzed,
            'teammates': sorted_teammates
        }
