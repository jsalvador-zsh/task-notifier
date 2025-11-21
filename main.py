#!/usr/bin/env python3
"""
Task Notifier - Sistema de alertas por voz para tareas
Monitorea tareas próximas a vencer o vencidas y notifica por audio usando síntesis de voz
"""

import os
import time
import psycopg2
from datetime import datetime, timedelta, timezone
import subprocess
import platform
import threading

# Importar configuración y GUI
import config
from gui_flet import GUIManager  # Interfaz moderna con Flet

# Set para evitar notificar la misma tarea múltiples veces
notified_tasks = set()

# Historial de notificaciones (últimas 100)
notification_history = []
MAX_HISTORY_SIZE = 100

# Manager de GUI
gui_manager = None

# Detectar sistema operativo
IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'


class TaskNotifier:
    """Gestor de notificaciones de tareas"""

    def __init__(self):
        self.conn = None
        self.connect_db()

    def connect_db(self):
        """Conectar a PostgreSQL"""
        try:
            self.conn = psycopg2.connect(config.DATABASE_URL)
            print("✅ Conectado a PostgreSQL")
            if gui_manager:
                gui_manager.update_state("active", "Conectado a BD")
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")
            if gui_manager:
                gui_manager.update_state("alert", "Error de conexión")
            raise

    def get_tasks_to_notify(self):
        """Obtener tareas que requieren notificación"""
        try:
            cursor = self.conn.cursor()

            now = datetime.now(timezone.utc)
            alert_time = now + timedelta(hours=config.ALERT_HOURS_BEFORE)

            # Buscar tareas pendientes o en progreso que:
            # 1. Ya vencieron (due_date < now)
            # 2. Están próximas a vencer (due_date < alert_time)
            query = """
                SELECT id, title, description, due_date, status, priority
                FROM tasks
                WHERE status IN ('pending', 'in_progress')
                  AND due_date IS NOT NULL
                  AND due_date <= %s
                ORDER BY due_date ASC
            """

            cursor.execute(query, (alert_time,))
            tasks = cursor.fetchall()
            cursor.close()

            return tasks

        except Exception as e:
            print(f"❌ Error al obtener tareas: {e}")
            # Reconectar si hay error
            self.connect_db()
            return []

    def generate_notification_text(self, task):
        """Generar texto de notificación basado en la tarea"""
        task_id, title, description, due_date, status, priority = task

        now = datetime.now(timezone.utc)

        # Convertir due_date a datetime si es solo date
        if isinstance(due_date, datetime):
            # Si ya es datetime, asegurarse que tiene timezone
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
        else:
            # Si es date, convertir a datetime al inicio del día UTC
            due_date = datetime.combine(due_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        # Determinar si está vencida o próxima a vencer
        if due_date < now:
            # Tarea vencida
            time_diff = now - due_date

            if time_diff.days > 0:
                time_text = f"hace {time_diff.days} día" + ("s" if time_diff.days > 1 else "")
            else:
                hours = int(time_diff.total_seconds() / 3600)
                time_text = f"hace {hours} hora" + ("s" if hours > 1 else "")

            # Determinar urgencia por prioridad
            priority_text = ""
            if priority == "urgent":
                priority_text = "URGENTE: "
            elif priority == "high":
                priority_text = "IMPORTANTE: "

            message = f"{priority_text}¡Atención! La tarea '{title}' venció {time_text}."
        else:
            # Tarea próxima a vencer
            time_diff = due_date - now

            if time_diff.days > 0:
                time_text = f"en {time_diff.days} día" + ("s" if time_diff.days > 1 else "")
            else:
                hours = int(time_diff.total_seconds() / 3600)
                time_text = f"en {hours} hora" + ("s" if hours > 1 else "")

            message = f"Recordatorio: La tarea '{title}' vence {time_text}."

        return message

    def text_to_speech(self, text):
        """Convertir texto a voz usando comandos nativos del sistema"""
        try:
            print(f"🔊 Reproduciendo audio: {text}")

            if IS_MACOS:
                # macOS: usar comando 'say' nativo
                # Listar voces disponibles: say -v '?'
                # Voces en español: Paulina (es_MX), Jorge (es_ES), Monica (es_MX)
                voice = "Paulina"  # Voz en español de México
                rate = config.TTS_SPEED  # Palabras por minuto

                # Ejecutar comando say
                subprocess.run(
                    ["say", "-v", voice, "-r", str(rate), text],
                    check=True,
                    capture_output=True
                )

            elif IS_WINDOWS:
                # Windows: usar PowerShell con System.Speech
                ps_script = f"""
                Add-Type -AssemblyName System.Speech
                $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
                $synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet,
                                          [System.Speech.Synthesis.VoiceAge]::NotSet,
                                          0,
                                          [System.Globalization.CultureInfo]::GetCultureInfo('es-ES'))
                $synth.Rate = {int((config.TTS_SPEED - 175) / 25)}
                $synth.Volume = {int(config.ALERT_VOLUME * 100)}
                $synth.Speak('{text}')
                """
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    check=True,
                    capture_output=True
                )

            elif IS_LINUX:
                # Linux: usar espeak-ng
                rate_espeak = config.TTS_SPEED  # espeak usa palabras por minuto
                volume = int(config.ALERT_VOLUME * 100)

                subprocess.run(
                    ["espeak-ng", "-v", "es", "-s", str(rate_espeak), "-a", str(volume), text],
                    check=True,
                    capture_output=True
                )
            else:
                print("⚠️ Sistema operativo no soportado para TTS")
                return False

            return True

        except FileNotFoundError as e:
            print(f"❌ Comando de voz no encontrado: {e}")
            print("💡 Instrucciones de instalación:")
            if IS_MACOS:
                print("   En macOS, descarga voces en español desde:")
                print("   Preferencias del Sistema > Accesibilidad > Contenido Hablado")
            elif IS_WINDOWS:
                print("   En Windows, instala voces en español desde:")
                print("   Configuración > Hora e idioma > Voz")
            elif IS_LINUX:
                print("   En Linux, instala espeak-ng:")
                print("   sudo apt-get install espeak-ng")
            return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Error al ejecutar comando de voz: {e}")
            return False

        except Exception as e:
            print(f"❌ Error al generar/reproducir audio: {e}")
            return False

    def notify_task(self, task, force=False):
        """Notificar una tarea por voz"""
        task_id = task[0]
        task_title = task[1]

        # Evitar notificar la misma tarea múltiples veces (excepto si es forzado)
        if not force and task_id in notified_tasks:
            return

        # Generar mensaje
        message = self.generate_notification_text(task)

        # Convertir a voz y reproducir
        success = self.text_to_speech(message)

        if success:
            # Marcar como notificada
            notified_tasks.add(task_id)

            # Agregar al historial
            global notification_history
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            history_entry = f"[{timestamp}] {task_title}"
            notification_history.append(history_entry)

            # Limitar tamaño del historial
            if len(notification_history) > MAX_HISTORY_SIZE:
                notification_history = notification_history[-MAX_HISTORY_SIZE:]

            print(f"✅ Notificación enviada: {message}")

    def check_and_notify(self):
        """Verificar tareas y enviar notificaciones"""
        print(f"\n🔍 Revisando tareas... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

        # Actualizar GUI: revisando
        if gui_manager:
            gui_manager.update_state("checking", "Revisando tareas...")

        tasks = self.get_tasks_to_notify()

        if not tasks:
            print("✓ No hay tareas pendientes que requieran notificación")
            # Actualizar GUI: sin tareas
            if gui_manager:
                gui_manager.update_state("active", "Sistema activo")
            return

        print(f"📋 Encontradas {len(tasks)} tarea(s) para notificar")

        # Actualizar GUI: alertas encontradas
        if gui_manager:
            gui_manager.update_state("alert", f"{len(tasks)} tarea(s) pendiente(s)", len(tasks))

        for task in tasks:
            self.notify_task(task)

        # Volver a estado activo después de notificar
        if gui_manager:
            gui_manager.update_state("active", "Notificaciones enviadas")

    def search_tasks(self, search_text="", filter_status="all"):
        """Buscar tareas en la base de datos"""
        try:
            cursor = self.conn.cursor()

            # Construir query según filtros
            query = """
                SELECT id, title, due_date, status, priority
                FROM tasks
                WHERE 1=1
            """
            params = []

            # Filtro de búsqueda por texto
            if search_text:
                query += " AND (title ILIKE %s OR description ILIKE %s)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])

            # Filtro por estado
            if filter_status == "pending":
                query += " AND status = 'pending'"
            elif filter_status == "in_progress":
                query += " AND status = 'in_progress'"
            elif filter_status == "overdue":
                query += " AND status IN ('pending', 'in_progress') AND due_date < CURRENT_DATE"

            query += " ORDER BY due_date ASC LIMIT 50"

            cursor.execute(query, params)
            tasks = cursor.fetchall()
            cursor.close()

            return tasks

        except Exception as e:
            print(f"❌ Error al buscar tareas: {e}")
            return []

    def notify_tasks_manual(self, tasks):
        """Notificar tareas manualmente (forzar notificación)"""
        for task in tasks:
            # Convertir a formato completo si es necesario
            if len(task) == 5:
                # Agregar descripción vacía
                task = (task[0], task[1], "", task[2], task[3], task[4])
            self.notify_task(task, force=True)

    def update_settings(self, settings):
        """Actualizar configuración en tiempo real"""
        config.CHECK_INTERVAL_SECONDS = settings['check_interval']
        config.ALERT_HOURS_BEFORE = settings['alert_hours']
        config.ALERT_VOLUME = settings['volume']
        config.TTS_SPEED = settings['speed']

        print(f"✅ Configuración actualizada:")
        print(f"   - Intervalo: {config.CHECK_INTERVAL_SECONDS}s")
        print(f"   - Anticipación: {config.ALERT_HOURS_BEFORE}h")
        print(f"   - Volumen: {int(config.ALERT_VOLUME * 100)}%")
        print(f"   - Velocidad: {config.TTS_SPEED} palabras/min")

    def run_loop(self):
        """Loop principal del notificador (ejecutar en hilo secundario)"""
        print("=" * 60)
        print("🔔 TASK NOTIFIER - Sistema de Alertas por Voz")
        print("=" * 60)
        print(f"⏱️  Intervalo de revisión: {config.CHECK_INTERVAL_SECONDS} segundos")
        print(f"⚠️  Alertar con: {config.ALERT_HOURS_BEFORE} horas de anticipación")
        print(f"🔊 Volumen: {int(config.ALERT_VOLUME * 100)}%")
        print("=" * 60)
        print("\n✨ Interfaz gráfica moderna con Flet activada")
        print("   - 🔍 Buscar Tareas - Buscar y notificar manualmente")
        print("   - 🔄 Revisar Ahora - Forzar revisión de tareas")
        print("   - ⚙️ Configuración - Ajustar intervalos y tiempos")
        print("   - 📜 Historial - Ver notificaciones enviadas")
        print("\n")

        # Actualizar GUI inicial
        if gui_manager:
            gui_manager.update_state("active", "Iniciando...")

        try:
            while True:
                self.check_and_notify()
                time.sleep(config.CHECK_INTERVAL_SECONDS)

        except Exception as e:
            print(f"\n❌ Error en notificador: {e}")
            if gui_manager:
                gui_manager.update_state("alert", "Error fatal")
            if self.conn:
                self.conn.close()


def main():
    """Función principal"""
    global gui_manager

    # Validar configuración
    if not config.DATABASE_URL:
        print("❌ Error: DATABASE_URL no está configurada en config.py")
        return

    print("🚀 Iniciando Task Notifier con interfaz moderna Flet...\n")

    # Crear GUI manager (debe estar en el hilo principal)
    gui_manager = GUIManager()
    gui_manager.start()

    # Crear notificador
    notifier = TaskNotifier()

    # Conectar callbacks de la GUI
    gui_manager.set_manual_check_callback(lambda: notifier.check_and_notify())
    gui_manager.set_get_tasks_callback(lambda search_text="", filter_status="all": notifier.search_tasks(search_text, filter_status))
    gui_manager.set_notify_tasks_callback(lambda tasks: notifier.notify_tasks_manual(tasks))
    gui_manager.set_get_history_callback(lambda: notification_history)
    gui_manager.set_save_settings_callback(lambda settings: notifier.update_settings(settings))

    # Iniciar notificador en hilo secundario
    notifier_thread = threading.Thread(target=notifier.run_loop, daemon=True)
    notifier_thread.start()

    # Ejecutar GUI en el hilo principal (BLOQUEANTE - debe ser el último)
    try:
        gui_manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Deteniendo notificador...")
    finally:
        gui_manager.stop()
        if notifier.conn:
            notifier.conn.close()
        print("✅ Programa finalizado")


if __name__ == "__main__":
    main()
