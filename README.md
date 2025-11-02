# myLife - Sistema de Gestão de Tarefas

Sistema completo de gestão de tarefas com autenticação, banco de dados e recuperação de senha.

## 🚀 Funcionalidades

- ✅ Sistema de autenticação (login, cadastro, logout)
- ✅ Banco de dados multi-usuário (cada usuário tem suas próprias tarefas)
- ✅ Recuperação de senha por email
- ✅ Dashboard com estatísticas e calendário semanal
- ✅ Tarefas com descrição, data e links
- ✅ Interface responsiva e moderna

## 📋 Pré-requisitos

- Python 3.11+
- pip

## 🔧 Instalação Local

1. **Clone o repositório:**
```bash
git clone <seu-repositorio>
cd Gestão_Tarefa
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente (opcional para email):**
Crie um arquivo `.env` ou configure diretamente no código:
```bash
export MAIL_USERNAME=seu-email@gmail.com
export MAIL_PASSWORD=sua-senha-app
export SECRET_KEY=sua-chave-secreta
```

4. **Execute o aplicativo:**
```bash
python app.py
```

5. **Acesse no navegador:**
```
http://localhost:5000
```

## 📧 Configuração de Email (Opcional)

Para habilitar recuperação de senha por email:

### Gmail:
1. Ative verificação em duas etapas
2. Gere uma senha de app: https://myaccount.google.com/apppasswords
3. Configure as variáveis:
```bash
export MAIL_USERNAME=seu-email@gmail.com
export MAIL_PASSWORD=sua-senha-app
```

### Outlook/Hotmail:
```bash
export MAIL_SERVER=smtp-mail.outlook.com
export MAIL_USERNAME=seu-email@hotmail.com
export MAIL_PASSWORD=sua-senha
```

## 🌐 Hospedagem Gratuita no Render

### Passo a Passo:

1. **Crie uma conta no Render:**
   - Acesse: https://render.com
   - Faça login com GitHub, GitLab ou Google

2. **Conecte seu repositório:**
   - No dashboard, clique em "New +" → "Web Service"
   - Conecte seu repositório do GitHub/GitLab
   - Ou faça upload do código

3. **Configure o serviço:**
   - **Name:** mylife-app
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

4. **Adicione variáveis de ambiente:**
   - No dashboard do serviço, vá em "Environment"
   - Adicione:
     ```
     SECRET_KEY=<gere uma chave aleatória>
     FLASK_DEBUG=False
     DATABASE_URL=<será criado automaticamente pelo banco>
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     MAIL_USE_TLS=True
     MAIL_USERNAME=seu-email@gmail.com
     MAIL_PASSWORD=sua-senha-app
     ```

5. **Crie o banco de dados PostgreSQL:**
   - No dashboard, clique em "New +" → "PostgreSQL"
   - **Name:** mylife-db
   - **Plan:** Free
   - Copie a `DATABASE_URL` e adicione como variável de ambiente

6. **Deploy:**
   - Render fará deploy automático
   - Aguarde alguns minutos
   - Seu site estará disponível em: `https://mylife-app.onrender.com`

## 🔐 Segurança

- ✅ Senhas são armazenadas com hash (Werkzeug)
- ✅ Tokens de recuperação expiram em 1 hora
- ✅ Proteção CSRF (Flask-Login)
- ✅ Variáveis sensíveis em variáveis de ambiente
- ✅ SQL Injection protegido (SQLAlchemy ORM)

## 📱 Uso

1. **Cadastre-se** criando uma conta
2. **Faça login** com email e senha
3. **Adicione tarefas** usando o formulário
4. **Marque tarefas como concluídas** clicando em "Concluir"
5. **Personalize** o nome da sua lista
6. **Visualize estatísticas** no dashboard

## 🛠️ Tecnologias Utilizadas

- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **Flask-Login** - Autenticação de usuários
- **Flask-Mail** - Envio de emails
- **SQLite/PostgreSQL** - Banco de dados
- **Gunicorn** - Servidor WSGI para produção

## 👨‍💻 Desenvolvedor

**João Pedro Parizotto**
- Email: joaopedrocallado@hotmail.com
- Para projetos, propostas ou contato, envie um email!

## 📝 Licença

Este projeto foi desenvolvido por João Pedro Parizotto.
