"""
Interfaz Gráfica del Task Notifier
===================================
Avatar flotante que muestra el estado del programa
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import os
import config


class FloatingAvatar:
    """Widget flotante que muestra el estado del notificador"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Notifier")

        # Configurar ventana sin bordes y siempre visible
        self.root.overrideredirect(True)  # Sin bordes de ventana
        self.root.attributes('-topmost', config.ALWAYS_ON_TOP)  # Siempre visible
        self.root.attributes('-alpha', config.WINDOW_ALPHA)  # Transparencia

        # Tamaño de la ventana
        window_size = config.AVATAR_SIZE + 40  # Espacio para texto
        self.root.geometry(f"{window_size}x{window_size+60}")

        # Posicionar en esquina superior derecha
        self._position_window()

        # Estado actual
        self.current_state = "active"  # active, checking, alert
        self.status_text = "Esperando..."
        self.tasks_count = 0

        # Cargar imagen del avatar
        self.avatar_image = None
        self.photo_image = None
        self._load_avatar_image()

        # Crear widgets
        self._create_widgets()

        # Permitir mover la ventana
        self.root.bind('<Button-1>', self._start_move)
        self.root.bind('<B1-Motion>', self._on_move)

        # Menú contextual (clic derecho)
        self._create_context_menu()

    def _position_window(self):
        """Posicionar ventana en esquina superior derecha"""
        # Obtener tamaño de la pantalla
        screen_width = self.root.winfo_screenwidth()

        # Calcular posición
        x = screen_width - config.AVATAR_SIZE - 40 - config.AVATAR_MARGIN_RIGHT
        y = config.AVATAR_MARGIN_TOP

        self.root.geometry(f"+{x}+{y}")

    def _load_avatar_image(self):
        """Cargar y preparar la imagen del avatar"""
        try:
            # Buscar imagen desde config
            image_path = config.AVATAR_IMAGE_PATH

            # Intentar diferentes rutas
            if not os.path.exists(image_path):
                image_path = os.path.join(os.path.dirname(__file__), config.AVATAR_IMAGE_PATH)

            if not os.path.exists(image_path):
                image_path = os.path.join(os.getcwd(), config.AVATAR_IMAGE_PATH)

            if os.path.exists(image_path):
                # Cargar imagen
                img = Image.open(image_path)

                # Redimensionar a tamaño del avatar
                size = config.AVATAR_SIZE - 20  # Margen interno
                img = img.resize((size, size), Image.Resampling.LANCZOS)

                # Crear máscara circular
                mask = Image.new('L', (size, size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, size, size), fill=255)

                # Aplicar máscara circular a la imagen
                output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)

                self.avatar_image = output
                print("✅ Imagen del avatar cargada exitosamente")
            else:
                print("⚠️  No se encontró image.png, usando avatar por defecto")
                self.avatar_image = None

        except Exception as e:
            print(f"⚠️  Error al cargar imagen del avatar: {e}")
            self.avatar_image = None

    def _create_widgets(self):
        """Crear los elementos visuales"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el avatar circular
        self.canvas = tk.Canvas(
            main_frame,
            width=config.AVATAR_SIZE,
            height=config.AVATAR_SIZE,
            bg='#2c3e50',
            highlightthickness=0
        )
        self.canvas.pack(pady=(5, 10))

        # Dibujar círculo inicial
        self._draw_avatar()

        # Label de estado
        self.status_label = tk.Label(
            main_frame,
            text=self.status_text,
            font=('Arial', 9),
            fg='white',
            bg='#2c3e50',
            wraplength=config.AVATAR_SIZE + 20
        )
        self.status_label.pack()

        # Label de última revisión
        self.time_label = tk.Label(
            main_frame,
            text="Iniciando...",
            font=('Arial', 7),
            fg='#95a5a6',
            bg='#2c3e50'
        )
        self.time_label.pack(pady=(5, 0))

    def _draw_avatar(self):
        """Dibujar el avatar circular con imagen personalizada"""
        self.canvas.delete("all")

        # Color según estado
        colors = {
            "active": config.AVATAR_COLOR_ACTIVE,
            "checking": config.AVATAR_COLOR_CHECKING,
            "alert": config.AVATAR_COLOR_ALERT
        }
        color = colors.get(self.current_state, config.AVATAR_COLOR_ACTIVE)

        center_x = config.AVATAR_SIZE // 2
        center_y = config.AVATAR_SIZE // 2

        if self.avatar_image:
            # Si hay imagen personalizada, usarla
            # Aplicar tinte de color según estado
            img_with_border = self._apply_color_tint(self.avatar_image, color)
            self.photo_image = ImageTk.PhotoImage(img_with_border)

            # Dibujar imagen en el canvas
            self.canvas.create_image(
                center_x, center_y,
                image=self.photo_image
            )

            # Dibujar borde circular de color
            border_width = 4 if self.current_state != "checking" else 6
            self.canvas.create_oval(
                10, 10,
                config.AVATAR_SIZE - 10, config.AVATAR_SIZE - 10,
                outline=color,
                width=border_width
            )

        else:
            # Fallback: dibujar círculo con color e icono
            self.canvas.create_oval(
                10, 10,
                config.AVATAR_SIZE - 10, config.AVATAR_SIZE - 10,
                fill=color,
                outline='white',
                width=3
            )

            # Iconos según estado
            if self.current_state == "active":
                # Checkmark
                self.canvas.create_line(
                    center_x - 15, center_y,
                    center_x - 5, center_y + 10,
                    center_x + 15, center_y - 10,
                    fill='white',
                    width=4,
                    capstyle=tk.ROUND
                )
            elif self.current_state == "checking":
                # Puntos animados
                for i in range(3):
                    x = center_x - 15 + (i * 15)
                    self.canvas.create_oval(
                        x - 3, center_y - 3,
                        x + 3, center_y + 3,
                        fill='white',
                        outline='white'
                    )

        # Badge de notificaciones (para todos los estados si hay tareas)
        if self.tasks_count > 0:
            # Badge rojo con número en esquina superior derecha
            badge_x = config.AVATAR_SIZE - 15
            badge_y = 15

            # Círculo rojo
            self.canvas.create_oval(
                badge_x - 12, badge_y - 12,
                badge_x + 12, badge_y + 12,
                fill='#f44336',
                outline='white',
                width=2
            )

            # Número
            self.canvas.create_text(
                badge_x, badge_y,
                text=str(self.tasks_count),
                font=('Arial', 10, 'bold'),
                fill='white'
            )

    def _apply_color_tint(self, image, color):
        """Aplicar overlay de color a la imagen según el estado"""
        # Convertir color hex a RGB
        color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        # Crear overlay de color semi-transparente
        overlay = Image.new('RGBA', image.size, color_rgb + (40,))  # Alpha bajo para tinte sutil

        # Combinar imagen original con overlay
        result = Image.alpha_composite(image.convert('RGBA'), overlay)

        return result

    def _create_context_menu(self):
        """Crear menú contextual"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="📊 Ver Estado", command=self._show_status)
        self.context_menu.add_command(label="🔍 Buscar Tareas", command=self._show_task_search)
        self.context_menu.add_command(label="📜 Historial", command=self._show_history)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Revisar Ahora", command=self._trigger_check)
        self.context_menu.add_command(label="⚙️ Configuración", command=self._show_settings)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Salir", command=self._quit)

        self.root.bind('<Button-2>', self._show_context_menu)  # Clic derecho en macOS
        self.root.bind('<Button-3>', self._show_context_menu)  # Clic derecho en Windows/Linux

    def _show_context_menu(self, event):
        """Mostrar menú contextual"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _show_status(self):
        """Mostrar ventana con información detallada"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Estado del Task Notifier")
        status_window.geometry("400x350")
        status_window.attributes('-topmost', True)

        frame = tk.Frame(status_window, padx=20, pady=20, bg='#f5f5f5')
        frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_frame = tk.Frame(frame, bg='#2c3e50', padx=10, pady=10)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(
            title_frame,
            text="🔔 Task Notifier",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        ).pack()

        # Estado actual
        status_frame = tk.LabelFrame(frame, text="Estado Actual", padx=10, pady=10, bg='#f5f5f5')
        status_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            status_frame,
            text=f"Estado: {self.status_text}",
            font=('Arial', 10),
            bg='#f5f5f5'
        ).pack(anchor=tk.W)

        if self.tasks_count > 0:
            tk.Label(
                status_frame,
                text=f"Tareas pendientes: {self.tasks_count}",
                font=('Arial', 10),
                bg='#f5f5f5',
                fg='#f44336'
            ).pack(anchor=tk.W)

        # Configuración
        config_frame = tk.LabelFrame(frame, text="Configuración", padx=10, pady=10, bg='#f5f5f5')
        config_frame.pack(fill=tk.X, pady=(0, 10))

        config_items = [
            ("Intervalo de revisión:", f"{config.CHECK_INTERVAL_SECONDS}s"),
            ("Anticipación de alerta:", f"{config.ALERT_HOURS_BEFORE}h"),
            ("Volumen:", f"{int(config.ALERT_VOLUME * 100)}%"),
            ("Velocidad de voz:", f"{config.TTS_SPEED} palabras/min")
        ]

        for label, value in config_items:
            item_frame = tk.Frame(config_frame, bg='#f5f5f5')
            item_frame.pack(fill=tk.X, pady=2)

            tk.Label(
                item_frame,
                text=label,
                font=('Arial', 9),
                bg='#f5f5f5',
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)

            tk.Label(
                item_frame,
                text=value,
                font=('Arial', 9, 'bold'),
                bg='#f5f5f5'
            ).pack(side=tk.LEFT)

        # Botones
        button_frame = tk.Frame(frame, bg='#f5f5f5')
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="⚙️ Configurar",
            command=lambda: [status_window.destroy(), self._show_settings()],
            bg='#2196F3',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            button_frame,
            text="Cerrar",
            command=status_window.destroy,
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

    def _show_task_search(self):
        """Mostrar ventana para buscar y notificar tareas manualmente"""
        search_window = tk.Toplevel(self.root)
        search_window.title("Buscar Tareas")
        search_window.geometry("600x450")
        search_window.attributes('-topmost', True)

        frame = tk.Frame(search_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Título
        tk.Label(
            frame,
            text="🔍 Buscar y Notificar Tareas",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))

        # Barra de búsqueda
        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_frame, text="Buscar:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        search_entry = tk.Entry(search_frame, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Botones de filtro
        filter_frame = tk.Frame(frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        filter_var = tk.StringVar(value="all")
        tk.Radiobutton(filter_frame, text="Todas", variable=filter_var, value="all").pack(side=tk.LEFT)
        tk.Radiobutton(filter_frame, text="Pendientes", variable=filter_var, value="pending").pack(side=tk.LEFT)
        tk.Radiobutton(filter_frame, text="En progreso", variable=filter_var, value="in_progress").pack(side=tk.LEFT)
        tk.Radiobutton(filter_frame, text="Vencidas", variable=filter_var, value="overdue").pack(side=tk.LEFT)

        # Lista de tareas con scrollbar
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        task_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED
        )
        task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=task_listbox.yview)

        # Función para cargar tareas
        def load_tasks():
            if hasattr(self, 'on_get_tasks'):
                tasks = self.on_get_tasks(
                    search_text=search_entry.get(),
                    filter_status=filter_var.get()
                )
                task_listbox.delete(0, tk.END)
                for task in tasks:
                    task_id, title, due_date, status, priority = task
                    # Formato: [PRIORIDAD] Título - Vence: fecha (Estado)
                    priority_icon = "🔴" if priority == "urgent" else "🟡" if priority == "high" else "🟢"
                    display = f"{priority_icon} {title} - Vence: {due_date} ({status})"
                    task_listbox.insert(tk.END, display)
                    task_listbox.task_data = getattr(task_listbox, 'task_data', [])
                    task_listbox.task_data.append(task)

        # Botón de búsqueda
        tk.Button(search_frame, text="Buscar", command=load_tasks).pack(side=tk.LEFT)

        # Botones de acción
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X)

        def notify_selected():
            selection = task_listbox.curselection()
            if selection and hasattr(self, 'on_notify_tasks'):
                selected_tasks = [task_listbox.task_data[i] for i in selection]
                self.on_notify_tasks(selected_tasks)
                tk.messagebox.showinfo("Éxito", f"Notificando {len(selected_tasks)} tarea(s)")
                search_window.destroy()

        tk.Button(
            button_frame,
            text="🔊 Notificar Seleccionadas",
            command=notify_selected,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            button_frame,
            text="Cerrar",
            command=search_window.destroy
        ).pack(side=tk.LEFT)

        # Cargar tareas inicialmente
        load_tasks()

    def _show_history(self):
        """Mostrar historial de notificaciones"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Historial de Notificaciones")
        history_window.geometry("500x400")
        history_window.attributes('-topmost', True)

        frame = tk.Frame(history_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="📜 Historial de Notificaciones",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 10))

        # Lista con scrollbar
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        history_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 9),
            yscrollcommand=scrollbar.set
        )
        history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_listbox.yview)

        # Cargar historial
        if hasattr(self, 'on_get_history'):
            history = self.on_get_history()
            for entry in history:
                history_listbox.insert(tk.END, entry)
        else:
            history_listbox.insert(tk.END, "No hay notificaciones en el historial")

        tk.Button(
            frame,
            text="Cerrar",
            command=history_window.destroy
        ).pack()

    def _show_settings(self):
        """Mostrar ventana de configuración"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configuración")
        settings_window.geometry("450x400")
        settings_window.attributes('-topmost', True)

        frame = tk.Frame(settings_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame,
            text="⚙️ Configuración",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Intervalo de revisión
        interval_frame = tk.Frame(frame)
        interval_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            interval_frame,
            text="Intervalo de revisión (segundos):",
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        interval_var = tk.IntVar(value=config.CHECK_INTERVAL_SECONDS)
        interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=30,
            to=3600,
            increment=30,
            textvariable=interval_var,
            width=10,
            font=('Arial', 10)
        )
        interval_spinbox.pack(side=tk.RIGHT)

        # Tiempo de anticipación
        alert_frame = tk.Frame(frame)
        alert_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            alert_frame,
            text="Alertar con anticipación (horas):",
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        alert_var = tk.IntVar(value=config.ALERT_HOURS_BEFORE)
        alert_spinbox = tk.Spinbox(
            alert_frame,
            from_=1,
            to=168,  # 1 semana
            increment=1,
            textvariable=alert_var,
            width=10,
            font=('Arial', 10)
        )
        alert_spinbox.pack(side=tk.RIGHT)

        # Volumen
        volume_frame = tk.Frame(frame)
        volume_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            volume_frame,
            text="Volumen:",
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        volume_var = tk.DoubleVar(value=config.ALERT_VOLUME)
        volume_scale = tk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=volume_var,
            length=200
        )
        volume_scale.pack(side=tk.RIGHT)

        # Velocidad de voz
        speed_frame = tk.Frame(frame)
        speed_frame.pack(fill=tk.X, pady=10)

        tk.Label(
            speed_frame,
            text="Velocidad de voz (palabras/min):",
            font=('Arial', 10)
        ).pack(side=tk.LEFT)

        speed_var = tk.IntVar(value=config.TTS_SPEED)
        speed_spinbox = tk.Spinbox(
            speed_frame,
            from_=100,
            to=300,
            increment=25,
            textvariable=speed_var,
            width=10,
            font=('Arial', 10)
        )
        speed_spinbox.pack(side=tk.RIGHT)

        # Botones
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=20)

        def save_settings():
            if hasattr(self, 'on_save_settings'):
                self.on_save_settings({
                    'check_interval': interval_var.get(),
                    'alert_hours': alert_var.get(),
                    'volume': volume_var.get(),
                    'speed': speed_var.get()
                })
                tk.messagebox.showinfo("Éxito", "Configuración guardada correctamente")
                settings_window.destroy()

        tk.Button(
            button_frame,
            text="Guardar",
            command=save_settings,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            button_frame,
            text="Cancelar",
            command=settings_window.destroy
        ).pack(side=tk.LEFT)

    def _trigger_check(self):
        """Disparar revisión manual (callback que se define externamente)"""
        if hasattr(self, 'on_manual_check'):
            self.on_manual_check()

    def _quit(self):
        """Cerrar aplicación"""
        self.root.quit()

    def _start_move(self, event):
        """Iniciar movimiento de ventana"""
        self.x = event.x
        self.y = event.y

    def _on_move(self, event):
        """Mover ventana"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def update_state(self, state, status_text="", tasks_count=0):
        """
        Actualizar estado del avatar

        Args:
            state: "active", "checking", "alert"
            status_text: Texto de estado a mostrar
            tasks_count: Número de tareas (para alertas)
        """
        self.current_state = state
        self.status_text = status_text
        self.tasks_count = tasks_count

        # Actualizar en el hilo de GUI
        self.root.after(0, self._update_ui)

    def _update_ui(self):
        """Actualizar interfaz (debe llamarse desde el hilo de GUI)"""
        self._draw_avatar()
        self.status_label.config(text=self.status_text)
        self.time_label.config(text=f"Última revisión: {datetime.now().strftime('%H:%M:%S')}")

    def run(self):
        """Iniciar loop de la GUI"""
        self.root.mainloop()

    def stop(self):
        """Detener la GUI"""
        self.root.quit()


class GUIManager:
    """Gestor de la interfaz gráfica (debe ejecutarse en hilo principal)"""

    def __init__(self):
        self.avatar = FloatingAvatar()
        self.running = False

    def start(self):
        """Iniciar GUI - DEBE llamarse desde el hilo principal"""
        self.running = True

    def run(self):
        """Ejecutar loop principal de GUI - BLOQUEANTE"""
        self.avatar.run()

    def update_state(self, state, status_text="", tasks_count=0):
        """Actualizar estado del avatar (thread-safe)"""
        if self.avatar:
            self.avatar.update_state(state, status_text, tasks_count)

    def set_manual_check_callback(self, callback):
        """Definir callback para revisión manual"""
        if self.avatar:
            self.avatar.on_manual_check = callback

    def set_get_tasks_callback(self, callback):
        """Definir callback para obtener tareas"""
        if self.avatar:
            self.avatar.on_get_tasks = callback

    def set_notify_tasks_callback(self, callback):
        """Definir callback para notificar tareas"""
        if self.avatar:
            self.avatar.on_notify_tasks = callback

    def set_get_history_callback(self, callback):
        """Definir callback para obtener historial"""
        if self.avatar:
            self.avatar.on_get_history = callback

    def set_save_settings_callback(self, callback):
        """Definir callback para guardar configuración"""
        if self.avatar:
            self.avatar.on_save_settings = callback

    def stop(self):
        """Detener GUI"""
        self.running = False
        if self.avatar:
            self.avatar.stop()


if __name__ == "__main__":
    # Prueba de la interfaz
    import time

    manager = GUIManager()
    manager.start()

    print("GUI iniciada. Probando estados...")

    try:
        # Probar diferentes estados
        for i in range(10):
            time.sleep(2)

            if i % 3 == 0:
                manager.update_state("active", "Sistema activo")
            elif i % 3 == 1:
                manager.update_state("checking", "Revisando tareas...")
            else:
                manager.update_state("alert", f"¡{i} tareas pendientes!", i)
    except KeyboardInterrupt:
        print("\nCerrando...")
    finally:
        manager.stop()
