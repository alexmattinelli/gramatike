#!/usr/bin/env python3
"""
Script de diagnóstico para configuração de email SMTP (especialmente Brevo).
Testa conexão, autenticação e envio de email com mensagens detalhadas.
"""

import sys
import os
import argparse
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def test_smtp_connection(host, port, use_tls=True):
    """Testa se consegue conectar ao servidor SMTP."""
    print(f"\n1. Testando conexão com {host}:{port}...")
    try:
        server = smtplib.SMTP(host, port, timeout=15)
        print(f"   ✓ Conexão estabelecida com sucesso")
        return server
    except Exception as e:
        print(f"   ✗ ERRO ao conectar: {e}")
        return None

def test_tls(server):
    """Testa se consegue estabelecer TLS."""
    print(f"\n2. Testando TLS/STARTTLS...")
    try:
        server.starttls()
        print(f"   ✓ TLS estabelecido com sucesso")
        return True
    except Exception as e:
        print(f"   ✗ ERRO ao estabelecer TLS: {e}")
        return False

def test_authentication(server, username, password):
    """Testa autenticação SMTP."""
    print(f"\n3. Testando autenticação...")
    print(f"   Username: {username[:20]}{'...' if len(username) > 20 else ''}")
    try:
        server.login(username, password)
        print(f"   ✓ Autenticação bem-sucedida")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"   ✗ ERRO de autenticação: {e}")
        print(f"   DICA: Para Brevo, username e password devem ser a MESMA chave SMTP (xsmtpsib-...)")
        return False
    except Exception as e:
        print(f"   ✗ ERRO inesperado na autenticação: {e}")
        return False

def test_send_email(server, from_email, to_email, sender_name="Gramátike"):
    """Testa envio de email."""
    print(f"\n4. Testando envio de email...")
    print(f"   De: {from_email}")
    print(f"   Para: {to_email}")
    
    try:
        html_body = """
        <div style='font-family: Arial, sans-serif;'>
            <h2>Email de Teste - Diagnóstico Brevo</h2>
            <p>Este é um email de teste enviado pelo script de diagnóstico do Gramátike.</p>
            <p>Se você recebeu este email, a configuração SMTP está funcionando corretamente!</p>
        </div>
        """
        
        msg = MIMEText(html_body, 'html', 'utf-8')
        msg['Subject'] = 'Teste de Email - Diagnóstico Gramátike'
        msg['From'] = formataddr((sender_name, from_email))
        msg['To'] = to_email
        
        server.sendmail(from_email, [to_email], msg.as_string())
        print(f"   ✓ Email enviado com sucesso!")
        print(f"   VERIFIQUE: Caixa de entrada de {to_email} (pode estar no spam)")
        return True
    except Exception as e:
        print(f"   ✗ ERRO ao enviar email: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Diagnóstico de configuração SMTP para Brevo/Sendinblue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Usando variáveis de ambiente
  export BREVO_SMTP_KEY="xsmtpsib-..."
  python3 scripts/diagnose_email.py test@example.com

  # Passando parâmetros manualmente
  python3 scripts/diagnose_email.py test@example.com \\
    --server smtp-relay.brevo.com \\
    --smtp-key xsmtpsib-... \\
    --from no-reply@gramatike.com.br

IMPORTANTE para Brevo:
  1. A chave SMTP começa com 'xsmtpsib-' (não confundir com API Key 'xkeysib-')
  2. Username e Password devem ser A MESMA chave SMTP
  3. O email remetente DEVE estar verificado no Brevo
  4. Configure SPF/DKIM no seu domínio
        """
    )
    
    parser.add_argument('to_email', help='Email de destino para o teste')
    parser.add_argument('--server', default='smtp-relay.brevo.com', 
                        help='Servidor SMTP (padrão: smtp-relay.brevo.com)')
    parser.add_argument('--port', type=int, default=587, 
                        help='Porta SMTP (padrão: 587)')
    parser.add_argument('--smtp-key', help='Chave SMTP do Brevo (xsmtpsib-...)')
    parser.add_argument('--from', dest='from_email', 
                        default='no-reply@gramatike.com.br',
                        help='Email remetente (deve estar verificado no Brevo)')
    parser.add_argument('--from-name', dest='from_name', 
                        default='Gramátike',
                        help='Nome do remetente')
    parser.add_argument('--no-tls', action='store_true', 
                        help='Desabilitar TLS (não recomendado)')
    
    args = parser.parse_args()
    
    # Tenta pegar SMTP key do ambiente se não fornecida
    smtp_key = args.smtp_key or os.getenv('BREVO_SMTP_KEY') or os.getenv('BREVO_API_KEY')
    
    if not smtp_key:
        print("ERRO: Chave SMTP não fornecida.")
        print("Use --smtp-key ou defina BREVO_SMTP_KEY no ambiente.")
        sys.exit(1)
    
    # Validação básica da chave
    if smtp_key.startswith('xkeysib-'):
        print("⚠ AVISO: Você está usando uma API Key (xkeysib-), não uma SMTP Key.")
        print("         Para Brevo, você precisa da SMTP Key (xsmtpsib-...).")
        print("         A API Key pode funcionar, mas a SMTP Key é recomendada.")
    elif not smtp_key.startswith('xsmtpsib-'):
        print("⚠ AVISO: Chave SMTP não começa com 'xsmtpsib-'.")
        print("         Verifique se está usando a chave correta do Brevo.")
    
    print("=" * 70)
    print("DIAGNÓSTICO DE EMAIL SMTP - BREVO")
    print("=" * 70)
    print(f"\nConfiguração:")
    print(f"  Servidor: {args.server}:{args.port}")
    print(f"  TLS: {'Sim' if not args.no_tls else 'Não'}")
    print(f"  De: {args.from_email}")
    print(f"  Para: {args.to_email}")
    
    # Executa testes sequencialmente
    server = test_smtp_connection(args.server, args.port)
    if not server:
        print("\n❌ Falha na conexão. Verifique firewall e conexão com internet.")
        sys.exit(1)
    
    if not args.no_tls:
        if not test_tls(server):
            print("\n❌ Falha no TLS. Tente --no-tls (não recomendado).")
            server.quit()
            sys.exit(1)
    
    if not test_authentication(server, smtp_key, smtp_key):
        print("\n❌ Falha na autenticação. Verifique a chave SMTP.")
        server.quit()
        sys.exit(1)
    
    if not test_send_email(server, args.from_email, args.to_email, args.from_name):
        print("\n❌ Falha no envio. Verifique se o email remetente está verificado no Brevo.")
        server.quit()
        sys.exit(1)
    
    server.quit()
    
    print("\n" + "=" * 70)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 70)
    print("\nPróximos passos:")
    print("  1. Verifique se o email chegou em", args.to_email)
    print("  2. Configure as mesmas variáveis de ambiente no Vercel/produção:")
    print(f"     MAIL_SERVER={args.server}")
    print(f"     MAIL_PORT={args.port}")
    print(f"     MAIL_USE_TLS=true")
    print(f"     MAIL_USERNAME={smtp_key[:20]}...")
    print(f"     MAIL_PASSWORD={smtp_key[:20]}...")
    print(f"     MAIL_DEFAULT_SENDER={args.from_email}")
    print(f"     MAIL_SENDER_NAME={args.from_name}")
    print("\n")

if __name__ == '__main__':
    main()
