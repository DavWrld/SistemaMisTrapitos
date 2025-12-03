# =============================================================================
# ESTILOS.PY - CONFIGURACIÓN VISUAL "MIS TRAPITOS"
# =============================================================================
import tkinter as tk
from tkinter import ttk

# --- PALETA DE COLORES (AZUL BOUTIQUE) ---
COLOR_FONDO_APP     = "#F4F7F6"  # Gris muy claro azulado (Fondo general)
COLOR_SIDEBAR       = "#1A253A"  # Azul noche oscuro (Menu lateral)
COLOR_SIDEBAR_HOVER = "#2C3E50"  # Azul grisaceo (Al pasar el mouse en menu)
COLOR_PRIMARY       = "#2980B9"  # Azul brillante (Botones principales)
COLOR_SUCCESS       = "#27AE60"  # Verde esmeralda (Guardar/Cobrar)
COLOR_DANGER        = "#C0392B"  # Rojo (Eliminar/Salir)
COLOR_WARNING       = "#F39C12"  # Naranja (Editar/Importar)
COLOR_TEXTO         = "#2C3E50"  # Texto oscuro
COLOR_BLANCO        = "#FFFFFF"

# --- TIPOGRAFÍAS ---
FONT_H1 = ("Segoe UI", 20, "bold")      # Títulos grandes
FONT_H2 = ("Segoe UI", 14, "bold")      # Subtítulos
FONT_NORMAL = ("Segoe UI", 11)          # Texto normal
FONT_BOLD = ("Segoe UI", 11, "bold")    # Texto negrita
FONT_SMALL = ("Segoe UI", 9)            # Detalles

def aplicar_tema(root):
    """
    Aplica el tema visual a la ventana raiz o toplevels.
    """
    try:
        root.configure(bg=COLOR_FONDO_APP)
    except:
        pass # Por si es un frame que no soporta config bg directo
    
    style = ttk.Style()
    style.theme_use('clam') # Usamos 'clam' para mayor control de colores

    # --- Estilo de Tablas (Treeview) ---
    style.configure("Treeview",
                    background=COLOR_BLANCO,
                    foreground=COLOR_TEXTO,
                    rowheight=30, # Filas más altas para mejor lectura
                    fieldbackground=COLOR_BLANCO,
                    font=("Segoe UI", 10))
    
    style.configure("Treeview.Heading",
                    background=COLOR_PRIMARY,
                    foreground=COLOR_BLANCO,
                    font=("Segoe UI", 10, "bold"))
    
    style.map("Treeview",
              background=[('selected', '#AED6F1')], # Azul muy suave al seleccionar
              foreground=[('selected', 'black')])

    # --- Estilos de Combobox ---
    style.configure("TCombobox", padding=5)

    return style

# --- FUNCIONES DE AYUDA PARA WIDGETS ANTIGUOS (TK) ---
def style_button_primary(btn):
    btn.configure(bg=COLOR_PRIMARY, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2")

def style_button_success(btn):
    btn.configure(bg=COLOR_SUCCESS, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2")

def style_button_danger(btn):
    btn.configure(bg=COLOR_DANGER, fg=COLOR_BLANCO, font=FONT_BOLD, 
                  bd=0, padx=15, pady=8, cursor="hand2")

def style_button_sidebar(btn):
    btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_BLANCO, font=("Segoe UI", 11), 
                  bd=0, pady=12, padx=20, anchor="w", cursor="hand2")
    
    # Efecto Hover simple
    def on_enter(e): btn['bg'] = COLOR_SIDEBAR_HOVER
    def on_leave(e): btn['bg'] = COLOR_SIDEBAR
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

def style_entry(entry):
    entry.configure(font=FONT_NORMAL, bd=1, relief="solid")