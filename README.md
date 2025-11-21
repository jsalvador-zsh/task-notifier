# Task Notifier - Guía de Interfaz Flet

## ✨ Nueva Interfaz Moderna

Tu Task Notifier ahora cuenta con una interfaz completamente renovada usando **Flet** con Material Design 3.

### 🎨 Mejoras Visuales

#### **Ventana Principal**
- Header con gradiente azul moderno
- Badge circular animado que muestra el estado del sistema:
  - 🟢 **Verde**: Sistema activo
  - 🔵 **Azul**: Revisando tareas
  - 🟠 **Naranja**: Alertas pendientes
- Contador de tareas pendientes en badge rojo
- Tarjeta con configuración actual visible
- Botones modernos con iconos Material

#### **Características Nuevas**
1. **Animaciones suaves** entre estados
2. **Material Design 3** - aspecto profesional y moderno
3. **Snackbars informativos** para feedback al usuario
4. **Diálogos modales** con mejor UX
5. **Campos de búsqueda y filtros** mejorados
6. **Cards para tareas e historial** más legibles

### 📦 Funcionalidades

#### **Búsqueda de Tareas**
- Campo de búsqueda en tiempo real
- Filtros por estado: Todas, Pendientes, En progreso, Vencidas
- Visualización con iconos de prioridad:
  - 🔴 Urgente
  - 🟡 Alta
  - 🟢 Normal
- Selección múltiple con checkboxes
- Botón "Notificar Seleccionadas"

#### **Historial**
- Lista cronológica de notificaciones
- Cards con iconos
- Scroll automático
- Información clara de fecha/hora

#### **Configuración**
- Sliders modernos para volumen
- Campos numéricos con validación
- Guardado inmediato
- Feedback visual de éxito

### 🚀 Cómo Ejecutar

#### **Modo Desarrollo**
```bash
cd task-notifier
source venv/bin/activate
python main.py
```

#### **Probar solo la interfaz**
```bash
python gui_flet.py
```

### 📱 Crear Ejecutable Portable

Flet facilita la creación de ejecutables para Windows, macOS y Linux.

#### **Instalación de herramientas**
```bash
pip install flet
```

#### **Crear ejecutable para macOS**
```bash
flet build macos
```

El ejecutable estará en: `build/macos/`

#### **Crear ejecutable para Windows** (desde macOS con Docker)
```bash
flet build windows
```

#### **Crear ejecutable para Linux**
```bash
flet build linux
```

### ⚙️ Configurar el Build

Crea un archivo `pyproject.toml` en la raíz del proyecto:

```toml
[tool.flet]
name = "Task Notifier"
description = "Sistema de Alertas por Voz para Tareas"
version = "2.0.0"
author = "Tu Nombre"

[build-system]
requires = ["flet>=0.24.0"]
```

### 🎯 Opciones Avanzadas de Build

#### **Ejecutable con icono personalizado**
```bash
flet build macos --icon icon.png
```

#### **Ejecutable sin consola** (solo ventana)
```bash
flet build macos --no-console
```

#### **Especificar nombre del ejecutable**
```bash
flet build macos --product "Task Notifier Pro"
```

### 📂 Estructura de Archivos

```
task-notifier/
├── main.py              # Archivo principal (usa gui_flet.py)
├── gui_flet.py          # Nueva interfaz moderna con Flet ✨
├── gui.py               # Interfaz antigua Tkinter (respaldo)
├── config.py            # Configuración
├── requirements.txt     # Dependencias (incluye flet)
└── venv/                # Entorno virtual
```

### 🔄 Migración Completada

**Cambios realizados:**
- ✅ Flet instalado y configurado
- ✅ Nueva interfaz `gui_flet.py` creada
- ✅ `main.py` actualizado para usar Flet
- ✅ Todos los diálogos modernizados
- ✅ Callbacks compatibles con el sistema existente
- ✅ Mantiene toda la funcionalidad original

**Archivos antiguos:**
- `gui.py` - Interfaz Tkinter original (conservada como respaldo)

### 💡 Tips de Uso

1. **Cambiar entre modos**: Si quieres volver a Tkinter temporalmente:
   ```python
   # En main.py, línea 17
   from gui import GUIManager  # Tkinter
   # O
   from gui_flet import GUIManager  # Flet (actual)
   ```

2. **Personalizar colores**: Edita `config.py` para ajustar colores del avatar

3. **Modo oscuro**: Puedes cambiar el tema en `gui_flet.py`, línea 44:
   ```python
   page.theme_mode = ft.ThemeMode.DARK  # Modo oscuro
   ```

### 🐛 Solución de Problemas

#### **Error: "No module named 'flet'"**
```bash
pip install flet>=0.24.0
```

#### **Ventana no aparece**
Verifica que no haya otro proceso de Python ejecutándose con Flet.

#### **Build falla**
Asegúrate de tener todas las dependencias instaladas:
```bash
pip install -r requirements.txt
```

### 📊 Comparativa Tkinter vs Flet

| Característica | Tkinter (Antiguo) | Flet (Nuevo) |
|---------------|-------------------|--------------|
| Diseño | Básico | Material Design 3 |
| Animaciones | No | Sí |
| Responsive | Limitado | Completo |
| Ejecutable | PyInstaller | Flet build |
| Tamaño exe | ~50MB | ~30MB |
| Desarrollo | Más código | Código limpio |
| Modernidad | ⭐⭐ | ⭐⭐⭐⭐⭐ |

### 🎉 Siguiente Paso: Crear Ejecutable

Cuando estés listo para distribuir la aplicación:

```bash
# Para macOS
flet build macos --no-console --product "Task Notifier"

# El ejecutable estará en:
# build/macos/Task Notifier.app
```

Puedes distribuir esta aplicación como un archivo .app portable que no requiere instalación de Python.

---

**¡Disfruta de tu nueva interfaz moderna!** 🚀
