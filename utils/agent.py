from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

from utils.Search import chromaSearchPlan

def print_full(text, chunk_size=1000):
    for i in range(0, len(text), chunk_size):
        print(text[i:i+chunk_size])

def gerarPrompt_query(query, nResults, threshold, vector_store):
    relevant = True
    results = chromaSearchPlan(query , nResults, vector_store)
    
    relevant_docs = []
    for doc, score in results:
        if score >= threshold:
            relevant_docs.append(doc.page_content)
            
            
    
    if not relevant_docs:
        relevant = False
        message = "Não há informação suficiente nos documentos para responder a query."
        return message, relevant
    else:
        relevant = True
        context_text = "\n\n".join(relevant_docs)
        prompt = f"""
        Você é um assistente que responde perguntas baseando-se apenas no contexto fornecido. Não utilize informações externas. No máximo acrescente ascentuação onde faltar.
        Contexto:
        {context_text}

        Em vez de mencionar “SPEAKER(nº)”, refira-se aos falantes como “um determinado indivíduo”, “outro indivíduo”, “uma pessoa”, “o participante”, “uma fonte”, “o palestrante”, “o interlocutor”, ou outros termos equivalentes, mantendo o sentido de que se trata de pessoas que falaram durante a palestra.
        Pergunta:
        {query}
        Responda de forma concisa e mencione os documentos como fontes, sem inventar informações.

        Resposta concisa:
        """
        return prompt, relevant

def gerarAnswer(query, nResult, threshold, vetor_store):
    result, relevant = gerarPrompt_query(query, nResult, threshold, vetor_store)
    if relevant:
        model = ChatOpenAI(model_name="gpt-4o", temperature = 0)
        answer = model.invoke(result)
        return answer.content
    else:
        return result

 