"""
Módulo de serviços para gerenciamento de conexões com bancos de dados.
Fornece funcionalidades para criar e deletar conexões com bancos de dados.
"""

from typing import Dict
from fastapi import HTTPException, status

from entities.database_agente import DatabaseAgent

class DatabaseService:
    """
    Serviço para gerenciamento de conexões com bancos de dados.
    
    Esta classe fornece métodos estáticos para gerenciar conexões
    com diferentes bancos de dados SQL Server.
    """
    
    DRIVER_NAME = "ODBC Driver 17 for SQL Server"
    
    @classmethod
    def validate_connection_params(
        cls,
        db_name: str,
        server: str,
        database: str,
        user: str,
        password: str
    ) -> None:
        """
        Valida os parâmetros de conexão com o banco de dados.
        
        Args:
            db_name: Nome identificador do banco de dados
            server: Endereço do servidor
            database: Nome do banco de dados
            user: Nome do usuário
            password: Senha do usuário
            
        Raises:
            ValueError: Se algum dos parâmetros for inválido
        """
        if not db_name or not isinstance(db_name, str):
            raise ValueError("Nome do banco de dados é obrigatório")
        
        if not server or not isinstance(server, str):
            raise ValueError("Servidor é obrigatório")
            
        if not database or not isinstance(database, str):
            raise ValueError("Database é obrigatório")
            
        if not user or not isinstance(user, str):
            raise ValueError("Usuário é obrigatório")
            
        if not password or not isinstance(password, str):
            raise ValueError("Senha é obrigatória")
            
        if db_name in DatabaseAgent.CONNECTION_STRINGS:
            raise ValueError(f"Já existe um banco de dados cadastrado com o nome '{db_name}'")

    @classmethod
    def create_database(
        cls,
        db_name: str,
        server: str,
        database: str,
        user: str,
        password: str
    ) -> Dict[str, str]:
        """
        Cria uma nova conexão com banco de dados.
        
        Args:
            db_name: Nome identificador do banco de dados
            server: Endereço do servidor
            database: Nome do banco de dados
            user: Nome do usuário
            password: Senha do usuário
            
        Returns:
            Dicionário com mensagem de sucesso
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
            HTTPException: Se houver erro ao criar a conexão
        """
        try:
            cls.validate_connection_params(db_name, server, database, user, password)
            
            connection_string = (
                f"DRIVER={{{cls.DRIVER_NAME}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={user};"
                f"PWD={password};"
            )
            
            DatabaseAgent.add_connection(db_name, connection_string)
            
            return {"message": f"Banco de dados '{db_name}' criado com sucesso."}
            
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar conexão com banco de dados: {str(e)}"
            )
    
    @classmethod
    def delete_database(cls, db_name: str) -> Dict[str, str]:
        """
        Remove uma conexão com banco de dados.
        
        Args:
            db_name: Nome identificador do banco de dados a ser removido
            
        Returns:
            Dicionário com mensagem de sucesso
            
        Raises:
            HTTPException: Se o banco não for encontrado ou houver erro na remoção
        """
        try:
            if not db_name:
                raise ValueError("Nome do banco de dados é obrigatório")
                
            if db_name not in DatabaseAgent.CONNECTION_STRINGS:
                raise ValueError(f"Banco de dados '{db_name}' não encontrado")
                
            del DatabaseAgent.CONNECTION_STRINGS[db_name]
            return {"message": f"Banco de dados '{db_name}' removido com sucesso."}
            
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(ve)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover banco de dados: {str(e)}"
            )
            
    @classmethod
    def get_connection_string(cls, db_name: str) -> str:
        """
        Obtém a string de conexão de um banco de dados.
        
        Args:
            db_name: Nome identificador do banco de dados
            
        Returns:
            String de conexão do banco de dados
            
        Raises:
            HTTPException: Se o banco não for encontrado
        """
        try:
            if not db_name:
                raise ValueError("Nome do banco de dados é obrigatório")
                
            if db_name not in DatabaseAgent.CONNECTION_STRINGS:
                raise ValueError(f"Banco de dados '{db_name}' não encontrado")
                
            return DatabaseAgent.CONNECTION_STRINGS[db_name]
            
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(ve)
            )