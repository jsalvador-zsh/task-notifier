"""
Configuración del Task Notifier
================================
IMPORTANTE: Edita estos valores con tus credenciales y preferencias
"""

# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = "postgresql://taskwise_user:taskwise_secure_password_2024@167.235.225.187:5432/taskwise_db"

# ============================================================
# CONFIGURACIÓN DE VOZ (pyttsx3)
# ============================================================
# El sistema usará las voces instaladas en tu sistema operativo
# En Windows: Voces SAPI5 (busca voces en español en Configuración > Hora e idioma > Voz)
# En macOS: Voces disponibles en Preferencias del Sistema > Accesibilidad > Contenido Hablado
# En Linux: Voces de espeak-ng o festival

# Velocidad de lectura (palabras por minuto)
# Valor típico: 150-200 (ajusta según tu preferencia)
TTS_SPEED = 175

# ============================================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================================
# Intervalo de revisión en segundos (cada cuánto buscar tareas)
CHECK_INTERVAL_SECONDS = 180  # 3 minutos

# Alertar con X horas de anticipación
ALERT_HOURS_BEFORE = 24  # 24 horas

# Volumen del audio (0.0 = silencio, 1.0 = máximo)
ALERT_VOLUME = 1.0

# ============================================================
# CONFIGURACIÓN DE INTERFAZ GRÁFICA
# ============================================================
# Ruta a la imagen del avatar (debe ser PNG con fondo transparente)
# Si no existe, se usará un círculo de color por defecto
AVATAR_IMAGE_PATH = "image.png"

# Tamaño del avatar flotante
AVATAR_SIZE = 80

# Posición desde el borde derecho (en píxeles)
AVATAR_MARGIN_RIGHT = 20

# Posición desde el borde superior (en píxeles)
AVATAR_MARGIN_TOP = 60

# Color del avatar cuando está activo
AVATAR_COLOR_ACTIVE = "#4CAF50"  # Verde

# Color del avatar cuando está revisando
AVATAR_COLOR_CHECKING = "#2196F3"  # Azul

# Color del avatar cuando hay alerta
AVATAR_COLOR_ALERT = "#FF5722"  # Rojo/Naranja

# Transparencia de la ventana (0.0 = invisible, 1.0 = opaco)
WINDOW_ALPHA = 0.95

# Mantener ventana siempre visible (encima de otras)
ALWAYS_ON_TOP = True
