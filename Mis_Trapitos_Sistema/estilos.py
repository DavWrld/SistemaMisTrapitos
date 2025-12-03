import tkinter as tk
from tkinter import ttk

# =============================================================================
# PALETA DE COLORES (AZUL BOUTIQUE)
# =============================================================================
COLOR_FONDO_APP     = "#F4F7F6"  # Gris muy claro azulado (Fondo general)
COLOR_SIDEBAR       = "#1A253A"  # Azul noche oscuro (Menu lateral)
COLOR_SIDEBAR_HOVER = "#2C3E50"  # Azul grisaceo (Al pasar el mouse en menu)
COLOR_PRIMARY       = "#2980B9"  # Azul brillante (Botones principales)
COLOR_SUCCESS       = "#27AE60"  # Verde esmeralda (Guardar/Cobrar)
COLOR_DANGER        = "#C0392B"  # Rojo (Eliminar/Salir)
COLOR_WARNING       = "#F39C12"  # Naranja (Editar/Importar)
COLOR_TEXTO         = "#2C3E50"  # Texto oscuro
COLOR_BLANCO        = "#FFFFFF"

# =============================================================================
# TIPOGRAFÍAS
# =============================================================================
# Usamos una fuente segura como 'Segoe UI' (Windows) o 'Helvetica'/'Arial' si no existe
FONT_H1 = ("Segoe UI", 20, "bold")      # Títulos grandes
FONT_H2 = ("Segoe UI", 14, "bold")      # Subtítulos
FONT_NORMAL = ("Segoe UI", 11)          # Texto normal
FONT_BOLD = ("Segoe UI", 11, "bold")    # Texto negrita

# =============================================================================
# CONFIGURACIÓN DEL TEMA (TTK)
# =============================================================================
def configurar_estilo():
    """Configura el estilo visual de los widgets modernos (ttk)."""
    style = ttk.Style()
    
    # Intentar usar el tema 'clam' que permite mejor personalización de colores
    # Si no está disponible, usa el por defecto.
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    
    # --- Estilo para Tablas (Treeview) ---
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    fieldbackground="white",
                    rowheight=25,
                    font=("Segoe UI", 10))
    
    style.configure("Treeview.Heading",
                    background=COLOR_PRIMARY,
                    foreground="white",
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
    
    style.map("Treeview",
              background=[('selected', '#AED6F1')], # Azul suave al seleccionar
              foreground=[('selected', 'black')])

    # --- Estilo para Combobox ---
    style.configure("TCombobox", padding=5)

    return style

# =============================================================================
# FUNCIONES AUXILIARES PARA BOTONES (TKINTER NORMAL)
# =============================================================================
# Estas funciones aplican estilos predefinidos a los botones estándar de Tkinter

def style_button_primary(btn):
    """Botón Azul (Acciones principales)"""
    btn.configure(bg=COLOR_PRIMARY, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2", activebackground="#1F618D", activeforeground="white")

def style_button_success(btn):
    """Botón Verde (Confirmaciones, Agregar)"""
    btn.configure(bg=COLOR_SUCCESS, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2", activebackground="#1E8449", activeforeground="white")

def style_button_danger(btn):
    """Botón Rojo (Eliminar, Salir)"""
    btn.configure(bg=COLOR_DANGER, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2", activebackground="#922B21", activeforeground="white")

def style_button_warning(btn):
    """Botón Naranja (Alertas, Importar)"""
    btn.configure(bg=COLOR_WARNING, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2", activebackground="#D68910", activeforeground="white")

def style_button_sidebar(btn):
    """Botón del Menú Lateral"""
    btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_BLANCO, font=("Segoe UI", 11), 
                  bd=0, padx=20, pady=12, cursor="hand2", anchor="w", activebackground=COLOR_SIDEBAR_HOVER, activeforeground="white")