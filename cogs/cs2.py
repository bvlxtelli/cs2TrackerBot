import discord
from discord.ext import commands, tasks
import logging
from services.user_service import UserService
from services.leetify_service import LeetifyService
from services.match_tracker_service import MatchTrackerService
from services.config_service import ConfigService
from services.stats_service import StatsService
from services.embed_service import EmbedService

logger = logging.getLogger(__name__)

# View class para navegação do leaderboard
class LeaderboardView(discord.ui.View):
    def __init__(self, user_stats, author):
        super().__init__(timeout=180)
        self.user_stats = user_stats
        self.author = author
        self.current_page = 0
        self.total_pages = (len(user_stats) + 4) // 5  # 5 usuários por página
        self.update_buttons()

    def update_buttons(self):
        # Desabilitar botões conforme necessário
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page >= self.total_pages - 1)

    def create_embed(self, page):
        start_idx = page * 5
        end_idx = min(start_idx + 5, len(self.user_stats))
        page_users = self.user_stats[start_idx:end_idx]

        embed = discord.Embed(
            title="🏆 Leaderboard CS2",
            description=f"Ranking baseado em K/D médio (últimas 10 partidas)\nPágina {page + 1}/{self.total_pages}",
            color=0xFFD700
        )

        for idx, user_data in enumerate(page_users, start=start_idx + 1):
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"**{idx}.**"
            user = user_data['discord_user']
            kd = user_data['avg_kd']
            matches = user_data['matches_played']

            embed.add_field(
                name=f"{medal} {user.display_name}",
                value=f"📊 K/D: **{kd:.2f}** | 🎮 {matches} partidas",
                inline=False
            )

        return embed

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Apenas o autor do comando pode usar os botões
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ Apenas quem solicitou pode navegar!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="◀ Anterior", style=discord.ButtonStyle.gray, custom_id="prev")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        embed = self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Próximo ▶", style=discord.ButtonStyle.gray, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        self.update_buttons()
        embed = self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

