"""
Módulo de controllers para gerenciamento de usuários e consultas ao banco de dados.
Este módulo contém todas as rotas da API e suas respectivas implementações.
"""

from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from entities.model_provider import ModelProvider
from entities.register_request import RegisterRequest
from entities.login_request import LoginRequest
from entities.token_response import TokenResponse
from entities.reset_password_request import ResetPasswordRequest
from entities.ask_query_response import AskQueryResponse
from entities.ask_query_request import AskQueryRequest
from entities.database_agente import DatabaseAgent
from services.user_service import UserService, get_current_user

from services.database_services import DatabaseService

router = APIRouter()
bearer_scheme = HTTPBearer()

@router.post(
    "/register",
    response_model=Dict[str, str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED,
    description="Registra um novo usuário no sistema"
)
async def register_user(
    req: RegisterRequest,
    user_service: UserService = Depends(UserService.get_user_service)
) -> Dict[str, str]:
    """
    Endpoint para registro de novos usuários.
    
    Args:
        req: Dados do usuário a ser registrado
        user_service: Serviço de usuário injetado via dependência
    
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se houver erro no registro
    """
    try:
        user_service.register_user(req.username, req.password, req.confirm_password)
        return {"message": "Usuário cadastrado com sucesso"}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao cadastrar usuário: {str(e)}"
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    description="Realiza login do usuário"
)
async def login(
    req: LoginRequest,
    user_service: UserService = Depends(UserService.get_user_service)
) -> TokenResponse:
    """
    Endpoint para autenticação de usuários.
    
    Args:
        req: Credenciais do usuário
        user_service: Serviço de usuário injetado via dependência
    
    Returns:
        Token de acesso
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    try:
        auth_result = user_service.login_user(req.username, req.password)
        return TokenResponse(access_token=auth_result["access_token"])
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao realizar login: {str(e)}"
        )

@router.post(
    "/reset_password",
    response_model=Dict[str, str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    description="Reseta a senha do usuário"
)
async def reset_password(
    req: ResetPasswordRequest,
    user_service: UserService = Depends(UserService.get_user_service)
) -> Dict[str, str]:
    """
    Endpoint para reset de senha.
    
    Args:
        req: Dados para reset de senha
        user_service: Serviço de usuário injetado via dependência
    
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se houver erro no reset de senha
    """
    try:
        user_service.reset_password(req.username, req.password, req.confirm_password)
        return {"message": "Senha atualizada com sucesso"}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao resetar senha: {str(e)}"
        )

@router.post(
    "/create_database",
    response_model=Dict[str, str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_201_CREATED,
    description="Cria um novo banco de dados"
)
async def create_database(
    db_name: str,
    server: str,
    database: str,
    user: str,
    password: str
) -> Dict[str, str]:
    """
    Endpoint para criação de banco de dados.
    
    Args:
        db_name: Nome do banco de dados
        server: Servidor do banco
        database: Nome do database
        user: Usuário do banco
        password: Senha do banco
    
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se houver erro na criação do banco
    """
    try:
        message = DatabaseService.create_database(db_name, server, database, user, password)
        return {"message": message}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar banco de dados: {str(e)}"
        )

@router.get(
    "/databases",
    response_model=List[str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    description="Lista todos os bancos de dados disponíveis"
)
async def get_available_databases() -> List[str]:
    """
    Endpoint para listar bancos de dados disponíveis.
    
    Returns:
        Lista de bancos de dados
    """
    return list(DatabaseAgent.CONNECTION_STRINGS.keys())

@router.delete(
    "/delete_database/{db_name}",
    response_model=Dict[str, str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    description="Remove um banco de dados"
)
async def delete_database(db_name: str) -> Dict[str, str]:
    """
    Endpoint para deletar banco de dados.
    
    Args:
        db_name: Nome do banco a ser deletado
    
    Returns:
        Mensagem de sucesso
        
    Raises:
        HTTPException: Se houver erro na deleção do banco
    """
    try:
        message = DatabaseService.delete_database(db_name)
        return {"message": message}
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar banco de dados: {str(e)}"
        )

@router.get(
    "/models",
    response_model=List[str],
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    description="Lista todos os modelos disponíveis"
)
async def get_available_models() -> List[str]:
    """
    Endpoint para listar modelos disponíveis.
    
    Returns:
        Lista de modelos
    """
    return ModelProvider.get_available_models()

@router.post(
    "/ask",
    response_model=AskQueryResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    description="Realiza uma consulta ao banco de dados"
)
async def ask_question(req: AskQueryRequest) -> AskQueryResponse:
    """
    Endpoint para realizar consultas ao banco de dados.
    
    Args:
        req: Dados da consulta
    
    Returns:
        Resposta da consulta
        
    Raises:
        HTTPException: Se houver erro na consulta
    """
    try:
        agent = DatabaseAgent(
            db_name=req.db_name,
            model=req.model,
            api_key=req.api_key
        )
        answer = agent.ask_question(req.question)
        return AskQueryResponse(answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar o banco de dados: {str(e)}"
        )
