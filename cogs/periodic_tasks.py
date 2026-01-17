import discord
from discord.ext import commands, tasks
import logging
import random
import datetime
import json
import os
from services.config_service import ConfigService
from services.leetify_service import LeetifyService
from services.stats_service import StatsService
from services.embed_service import EmbedService

logger = logging.getLogger(__name__)

class PeriodicTasks(commands.Cog):
    '''
    Cog responsável por tarefas periódicas como resumos e mensagens aleatórias.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.random_messages.start()
        self.daily_summary.start()
        # self.weekly_summary.start() # Pode ser implementado depois

    def cog_unload(self):
        self.random_messages.cancel()
        self.daily_summary.cancel()

    @tasks.loop(hours=4) # Verificar a cada 4 horas se deve mandar mensagem
    async def random_messages(self):
        '''
        Envia mensagens aleatórias para engajamento.
        '''
        channel_id = ConfigService.get_notification_channel()
        if not channel_id:
            return

        # Chanve de 20% de enviar mensagem a cada check (pra não ficar chato)
        if random.random() > 0.2:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
            
        messages = [
            "Alguém on pra um compzin?",
            "Bora subir esse rating ou vão ficar chorando?",
            "Seus stats estão caindo hein... bora jogar!",
            "Global não se pega sozinho (mentira pega sim se for bom)",
            "Dica do dia: Usem smokes, por favor.",
            "Já treinou seu spray hoje?",
            "Saudades da Mirage...",
            "Quem vamos? 🔫",
            "To entediado, alguém feeda uma pra eu analisar?",
            "Aquele 1v3 ontem foi sorte hein..."
        ]
        
        await channel.send(random.choice(messages))

    @random_messages.before_loop
    async def before_random_messages(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def daily_summary(self):
        '''
        Envia resumo diário dos melhores jogadores.
        '''
        channel_id = ConfigService.get_notification_channel()
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return

        # Carregar usuários
        if not os.path.exists('data/users.json'):
            return

        with open('data/users.json', 'r') as f:
            users = json.load(f)

        if not users:
            return

        user_stats = []
        for discord_id, steam_id in users.items():
            try:
                # Pegar apenas as MUITO recentes (últimas 24h seria ideal, mas API não filtra por tempo, 
                # então pegamos as últimas 5 e vemos se foram 'hoje')
                # Para simplificar este MVP, vamos pegar as últimas 20 partidas e filtrar localmente se possível,
                # ou apenas fazer um ranking das últimas 20 partidas gerais ("Momento Atual")
                
                matches = LeetifyService.get_recent_matches(steam_id)
                # O ideal seria filtrar por data, mas o objeto match summary pode não ter data explícita fácil sem detalhe
                # O summary tem 'finished_at'? Não tenho certeza sem ver o JSON real, mas assumo que sim ou similar.
                # Se não tiver, vamos fazer ranking das "Últimas 5"
                
                recent_matches = matches[:5] 
                stats = StatsService.calculate_average_stats(recent_matches, steam_id)
                
                if stats:
                    discord_user = self.bot.get_user(int(discord_id))
                    if not discord_user:
                        try:
                            discord_user = await self.bot.fetch_user(int(discord_id))
                        except:
                            discord_user = None
                    
                    if discord_user:
                        user_stats.append({
                            'name': discord_user.display_name,
                            'kd': stats['avg_kd'],
                            'rating': stats['avg_rating'],
                            'winrate': stats['win_rate']
                        })
            except Exception as e:
                logger.error(f"Erro ao processar resumo para {discord_id}: {e}")

        if not user_stats:
            return

        # Ordenar por Rating
        user_stats.sort(key=lambda x: x['rating'], reverse=True)
        
        top_3 = user_stats[:3]
        
        embed = discord.Embed(
            title="📅 Resumo Diário - Top Players",
            description="Quem está carregando e quem está afundando (baseado nas últimas 5 partidas):",
            color=0xFFD700
        )
        
        medals = ["🥇", "🥈", "🥉"]
        for idx, p in enumerate(top_3):
            embed.add_field(
                name=f"{medals[idx]} {p['name']}",
                value=f"⭐ Rating: {p['rating']:.2f} | 💀 KD: {p['kd']:.2f} | 🏆 WR: {p['winrate']:.0f}%",
                inline=False
            )
            
        await channel.send(embed=embed)

    @daily_summary.before_loop
    async def before_daily_summary(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(PeriodicTasks(bot))
