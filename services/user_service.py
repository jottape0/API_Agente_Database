import os
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

# Bibliotecas terceiras
import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não foi definido corretamente nas variáveis de ambiente!")

ALGORITHM = "HS256"

# Verificar que todas as variáveis de ambiente necessárias estão presentes
required_env_vars = ['DB_DRIVER', 'DB_SERVER', 'DB_DATABASE', 'DB_TRUSTED_CONNECTION']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")

# Configuração da conexão com o banco de dados
conn_str_users = (
    f"DRIVER={{{os.environ['DB_DRIVER']}}};"
    f"SERVER={os.environ['DB_SERVER']};"
    f"DATABASE={os.environ['DB_DATABASE']};"
    f"Trusted_Connection={os.environ['DB_TRUSTED_CONNECTION']};"
)

encoded_conn_str_users = quote_plus(conn_str_users)
users_db_uri = f"mssql+pyodbc:///?odbc_connect={encoded_conn_str_users}"

# Configuração do esquema de autenticação
bearer_scheme = HTTPBearer()


class UserService:
    """
    Serviço para gerenciamento de usuários, autenticação e autorização.
    
    Este serviço provê funcionalidades para registro, login, reset de senha,
    criação e verificação de tokens JWT.
    """

    def __init__(self, db_uri: str):
        """
        Inicializa o serviço de usuário.
        
        Args:
            db_uri: String de conexão com o banco de dados.
        """
        self.engine = create_engine(db_uri)

    def register_user(self, username: str, password: str, confirm_password: str) -> None:
        """
        Registra um novo usuário no sistema.
        
        Args:
            username: Nome de usuário.
            password: Senha do usuário.
            confirm_password: Confirmação da senha.
            
        Raises:
            ValueError: Se as senhas não coincidirem.
            Exception: Se ocorrer um erro ao cadastrar o usuário.
        """
        if password != confirm_password:
            raise ValueError("As senhas não coincidem.")
            
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        try:
            with self.engine.connect() as conn:
                query = text("INSERT INTO Usuarios (username, password_hash) VALUES (:username, :password)")
                conn.execute(query, {"username": username, "password": hashed_password})
                conn.commit()
        except Exception as e:
            raise Exception(f"Erro ao cadastrar usuário: {e}")
        
    def login_user(self, username: str, password: str) -> Dict[str, str]:
        """
        Realiza o login de um usuário e retorna um token de acesso.
        
        Args:
            username: Nome de usuário.
            password: Senha do usuário.
            
        Returns:
            Dicionário contendo o token de acesso e seu tipo.
            
        Raises:
            ValueError: Se o usuário ou senha estiverem incorretos.
            Exception: Se ocorrer um erro ao validar o login.
        """
        try:
            with self.engine.connect() as conn:
                query = text("SELECT username, password_hash FROM Usuarios WHERE username = :username")
                result = conn.execute(query, {"username": username})
                user_data = result.fetchone()
                
            if not user_data:
                raise ValueError("Usuário ou senha incorretos.")
                
            db_username, hashed_password = user_data
            
            if not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
                raise ValueError("Usuário ou senha incorretos.")
                
            access_token = self.create_access_token({"username": str(db_username)})
            return {"access_token": access_token, "token_type": "bearer"}
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Erro ao validar login: {e}")
        
    def reset_password(self, username: str, new_password: str, confirm_password: str) -> None:
        """
        Reseta a senha de um usuário.
        
        Args:
            username: Nome de usuário.
            new_password: Nova senha.
            confirm_password: Confirmação da nova senha.
            
        Raises:
            ValueError: Se as senhas não coincidirem ou o usuário não for encontrado.
            Exception: Se ocorrer um erro ao atualizar a senha.
        """
        if new_password != confirm_password:
            raise ValueError("As senhas não coincidem.")
            
        hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        try:
            with self.engine.connect() as conn:
                query = text("UPDATE Usuarios SET password_hash = :password WHERE username = :username")
                result = conn.execute(query, {"password": hashed_password, "username": username})
                conn.commit()
                
                if result.rowcount == 0:
                    raise ValueError("Usuário não encontrado.")
                    
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Erro ao atualizar senha: {e}")
        
    @staticmethod
    def get_user_service() -> 'UserService':
        """
        Retorna uma instância do serviço de usuário.
        
        Returns:
            Uma instância do UserService.
        """
        return UserService(users_db_uri)

    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Cria um token de acesso JWT.
        
        Args:
            data: Dados a serem incluídos no token.
            
        Returns:
            Token JWT codificado.
        """
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return token

    @staticmethod
    def verify_token(token: str) -> str:
        """
        Verifica e decodifica um token JWT.
        
        Args:
            token: Token JWT a ser verificado.
            
        Returns:
            Nome de usuário extraído do token.
            
        Raises:
            HTTPException: Se o token for inválido ou expirado.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("username")
            
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Token inválido. Usuário não encontrado."
                )
                
            return username
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token expirado."
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token inválido."
            )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    user_service: UserService = Depends(UserService.get_user_service)
) -> str:
    """
    Obtém o usuário atual a partir do token de autenticação.
    
    Esta função é usada como dependência em rotas protegidas.
    
    Args:
        credentials: Credenciais de autorização HTTP.
        user_service: Instância do serviço de usuário.
        
    Returns:
        Nome de usuário obtido do token.
        
    Raises:
        HTTPException: Se o token não for fornecido ou for inválido.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido."
        )
    
    token = credentials.credentials
    try:
        username = user_service.verify_token(token)
        return username
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro na verificação do token: {str(e)}"
        )