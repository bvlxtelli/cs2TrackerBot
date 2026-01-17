import discord
from discord.ext import commands
import difflib
import logging

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    '''
    Cog responsável por tratar erros de comandos e sugerir correções.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''
        Evento disparado quando ocorre um erro em um comando.
        '''
        if isinstance(error, commands.CommandNotFound):
            # Tentar encontrar o comando mais próximo
            cmd = ctx.invoked_with
            all_commands = [c.name for c in self.bot.commands]
            # Adicionar aliases
            for c in self.bot.commands:
                all_commands.extend(c.aliases)
            
            matches = difflib.get_close_matches(cmd, all_commands, n=1, cutoff=0.6)
            
            if matches:
                 await ctx.send(f"❌ Comando `{cmd}` não encontrado. Você quis dizer `!{matches[0]}`?")
            else:
                 # Ignorar se não houver nada parecido, para não spammar
                 pass
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Faltam argumentos! Uso correto: `!{ctx.command.name} {ctx.command.signature}`")
            return

        if isinstance(error, commands.BadArgument):
             await ctx.send("❌ Argumento inválido fornecido.")
             return

        # Logar outros erros
        logger.error(f'Erro no comando {ctx.command}: {error}')
        # Opcional: enviar mensagem genérica de erro
        # await ctx.send("❌ Ocorreu um erro ao executar este comando.")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
