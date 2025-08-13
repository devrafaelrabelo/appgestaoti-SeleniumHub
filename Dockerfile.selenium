# Usa a imagem oficial do Selenium com Chrome
FROM selenium/node-chrome:latest

# Etapa root para configurar perfil, antivnc, antifingerprint
USER root

# Instala utilitários necessários
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl unzip x11vnc && \
  rm -rf /var/lib/apt/lists/*

# Cria diretório de perfil do Chrome
RUN mkdir -p /home/seluser/chrome-profile/Default

# Copia o perfil personalizado do Chrome (opcional)
COPY chrome-profile/Default /home/seluser/chrome-profile/Default

# Gera nova senha VNC
RUN mkdir -p /home/seluser/.vnc && \
  x11vnc -storepasswd "include@1279" /home/seluser/.vnc/passwd && \
  chown -R seluser:seluser /home/seluser/.vnc && \
  chmod 600 /home/seluser/.vnc/passwd

# Corrige permissões do perfil
RUN chown -R seluser:seluser /home/seluser/chrome-profile

# Retorna ao usuário padrão da imagem Selenium
USER seluser

# Variáveis do Selenium Node
ENV SE_NODE_OVERRIDE_MAX_SESSIONS=true
ENV SE_NODE_MAX_SESSIONS=1
ENV SE_NODE_SESSION_TIMEOUT=300

# Configurações antifingerprint para o Chrome
ENV CHROME_OPTIONS="\
  --user-data-dir=/home/seluser/chrome-profile \
  --profile-directory=Default \
  --no-sandbox \
  --disable-dev-shm-usage \
  --disable-blink-features=AutomationControlled \
  --disable-extensions \
  --disable-infobars \
  --disable-popup-blocking \
  --disable-background-networking \
  --disable-default-apps \
  --disable-sync \
  --disable-translate \
  --mute-audio \
  --start-maximized \
  --disable-web-security \
  --ignore-certificate-errors \
  --ignore-ssl-errors \
  --disable-features=IsolateOrigins,site-per-process \
  --blink-settings=imagesEnabled=false"
