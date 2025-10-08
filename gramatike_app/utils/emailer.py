import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from flask import current_app

# Logo do Gramátike em base64 (favicon.png 48x48)
LOGO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAHVElEQVR4nO2ZW4xVVxnHf2vt6zn7nDM3ZhhhyFTuZbgWhAohhBSSJtqk0UQTNdGHJia+mPjgg4kmvvhgYmJ88KXRB19MfDAx0cSYaGKiSWOiSU0kBWkLlFKYGYYZZu6XOXvvtf6+rL0PZ2DOMDCdSdsv+WXvvc4+a+//+v/W+ta3BG7hFm7hpgYxQ42E6EeAZcAfga8AJw1uh1r6v/2b/01gH7AZWB3PPwSsEUKAd8jnRTUj5k/NKr8u7gVacvVu13gKKEfMD/s8AVn9rxI6OgLg/wXgKLAP2CCEIErD9Qr+bYT/TwT+F+CfiH+rgN+NB2A68AdGtxcKmQx+KAOVCigF2oLrAnMqvzGqHfpNCpYAtwOfBD4R93v0cwDc/r7nTrH5NwqpJZOZDH8H8FvgceAL9VL/IvDOyMqIJFNl/Rn9JuBbwLfj+VOjAlhrfgG8BrwOPBY97kP/KPCJuO/fDgAnxhqoVQPVqpJa00yXS/4DwC+AV4CPxXNHojyGpQ58WSlFSXh+BJgf5vGdqIHPjcogDby5Bnr7VFlredWY8GLUwKNRxkcj6JNxnjfXQE9M4+w49MdlEYA2xtTL5fIfgZ8DPwN+GrV8KmqgEbXQ1Ko1UiqXjgkh7gN2AGsndCpqYDqwQ0qxUQjxgBDiVeAAcH9M5UgDx+L+fgMAVEvz4vrPz/xpaflfgKeAp4Gno5fPAK8AP/yA3Pv+rwBPA99Xqt4M++E+54CHo/w9rYGXR2RQpYZk9a/AL4FdwK6oifPR+y8DvwNeB/YCy8qlegV4CXgBeHYCnO8/Fvd3Rc0XYzrnhBD/Ak7G/eAsgMsmkE2eM8PYXq2TP++qlt8TQrT0Sek/AZ4D/hy1/mJM498DL8Tv2IuOXgD2A39Dxy9G7T8XNf/n6Pl/xOO/EcbnxPNLUftvmkj2/Ru4VCr5rbkcRVIK/y6wG9gJPBtl/27M8d3R438B/o4G/A86gP3o9N0V9/fH8/+On7UH+GM8/x56ELfH8z9G4N+K6zwXn/FsqeRnJ5JNJwL/DvB+pRr+0FP7dwJfivkb5fMidDJqIAHejpoIGniw/jgzej5p4J4YRx/I+w/aPfRgHqhf79/j14J/XwBBJgMohc+M7N+K9P/PpPOPh/P/N/RbAJiBjnZC/2VgvhBiYbx+Jcojxs95U2sAAAvB/5tAt/5tBV4DXo3aG3W8FvCjiRzn88AWIcTNGh7/p/cMAO4DjgPvxfdvxLw/Hd/H/IemkuufifN/s+bkVDXwIPqXf2KAeBDYHpOuHb9mLN4z2jOQ15Z/ksARnVR+HJhrzNB7H2rgFXTgLonx4QT8y2q/N9FkfjHQR2dgZ6HrTQfujOs/Edff0Q9Af5pU/WnAwih/Q/o7Ufkvon/51+N+dyfkX5tK/unxAGx8w5to79c18FPBP4Aej0dZBL65/RH0oG6J+5ujBh6Mn/VAzP9NUQMPxfUfivN8KGrgocjnwbj+w1EDm+J+0MAD8fzNUQPbhqXfcqMm9kHrr8EXrv8I+hd8YrSMYSfxELrV3h5zejtyeBjdDm+P+zvicTvwSLw21rj+MPqXX19I4/pdkc8j8buhf+H1+48AD4/KxOh4E+i2O7j+Jvo/0e1xc/xQG8P0t6P/Exu3/o5I/uG4vxPN4ZF43WbgE/G6LWgOd6P/M7fi+rdEDn06zuPOaWrg0cnmP10AO6cJYPsU8n94shx+2AC2TQPAtqkC2DpNAA9MEcDWqeSfANhycwBsmSqALRP1fN3aBuO/NaZ/4+YBrJsGgHVTBbBuKvnXA+uny2HddAGsHY//dZM7vnYS+ddOBcDHpglg7VQBrJ1K/jWTOr5mMvnXTPL42skA3DxdAKtvEvzNHd8wCf/1kwBYO0UA6yfrvxuBr/3vAayeCoDVNwegZyr5V0/if/VkAFbfJIBVNwe/arIcVk2Hw6o/AKsBXgeOoOtKLnY3LD6aVnEhR//aHwDiAvNJdK0/BrwGfBgwwFfRHR8CPvt/BeC++MAtaANfRnf3RcBGIcQKoC8u6Wvt1U7osqtzxdL/FMB69GC+i279N6Mnr0WLdxOaX78Q4iN9WnUAP0K3eivR3/k8uvN3gI2RezeaV0uc+zeq1fBU/4IFfwr4E7omzAReic9ZCmwB7gA+BPwFLT8DnvkAtFvrzRH8A+hOzUJzuwsoA58HvobOZS7u54xWPcCPf/i1Z/sfAn4HfDY+Y0k8b0FLw4co2+8A7kXLzzKtuoGnTp/r3wB8B/g+sApdIpaiFWEhWv5zo/u/EM1xFVohVqO5L0A3Pr8Q42pF/IwFUQMr0a38HLTnl6PlIRc1sAw9yDOBF07V/P8g8ANgc5TfMuBx4LvAd9EKcD9aXhegO30/upN3oOV/Plq+Z6EVYTZavu9Gp/Ht6BS/A91Sr0TLz6KogXnxswajZO5Bd/oX//P/+y3cjPg3HvkSZPWAVfoAAAAASUVORK5CYII="

