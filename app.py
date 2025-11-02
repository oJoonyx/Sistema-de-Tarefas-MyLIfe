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
database_url = os.getenv('DATABASE_URL', 'sqlite:///tarefas.db')
# Ajustar para PostgreSQL no Render (formato: postgresql://...)
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Rota inicial - redireciona para login ou index
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha):
            login_user(usuario)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'error')
    
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
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
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
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# Rota de recuperação de senha (formulário)
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        usuario = Usuario.query.filter_by(email=email).first()
        
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
                    flash('Erro ao enviar email. O link de recuperação foi gerado. Entre em contato com o suporte.', 'error')
                    # Em caso de erro, ainda permite mostrar o link manualmente (apenas em DEBUG)
                    if app.config.get('DEBUG'):
                        flash(f'Link de recuperação (DEBUG): {recovery_url}', 'info')
            else:
                # Email não configurado - fornecer link manualmente (apenas em desenvolvimento)
                recovery_url = url_for('redefinir_senha', token=token, _external=True)
                if app.config.get('DEBUG'):
                    flash(f'⚠️ Email não configurado. Use este link para recuperar: {recovery_url}', 'warning')
                else:
                    flash('⚠️ Email não configurado. Entre em contato com o suporte.', 'warning')
        else:
            flash('Email não encontrado em nossa base de dados.', 'error')
    
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

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=True,
        use_debugger=True,
        host='0.0.0.0',
        port=5000
    )
