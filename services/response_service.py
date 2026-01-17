class ResponseService:
    '''
    Serviço responsável por fornecer as respostas para os comandos do bot.
    '''

    @staticmethod
    def get_ping_response() -> str:
        '''
        Retorna a resposta para o comando de ping.

        Returns:
            str: A resposta "Pong!".
        '''
        return "Pong!"

    @staticmethod
    def get_fala_response() -> str:
        '''
        Retorna a resposta para o comando fala.

        Returns:
            str: A resposta "moura".
        '''
        return "moura"

    @staticmethod
    def get_bolso_response() -> str:
        '''
        Retorna a resposta para o comando bolso.

        Returns:
            str: A resposta "naro".
        '''
        return "naro"
