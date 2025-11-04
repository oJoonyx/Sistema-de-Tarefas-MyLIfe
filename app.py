from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import secrets
import locale
import os

app = Flask(__name__, template_folder='modelos')

# Configuração básica (usa variável de ambiente para produção)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
app.config['TESTING'] = False

# Configuração do banco de dados (usa variável de ambiente ou padrão local)
database_url = os.getenv('DATABASE_URL', None)
if not database_url:
    # Usar caminho absoluto para garantir persistência
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, 'tarefas.db')
    database_url = f'sqlite:///{database_path}'
else:
    # Ajustar para PostgreSQL no Render (formato: postgresql://...)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Garantir que o banco não seja recriado se já existir
app.config['SQLALCHEMY_ECHO'] = False

# Configuração do email (usando variáveis de ambiente para segurança)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
try:
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
except (ValueError, TypeError):
    app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', '')
# CERTIFIQUE-SE DE QUE MAIL_SUPPRESS_SEND ESTÁ DEFINIDO COMO False EM PRODUÇÃO!
app.config['MAIL_SUPPRESS_SEND'] = os.getenv('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Inicializar Mail apenas se configurações estiverem disponíveis
EMAIL_ENABLED = False
try:
    if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
        mail = Mail(app)
        EMAIL_ENABLED = True
    else:
        mail = None
        EMAIL_ENABLED = False
        print("⚠️  Email não configurado. Funcionalidade de recuperação de senha desabilitada.")
        print("   Configure as variáveis MAIL_USERNAME e MAIL_PASSWORD para habilitar.")
except Exception as e:
    mail = None
    EMAIL_ENABLED = False
    print(f"⚠️  Erro ao configurar email: {e}")

# Configurar locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR')
    except:
        pass

# Modelo de Usuário
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    nome_lista = db.Column(db.String(100), default="Minha Lista de Tarefas")
    token_recuperacao = db.Column(db.String(100))
    token_expiracao = db.Column(db.DateTime)
    tarefas = db.relationship('Tarefa', backref='usuario', lazy=True, cascade='all, delete-orphan')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def gerar_token_recuperacao(self):
        try:
            self.token_recuperacao = secrets.token_urlsafe(32)
            self.token_expiracao = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            return self.token_recuperacao
        except Exception as e:
            db.session.rollback()
            raise e

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    data = db.Column(db.String(20))
    link = db.Column(db.String(500))
    feito = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# Função auxiliar para calcular semana
def obter_semana():
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
             'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    
    hoje_str = hoje.strftime('%d/%m')
    semana = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        dia_str = dia.strftime('%d/%m')
        semana.append({
            'dia': dia_str,
            'dia_semana': dias_semana[i],
            'dia_numero': dia.day,
            'mes': meses[dia.month - 1],
            'ano': dia.year,
            'e_hoje': dia_str == hoje_str
        })
    return semana, hoje



# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        
        # Buscar email de forma case-insensitive
        usuario = Usuario.query.filter(db.func.lower(Usuario.email) == email.lower()).first()
        
        if usuario:
            if usuario.check_senha(senha):
                login_user(usuario)
                print(f"✅ Login realizado: {email}")
                flash('Login realizado com sucesso!', 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('index'))
            else:
                print(f"❌ Senha incorreta para: {email}")
                flash('Senha incorreta.', 'error')
        else:
            print(f"❌ Email não encontrado: {email}")
            # Debug: mostrar quantos usuários existem
            total_usuarios = Usuario.query.count()
            print(f"📊 Total de usuários no banco: {total_usuarios}")
            flash('Email não encontrado. Verifique se digitou corretamente ou cadastre-se.', 'error')
    
    return render_template('login.html')

# Rota de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        
        # Validações
        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('cadastro.html')
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('cadastro.html')
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('cadastro.html')
        
        # Verificar se email já existe (case-insensitive)
        if Usuario.query.filter(db.func.lower(Usuario.email) == email.lower()).first():
            flash('Este email já está cadastrado. Faça login ou use a recuperação de senha.', 'error')
            return render_template('cadastro.html')
        
        # Criar novo usuário
        novo_usuario = Usuario(nome=nome, email=email)
        novo_usuario.set_senha(senha)
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('cadastro.html')

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

# Rota de recuperação de senha (formulário)
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        # Buscar email de forma case-insensitive
        usuario = Usuario.query.filter(db.func.lower(Usuario.email) == email.lower()).first()
        
        if usuario:
            token = usuario.gerar_token_recuperacao()
            
            # Enviar email com link de recuperação
            if EMAIL_ENABLED and mail:
                try:
                    recovery_url = url_for('redefinir_senha', token=token, _external=True)
                    
                    msg = Message(
                        subject='Recuperação de Senha - myLife',
                        sender=app.config.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME']),
                        recipients=[email]
                    )
                    msg.body = f'''Olá {usuario.nome},

Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:

{recovery_url}

Este link expira em 1 hora.

Se você não solicitou esta recuperação, ignore este email.

Atenciosamente,
myLife
                    '''
                    mail.send(msg)
                    flash('Email de recuperação enviado! Verifique sua caixa de entrada.', 'success')
                except Exception as e:
                    # Em desenvolvimento, mostra o erro. Em produção, apenas mensagem genérica
                    error_msg = str(e) if app.config.get('DEBUG') else ''
                    print(f"Erro ao enviar email: {error_msg}")
                    flash('Erro ao enviar email. Tente novamente mais tarde ou entre em contato com o suporte.', 'error')
            else:
                # Email não configurado
                if app.config.get('DEBUG'):
                    # Apenas em desenvolvimento: mostrar link para debug
                    recovery_url = url_for('redefinir_senha', token=token, _external=True)
                    flash(f'⚠️ Email não configurado. Use este link para recuperar (APENAS DESENVOLVIMENTO): {recovery_url}', 'warning')
                else:
                    # Em produção: nunca mostrar o link
                    flash('⚠️ Email não configurado. Entre em contato com o suporte.', 'warning')
        else:
            # Mensagem mais útil e com sugestão de ação
            flash('Email não encontrado em nossa base de dados. Verifique se digitou corretamente ou cadastre-se primeiro.', 'error')
    
    return render_template('recuperar_senha.html')

# Rota para redefinir senha
@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    usuario = Usuario.query.filter_by(token_recuperacao=token).first()
    
    if not usuario or not usuario.token_expiracao or usuario.token_expiracao < datetime.utcnow():
        flash('Link inválido ou expirado. Solicite uma nova recuperação.', 'error')
        return redirect(url_for('recuperar_senha'))
    
    if request.method == 'POST':
        senha = request.form.get('senha', '').strip()
        confirmar_senha = request.form.get('confirmar_senha', '').strip()
        
        if not senha or not confirmar_senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('redefinir_senha.html', token=token)
        
        if senha != confirmar_senha:
            flash('As senhas não coincidem.', 'error')
            return render_template('redefinir_senha.html', token=token)
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('redefinir_senha.html', token=token)
        
        usuario.set_senha(senha)
        usuario.token_recuperacao = None
        usuario.token_expiracao = None
        db.session.commit()
        
        flash('Senha redefinida com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('redefinir_senha.html', token=token)

# Rota principal - exibe lista de tarefas (protegida)
@app.route('/')
@app.route('/dashboard')
@login_required
def index():
    tarefas_usuario = Tarefa.query.filter_by(usuario_id=current_user.id).all()
    tarefas_classificadas = sorted(tarefas_usuario, key=lambda t: t.feito)
    
    # Calcular estatísticas
    total_tarefas = len(tarefas_usuario)
    tarefas_completas = sum(1 for t in tarefas_usuario if t.feito)
    porcentagem = int((tarefas_completas / total_tarefas * 100) if total_tarefas > 0 else 0)
    
    # Obter semana
    semana, hoje = obter_semana()
    
    return render_template('index.html', 
                         tarefas=tarefas_classificadas,
                         nome_lista=current_user.nome_lista,
                         total_tarefas=total_tarefas,
                         tarefas_completas=tarefas_completas,
                         porcentagem=porcentagem,
                         semana=semana,
                         hoje=hoje.strftime('%d/%m/%Y'))

# Ação para adicionar nova tarefa
@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    texto_tarefa = request.form.get('texto_tarefa', '').strip()
    descricao = request.form.get('descricao', '').strip()
    data = request.form.get('data', '').strip()
    link = request.form.get('link', '').strip()
    
    if texto_tarefa:
        try:
            nova_tarefa = Tarefa(
                texto=texto_tarefa,
                descricao=descricao,
                data=data,
                link=link,
                usuario_id=current_user.id
            )
            db.session.add(nova_tarefa)
            db.session.commit()
            flash('Tarefa adicionada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao adicionar tarefa. Tente novamente.', 'error')
            print(f"Erro ao adicionar tarefa: {e}")
    else:
        flash('O título da tarefa é obrigatório.', 'error')
    
    return redirect(url_for('index'))

# Ação para atualizar nome da lista
@app.route('/atualizar_nome', methods=['POST'])
@login_required
def atualizar_nome():
    novo_nome = request.form.get('nome_lista', '').strip()
    if novo_nome:
        try:
            current_user.nome_lista = novo_nome
            db.session.commit()
            flash('Nome da lista atualizado!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar nome da lista.', 'error')
            print(f"Erro ao atualizar nome: {e}")
    else:
        flash('O nome da lista não pode estar vazio.', 'error')
    
    return redirect(url_for('index'))

# Ação para completar tarefa
@app.route('/completar/<int:id>')
@login_required
def completo(id):
    try:
        tarefa = Tarefa.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        tarefa.feito = True
        db.session.commit()
        flash('Tarefa marcada como concluída!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao marcar tarefa como concluída.', 'error')
        print(f"Erro ao completar tarefa: {e}")
    
    return redirect(url_for('index'))
# ===============================================
# INÍCIO DO BLOCO DE NOVAS ROTAS
# ===============================================

# Rota de Perfil (acessada pelo template 'perfil.html')
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        novo_nome = request.form.get('nome', '').strip()
        if novo_nome:
            try:
                current_user.nome = novo_nome
                db.session.commit()
                flash('Nome atualizado com sucesso!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Erro ao atualizar nome.', 'error')
        else:
            flash('O nome não pode ser vazio.', 'error')
        return redirect(url_for('perfil'))
        
    return render_template('perfil.html', user=current_user)


# Ação para deletar tarefa
@app.route('/deletar/<int:id>')
@login_required
def deletar(id):
    try:
        # Garante que a tarefa pertença ao usuário logado
        tarefa = Tarefa.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        db.session.delete(tarefa)
        db.session.commit()
        flash('Tarefa deletada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao deletar tarefa. Tente novamente.', 'error')
        print(f"Erro ao deletar tarefa: {e}")
    
    return redirect(url_for('index'))


# Ação para reverter status (desfazer conclusão)
@app.route('/reverter/<int:id>')
@login_required
def reverter(id):
    try:
        tarefa = Tarefa.query.filter_by(id=id, usuario_id=current_user.id).first_or_404()
        tarefa.feito = False
        db.session.commit()
        flash('Tarefa desmarcada como concluída.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao reverter status da tarefa.', 'error')
        print(f"Erro ao reverter tarefa: {e}")
    
    return redirect(url_for('index'))

# ===============================================
# FIM DO BLOCO DE NOVAS ROTAS
# ===============================================
# Criar tabelas do banco de dados (não recria se já existirem)
with app.app_context():
    try:
        # create_all só cria tabelas que não existem (não apaga dados existentes)
        db.create_all()
        print("✅ Banco de dados verificado. Tabelas criadas se necessário.")
        
        # Verificar se o banco está funcionando
        try:
            usuario_count = Usuario.query.count()
            print(f"📊 Usuários cadastrados no banco: {usuario_count}")
        except:
            print("📊 Banco de dados vazio (primeira execução)")
    except Exception as e:
        print(f"⚠️  Erro ao inicializar banco de dados: {e}")
        print(f"   Caminho do banco: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=True,
        use_debugger=True,
        host='0.0.0.0',
        port=5000
    )