def _render_email_template(title: str, content: str) -> str:
    """Template base para todos os e-mails com logo e design consistente."""
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Mansalva&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
</head>
<body style="margin:0; padding:0; font-family:'Nunito', Arial, sans-serif; background:#f5f7fb; color:#222;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb; padding:40px 20px;">
        <tr>
            <td align="center">
                <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px; background:#ffffff; border-radius:20px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                    <!-- Header com logo -->
                    <tr>
                        <td style="background:linear-gradient(135deg, #9B5DE5 0%, #6233B5 100%); padding:40px 30px; text-align:center;">
                            <img src="data:image/png;base64,{LOGO_BASE64}" alt="Gramátike" width="60" height="60" style="display:block; margin:0 auto 16px;">
                            <h1 style="margin:0; font-family:'Mansalva', cursive; font-size:32px; color:#ffffff; font-weight:400; letter-spacing:1px;">Gramátike</h1>
                        </td>
                    </tr>
                    <!-- Conteúdo -->
                    <tr>
                        <td style="padding:40px 30px;">
                            <h2 style="margin:0 0 20px; font-size:24px; color:#6233B5; font-weight:700;">{title}</h2>
                            {content}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background:#f9f9f9; padding:30px; text-align:center; border-top:1px solid #e5e7eb;">
                            <p style="margin:0 0 8px; font-size:14px; color:#666;">
                                © 2025 Gramátike • Inclusão e Gênero Neutro
                            </p>
                            <p style="margin:0; font-size:12px; color:#999;">
                                Este é um e-mail automático.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """

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
    content = f"""
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Olá, <strong>{username}</strong>! 👋
        </p>
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Sua conta foi criada com sucesso. Estamos muito felizes em ter você aqui!
        </p>
        <div style="background:#f7f8ff; border-left:4px solid #9B5DE5; padding:20px; margin:24px 0; border-radius:8px;">
            <p style="margin:0 0 12px; font-size:15px; font-weight:600; color:#6233B5;">
                Explore o Gramátike:
            </p>
            <ul style="margin:0; padding-left:20px; color:#555; line-height:1.8;">
                <li><strong>Edu:</strong> Trilhas de estudo e conteúdos educativos</li>
                <li><strong>Comunidade:</strong> Postagens e interações com outres usuáries</li>
                <li><strong>Exercícios:</strong> Pratique e aprenda gramática</li>
            </ul>
        </div>
        <p style="margin:24px 0 0; font-size:15px; line-height:1.6; color:#555;">
            Qualquer dúvida, estamos aqui para ajudar! Bons estudos! 📚✨
        </p>
    """
    return _render_email_template("Bem-vinde ao Gramátike!", content)


def render_verify_email(username: str, verify_url: str) -> str:
    content = f"""
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Olá, <strong>{username}</strong>! 👋
        </p>
        <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
            Para proteger sua conta e garantir a segurança dos seus dados, precisamos confirmar seu e-mail.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding:20px 0;">
                    <a href="{verify_url}" style="display:inline-block; background:linear-gradient(135deg, #9B5DE5 0%, #6233B5 100%); color:#ffffff; padding:16px 40px; border-radius:12px; text-decoration:none; font-weight:700; font-size:16px; box-shadow:0 4px 12px rgba(155,93,229,0.3);">
                        ✓ Confirmar e-mail
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin:24px 0 0; font-size:14px; line-height:1.6; color:#666; text-align:center;">
            Se você não criou uma conta no Gramátike, pode ignorar este e-mail com segurança.
        </p>
    """
    return _render_email_template("Confirme seu e-mail", content)


def render_reset_email(username: str, reset_url: str) -> str:
    content = f"""
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Olá, <strong>{username}</strong>! 👋
        </p>
        <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
            Recebemos um pedido para redefinir a senha da sua conta. Clique no botão abaixo para criar uma nova senha.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding:20px 0;">
                    <a href="{reset_url}" style="display:inline-block; background:linear-gradient(135deg, #9B5DE5 0%, #6233B5 100%); color:#ffffff; padding:16px 40px; border-radius:12px; text-decoration:none; font-weight:700; font-size:16px; box-shadow:0 4px 12px rgba(155,93,229,0.3);">
                        🔑 Redefinir senha
                    </a>
                </td>
            </tr>
        </table>
        <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:16px; margin:24px 0; border-radius:8px;">
            <p style="margin:0; font-size:14px; line-height:1.6; color:#856404;">
                ⚠️ Se você não solicitou esta alteração, ignore este e-mail e sua senha permanecerá inalterada.
            </p>
        </div>
    """
    return _render_email_template("Redefinir senha", content)


def render_change_email_email(username: str, confirm_url: str, new_email: str) -> str:
    content = f"""
        <p style="margin:0 0 20px; font-size:16px; line-height:1.6; color:#333;">
            Olá, <strong>{username}</strong>! 👋
        </p>
        <p style="margin:0 0 12px; font-size:16px; line-height:1.6; color:#333;">
            Você solicitou alterar o e-mail da sua conta para:
        </p>
        <div style="background:#f7f8ff; padding:16px; margin:12px 0 24px; border-radius:8px; text-align:center;">
            <p style="margin:0; font-size:18px; font-weight:700; color:#6233B5;">
                {new_email}
            </p>
        </div>
        <p style="margin:0 0 24px; font-size:16px; line-height:1.6; color:#333;">
            Para confirmar esta alteração, clique no botão abaixo:
        </p>
        <table width="100%" cellpadding="0" cellspacing="0">
            <tr>
                <td align="center" style="padding:20px 0;">
                    <a href="{confirm_url}" style="display:inline-block; background:linear-gradient(135deg, #9B5DE5 0%, #6233B5 100%); color:#ffffff; padding:16px 40px; border-radius:12px; text-decoration:none; font-weight:700; font-size:16px; box-shadow:0 4px 12px rgba(155,93,229,0.3);">
                        ✓ Confirmar novo e-mail
                    </a>
                </td>
            </tr>
        </table>
        <p style="margin:24px 0 0; font-size:14px; line-height:1.6; color:#666; text-align:center;">
            Se você não solicitou esta alteração, ignore este e-mail e sua conta continuará com o e-mail atual.
        </p>
    """
    return _render_email_template("Confirmar novo e-mail", content)

