class PromptMestre:
    def __init__(self):
       

        self.persona = "Um especialista em preços de peças de computador."
        self.tarefa = "Ler preços de peças de computador na internet e filtrar o melhor preço."
        self.restricao = "Não ler preços de outras coisas e seguir um protocolo respeitável (não indicar lojas fakes)."
        self.formato = "Responder de uma forma muito maneira, mas simples de entender."

    def montar_system_prompt(self) -> str:
        system_prompt = f"""
        PERSONA: {self.persona}
        TAREFA: {self.tarefa}
        RESTRIÇÃO: {self.restricao}
        FORMATO: {self.formato}
        """
        return system_prompt.strip()

    def get_prompt(self) -> str:
        return self.montar_system_prompt()

if __name__ == "__main__":
    pm = PromptMestre()
    
    print("=" * 30)
    print("PROMPT MESTRE GERADO:")
    print("-" * 30)
    print(pm.get_prompt())
    print("=" * 30)