"""
        CRITÉRIOS DE SINCRONIZAÇÃO:

        Deve-se garantir que a inscrição tenha os estados de seus boletos
        iguais nas duas plataformas. Este estado deve ser verificado em dois
        sentidos:
            - Congressy -> MixEvents: todos os boletos cancelados da inscrição
                           na Mix devem estar ativos na Congressy.
            - MixEvents -> Congressy: todos os boletos ativos da inscrição na
                           Mix devem estar ativos na Congressy.
        """