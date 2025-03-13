from pydantic import BaseModel, Field, field_validator
from entities.database_agente import DatabaseAgent
from entities.model_provider import ModelProvider

class AskQueryRequest(BaseModel):
    question: str
    db_name: str  = Field(
        default="CRM Reports",
        description="Escolha o sistema que deseja conectar: CRM Reports, Group Atendimento Recargas"
    )
    # db_server: str = "string"
    # db_database: str = "string"
    # db_user: str = "string"
    # db_password: str = "string"
    model: str = Field(
        default=ModelProvider.AVAILABLE_MODELS[0],
        pattern=f'^({"|".join(ModelProvider.AVAILABLE_MODELS)})$'
    )
    api_key: str = None  # Se fornecida, usará esta chave para o OpenAI

    @field_validator('db_name')
    @classmethod
    def validate_db_name(cls, value):
        if value not in DatabaseAgent.CONNECTION_STRINGS.keys():
            raise ValueError(
                f"Banco de dados inválido. Opções disponíveis: {', '.join(DatabaseAgent.CONNECTION_STRINGS.keys())}"
            )
        return value

    @field_validator('model')
    @classmethod
    def validate_model(cls, value):
        if value not in ModelProvider.AVAILABLE_MODELS:
            raise ValueError(
                f"Modelo inválido. Opções disponíveis: {', '.join(ModelProvider.AVAILABLE_MODELS)}"
            )
        return value
    