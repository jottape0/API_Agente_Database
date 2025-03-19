Documentação da API

Esta documentação descreve os endpoints disponíveis e os esquemas utilizados na API. A API foi desenvolvida utilizando FastAPI, versão 0.1.0.
Endpoints
1. Registro de Usuário

    Endpoint: /register
    Método: POST
    Descrição: Registra um novo usuário no sistema.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
        Body (JSON):
            username (string) – Nome do usuário.
            password (string) – Senha do usuário.
            confirm_password (string) – Confirmação da senha.
    Respostas:
        201: Usuário registrado com sucesso. Retorna um objeto JSON com propriedades adicionais (par chave/valor do tipo string).
        422: Erro de validação, retornando os detalhes do erro.

2. Login

    Endpoint: /login
    Método: POST
    Descrição: Realiza o login do usuário.
    Requisição:
        Body (JSON):
            username (string) – Nome do usuário.
            password (string) – Senha do usuário.
    Respostas:
        200: Login realizado com sucesso. Retorna um token de acesso.
        422: Erro de validação.

3. Reset de Senha

    Endpoint: /reset_password
    Método: POST
    Descrição: Reseta a senha do usuário.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
        Body (JSON):
            username (string) – Nome do usuário.
            password (string) – Nova senha.
            confirm_password (string) – Confirmação da nova senha.
    Respostas:
        200: Senha redefinida com sucesso.
        422: Erro de validação.

4. Criação de Banco de Dados

    Endpoint: /create_database
    Método: POST
    Descrição: Cria um novo banco de dados.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
        Parâmetros de Query:
            db_name (string) – Nome do banco de dados.
            server (string) – Endereço ou nome do servidor.
            database (string) – Nome da base de dados.
            user (string) – Nome de usuário para o banco.
            password (string) – Senha para o banco.
    Respostas:
        201: Banco de dados criado com sucesso.
        422: Erro de validação.

5. Listar Bancos de Dados Disponíveis

    Endpoint: /databases
    Método: GET
    Descrição: Lista todos os bancos de dados disponíveis.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
    Respostas:
        200: Retorna uma lista (array) de nomes de bancos de dados.

6. Remoção de Banco de Dados

    Endpoint: /delete_database/{db_name}
    Método: DELETE
    Descrição: Remove um banco de dados.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
        Parâmetros de Caminho:
            db_name (string) – Nome do banco de dados a ser removido.
    Respostas:
        200: Banco de dados removido com sucesso.
        422: Erro de validação.

7. Listar Modelos Disponíveis

    Endpoint: /models
    Método: GET
    Descrição: Lista todos os modelos disponíveis.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
    Respostas:
        200: Retorna uma lista (array) com os modelos disponíveis.

8. Consulta ao Banco de Dados

    Endpoint: /ask
    Método: POST
    Descrição: Realiza uma consulta ao banco de dados.
    Requisição:
        Cabeçalhos: HTTPBearer (autenticação)
        Body (JSON):
            question (string) – Pergunta ou consulta a ser realizada. (Obrigatório)
            db_name (string) – Nome do banco de dados a ser consultado. (Padrão: "CRM Reports")
            model (string) – Modelo a ser utilizado. Valores aceitos: gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo. (Padrão: "gpt-4o-mini")
            api_key (string) – Chave da API (se necessário).
    Respostas:
        200: Consulta realizada com sucesso. Retorna a resposta da consulta.
        422: Erro de validação.

Schemas
AskQueryRequest

    Descrição: Esquema para requisição de consulta.
    Propriedades:
        question (string) – Obrigatório.
        db_name (string) – Nome do banco de dados. (Padrão: "CRM Reports")
        model (string) – Modelo a ser utilizado. Aceita: gpt-4o-mini, gpt-4-turbo, gpt-4, gpt-3.5-turbo. (Padrão: "gpt-4o-mini")
        api_key (string) – Chave da API.

AskQueryResponse

    Descrição: Esquema para resposta da consulta.
    Propriedades:
        answer (string) – Obrigatório.

HTTPValidationError

    Descrição: Esquema para erros de validação HTTP.
    Propriedades:
        detail (array) – Lista de erros de validação.

LoginRequest

    Descrição: Esquema para requisição de login.
    Propriedades:
        username (string) – Obrigatório.
        password (string) – Obrigatório.

RegisterRequest

    Descrição: Esquema para registro de um novo usuário.
    Propriedades:
        username (string) – Obrigatório.
        password (string) – Obrigatório.
        confirm_password (string) – Obrigatório.

ResetPasswordRequest

    Descrição: Esquema para resetar a senha do usuário.
    Propriedades:
        username (string) – Obrigatório.
        password (string) – Obrigatório.
        confirm_password (string) – Obrigatório.

TokenResponse

    Descrição: Esquema para resposta de autenticação.
    Propriedades:
        access_token (string) – Obrigatório.
        token_type (string) – Tipo do token. (Padrão: "bearer")

ValidationError

    Descrição: Detalhes dos erros de validação.
    Propriedades:
        loc (array) – Indica a localização do erro.
        msg (string) – Mensagem descritiva do erro.
        type (string) – Tipo do erro.

Autenticação

A maioria dos endpoints requer autenticação via HTTP Bearer Token. Certifique-se de incluir o token de acesso no cabeçalho Authorization das requisições que necessitam de autenticação.
