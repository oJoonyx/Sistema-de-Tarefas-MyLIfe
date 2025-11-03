# Guia de Solução de Problemas - myLife

## Problema: Email não encontrado / Banco de dados sendo apagado

### Possíveis Causas e Soluções:

### 1. Banco de Dados Local (Desenvolvimento)

**Problema:** O banco SQLite pode estar sendo recriado ou perdido.

**Solução:**
- O banco agora usa caminho absoluto: `E:\Gestão_Tarefa\tarefas.db`
- Verifique se o arquivo `tarefas.db` existe na pasta do projeto
- Se não existir, execute `python app.py` uma vez para criar

**Como verificar:**
```bash
# Verifique se o arquivo existe
dir tarefas.db

# Ou no PowerShell
Test-Path tarefas.db
```

### 2. Busca de Email Case-Insensitive

**Problema:** O sistema agora busca emails sem distinguir maiúsculas/minúsculas.

**Exemplo:**
- Se você cadastrou: `Joao@Gmail.com`
- Você pode fazer login com: `joao@gmail.com` ou `JOAO@GMAIL.COM`

### 3. Banco de Dados em Produção (Render)

**Problema:** No Render, você precisa usar PostgreSQL, não SQLite.

**Solução:**
1. Crie um banco PostgreSQL no Render
2. Configure a variável `DATABASE_URL` com a URL do PostgreSQL
3. O sistema detectará automaticamente e usará PostgreSQL

**Configuração no Render:**
```
DATABASE_URL=postgresql://usuario:senha@host:porta/banco
```

### 4. Logs de Debug

O sistema agora mostra logs no console:
- ✅ = Sucesso
- ❌ = Erro
- 📊 = Informação

**Exemplo de logs:**
```
✅ Banco de dados verificado. Tabelas criadas se necessário.
📊 Usuários cadastrados no banco: 3
✅ Novo usuário criado: teste@email.com (ID: 1)
✅ Login realizado: teste@email.com
```

### 5. Verificar Banco de Dados

**No console Python:**
```python
from app import app, db, Usuario
with app.app_context():
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"ID: {u.id}, Nome: {u.nome}, Email: {u.email}")
```

### 6. Problema de Persistência

**Se o banco continua sendo apagado:**

1. **Verifique permissões da pasta:**
   - Certifique-se que a pasta tem permissão de escrita

2. **Verifique se está usando o banco correto:**
   - O banco deve estar em: `E:\Gestão_Tarefa\tarefas.db`
   - Não em: `E:\Gestão_Tarefa\instance\tarefas.db`

3. **Backup do banco:**
   - Faça backup do arquivo `tarefas.db` regularmente
   - Copie para outro local seguro

### 7. Múltiplos Dispositivos

**O sistema funciona em múltiplos dispositivos se:**
- ✅ Você está usando o mesmo servidor (mesmo IP/domínio)
- ✅ O banco de dados está acessível para todos os dispositivos
- ✅ Você está usando a mesma URL para acessar

**Para desenvolvimento local:**
- Use o IP local da sua máquina: `http://SEU_IP:5000`
- Não use `localhost` (cada dispositivo tem seu próprio localhost)

**Para produção (Render):**
- Use a URL do Render: `https://seu-app.onrender.com`
- Funciona em qualquer dispositivo

### 8. Verificar se Email Está no Banco

**Comando SQL direto (se usar SQLite):**
```bash
# Instale o sqlite3 (geralmente já vem com Python)
sqlite3 tarefas.db

# Depois execute:
SELECT id, nome, email FROM usuario;
```

### 9. Problema Comum: Email Duplicado

**Se você tenta cadastrar e diz que já existe, mas não consegue fazer login:**

1. Verifique se digitou o email exatamente igual
2. O sistema agora é case-insensitive, então `Joao@Email.com` = `joao@email.com`
3. Use a recuperação de senha se esqueceu

### 10. Resetar Banco (CUIDADO - Apaga todos os dados)

**Apenas se necessário:**
```python
from app import app, db, Usuario, Tarefa
with app.app_context():
    # CUIDADO: Isso apaga TUDO
    db.drop_all()
    db.create_all()
    print("Banco resetado")
```

## Contato

Se o problema persistir:
- Email: joaopedrocallado@hotmail.com
- Verifique os logs no console do servidor
- Anote as mensagens de erro que aparecem

