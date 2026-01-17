import discord
from typing import Dict, List, Optional

class EmbedService:
    '''
    Serviço responsável APENAS pela criação visual de Embeds do Discord.
    '''

    @staticmethod
    def create_error_embed(message: str) -> discord.Embed:
        return discord.Embed(
            title="❌ Erro",
            description=message,
            color=0xFF0000
        )

    @staticmethod
    def _get_humorous_comment(kd: float, win_rate: float = 50.0) -> str:
        if kd < 0.6:
            return "💀 **Mano? Tá jogando de monitor desligado?**"
        elif kd < 0.8:
            return "🥔 **Aquele famoso peso de papel...**"
        elif kd < 1.0:
            return "📉 **Negativo é foda kkkk**"
        elif kd < 1.2:
            return "😐 **Tá honesto, pelo menos não ficou negativo.**"
        elif kd < 1.5:
            return "🔥 **Tá jogando muito!**"
        elif kd < 2.0:
            return "👽 **Tá xitado ctz!**"
        else:
            return "🤖 **ATIVOU O SPINBOT?**"

    @staticmethod
    def create_performance_embed(user: discord.User, stats: Dict) -> discord.Embed:
        count = stats['matches_count']
        kd = stats['avg_kd']
        comment = EmbedService._get_humorous_comment(kd, stats['win_rate'])
        
        embed = discord.Embed(
            title=f"📊 Performance de {user.display_name}",
            description=f"Análise das últimas **{count}** partidas\n\n{comment}",
            color=0x0099FF
        )
        embed.add_field(name="K/D", value=f"**{stats['avg_kd']:.2f}**", inline=True)
        embed.add_field(name="HS%", value=f"🎯 **{stats['avg_hs_pct']:.1f}%**", inline=True)
        embed.add_field(name="Rating", value=f"⭐ **{stats['avg_rating']:.2f}**", inline=True)
        embed.add_field(name="Win Rate", value=f"🏆 **{stats['win_rate']:.1f}%**", inline=True)
        embed.add_field(name="Vitórias", value=f"{stats['wins']}/{count}", inline=True)
        embed.add_field(name="Total K/D", value=f"💀 {stats['total_kills']}/{stats['total_deaths']}", inline=True)
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed

    @staticmethod
    def create_match_embed(match_details: Dict, registered_players: List[Dict], has_cheater: bool) -> discord.Embed:
        map_name = match_details.get('map_name', 'Desconhecido')
        scores = match_details.get('team_scores', [])
        t2_score = next((s['score'] for s in scores if s['team_number'] == 2), 0)
        t3_score = next((s['score'] for s in scores if s['team_number'] == 3), 0)
        
        description = f"**Placar**: {t2_score} x {t3_score}"
        if has_cheater:
            description = "⚠️ **Partida com jogador banido detectado**\n" + description

        embed = discord.Embed(
            title=f"🎮 Análise da Partida - {map_name}",
            description=description,
            color=0xFF0000 if has_cheater else 0x0099ff
        )

        for player in registered_players:
            # Tentar extrair KD do texto (hack rápido já que não passei estruturado) ou passar estruturado
            # Como mantivemos a compatibilidade, vamos adicionar o comentário num campo separado ou junto
            # Melhor não poluir muito o field value, vamos deixar como está nos fields e só mudar a cor/titulo se for algo mto absurdo
            embed.add_field(
                name=f"👤 {player['display_name']}",
                value=player['stats_text'],
                inline=False
            )
            
        replay_url = match_details.get('replay_url')
        if replay_url:
            embed.add_field(name="🎬 Assistir Replay", value=f"[Clique aqui]({replay_url})", inline=False)
            
        embed.set_footer(text=f"Match ID: {match_details.get('id')}")
        return embed

    @staticmethod
    def create_profile_embed(user: discord.User, profile_data: Dict, squad_data: List[Dict] = None) -> discord.Embed:
        embed = discord.Embed(
            title=f"📋 Perfil Completo de {user.display_name}",
            description=f"Steam: {profile_data.get('name', 'Unknown')}",
            color=0x00D9FF
        )
        
        # Ranks
        ranks = profile_data.get('ranks', {})
        rank_text = f"**Premier**: {ranks.get('premier', 'N/A')} ⭐\n**Leetify**: {ranks.get('leetify', 'N/A')}"
        
        best_maps = sorted(ranks.get('competitive', []), key=lambda x: x.get('rank', 0), reverse=True)[:3]
        if best_maps:
            rank_text += "\n**Melhores Mapas:**"
            for m in best_maps:
                rank_text += f"\n  • {m.get('map_name', '').replace('de_', '').title()}: Rank {m.get('rank')}"
        
        embed.add_field(name="🏆 Ranks", value=rank_text, inline=False)
        
        # Stats
        stats = profile_data.get('stats', {})
        total_matches = profile_data.get('total_matches', 0)
        winrate = profile_data.get('winrate', 0) * 100
        wins = int(total_matches * (winrate / 100))
        
        stats_text = (
            f"**Win Rate**: {winrate:.1f}% ({wins}W/{total_matches - wins}L)\n"
            f"**HS%**: 🎯 {stats.get('accuracy_head', 0):.1f}%\n"
            f"**Pre-Aim**: {stats.get('preaim', 0):.1f}ms\n"
            f"**Total**: {total_matches} partidas"
        )
        embed.add_field(name="📊 Stats Gerais", value=stats_text, inline=False)

        # Squad
        if squad_data:
            squad_text = ""
            medals = ["🥇", "🥈", "🥉"]
            for idx, member in enumerate(squad_data):
                 medal = medals[idx] if idx < 3 else f"{idx+1}."
                 squad_text += f"{medal} {member['display_name']} - {member['count']} jogos\n"
            embed.add_field(name="👥 Squad Frequente", value=squad_text, inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        return embed

    @staticmethod
    def create_cheater_report_embed(user: discord.User, report: Dict) -> discord.Embed:
        cheaters = report['matches']
        total = report['total']
        
        embed = discord.Embed(
            title=f"⚠️ Relatório de Cheaters - {user.display_name}",
            description=f"Análise recente",
            color=0xFF0000 if total > 0 else 0x00FF00
        )
        
        embed.add_field(
            name="📊 Resumo",
            value=f"**{total}** partidas com cheaters ({report['percentage']:.1f}%)",
            inline=False
        )
        
        if cheaters:
            text = ""
            for m in cheaters[:10]:
                text += f"• {m['map'].replace('de_', '').title()} - `{m['id'][:8]}...`\n"
            if len(cheaters) > 10:
                text += f"\n_...e mais {len(cheaters)-10} partidas_"
            embed.add_field(name="🎮 Partidas Afetadas", value=text, inline=False)
        else:
             embed.add_field(name="✅ Boa notícia!", value="Nenhum cheater detectado.", inline=False)
             
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed

    @staticmethod
    def create_notification_embed(user: discord.User, match: Dict, stats: Dict, other_players: List[str]) -> discord.Embed:
        map_name = match.get('map_name', 'Desconhecido')
        match_id = match.get('id')
        kd = stats.get('kd_ratio', 0)
        
        comment = EmbedService._get_humorous_comment(kd)

        embed = discord.Embed(
            title="🆕 Nova Partida Detectada!",
            description=f"**{user.mention}** jogou em **{map_name}**\n\n{comment}",
            color=0x00FF00
        )

        embed.add_field(
            name="📊 Performance", 
            value=f"K/D: {stats.get('kd_ratio', 0):.2f} ({stats.get('total_kills')}/{stats.get('total_deaths')})", 
            inline=False
        )
        
        if other_players:
            embed.add_field(name="👥 Jogadores Cadastrados", value=", ".join(other_players), inline=False)

        embed.set_footer(text=f"Use !partida {match_id} para ver detalhes")
        return embed

    @staticmethod
    def create_recent_matches_embed(user: discord.User, matches: List[Dict], steam_id: str) -> discord.Embed:
        embed = discord.Embed(
            title=f"🕰️ Últimas Partidas de {user.display_name}",
            description="Histórico recente:",
            color=0x9900FF
        )
        
        for match in matches:
            map_name = match.get('map_name', 'Unknown').replace('de_', '').title()
            
            # Precisamos extrair stats do jogador nesta partida
            # A lista de matches do endpoint /profile/matches do Leetify v3 costuma ter os stats do jogador diretamente no objeto da lista
            # VAMOS VERIFICAR: O endpoint /profile/matches retornado pelo LeetifyService.get_recent_matches retorna uma lista.
            # Se for o endpoint v3, ele geralmente retorna stats resumidos. 
            # Assumindo que o objeto 'match' já tenha os stats pessoais ou que precisamos extrair de 'stats' se for full detail.
            # Como update anterior usa StatsService.extract_player_stats, isso implica que temos full detail ou structure similar.
            # Mas get_recent_matches retorna o que o endpoint dá. 
            # SE for o v3/profile/matches, o JSON de cada item costuma ter: { "id":..., "map_name":..., "user_stats": {...} } ou similar.
            # OU se for a lista v2, não tem stats.
            # Olhando o código anterior: StatsService.extract_player_stats percorre match.get('stats', []) procurando steam64_id.
            # Isso sugere que get_recent_matches retorna objetos FULL match details OU que a lista tem esse campo 'stats' (array de jogadores).
            # Vamos assumir que temos acesso a stats do player.
            
            # Tentar extrair stats usando StatsService logic se possível
            player_stats = None
            if 'stats' in match: 
                player_stats = next((s for s in match['stats'] if s['steam64_id'] == steam_id), None)
            elif 'own_stats' in match: 
                player_stats = match['own_stats']
            
            kd = 0.0
            rating = 0.0
            hs_pct = 0.0
            damage = 0
            result = "❓"
            
            if player_stats:
                kd = player_stats.get('kd_ratio', 0)
                rating = player_stats.get('leetify_rating', 0)
                kills = player_stats.get('total_kills', 1)
                hs = player_stats.get('total_hs_kills', 0)
                hs_pct = (hs / kills) * 100 if kills > 0 else 0
                damage = player_stats.get('total_damage', 0)

                if match.get('winner_team_number') == player_stats.get('initial_team_number'):
                    result = "✅" 
                elif match.get('winner_team_number') == 0: 
                    result = "🤝"
                else:
                    result = "❌" 
            
            val = f"`{match.get('id')}`"
            if player_stats:
                val = (
                    f"💀 K/D: **{kd:.2f}** | ⭐ Rating: **{rating:.2f}**\n"
                    f"🎯 HS%: {hs_pct:.0f}% | 💥 Dano: {damage}\n"
                    f"📅 {match.get('game_finished_at', '')[:10]}"
                )
            
            embed.add_field(
                name=f"{result} {map_name}",
                value=val,
                inline=False
            )
            
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed
