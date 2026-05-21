import os
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS

load_dotenv()

class IAService:
    MODELO = "llama-3.3-70b-versatile"
    MAX_TOKENS = 1024

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("ERRO: A GROQ_API_KEY não foi encontrada no arquivo .env!")
        self.cliente = Groq(api_key=api_key)

    def _deve_pesquisar_na_internet(self, mensagem_usuario: str) -> bool:
        """
        Usa uma chamada rápida à Groq para interpretar se o usuário está querendo
        saber preços, promoções ou procurando uma peça de hardware.
        """
        prompt_decisao = (
            "Analise a mensagem do usuário e responda APENAS com a palavra 'SIM' ou 'NAO'.\n"
            "Responda SIM se o usuário estiver explicitamente procurando comprar uma peça, querendo saber "
            "o preço de um componente, pedindo links de hardware ou procurando promoções.\n"
            "Responda NAO se for apenas uma saudação, conversa fiada, pergunta genérica de compatibilidade "
            "ou se não envolver busca de valores/produtos específicos.\n\n"
            f"Mensagem do usuário: '{mensagem_usuario}'"
        )
        
        try:
            resposta = self.cliente.chat.completions.create(
                model=self.MODELO,
                max_tokens=5,
                messages=[{"role": "user", "content": prompt_decisao}]
            )
            decisao = resposta.choices[0].message.content.strip().upper()
            return "SIM" in decisao
        except Exception:
            return True 

    def enviar_mensagem(self, historico: list, system_prompt: str) -> str:
        try:
        
            ultima_mensagem_usuario = ""
            if historico:
                for msg in reversed(historico):
                    if msg.get("role") == "user":
                        ultima_mensagem_usuario = msg.get("content", "")
                        break

            contexto_web = ""
            
          
            if ultima_mensagem_usuario and self._deve_pesquisar_na_internet(ultima_mensagem_usuario):
                
              
                termo_limpo = (
                    ultima_mensagem_usuario.lower()
                    .replace("procura", "").replace("busque", "").replace("ache", "")
                    .replace("comprar", "").replace("um ", "").replace("uma ", "").strip()
                )
                
                termo_busca = f'"{termo_limpo}" comprar preço "em oferta" (site:kabum.com.br OR site:pichau.com.br OR site:terabyteshop.com.br)'
                print(f"\n[JARVIS] Intenção de busca detectada! Pesquisando por: {termo_busca}")

                try:
                    with DDGS() as ddgs:
                        resultados = ddgs.text(termo_busca, max_results=6)
                        if resultados:
                            for r in resultados:
                                url_lower = r['href'].lower()
                                de_buscar = ["/conta", "/carrinho", "/login", "?search=", "com.br/&", "com.br/$", "ranking", "institucional"]
                                if any(exclusao in url_lower for exclusao in de_buscar):
                                    continue
                                contexto_web += f"PRODUTO: {r['title']}\nLINK DIRETO: {r['href']}\nCONTEÚDO: {r['body']}\n\n"
                except Exception as e:
                    print(f"Aviso: Falha ao buscar na web ({e}).")
            else:
                print("\n[JARVIS] Conversa normal detectada. Respondendo direto sem busca.")

            
            instrucoes_finais = f"{system_prompt}\n\n"
            if contexto_web:
                instrucoes_finais += (
                    "INSTRUÇÕES EM TEMPO REAL:\n"
                    "O usuário quer pesquisar preços. Use os dados abaixo para listar os modelos, lojas e valores.\n"
                    "Você DEVE OBRIGATORIAMENTE fornecer os links diretos recebidos abaixo no formato Markdown: [Ver na Loja](LINK).\n\n"
                    f"DADOS DA INTERNET:\n{contexto_web}"
                )
            else:
                instrucoes_finais += "O usuário está apenas conversando com você. Responda amigavelmente como o assistente Jarvis, sem inventar links ou preços."

           
            mensagem = [{"role": "system", "content": instrucoes_finais}] + historico

            resposta = self.cliente.chat.completions.create(
                model=self.MODELO,
                max_tokens=self.MAX_TOKENS,
                messages=mensagem
            )

            return resposta.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Erro no serviço de IA: {str(e)}")