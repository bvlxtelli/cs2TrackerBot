import discord
from discord.ext import commands
import logging
from services.response_service import ResponseService

logger = logging.getLogger(__name__)

class GeneralCommands(commands.Cog):
    '''
    Cog responsável pelos comandos gerais do bot.
    '''

    def __init__(self, bot):
        '''
        Inicializa o Cog de comandos gerais.

        Args:
            bot (commands.Bot): A instância do bot.
        '''
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Evento disparado quando o Cog está pronto.
        '''
        logger.info(f'GeneralCommands Cog loaded.')

    @commands.command(name="ping", help="Responde com Pong!")
    async def ping(self, ctx):
        '''
        Responde ao comando ping com "Pong!".
        
        Args:
            ctx (commands.Context): O contexto do comando.
        '''
        resposta = ResponseService.get_ping_response()
        logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
        await ctx.send(resposta)

    @commands.command(name="fala", help="Comando fala")
    async def fala(self, ctx):
        '''
        Responde ao comando fala com "moura".
        
        Args:
            ctx (commands.Context): O contexto do comando.
        '''
        resposta = ResponseService.get_fala_response()
        logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
        await ctx.send(resposta)

    @commands.command(name="bolso", help="Comando bolso")
    async def bolso(self, ctx):
        '''
        Responde ao comando bolso com "naro".
        
        Args:
            ctx (commands.Context): O contexto do comando.
        '''
        resposta = ResponseService.get_bolso_response()
        logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
        await ctx.send(resposta)

async def setup(bot):
    '''
    Função de configuração para carregar o Cog.

    Args:
        bot (commands.Bot): A instância do bot.
    '''
    await bot.add_cog(GeneralCommands(bot))