class CS2Commands(commands.Cog):
    '''
    Cog responsável pelos comandos de tracking de CS2.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.check_new_matches.start()  # Inicia o background task

    def cog_unload(self):
        self.check_new_matches.cancel()

    @commands.command(name="cadastro", help="Vincula um Steam ID ao usuário do Discord.")
    async def cadastro(self, ctx, usuario: discord.User, steam_id: str):
        '''
        Parâmetros:
            usuario: Menção ao usuário (@usuario)
            steam_id: ID Steam 64
        '''
        UserService.register_user(str(usuario.id), steam_id)
        
        embed = discord.Embed(
            title="✅ Cadastro Realizado",
            description=f"{usuario.mention} vinculado com sucesso!",
            color=0x00FF00
        )
        embed.add_field(name="Steam ID", value=f"`{steam_id}`", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="performance", help="Mostra dados de performance recentes.")
    async def performance(self, ctx, usuario: discord.User = None):
        target_user = usuario or ctx.author
        steam_id = UserService.get_steam_id(str(target_user.id))

        if not steam_id:
            await ctx.send(embed=EmbedService.create_error_embed(f"{target_user.mention} não possui Steam ID vinculado."))
            return

        matches = LeetifyService.get_recent_matches(steam_id)
        if not matches:
            await ctx.send(embed=EmbedService.create_error_embed(f"Nenhuma partida recente encontrada para {target_user.mention}."))
            return

        # Calcular stats
        stats = StatsService.calculate_average_stats(matches[:10], steam_id)
        
        if not stats:
            await ctx.send(embed=EmbedService.create_error_embed(f"Sem dados suficientes para {target_user.mention}."))
            return

        embed = EmbedService.create_performance_embed(target_user, stats)
        await ctx.send(embed=embed)

    @commands.command(name="kd", help="Mostra stats principais recentes (K/D, HS%, Rating, Win Rate%).")
    async def kd(self, ctx, usuario: discord.User = None):
        # Reutiliza a mesma lógica de performance, pois os dados são os mesmos, apenas a flag/uso poderia mudar se quiséssemos algo mais simples
        # Mas como o pedido foi expandir o KD para mostrar tudo, ele virou um alias funcional do performance praticamente.
        # Vamos manter separado caso a apresentação mude no futuro.
        await self.performance(ctx, usuario)

    @commands.command(name="partida", help="Mostra análise detalhada de uma partida.")
    async def partida(self, ctx, match_id: str):
        match = LeetifyService.get_match_details(match_id)
        if not match or 'stats' not in match:
            await ctx.send(embed=EmbedService.create_error_embed("Partida não encontrada."))
            return

        # Carregar usuários para mapear IDs
        import json
        import os
        steam_to_discord = {}
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r') as f:
                users_data = json.load(f)
                steam_to_discord = {v: k for k, v in users_data.items()}

        registered_players_data = []
        for stat in match.get('stats', []):
            steam_id = stat['steam64_id']
            if steam_id in steam_to_discord:
                try:
                    d_user = await self.bot.fetch_user(int(steam_to_discord[steam_id]))
                    display_name = d_user.mention
                except:
                    display_name = stat.get('name', 'Unknown')
                
                # Formatar o texto de stats aqui ou no EmbedService? 
                # Melhor passar dados estruturados para o EmbedService, mas para simplificar agora vou formatar o texto aqui
                # e passar uma lista de objetos prontos para exibição.
                
                stats_text = (
                    f"**K/D**: {stat.get('kd_ratio', 0):.2f} ({stat.get('total_kills')} / {stat.get('total_deaths')}) | 🎯 **HS**: {stat.get('total_hs_kills')}\n"
                    f"⭐ **MVPs**: {stat.get('mvps', 0)} | 💥 **DPR**: {stat.get('dpr', 0):.1f}\n"
                    f"📊 **Rating**: {stat.get('leetify_rating', 0):.3f} (CT: {stat.get('ct_leetify_rating', 0):.3f} / TR: {stat.get('t_leetify_rating', 0):.3f})\n"
                    f"💢 **Dano**: {stat.get('total_damage', 0)}"
                )
                
                registered_players_data.append({
                    'display_name': display_name,
                    'stats_text': stats_text
                })

        embed = EmbedService.create_match_embed(match, registered_players_data, match.get('has_banned_player', False))
        await ctx.send(embed=embed)

    @commands.command(name="squad", help="Mostra com quem você mais joga.")
    async def squad(self, ctx, usuario: discord.User = None):
        await self.perfil(ctx, usuario) # Squad agora faz parte do perfil na nova arquitetura, ou podemos manter separado

    @commands.command(name="perfil", help="Mostra perfil completo com ranks, stats gerais e squad.")
    async def perfil(self, ctx, usuario: discord.User = None):
        target_user = usuario or ctx.author
        steam_id = UserService.get_steam_id(str(target_user.id))
        
        if not steam_id:
             await ctx.send(embed=EmbedService.create_error_embed(f"{target_user.mention} não está cadastrado."))
             return

        profile = LeetifyService.get_user_profile(steam_id)
        if not profile:
             await ctx.send(embed=EmbedService.create_error_embed("Erro ao buscar perfil."))
             return

        # Processar Squad
        recent_teammates = profile.get('recent_teammates', [])[:3]
        squad_data = []
        
        # Mapeamento rápido
        import json
        steam_to_discord = {}
        try:
            with open('data/users.json', 'r') as f:
                steam_to_discord = {v: k for k, v in json.load(f).items()}
        except: pass

        for tm in recent_teammates:
            sid = tm.get('steam64_id')
            name = f"Steam: {sid[:8]}..."
            if sid in steam_to_discord:
                try:
                    u = await self.bot.fetch_user(int(steam_to_discord[sid]))
                    name = u.mention
                except: pass
            
            squad_data.append({'display_name': name, 'count': tm.get('recent_matches_count', 0)})

        embed = EmbedService.create_profile_embed(target_user, profile, squad_data)
        await ctx.send(embed=embed)

    @commands.command(name="xit", help="Conta quantos cheaters foram encontrados nas últimas X partidas.")
    async def xit(self, ctx, usuario: discord.User = None, limite: int = 20):
        target_user = usuario or ctx.author
        steam_id = UserService.get_steam_id(str(target_user.id))

        if not steam_id:
             await ctx.send(embed=EmbedService.create_error_embed(f"{target_user.mention} não está cadastrado."))
             return
             
        matches = LeetifyService.get_recent_matches(steam_id)
        if not matches:
             await ctx.send(embed=EmbedService.create_error_embed("Sem dados recentes."))
             return

        limit = max(1, min(limite, 100))
        report = StatsService.analyze_cheaters(matches[:limit])
        
        embed = EmbedService.create_cheater_report_embed(target_user, report)
        await ctx.send(embed=embed)

    @commands.command(name="recentes", help="Mostra as últimas 5 partidas.")
    async def recentes(self, ctx, usuario: discord.User = None):
        target_user = usuario or ctx.author
        steam_id = UserService.get_steam_id(str(target_user.id))

        if not steam_id:
             await ctx.send(embed=EmbedService.create_error_embed(f"{target_user.mention} não está cadastrado."))
             return
             
        matches = LeetifyService.get_recent_matches(steam_id)
        if not matches:
             await ctx.send(embed=EmbedService.create_error_embed("Nenhuma partida encontrada."))
             return

        # Pegar as 5 últimas
        recent_matches = matches[:5]
        
        embed = EmbedService.create_recent_matches_embed(target_user, recent_matches, steam_id)
        await ctx.send(embed=embed)



    @commands.command(name="leaderboard", aliases=["ranking", "top"], help="Mostra ranking de todos os usuários cadastrados.")
    async def leaderboard(self, ctx):
        '''
        Exibe um ranking com stats de todos os usuários cadastrados.
        '''
        import json
        import os
        
        if not os.path.exists('data/users.json'):
            await ctx.send(embed=EmbedService.create_error_embed("Nenhum usuário cadastrado."))
            return

        with open('data/users.json', 'r') as f:
            users = json.load(f)

        if not users:
            await ctx.send(embed=EmbedService.create_error_embed("Nenhum usuário cadastrado."))
            return

        # Coletar stats de todos os usuários
        user_stats = []
        for discord_id, steam_id in users.items():
            try:
                discord_user = await self.bot.fetch_user(int(discord_id))
                matches = LeetifyService.get_recent_matches(steam_id)
                
                if not matches:
                    continue
                
                # Calcular stats usando o StatsService
                stats = StatsService.calculate_average_stats(matches[:10], steam_id)
                if stats:
                    user_stats.append({
                        'discord_user': discord_user,
                        'avg_kd': stats['avg_kd'],
                        'matches_played': stats['matches_count']
                    })
            except Exception as e:
                logger.error(f"Erro ao processar usuário {discord_id}: {e}")
                continue

        if not user_stats:
            await ctx.send(embed=EmbedService.create_error_embed("Nenhum usuário com dados disponíveis."))
            return

        # Ordenar por K/D médio
        user_stats.sort(key=lambda x: x['avg_kd'], reverse=True)

        # Criar view com botões de navegação
        view = LeaderboardView(user_stats, ctx.author)
        embed = view.create_embed(0)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="config_canal", help="Configura o canal de notificações.")
    @commands.has_permissions(administrator=True)
    async def config_canal(self, ctx):
        '''
        Define o canal atual como o canal de notificações de novas partidas.
        '''
        ConfigService.set_notification_channel(ctx.channel.id)
        await ctx.send(f"✅ Canal {ctx.channel.mention} configurado para receber notificações de partidas!")

    @tasks.loop(minutes=45)
    async def check_new_matches(self):
        '''
        Task que roda a cada 45 minutos para verificar novas partidas.
        '''
        try:
            channel_id = ConfigService.get_notification_channel()
            if not channel_id:
                logger.info("Canal de notificações não configurado.")
                return

            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Canal {channel_id} não encontrado.")
                return

            # Carregar todos os usuários cadastrados
            import json
            import os
            if not os.path.exists('data/users.json'):
                return

            with open('data/users.json', 'r') as f:
                users = json.load(f)

            for discord_id, steam_id in users.items():
                # Buscar partidas recentes
                matches = LeetifyService.get_recent_matches(steam_id)
                if not matches:
                    continue

                latest_match = matches[0]
                latest_match_id = latest_match.get('id')

                # Comparar com última partida conhecida
                last_known_id = MatchTrackerService.get_last_match_id(discord_id)

                if last_known_id != latest_match_id:
                    # Nova partida encontrada!
                    MatchTrackerService.update_last_match(discord_id, latest_match_id)

                    # Buscar detalhes completos
                    match_details = LeetifyService.get_match_details(latest_match_id)
                    if not match_details:
                        continue

                    # Montar notificação
                    await self._send_match_notification(channel, discord_id, match_details)

        except Exception as e:
            logger.error(f"Erro no check_new_matches: {e}")

    @check_new_matches.before_loop
    async def before_check_new_matches(self):
        await self.bot.wait_until_ready()

    async def _send_match_notification(self, channel, discord_id, match):
        '''
        Envia notificação de nova partida.
        '''
        try:
            user = await self.bot.fetch_user(int(discord_id))
            steam_id = UserService.get_steam_id(discord_id)
            
            # Buscar stats do jogador
            player_stats = StatsService.extract_player_stats(match, steam_id)
            if not player_stats:
                return

            # Verificar outros usuários cadastrados na partida
            other_registered = []
            import json
            if os.path.exists('data/users.json'):
                with open('data/users.json', 'r') as f:
                    all_users = json.load(f)
                    registered_steam_ids = set(all_users.values())
                
                for stat in match.get('stats', []):
                    if stat['steam64_id'] in registered_steam_ids and stat['steam64_id'] != steam_id:
                        other_registered.append(stat.get('name', 'Unknown'))

            embed = EmbedService.create_notification_embed(user, match, player_stats, other_registered)
            await channel.send(embed=embed)

        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")

    @commands.command(name="ajuda", help="Lista personalizada de comandos.")
    async def ajuda(self, ctx):
        embed = discord.Embed(
            title="🤖 Ajuda - CS2 Tracker Bot",
            description="Comandos disponíveis para rastreamento de CS2:",
            color=0x00ff00
        )
        embed.add_field(
            name="📋 Perfil e Cadastro",
            value=(
                "`!cadastro @user <steamid>` - Vincula Steam ID ao usuário\n"
                "`!perfil [@user]` - Perfil completo com ranks, stats e squad"
            ),
            inline=False
        )
        embed.add_field(
            name="📊 Stats e Performance",
            value=(
                "`!performance [@user]` - Stats das últimas partidas\n"
                "`!recentes [@user]` - Últimas 5 partidas com stats detalhados\n"
                "`!kd [@user]` - K/D, HS%, Rating e Win Rate%\n"
                "`!leaderboard` - Ranking de todos os usuários"
            ),
            inline=False
        )
        embed.add_field(
            name="🎮 Partidas e Squad",
            value=(
                "`!partida <match_id>` - Análise detalhada de uma partida\n"
                "`!squad [@user]` - Companheiros de equipe frequentes\n"
                "`!xit [@user] [limite]` - Conta cheaters encontrados"
            ),
            inline=False
        )
        embed.add_field(
            name="⚙️ Configuração",
            value="`!config_canal` - [Admin] Define canal de notificações",
            inline=False
        )
        embed.add_field(
            name="🎲 Diversão",
            value="`!ping / !fala / !bolso` - Comandos de interação",
            inline=False
        )
        embed.set_footer(text="Use !<comando> para mais detalhes")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CS2Commands(bot))
