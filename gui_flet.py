"""
Interfaz Gráfica Moderna con Flet - Task Notifier
==================================================
Material Design 3 con animaciones y UX mejorada
"""

import flet as ft
from datetime import datetime
import threading
import config


class TaskNotifierApp:
    """Aplicación principal de Task Notifier con Flet"""

    def __init__(self):
        self.page = None
        self.current_state = "active"  # active, checking, alert
        self.status_text = "Iniciando..."
        self.tasks_count = 0
        self.running = False

        # Callbacks (se configuran externamente)
        self.on_manual_check = None
        self.on_get_tasks = None
        self.on_notify_tasks = None
        self.on_get_history = None
        self.on_save_settings = None

        # Referencias a elementos UI
        self.status_badge = None
        self.status_text_widget = None
        self.task_count_badge = None
        self.last_check_text = None

    def main(self, page: ft.Page):
        """Inicializar la aplicación Flet"""
        self.page = page

        # Configuración de la ventana
        page.title = "Task Notifier"
        page.window.width = 400
        page.window.height = 550
        page.window.resizable = True
        page.window.always_on_top = config.ALWAYS_ON_TOP
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0

        # Tema personalizado moderno
        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
            use_material3=True
        )

        # Posicionar en esquina superior derecha
        self._position_window()

        # Construir interfaz
        self._build_ui()

        # Sistema de bandeja (tray)
        self._setup_system_tray()

        self.running = True
        page.update()

    def _position_window(self):
        """Posicionar ventana en esquina superior derecha"""
        # En Flet, la posición se puede ajustar con window_left y window_top
        # Por ahora dejamos que el usuario la mueva, pero podemos calcularla
        pass

    def _build_ui(self):
        """Construir la interfaz principal"""

        # Header con gradiente
        header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        name=ft.Icons.NOTIFICATIONS_ACTIVE,
                        color=ft.Colors.WHITE,
                        size=32
                    ),
                    ft.Text(
                        "Task Notifier",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER),

                ft.Text(
                    "Sistema de Alertas por Voz",
                    size=12,
                    color=ft.Colors.WHITE70,
                    text_align=ft.TextAlign.CENTER
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
            padding=20,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.BLUE_700, ft.Colors.BLUE_900]
            ),
        )

        # Estado del sistema (Badge circular animado)
        self.status_badge = ft.Container(
            content=ft.Icon(
                name=ft.Icons.CHECK_CIRCLE,
                color=ft.Colors.WHITE,
                size=48
            ),
            width=100,
            height=100,
            border_radius=50,
            bgcolor=ft.Colors.GREEN_500,
            alignment=ft.alignment.center,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

        # Badge de contador de tareas
        self.task_count_badge = ft.Container(
            content=ft.Text(
                "0",
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            width=30,
            height=30,
            border_radius=15,
            bgcolor=ft.Colors.RED_500,
            alignment=ft.Alignment.center,
            visible=False,
            top=-5,
            right=-5,
        )

        # Stack para badge y contador
        status_stack = ft.Stack([
            self.status_badge,
            self.task_count_badge,
        ],
        width=100,
        height=100)

        # Texto de estado
        self.status_text_widget = ft.Text(
            self.status_text,
            size=16,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLUE_GREY_800
        )

        # Última revisión
        self.last_check_text = ft.Text(
            "Iniciando...",
            size=12,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER
        )

        # Sección de estado
        status_section = ft.Container(
            content=ft.Column([
                status_stack,
                ft.Divider(height=20, color="transparent"),
                self.status_text_widget,
                ft.Divider(height=5, color="transparent"),
                self.last_check_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            alignment=ft.Alignment.center,
        )

        # Configuración actual (cards)
        config_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Configuración Actual",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_800
                    ),
                    ft.Divider(height=10, color="transparent"),
                    self._create_config_row("Intervalo", f"{config.CHECK_INTERVAL_SECONDS}s", ft.Icons.TIMER),
                    self._create_config_row("Anticipación", f"{config.ALERT_HOURS_BEFORE}h", ft.Icons.ALARM),
                    self._create_config_row("Volumen", f"{int(config.ALERT_VOLUME * 100)}%", ft.Icons.VOLUME_UP),
                    self._create_config_row("Velocidad", f"{config.TTS_SPEED} ppm", ft.Icons.SPEED),
                ], spacing=8),
                padding=15,
            ),
            elevation=2,
        )

        # Botones de acción
        action_buttons = ft.Column([
            ft.ElevatedButton(
                "Buscar Tareas",
                icon=ft.Icons.SEARCH,
                on_click=lambda _: self._show_task_search(),
                width=300,
                height=45,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_600,
                    color=ft.Colors.WHITE,
                )
            ),
            ft.ElevatedButton(
                "Revisar Ahora",
                icon=ft.Icons.REFRESH,
                on_click=lambda _: self._trigger_check(),
                width=300,
                height=45,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_600,
                    color=ft.Colors.WHITE,
                )
            ),
            ft.Row([
                ft.OutlinedButton(
                    "Historial",
                    icon=ft.Icons.HISTORY,
                    on_click=lambda _: self._show_history(),
                    width=145,
                    height=45,
                ),
                ft.OutlinedButton(
                    "Configuración",
                    icon=ft.Icons.SETTINGS,
                    on_click=lambda _: self._show_settings(),
                    width=145,
                    height=45,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10)

        # Layout principal
        main_content = ft.Column([
            header,
            status_section,
            ft.Container(
                content=config_card,
                padding=ft.padding.symmetric(horizontal=20)
            ),
            ft.Divider(height=20, color="transparent"),
            ft.Container(
                content=action_buttons,
                padding=ft.padding.symmetric(horizontal=20)
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO)

        self.page.add(main_content)

    def _create_config_row(self, label, value, icon):
        """Crear fila de configuración con icono"""
        return ft.Row([
            ft.Icon(icon, size=20, color=ft.Colors.BLUE_GREY_600),
            ft.Text(label, size=12, color=ft.Colors.GREY_700, expand=True),
            ft.Text(value, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=10)

    def _setup_system_tray(self):
        """Configurar icono en bandeja del sistema"""
        # Flet soporta system tray en versiones recientes
        # Por ahora lo dejamos comentado hasta configurar el icono correcto
        pass

    def _show_task_search(self):
        """Mostrar diálogo de búsqueda de tareas"""
        search_field = ft.TextField(
            label="Buscar tareas",
            hint_text="Escribe para buscar...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.BLUE_400,
            width=500,
        )

        # Radio buttons para filtros
        filter_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="all", label="Todas"),
                ft.Radio(value="pending", label="Pendientes"),
                ft.Radio(value="in_progress", label="En progreso"),
                ft.Radio(value="overdue", label="Vencidas"),
            ]),
            value="all",
        )

        # Lista de tareas
        tasks_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=300,
        )

        selected_tasks = []
        task_data = []

        def load_tasks():
            """Cargar tareas desde el callback"""
            if self.on_get_tasks:
                tasks = self.on_get_tasks(
                    search_text=search_field.value or "",
                    filter_status=filter_radio.value
                )
                tasks_list.controls.clear()
                task_data.clear()
                selected_tasks.clear()

                if not tasks:
                    tasks_list.controls.append(
                        ft.Text("No se encontraron tareas", italic=True, color=ft.Colors.GREY_600)
                    )
                else:
                    for task in tasks:
                        task_id, title, due_date, status, priority = task
                        task_data.append(task)

                        # Icono según prioridad
                        if priority == "urgent":
                            icon = ft.Icons.ERROR
                            icon_color = ft.Colors.RED_500
                        elif priority == "high":
                            icon = ft.Icons.WARNING
                            icon_color = ft.Colors.ORANGE_500
                        else:
                            icon = ft.Icons.INFO
                            icon_color = ft.Colors.GREEN_500

                        # Checkbox para seleccionar
                        checkbox = ft.Checkbox(value=False)

                        def on_check_change(e, task_idx=len(task_data)-1):
                            if e.control.value:
                                selected_tasks.append(task_idx)
                            else:
                                if task_idx in selected_tasks:
                                    selected_tasks.remove(task_idx)

                        checkbox.on_change = on_check_change

                        # Card de tarea
                        task_card = ft.Card(
                            content=ft.Container(
                                content=ft.Row([
                                    checkbox,
                                    ft.Icon(icon, color=icon_color, size=24),
                                    ft.Column([
                                        ft.Text(title, weight=ft.FontWeight.BOLD, size=14),
                                        ft.Text(f"Vence: {due_date} • {status}", size=12, color=ft.Colors.GREY_700),
                                    ],
                                    expand=True,
                                    spacing=2),
                                ],
                                spacing=10),
                                padding=10,
                            ),
                            elevation=1,
                        )

                        tasks_list.controls.append(task_card)

                dialog.update()

        def notify_selected(e):
            """Notificar tareas seleccionadas"""
            if selected_tasks and self.on_notify_tasks:
                tasks_to_notify = [task_data[i] for i in selected_tasks]
                self.on_notify_tasks(tasks_to_notify)

                # Mostrar snackbar de éxito
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"✅ Notificando {len(tasks_to_notify)} tarea(s)"),
                        bgcolor=ft.Colors.GREEN_700,
                    )
                )
                dialog.open = False
                self.page.update()

        # Contenido del diálogo
        dialog_content = ft.Column([
            ft.Text("🔍 Buscar y Notificar Tareas", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            search_field,
            filter_radio,
            ft.ElevatedButton(
                "Buscar",
                icon=ft.Icons.SEARCH,
                on_click=lambda _: load_tasks(),
            ),
            ft.Divider(),
            ft.Text("Resultados:", weight=ft.FontWeight.BOLD),
            tasks_list,
        ],
        width=600,
        height=500,
        scroll=ft.ScrollMode.AUTO)

        # Diálogo
        dialog = ft.AlertDialog(
            modal=True,
            content=dialog_content,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton(
                    "🔊 Notificar Seleccionadas",
                    on_click=notify_selected,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

        # Cargar tareas inicialmente
        load_tasks()

    def _show_history(self):
        """Mostrar historial de notificaciones"""
        # Lista de historial
        history_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=400,
        )

        # Cargar historial
        if self.on_get_history:
            history = self.on_get_history()
            if history:
                for entry in history:
                    history_list.controls.append(
                        ft.Card(
                            content=ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.NOTIFICATIONS, color=ft.Colors.BLUE_500, size=20),
                                    ft.Text(entry, size=12, expand=True),
                                ],
                                spacing=10),
                                padding=10,
                            ),
                            elevation=1,
                        )
                    )
            else:
                history_list.controls.append(
                    ft.Text("No hay notificaciones en el historial", italic=True, color=ft.Colors.GREY_600)
                )
        else:
            history_list.controls.append(
                ft.Text("No hay notificaciones en el historial", italic=True, color=ft.Colors.GREY_600)
            )

        # Contenido del diálogo
        dialog_content = ft.Column([
            ft.Text("📜 Historial de Notificaciones", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            history_list,
        ],
        width=500,
        height=450)

        # Diálogo
        dialog = ft.AlertDialog(
            modal=True,
            content=dialog_content,
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _show_settings(self):
        """Mostrar diálogo de configuración"""
        # Controles de configuración
        interval_field = ft.TextField(
            label="Intervalo de revisión (segundos)",
            value=str(config.CHECK_INTERVAL_SECONDS),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="30-3600",
        )

        alert_field = ft.TextField(
            label="Anticipación de alerta (horas)",
            value=str(config.ALERT_HOURS_BEFORE),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="1-168",
        )

        volume_slider = ft.Slider(
            min=0,
            max=100,
            divisions=10,
            value=config.ALERT_VOLUME * 100,
            label="{value}%",
            width=300,
        )

        speed_field = ft.TextField(
            label="Velocidad de voz (palabras/min)",
            value=str(config.TTS_SPEED),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=300,
            hint_text="100-300",
        )

        def save_settings(e):
            """Guardar configuración"""
            if self.on_save_settings:
                try:
                    settings = {
                        'check_interval': int(interval_field.value),
                        'alert_hours': int(alert_field.value),
                        'volume': volume_slider.value / 100,
                        'speed': int(speed_field.value),
                    }
                    self.on_save_settings(settings)

                    # Mostrar snackbar de éxito
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("✅ Configuración guardada correctamente"),
                            bgcolor=ft.Colors.GREEN_700,
                        )
                    )
                    dialog.open = False
                    self.page.update()
                except ValueError:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("❌ Error: verifica los valores ingresados"),
                            bgcolor=ft.Colors.RED_700,
                        )
                    )

        # Contenido del diálogo
        dialog_content = ft.Column([
            ft.Text("⚙️ Configuración", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            interval_field,
            alert_field,
            ft.Column([
                ft.Text("Volumen", size=12, weight=ft.FontWeight.BOLD),
                volume_slider,
            ]),
            speed_field,
        ],
        width=400,
        spacing=15)

        # Diálogo
        dialog = ft.AlertDialog(
            modal=True,
            content=dialog_content,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton(
                    "Guardar",
                    on_click=save_settings,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _trigger_check(self):
        """Disparar revisión manual"""
        if self.on_manual_check:
            self.on_manual_check()
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("🔍 Revisando tareas..."),
                    bgcolor=ft.Colors.BLUE_700,
                )
            )

    def update_state(self, state, status_text="", tasks_count=0):
        """
        Actualizar estado del sistema (thread-safe)

        Args:
            state: "active", "checking", "alert"
            status_text: Texto de estado
            tasks_count: Número de tareas pendientes
        """
        self.current_state = state
        self.status_text = status_text
        self.tasks_count = tasks_count

        # Actualizar UI en el hilo principal de Flet
        if self.page:
            self.page.run_task(self._update_ui_async, state, status_text, tasks_count)

    async def _update_ui_async(self, state, status_text, tasks_count):
        """Actualizar UI de forma asíncrona"""
        if not self.page:
            return

        # Actualizar badge de estado (verificar que exista)
        if self.status_badge:
            if state == "active":
                self.status_badge.bgcolor = ft.Colors.GREEN_500
                self.status_badge.content.name = ft.Icons.CHECK_CIRCLE
            elif state == "checking":
                self.status_badge.bgcolor = ft.Colors.BLUE_500
                self.status_badge.content.name = ft.Icons.SYNC
            elif state == "alert":
                self.status_badge.bgcolor = ft.Colors.ORANGE_500
                self.status_badge.content.name = ft.Icons.WARNING

        # Actualizar texto de estado
        if self.status_text_widget:
            self.status_text_widget.value = status_text

        # Actualizar badge de contador
        if self.task_count_badge:
            if tasks_count > 0:
                self.task_count_badge.visible = True
                self.task_count_badge.content.value = str(tasks_count)
            else:
                self.task_count_badge.visible = False

        # Actualizar última revisión
        if self.last_check_text:
            self.last_check_text.value = f"Última revisión: {datetime.now().strftime('%H:%M:%S')}"

        self.page.update()

    def run(self):
        """Ejecutar la aplicación Flet"""
        ft.app(target=self.main)

    def stop(self):
        """Detener la aplicación"""
        self.running = False
        if self.page:
            self.page.window.destroy()


class GUIManager:
    """Gestor de la interfaz gráfica con Flet"""

    def __init__(self):
        self.app = TaskNotifierApp()
        self.running = False
        self.app_thread = None

    def start(self):
        """Iniciar GUI"""
        self.running = True

    def run(self):
        """Ejecutar loop principal de GUI - BLOQUEANTE"""
        self.app.run()

    def update_state(self, state, status_text="", tasks_count=0):
        """Actualizar estado (thread-safe)"""
        if self.app:
            self.app.update_state(state, status_text, tasks_count)

    def set_manual_check_callback(self, callback):
        """Definir callback para revisión manual"""
        if self.app:
            self.app.on_manual_check = callback

    def set_get_tasks_callback(self, callback):
        """Definir callback para obtener tareas"""
        if self.app:
            self.app.on_get_tasks = callback

    def set_notify_tasks_callback(self, callback):
        """Definir callback para notificar tareas"""
        if self.app:
            self.app.on_notify_tasks = callback

    def set_get_history_callback(self, callback):
        """Definir callback para obtener historial"""
        if self.app:
            self.app.on_get_history = callback

    def set_save_settings_callback(self, callback):
        """Definir callback para guardar configuración"""
        if self.app:
            self.app.on_save_settings = callback

    def stop(self):
        """Detener GUI"""
        self.running = False
        if self.app:
            self.app.stop()


if __name__ == "__main__":
    # Prueba de la interfaz
    import time

    manager = GUIManager()
    manager.start()

    print("GUI iniciada. Probando estados...")

    # Simular actualizaciones de estado en otro hilo
    def test_states():
        time.sleep(3)
        manager.update_state("active", "Sistema activo")
        time.sleep(2)
        manager.update_state("checking", "Revisando tareas...")
        time.sleep(2)
        manager.update_state("alert", "3 tareas pendientes", 3)

    test_thread = threading.Thread(target=test_states, daemon=True)
    test_thread.start()

    try:
        manager.run()
    except KeyboardInterrupt:
        print("\nCerrando...")
    finally:
        manager.stop()
