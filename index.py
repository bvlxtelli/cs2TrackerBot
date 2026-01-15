import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='[ %(asctime)s ] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_token(token: str) -> str:
    '''
    Recupera o token do ambiente.
    
    Args:
        token (str): Nome da variável de ambiente do token.
    Returns:
        str: O token.
    '''
    return os.getenv(token)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Conectado como {bot.user}")

    try:
        synced = await bot.tree.sync()
        logger.info(f"{len(synced)} slash commands sincronizados.")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos: {e}")

@bot.command()
async def ping(ctx):
    resposta = "Pong!"
    logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
    await ctx.send(resposta)

@bot.command()
async def fala(ctx):
    resposta = "moura"
    logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
    await ctx.send(resposta)

@bot.command()
async def bolso(ctx):
    resposta = "naro"
    logger.info(f"Comando {ctx.command.name} recebido. Respondendo com {resposta}!")
    await ctx.send(resposta)

#@bot.tree.command(name="ping", description="Testa a latência do bot")
#async def ping(interaction: discord.Interaction):
#    await interaction.response.send_message("🏓 Pong!")

#@bot.tree.command(name="fala", description="Descriçao do maior jogador de CS de todos os tempos")
#async def fala(interaction: discord.Interaction):
#    await interaction.response.send_message("moura")

#@bot.tree.command(name="hello", description="Diz olá")
#async def hello(interaction: discord.Interaction):
#    await interaction.response.send_message(f"Olá, {interaction.user.mention}!")

def main():
    '''
    Função principal para iniciar o bot.
    
    Returns:
        callable: Executa o bot.
    '''
    logger.info("Iniciando o bot...")
    token = get_token("BOT_TOKEN")

    return bot.run(token)

if __name__ == "__main__":
    main()