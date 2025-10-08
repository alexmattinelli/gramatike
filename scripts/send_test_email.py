import sys
import os
import argparse
# Garante que o diretório raiz do projeto esteja no sys.path
try:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
except Exception:
    pass
from gramatike_app import create_app
from flask import current_app
from gramatike_app.utils.emailer import send_email, render_test_email


def main():
    parser = argparse.ArgumentParser(description="Enviar e-mail de teste (config SMTP opcional)")
    parser.add_argument("to", help="Destino (e-mail)")
    parser.add_argument("--subject", default="Teste de e-mail - Gramátike")
    parser.add_argument("--html", default="""
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Este é um teste de e-mail do Gramátike com o template completo.
        </p>
        <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
            Abaixo você pode ver um exemplo de botão com o estilo padrão:
        </p>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding:20px 0;">
                    <a href="#" style="display:inline-block; background:linear-gradient(135deg, #9B5DE5 0%, #6233B5 100%); color:#ffffff; padding:16px 40px; border-radius:12px; text-decoration:none; font-weight:700; font-size:16px; box-shadow:0 4px 12px rgba(155,93,229,0.3);">
                        ✓ Botão de Exemplo
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin:24px 0 0; font-size:14px; line-height:1.6; color:#666; text-align:center;">
            Este e-mail foi enviado com sucesso!
        </p>
    """)
    parser.add_argument("--title", default="Teste de E-mail", help="Título do e-mail (aparece no template)")
    parser.add_argument("--server", dest="server")
    parser.add_argument("--port", dest="port", type=int)
    parser.add_argument("--tls", dest="tls", action="store_true")
    parser.add_argument("--user", dest="user")
    parser.add_argument("--password", dest="password")
    parser.add_argument("--from-email", dest="from_email")
    parser.add_argument("--from-name", dest="from_name")
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        # Permite sobrescrever config via CLI
        if args.server:
            current_app.config["MAIL_SERVER"] = args.server
        if args.port:
            current_app.config["MAIL_PORT"] = args.port
        if args.tls:
            current_app.config["MAIL_USE_TLS"] = True
        if args.user:
            current_app.config["MAIL_USERNAME"] = args.user
            # define DEFAULT_SENDER se não vier explícito
            if not current_app.config.get("MAIL_DEFAULT_SENDER"):
                current_app.config["MAIL_DEFAULT_SENDER"] = args.user
        if args.password:
            current_app.config["MAIL_PASSWORD"] = args.password
        if args.from_email:
            current_app.config["MAIL_DEFAULT_SENDER"] = args.from_email
        if args.from_name:
            current_app.config["MAIL_SENDER_NAME"] = args.from_name

        # Usa o template com logo e estilo
        html_formatted = render_test_email(args.title, args.html)
        
        ok = send_email(args.to, args.subject, html_formatted)
        if ok:
            print(f"[OK] E-mail enviado para {args.to} via {current_app.config.get('MAIL_SERVER')}.")
            sys.exit(0)
        else:
            print("[ERRO] Não foi possível enviar o e-mail. Verifique SMTP (servidor, porta, usuário, senha, TLS).")
            sys.exit(1)


if __name__ == "__main__":
    main()
