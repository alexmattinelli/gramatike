import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from flask import current_app

def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> bool:
    try:
        cfg = current_app.config
        host = cfg.get('MAIL_SERVER')
        port = cfg.get('MAIL_PORT', 587)
        use_tls = cfg.get('MAIL_USE_TLS', True)
        username = cfg.get('MAIL_USERNAME')
        password = cfg.get('MAIL_PASSWORD')
        sender = cfg.get('MAIL_DEFAULT_SENDER') or username
        sender_name = cfg.get('MAIL_SENDER_NAME', 'Gramátike')
        
        # Validação de configuração
        if not host or not sender:
            msg_error = 'Envio de e-mail desativado: MAIL_SERVER ou MAIL_DEFAULT_SENDER não configurados.'
            try:
                current_app.logger.warning(msg_error)
            except Exception:
                print(f"[AVISO] {msg_error}", flush=True)
            return False
        
        if not username or not password:
            msg_error = f'Configuração SMTP incompleta: MAIL_USERNAME ou MAIL_PASSWORD ausentes. Host: {host}'
            try:
                current_app.logger.warning(msg_error)
            except Exception:
                print(f"[AVISO] {msg_error}", flush=True)
            return False
        
        body_text = text_body or ''
        msg = MIMEText(html_body, 'html', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = formataddr((sender_name, sender))
        msg['To'] = to_email
        
        # Conexão SMTP
        with smtplib.SMTP(host, port, timeout=15) as server:
            # Habilita debug em desenvolvimento (comentado por padrão)
            # server.set_debuglevel(1)
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.sendmail(sender, [to_email], msg.as_string())
        
        # Log de sucesso
        try:
            current_app.logger.info(f"E-mail enviado com sucesso para {to_email}")
        except Exception:
            print(f"[INFO] E-mail enviado com sucesso para {to_email}", flush=True)
        
        return True
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Falha de autenticação SMTP: {e}. Verifique MAIL_USERNAME e MAIL_PASSWORD."
        try:
            current_app.logger.error(error_msg)
        except Exception:
            print(f"[ERRO] {error_msg}", flush=True)
        return False
    except smtplib.SMTPException as e:
        error_msg = f"Erro SMTP ao enviar e-mail para {to_email}: {e}"
        try:
            current_app.logger.error(error_msg)
        except Exception:
            print(f"[ERRO] {error_msg}", flush=True)
        return False
    except Exception as e:
        error_msg = f"Falha inesperada ao enviar e-mail para {to_email}: {type(e).__name__}: {e}"
        try:
            current_app.logger.error(error_msg)
        except Exception:
            print(f"[ERRO] {error_msg}", flush=True)
        return False

def render_welcome_email(username: str) -> str:
    return f"""
    <div style='font-family: Nunito, Arial, sans-serif; line-height:1.6; color:#222;'>
      <h2 style='margin:0 0 .6rem; font-weight:700;'>Bem-vinde ao Gramátike, {username}!</h2>
            <p>Conta criada com sucesso. Estamos felizes em ter você aqui.</p>
            <ul>
                <li>Edu: trilhas de estudo e conteúdos.</li>
                <li>Comunidade: postagens e interações.</li>
            </ul>
      <p style='margin:1rem 0 0;'>Qualquer coisa, responda este e-mail.</p>
      <p style='font-size:.9rem; color:#666;'>© 2025 Gramátike • Inclusão e Gênero Neutro</p>
    </div>
    """


def render_verify_email(username: str, verify_url: str) -> str:
        return f"""
        <div style='font-family: Nunito, Arial, sans-serif; line-height:1.6; color:#222;'>
            <h2 style='margin:0 0 .6rem; font-weight:700;'>Confirme seu e-mail</h2>
            <p>Oi, {username}. Para proteger sua conta, confirme seu e-mail clicando no botão abaixo.</p>
            <p><a href='{verify_url}' style='display:inline-block;background:#9B5DE5;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none;'>Confirmar e-mail</a></p>
            <p style='font-size:.9rem;color:#666'>Se você não criou uma conta no Gramátike, pode ignorar este e-mail.</p>
        </div>
        """


def render_reset_email(username: str, reset_url: str) -> str:
        return f"""
        <div style='font-family: Nunito, Arial, sans-serif; line-height:1.6; color:#222;'>
            <h2 style='margin:0 0 .6rem; font-weight:700;'>Redefinir senha</h2>
            <p>Oi, {username}. Recebemos um pedido para redefinir sua senha. Clique abaixo para continuar.</p>
            <p><a href='{reset_url}' style='display:inline-block;background:#9B5DE5;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none;'>Redefinir senha</a></p>
            <p style='font-size:.9rem;color:#666'>Se você não solicitou, ignore este e-mail.</p>
        </div>
        """


def render_change_email_email(username: str, confirm_url: str, new_email: str) -> str:
        return f"""
        <div style='font-family: Nunito, Arial, sans-serif; line-height:1.6; color:#222;'>
            <h2 style='margin:0 0 .6rem; font-weight:700;'>Confirmar novo e-mail</h2>
            <p>Oi, {username}. Você solicitou alterar o e-mail da sua conta para <strong>{new_email}</strong>.</p>
            <p>Clique no botão abaixo para confirmar a troca.</p>
            <p><a href='{confirm_url}' style='display:inline-block;background:#9B5DE5;color:#fff;padding:10px 14px;border-radius:8px;text-decoration:none;'>Confirmar novo e-mail</a></p>
            <p style='font-size:.9rem;color:#666'>Se você não solicitou esta alteração, ignore este e-mail e sua conta continuará com o e-mail atual.</p>
        </div>
        """
