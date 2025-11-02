# 🚀 Sistema de Gestão de Tarefas - MyLife

### [ ACESSE O SITE AQUI: https://sistema-de-tarefas-mylife.onrender.com ]

Sistema Web de produtividade pessoal completo, construído em Python/Flask, com foco em segurança, persistência de dados e gerenciamento detalhado de tarefas para um único usuário.

## ✨ Destaques & Funcionalidades

| Recurso | Descrição | Tecnologia |
| :--- | :--- | :--- |
| **Segurança (Auth)** | Autenticação completa, hash de senhas e proteção CSRF. | Flask-Login, Werkzeug |
| **Persistência de Dados** | Banco de dados multi-usuário (tarefas são isoladas por login). | SQLAlchemy (SQLite/PostgreSQL) |
| **Recuperação de Acesso** | Fluxo completo de Login, Cadastro e **Recuperação de Senha por Email**. | Flask-Mail |
| **Dashboard** | Visualização de estatísticas de produtividade e calendário. | Lógica Python |
| **Design** | Interface moderna e responsiva (adaptável a Desktop e Mobile). | CSS (Layout Flexível) |

## 🛠️ Tecnologias Principais

Este projeto Full-Stack foi desenvolvido utilizando:

- **Backend:** Python 3.11+
- **Framework:** Flask
- **ORM:** SQLAlchemy (Gerenciamento de DB)
- **Serviços:** Gunicorn (Servidor WSGI para Produção), Flask-Mail

## 🔧 Instalação Local (Development Setup)

Siga os passos para rodar o projeto em sua máquina:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/oJoonyx/Sistema-de-Tarefas-MyLIfe.git](https://github.com/oJoonyx/Sistema-de-Tarefas-MyLIfe.git)
    cd Sistema-de-Tarefas-MyLIfe
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure o Ambiente:**
    Crie um arquivo `.env` na raiz do projeto e defina suas chaves (essenciais para produção):
    ```bash
    SECRET_KEY=sua_chave_secreta_aqui
    MAIL_USERNAME=seu-email@gmail.com
    MAIL_PASSWORD=sua-senha-app-gerada
    ```

4.  **Execute o Aplicativo:**
    ```bash
    python app.py
    ```

## 🌐 Deploy (Hospedagem)

O projeto está configurado para **Deploy Contínuo** via Render, utilizando `gunicorn app:app` como comando de inicialização e variáveis de ambiente para credenciais.

---

## 👨‍💻 Desenvolvedor

**João Pedro Parizotto**

- **Contato:** joaopedrocallado@hotmail.com
- **LinkedIn:** (Insira seu link do LinkedIn para contato profissional!)

---

### 📌 Próxima Ação:

**1. Salve este código** no seu arquivo `README.md`.
**2. Envie a atualização final para o GitHub:**

```bash
git add README.md
git commit -m "docs: Remove localhost e finaliza README para deploy no Render"
git push origin main
