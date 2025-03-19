"""
Módulo para gerenciamento de agentes de banco de dados usando LangChain.
Fornece funcionalidades para consultas em linguagem natural em bancos SQL Server.
"""

import os
from typing import Dict, List, Optional
from urllib.parse import quote_plus

from fastapi import HTTPException, status
from langchain.agents import AgentExecutor, create_react_agent
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain import hub

class DatabaseAgent:
    """
    Agente para consultas em linguagem natural em bancos de dados SQL Server.
    
    Utiliza LangChain e modelos de linguagem para converter perguntas em linguagem
    natural para consultas SQL e retornar respostas formatadas.
    """

    # Dicionário de strings de conexão predefinidas
    CONNECTION_STRINGS: Dict[str, str] = {
        "Banco de dados 1": (
            f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_DATABASE')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
        ),
        "Banco de dados 2": (
            f"DRIVER={{{os.getenv('DB_DRIVER_CRM')}}};"
            f"SERVER={os.getenv('DB_SERVER_CRM')};"
            f"DATABASE={os.getenv('DB_DATABASE_CRM')};"
            f"UID={os.getenv('DB_USER_CRM')};"
            f"PWD={os.getenv('DB_PASSWORD_CRM')};"
        )
    }

    # Template para prompt de consulta
    PROMPT_TEMPLATE = """
        Você é um assistente especializado em consultas SQL para o banco de dados, mas também pode conversar sobre outros tópicos.

        Diretrizes importantes:
        1. Construa queries SQL eficientes e concisas, quando solicitado.
        2. Se a pergunta não estiver relacionada a SQL, responda como um assistente de chat, sem tentar gerar uma query. O seu nome Groupnim AI.
        3. Não quebre as linhas durante a montagem das queries SQL.
        4. Use aspas simples para strings nas queries.
        5. Você tem apenas permissão de leitura (SELECT).
        6. Formate a resposta final de forma amigável e em português brasileiro, sem incluir a query SQL.
        7. NÃO mostre a query SQL na resposta final, apenas os resultados ou a estrutura da consulta.
        8. NÃO explique seu raciocínio na resposta final.
        9. Se a pergunta não estiver clara, peça esclarecimentos.
        10. Considere sempre o contexto das perguntas anteriores ao gerar a consulta ou resposta.
        11. Se o usuário te perguntar em qual banco está conectado, não mostre as tabelas. Informe apenas o nome do banco de dados.
        12. Para perguntas matemáticas, realize os cálculos necessários e valide se o resultado está correto antes de responder.
        13. Se houver um erro nos cálculos fornecidos pelo usuário, corrija e forneça a resposta correta, explicando a correção de forma objetiva e direta.
        14. Sempre forneça respostas específicas e factuais, evitando suposições.

        Pergunta: {q}
    """

    def __init__(
        self,
        db_name: str,
        model: str,
        api_key: Optional[str] = None
    ):
        """
        Inicializa um novo agente de banco de dados.
        
        Args:
            db_name: Nome do banco de dados para conexão
            model: Nome do modelo de linguagem a ser usado
            api_key: Chave de API opcional para o modelo de linguagem
            
        Raises:
            HTTPException: Se houver erro na inicialização do agente
        """
        try:
            self._validate_inputs(db_name, model)
            
            self.db_name = db_name
            self.model_name = model
            self.api_key = api_key
            
            # Configurar ambiente e conexões
            self._setup_environment()
            self._initialize_agent()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao inicializar agente de banco de dados: {str(e)}"
            )

    def _validate_inputs(self, db_name: str, model: str) -> None:
        """Valida os parâmetros de entrada."""
        if not db_name or db_name not in self.CONNECTION_STRINGS:
            raise ValueError(f"Banco de dados '{db_name}' não encontrado")
        if not model:
            raise ValueError("Modelo de linguagem não especificado")

    def _setup_environment(self) -> None:
        """Configura o ambiente e conexões necessárias."""
        if self.api_key:
            os.environ['OPENAI_API_KEY'] = self.api_key
            
        self.uri = self._build_connection_uri()
        self.db = SQLDatabase.from_uri(self.uri)
        self.model = ChatOpenAI(model=self.model_name)

    def _initialize_agent(self) -> None:
        """Inicializa o agente LangChain."""
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.model)
        system_message = hub.pull('hwchase17/react')
        
        self.agent = create_react_agent(
            llm=self.model,
            tools=self.toolkit.get_tools(),
            prompt=system_message
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.toolkit.get_tools(),
            verbose=True,
            handle_parsing_errors=True
        )
        
        self.prompt_template = PromptTemplate.from_template(self.PROMPT_TEMPLATE)

    def _build_connection_uri(self) -> str:
        """
        Constrói a URI de conexão com o banco de dados.
        
        Returns:
            String formatada da URI de conexão
        """
        conn_str = self.CONNECTION_STRINGS[self.db_name]
        encoded_conn_str = quote_plus(conn_str)
        return f"mssql+pyodbc:///?odbc_connect={encoded_conn_str}"

    @classmethod
    def add_connection(cls, db_name: str, connection_string: str) -> None:
        """
        Adiciona uma nova string de conexão ao dicionário de conexões.
        
        Args:
            db_name: Nome do banco de dados
            connection_string: String de conexão completa
            
        Raises:
            ValueError: Se o banco já existir
        """
        if db_name in cls.CONNECTION_STRINGS:
            raise ValueError(f"Banco de dados '{db_name}' já existe")
        cls.CONNECTION_STRINGS[db_name] = connection_string

    @classmethod
    def remove_connection(cls, db_name: str) -> None:
        """
        Remove uma string de conexão do dicionário de conexões.
        
        Args:
            db_name: Nome do banco de dados a ser removido
            
        Raises:
            ValueError: Se o banco não for encontrado
        """
        if db_name not in cls.CONNECTION_STRINGS:
            raise ValueError(f"Banco de dados '{db_name}' não encontrado")
        del cls.CONNECTION_STRINGS[db_name]

    def ask_question(self, question: str) -> str:
        """
        Processa uma pergunta em linguagem natural e retorna a resposta.
        
        Args:
            question: Pergunta em linguagem natural
            
        Returns:
            Resposta processada pelo agente
            
        Raises:
            HTTPException: Se houver erro no processamento da pergunta
        """
        try:
            if not question:
                raise ValueError("Pergunta não pode estar vazia")
                
            formatted_prompt = self.prompt_template.format(q=question)
            output = self.agent_executor.invoke({'input': formatted_prompt})
            
            return output.get('output', 'Não foi possível obter a resposta')
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao processar pergunta: {str(e)}"
            )
