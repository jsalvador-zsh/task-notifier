
#!/usr/bin/env python3
"""
Ultra Minimal Task Notifier Widget

Widget circular minimalista que muestra solo el avatar.
- Tamaño: 70x70 píxeles
- Avatar circular con borde de color según estado
- Menú contextual (clic derecho) con todas las opciones
- Siempre visible en esquina superior derecha
- Transparente y discreto

Autor: Generado automáticamente
"""
import tkinter as tk
from tkinter import Menu, Toplevel, Label, Entry, Button, Text, Scrollbar, Scale, Frame, Listbox, MULTIPLE, END
from datetime import datetime
import threading
import os

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Intentar importar config
try:
    import config
except Exception:
    class _C:
        CHECK_INTERVAL_SECONDS = 180
        ALERT_HOURS_BEFORE = 24
        ALERT_VOLUME = 1.0
        TTS_SPEED = 180
        ALWAYS_ON_TOP = True
    config = _C()

class TaskNotifierTk:
    """Widget circular ultra minimalista"""

    WIDGET_SIZE = 70  # Tamaño del widget
    BORDER_WIDTH = 3  # Grosor del borde de estado

    # Ruta del avatar (relativa al directorio del script o directorio actual)
    @staticmethod
    def _get_avatar_path():
        """Obtener ruta del avatar buscando en múltiples ubicaciones"""
        possible_paths = [
            "image.png",  # Directorio actual
            os.path.join(os.path.dirname(__file__), "image.png"),  # Mismo dir que el script
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png"),  # Absoluto
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    AVATAR_PATH = _get_avatar_path.__func__()

    # Colores por estado
    COLORS = {
        "active": "#4CAF50",      # Verde - todo OK
        "checking": "#2196F3",    # Azul - revisando
        "alert": "#FF9800",       # Naranja - alertas
        "error": "#F44336"        # Rojo - error
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Task Notifier")

        # Ventana sin bordes y transparente
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)

        # Tamaño del widget
        self.root.geometry(f"{self.WIDGET_SIZE}x{self.WIDGET_SIZE}")
        self.root.resizable(False, False)

        # Callbacks
        self.on_manual_check = None
        self.on_get_tasks = None
        self.on_notify_tasks = None
        self.on_get_history = None
        self.on_save_settings = None

        # Estado
        self.current_state = "active"
        self.status_text = "Iniciando..."
        self.tasks_count = 0
        self.running = True

        # Avatar y canvas
        self.avatar_photo = None
        self.canvas = None

        # Construir UI
        self._build_ui()

        # Posicionar en esquina superior derecha
        self._position_top_right()

        # Bindings para interacción
        self._setup_bindings()

    def _position_top_right(self):
        """Posiciona el widget en esquina superior derecha"""
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        x = screen_w - self.WIDGET_SIZE - 15
        y = 50  # Debajo de la barra de menú
        self.root.geometry(f"+{x}+{y}")

    def _create_circular_avatar(self):
        """Crea avatar circular con borde de color"""
        if self.AVATAR_PATH is None or not os.path.exists(self.AVATAR_PATH):
            return None

        if not PIL_AVAILABLE:
            return None

        try:
            # Calcular tamaño del avatar (widget menos borde)
            avatar_size = self.WIDGET_SIZE - (self.BORDER_WIDTH * 2)

            # Cargar y redimensionar imagen
            img = Image.open(self.AVATAR_PATH).convert("RGBA")

            # Usar LANCZOS (compatible con Pillow 10.x)
            try:
                img = img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((avatar_size, avatar_size), Image.LANCZOS)

            # Crear máscara circular
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)

            # Aplicar máscara
            img.putalpha(mask)

            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error cargando avatar: {e}")
            return None

    def _build_ui(self):
        """Construir widget circular minimalista"""
        # Canvas para dibujar el avatar circular
        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDGET_SIZE,
            height=self.WIDGET_SIZE,
            bg="white",
            highlightthickness=0
        )
        self.canvas.pack()

        # Cargar avatar
        self.avatar_photo = self._create_circular_avatar()

        # Dibujar el widget
        self._redraw_widget()

    def _redraw_widget(self):
        """Redibuja el widget con el color de estado actual"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        color = self.COLORS.get(self.current_state, self.COLORS["active"])

        # Dibujar borde circular de color
        self.canvas.create_oval(
            0, 0,
            self.WIDGET_SIZE, self.WIDGET_SIZE,
            fill=color,
            outline=color,
            width=0
        )

        # Dibujar círculo blanco interior (para el avatar)
        offset = self.BORDER_WIDTH
        inner_size = self.WIDGET_SIZE - (offset * 2)
        self.canvas.create_oval(
            offset, offset,
            offset + inner_size, offset + inner_size,
            fill="white",
            outline="white",
            width=0
        )

        # Colocar avatar si existe
        if self.avatar_photo:
            self.canvas.create_image(
                self.WIDGET_SIZE // 2,
                self.WIDGET_SIZE // 2,
                image=self.avatar_photo
            )
        else:
            # Fallback: emoji
            self.canvas.create_text(
                self.WIDGET_SIZE // 2,
                self.WIDGET_SIZE // 2,
                text="📋",
                font=("Arial", 32)
            )

        # Badge de contador si hay tareas pendientes
        if self.tasks_count > 0:
            badge_size = 20
            badge_x = self.WIDGET_SIZE - badge_size // 2
            badge_y = badge_size // 2

            self.canvas.create_oval(
                badge_x - badge_size // 2,
                badge_y - badge_size // 2,
                badge_x + badge_size // 2,
                badge_y + badge_size // 2,
                fill="#F44336",
                outline="#F44336"
            )

            self.canvas.create_text(
                badge_x, badge_y,
                text=str(min(self.tasks_count, 99)),
                fill="white",
                font=("Arial", 10, "bold")
            )

    def _setup_bindings(self):
        """Configurar eventos de interacción"""
        # Variables para mover la ventana
        self.drag_data = {"x": 0, "y": 0}

        # Click izquierdo para arrastrar
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)

        # Click derecho para menú contextual
        self.canvas.bind("<Button-2>", self._show_context_menu)  # macOS: click derecho
        self.canvas.bind("<Button-3>", self._show_context_menu)  # Windows/Linux: click derecho

        # Doble click para revisar ahora
        self.canvas.bind("<Double-Button-1>", lambda e: self._trigger_check())

    def _start_drag(self, event):
        """Iniciar arrastre del widget"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def _on_drag(self, event):
        """Mover el widget"""
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    def _show_context_menu(self, event):
        """Mostrar menú contextual con todas las opciones"""
        menu = Menu(self.root, tearoff=0)

        # Estado actual
        state_emoji = {
            "active": "🟢",
            "checking": "🔵",
            "alert": "🟠",
            "error": "🔴"
        }
        emoji = state_emoji.get(self.current_state, "⚪")
        menu.add_command(
            label=f"{emoji} {self.status_text}",
            state="disabled"
        )

        menu.add_separator()

        # Opciones principales
        menu.add_command(label="🔍 Buscar tareas", command=self._show_task_search)
        menu.add_command(label="🔄 Revisar ahora", command=self._trigger_check)
        menu.add_command(label="📜 Historial", command=self._show_history)
        menu.add_command(label="⚙️ Configuración", command=self._show_settings)

        menu.add_separator()

        # Opciones secundarias
        menu.add_command(label="📍 Reposicionar", command=self._position_top_right)
        menu.add_command(label="❌ Salir", command=self._on_close)

        # Mostrar menú en la posición del cursor
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _show_task_search(self):
        """Diálogo para buscar tareas"""
        d = Toplevel(self.root)
        d.title("🔍 Buscar Tareas")
        d.geometry("480x380")
        d.transient(self.root)

        # Frame superior con búsqueda
        top = Frame(d, bg="white", padx=10, pady=10)
        top.pack(fill="x")

        Label(top, text="Buscar:", bg="white").pack(side="left")
        search_var = tk.StringVar()
        search_entry = Entry(top, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)

        btn_search = Button(top, text="🔍", command=lambda: load_tasks())
        btn_search.pack(side="left")

        # Lista de tareas
        list_frame = Frame(d)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        listbox = Listbox(list_frame, selectmode=MULTIPLE, yscrollcommand=scrollbar.set, font=("Arial", 10))
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        # Botones inferiores
        bottom = Frame(d, bg="white", padx=10, pady=10)
        bottom.pack(fill="x")

        Button(bottom, text="❌ Cerrar", command=d.destroy).pack(side="left")
        Button(bottom, text="🔊 Notificar", command=lambda: notify_selected()).pack(side="right")

        task_data = []

        def load_tasks():
            listbox.delete(0, END)
            task_data.clear()

            if not self.on_get_tasks:
                listbox.insert(END, "Sin conexión a la base de datos")
                return

            try:
                tasks = self.on_get_tasks(search_text=search_var.get(), filter_status="all")
            except TypeError:
                tasks = self.on_get_tasks()

            if not tasks:
                listbox.insert(END, "No se encontraron tareas")
                return

            for t in tasks:
                task_id, title, due_date, status, priority = t
                priority_icon = {"urgent": "🔴", "high": "🟡", "normal": "🟢"}.get(priority, "⚪")
                label = f"{priority_icon} {title} | {due_date}"
                task_data.append(t)
                listbox.insert(END, label)

        def notify_selected():
            sel = listbox.curselection()
            if not sel:
                self._show_message("Selecciona al menos una tarea")
                return

            tasks = [task_data[i] for i in sel]
            if self.on_notify_tasks:
                self.on_notify_tasks(tasks)
            self._show_message(f"✅ Notificando {len(tasks)} tarea(s)")
            d.destroy()

        load_tasks()

    def _show_history(self):
        """Diálogo de historial"""
        d = Toplevel(self.root)
        d.title("📜 Historial")
        d.geometry("420x350")
        d.transient(self.root)

        # Área de texto
        frame = Frame(d)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=("Arial", 10), state="disabled")
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)

        # Cargar historial
        history = []
        if self.on_get_history:
            try:
                history = self.on_get_history()
            except:
                pass

        if not history:
            history = ["Sin notificaciones registradas"]

        text.config(state="normal")
        for h in history:
            text.insert(END, f"📋 {h}\n\n")
        text.config(state="disabled")

        # Botón cerrar
        Button(d, text="✓ Cerrar", command=d.destroy).pack(pady=5)

    def _show_settings(self):
        """Diálogo de configuración"""
        d = Toplevel(self.root)
        d.title("⚙️ Configuración")
        d.geometry("380x280")
        d.transient(self.root)

        frame = Frame(d, padx=15, pady=15)
        frame.pack(fill="both", expand=True)

        # Variables
        interval_var = tk.StringVar(value=str(getattr(config, "CHECK_INTERVAL_SECONDS", 180)))
        alert_var = tk.StringVar(value=str(getattr(config, "ALERT_HOURS_BEFORE", 24)))
        volume_var = tk.DoubleVar(value=getattr(config, "ALERT_VOLUME", 1.0) * 100)
        speed_var = tk.StringVar(value=str(getattr(config, "TTS_SPEED", 175)))

        # Campos
        Label(frame, text="Intervalo de revisión (seg):").grid(row=0, column=0, sticky="w", pady=5)
        Entry(frame, textvariable=interval_var, width=15).grid(row=0, column=1, sticky="ew", pady=5)

        Label(frame, text="Anticipación (horas):").grid(row=1, column=0, sticky="w", pady=5)
        Entry(frame, textvariable=alert_var, width=15).grid(row=1, column=1, sticky="ew", pady=5)

        Label(frame, text="Volumen (%):").grid(row=2, column=0, sticky="w", pady=5)
        Scale(frame, from_=0, to=100, variable=volume_var, orient="horizontal").grid(row=2, column=1, sticky="ew", pady=5)

        Label(frame, text="Velocidad voz (ppm):").grid(row=3, column=0, sticky="w", pady=5)
        Entry(frame, textvariable=speed_var, width=15).grid(row=3, column=1, sticky="ew", pady=5)

        frame.columnconfigure(1, weight=1)

        def save():
            try:
                settings = {
                    "check_interval": int(interval_var.get()),
                    "alert_hours": int(alert_var.get()),
                    "volume": float(volume_var.get()) / 100.0,
                    "speed": int(speed_var.get()),
                }
                if self.on_save_settings:
                    self.on_save_settings(settings)
                self._show_message("✅ Configuración guardada")
                d.destroy()
            except Exception as e:
                self._show_message(f"❌ Error: {e}")

        # Botones
        btn_frame = Frame(d, pady=10)
        btn_frame.pack(fill="x")
        Button(btn_frame, text="Cancelar", command=d.destroy).pack(side="left", padx=15)
        Button(btn_frame, text="✓ Guardar", command=save, bg="#4CAF50", fg="white").pack(side="right", padx=15)

    def _trigger_check(self):
        """Disparar revisión manual"""
        if self.on_manual_check:
            try:
                self.on_manual_check()
                self._show_message("🔍 Revisando tareas...")
            except Exception as e:
                self._show_message(f"❌ Error: {e}")

    def _show_message(self, message):
        """Mostrar mensaje simple (temporal)"""
        # Crear ventana temporal
        msg = Toplevel(self.root)
        msg.overrideredirect(True)
        msg.attributes("-topmost", True)

        Label(msg, text=message, bg="#333", fg="white", padx=20, pady=10, font=("Arial", 10)).pack()

        # Centrar cerca del widget
        msg.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y() + self.WIDGET_SIZE + 10
        msg.geometry(f"+{x}+{y}")

        # Autodestruir después de 2 segundos
        msg.after(2000, msg.destroy)

    def update_state(self, state, status_text="", tasks_count=0):
        """Actualizar estado del widget (thread-safe)"""
        self.current_state = state
        self.status_text = status_text or state
        self.tasks_count = tasks_count
        # Programar actualización en hilo principal
        self.root.after(0, self._redraw_widget)

    def run(self):
        """Iniciar el widget"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        """Cerrar el widget"""
        self.running = False
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

class GUIManager:
    """Gestor del widget minimalista"""

    def __init__(self):
        self.root = tk.Tk()
        self.app = TaskNotifierTk(self.root)
        self.app_thread = None

    def start(self):
        """Iniciar en hilo secundario (para usar con main.py)"""
        self.app_thread = threading.Thread(target=self.app.run, daemon=True)
        self.app_thread.start()

    def run(self):
        """Iniciar en hilo principal (bloqueante)"""
        self.app.run()

    def update_state(self, state, status_text="", tasks_count=0):
        """Actualizar estado del widget"""
        self.app.update_state(state, status_text, tasks_count)

    def set_manual_check_callback(self, callback):
        """Callback para revisión manual"""
        self.app.on_manual_check = callback

    def set_get_tasks_callback(self, callback):
        """Callback para obtener tareas"""
        self.app.on_get_tasks = callback

    def set_notify_tasks_callback(self, callback):
        """Callback para notificar tareas"""
        self.app.on_notify_tasks = callback

    def set_get_history_callback(self, callback):
        """Callback para obtener historial"""
        self.app.on_get_history = callback

    def set_save_settings_callback(self, callback):
        """Callback para guardar configuración"""
        self.app.on_save_settings = callback

    def stop(self):
        """Detener el widget"""
        try:
            self.app._on_close()
        except:
            pass


# =============================================================================
# MODO DE PRUEBA
# =============================================================================
if __name__ == "__main__":
    print("🚀 Iniciando Task Notifier Widget - Modo de prueba")
    print("   - Haz clic derecho en el widget para ver el menú")
    print("   - Haz doble clic para revisar tareas")
    print("   - Arrastra el widget para moverlo\n")

    manager = GUIManager()

    # Callbacks de prueba
    def fake_get_tasks(search_text="", filter_status="all"):
        from datetime import datetime, timedelta
        now = datetime.now()
        return [
            (1, "Pagar proveedores", (now + timedelta(days=2)).strftime("%Y-%m-%d"), "pending", "high"),
            (2, "Revisar inventario", now.strftime("%Y-%m-%d"), "pending", "normal"),
            (3, "Cobrar cliente X", (now - timedelta(days=1)).strftime("%Y-%m-%d"), "pending", "urgent"),
            (4, "Reunión con equipo", (now + timedelta(days=1)).strftime("%Y-%m-%d"), "pending", "high"),
        ]

    def fake_notify(tasks):
        print(f"📢 Notificando {len(tasks)} tarea(s):")
        for t in tasks:
            print(f"   - {t[1]}")

    def fake_history():
        return [
            "[2025-11-20 09:00] Cobrar cliente X",
            "[2025-11-20 08:30] Reunión con equipo",
            "[2025-11-19 18:00] Revisar inventario",
            "[2025-11-19 15:30] Pagar proveedores",
        ]

    def fake_save_settings(settings):
        print(f"💾 Configuración guardada: {settings}")

    def fake_check():
        print("🔍 Revisión manual iniciada")
        # Simular encontrar tareas
        manager.update_state("checking", "Revisando...", 0)
        import time
        time.sleep(1)
        manager.update_state("alert", "3 tareas pendientes", 3)

    # Conectar callbacks
    manager.set_get_tasks_callback(fake_get_tasks)
    manager.set_notify_tasks_callback(fake_notify)
    manager.set_get_history_callback(fake_history)
    manager.set_save_settings_callback(fake_save_settings)
    manager.set_manual_check_callback(fake_check)

    # Simular cambios de estado después de iniciar
    def simulate_states():
        import time
        time.sleep(3)
        manager.update_state("checking", "Revisando tareas...", 0)
        time.sleep(2)
        manager.update_state("alert", "3 tareas pendientes", 3)
        time.sleep(5)
        manager.update_state("active", "Todo OK", 0)

    # Iniciar simulación de estados en hilo secundario
    import threading
    threading.Thread(target=simulate_states, daemon=True).start()

    # Iniciar widget
    manager.run()

