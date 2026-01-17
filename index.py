import discord
from discord.ext import commands
import logging
import os
import asyncio
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

def get_token(token_name: str) -> str:
    '''
    Recupera o token do ambiente.
    
    Args:
        token_name (str): Nome da variável de ambiente do token.
        
    Returns:
        str: O token recuperado, ou None se não encontrado.
    '''
    return os.getenv(token_name)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    '''
    Evento disparado quando o bot está conectado e pronto.
    '''
    logger.info(f"Conectado como {bot.user}")

    try:
        synced = await bot.tree.sync()
        logger.info(f"{len(synced)} slash commands sincronizados.")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos: {e}")

async def load_cogs():
    '''
    Carrega dinamicamente todos os Cogs do diretório 'cogs'.
    '''
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                logger.info(f'Carregado: {filename}')
            except Exception as e:
                logger.error(f'Falha ao carregar {filename}: {e}')

async def main():
    '''
    Função principal para iniciar o bot.
    
    Responsável por verificar o token, carregar os cogs e iniciar a conexão.
    '''
    logger.info("Iniciando o bot...")
    token = get_token("BOT_TOKEN")
    
    if not token:
        logger.error("Token não encontrado!")
        return

    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # ignore exit
        pass