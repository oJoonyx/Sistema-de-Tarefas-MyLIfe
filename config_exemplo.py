# Configuração de Email - Exemplo
# Copie este arquivo e ajuste com suas credenciais de email

# Para Gmail:
# 1. Ative a verificação em duas etapas
# 2. Gere uma senha de app: https://myaccount.google.com/apppasswords
# 3. Use essa senha no MAIL_PASSWORD

EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'seu-email@gmail.com',
    'MAIL_PASSWORD': 'sua-senha-app'
}

# Para Outlook/Hotmail:
# EMAIL_CONFIG = {
#     'MAIL_SERVER': 'smtp-mail.outlook.com',
#     'MAIL_PORT': 587,
#     'MAIL_USE_TLS': True,
#     'MAIL_USERNAME': 'seu-email@hotmail.com',
#     'MAIL_PASSWORD': 'sua-senha'
# }

