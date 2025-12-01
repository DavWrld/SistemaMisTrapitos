import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# ---------- FUNCIONES DE GUARDADO / CARGA ----------
def guardar_inventario():
    with open("inventario.json", "w") as f:
        json.dump(inventario, f, indent=4)

def cargar_inventario():
    if os.path.exists("inventario.json"):
        with open("inventario.json", "r") as f:
            return json.load(f)
    return []


# ---------- BASE DE DATOS INICIAL ----------
usuarios = {
    "Hector": "1234",
    "Jorge": "pass123",
    "Eduardo": "abc789",
    "David": "0000"
}

inventario = cargar_inventario()   # Se carga al iniciar


# ---------- LOGIN ----------
def verificar_login():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if usuario in usuarios and usuarios[usuario] == password:
        ventana_login.destroy()
        menu_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


# ---------- MENÚ PRINCIPAL ----------
def menu_principal():
    global ventana_menu
    ventana_menu = tk.Tk()
    ventana_menu.title("Mis Trapitos - Menú Principal")
    ventana_menu.geometry("500x400")
    ventana_menu.resizable(False, False)
    ventana_menu.configure(bg="#f5f5f5")

    tk.Label(ventana_menu, text="MIS TRAPITOS",
             font=("Arial", 22, "bold"), bg="#f5f5f5").pack(pady=20)

    tk.Button(ventana_menu, text="Ver Inventario", width=25, height=2,
              font=("Arial", 12), command=ventana_inventario).pack(pady=10)

    tk.Button(ventana_menu, text="Agregar Producto", width=25, height=2,
              font=("Arial", 12), command=ventana_agregar_producto).pack(pady=10)

    tk.Button(ventana_menu, text="Vender", width=25, height=2,
              font=("Arial", 12), command=ventana_vender).pack(pady=10)

    tk.Button(ventana_menu, text="Editar Inventario", width=25, height=2,
              font=("Arial", 12), command=ventana_editar_producto).pack(pady=10)

    ventana_menu.mainloop()


# ---------- VENTANA INVENTARIO ----------
def ventana_inventario():
    win = tk.Toplevel()
    win.title("Inventario - Mis Trapitos")
    win.geometry("1200x700")
    win.configure(bg="white")

    tk.Label(win, text="INVENTARIO COMPLETO", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    frame_tabla = tk.Frame(win)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=20)

    scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
    scroll_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)

    columnas = [
        "ID_Producto", "Descripción", "Categoría", "Talla", "Color",
        "Precio_Base", "Precio_Descuento", "Stock", "ID_Proveedor"
    ]

    tabla = ttk.Treeview(frame_tabla, columns=columnas,
                         show="headings",
                         yscrollcommand=scroll_y.set,
                         xscrollcommand=scroll_x.set)

    scroll_y.config(command=tabla.yview)
    scroll_x.config(command=tabla.xview)
    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    tabla.pack(fill="both", expand=True)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=130)

    for item in inventario:
        tabla.insert("", "end", values=item)


# ---------- AGREGAR PRODUCTO ----------
def ventana_agregar_producto():
    win = tk.Toplevel()
    win.title("Agregar Producto - Mis Trapitos")
    win.geometry("500x600")
    win.configure(bg="white")

    tk.Label(win, text="Agregar Nuevo Producto", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    campos = [
        "ID_Producto", "Descripción/Nombre", "Categoría", "Talla",
        "Color", "Precio_Base", "Precio_Descuento", "Stock/Cantidad",
        "ID_Proveedor"
    ]

    entradas = {}

    for campo in campos:
        tk.Label(win, text=campo, font=("Arial", 12), bg="white").pack()
        entry = tk.Entry(win, font=("Arial", 12), width=30)
        entry.pack(pady=5)
        entradas[campo] = entry

    def guardar():
        producto = [entradas[c].get() for c in campos]

        if any(v == "" for v in producto):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        inventario.append(producto)
        guardar_inventario()  # SE GUARDA AQUÍ
        messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        win.destroy()

    tk.Button(win, text="Guardar", bg="#4CAF50", fg="white",
              font=("Arial", 14), width=20, command=guardar).pack(pady=20)


# ---------- VENDER ----------
def ventana_vender():
    win = tk.Toplevel()
    win.title("Vender Producto")
    win.geometry("400x300")
    win.configure(bg="white")

    tk.Label(win, text="VENTA DE PRODUCTO", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    tk.Label(win, text="ID del Producto:", font=("Arial", 12), bg="white").pack()
    entry_id = tk.Entry(win, font=("Arial", 12))
    entry_id.pack(pady=5)

    tk.Label(win, text="Cantidad a vender:", font=("Arial", 12), bg="white").pack()
    entry_cant = tk.Entry(win, font=("Arial", 12))
    entry_cant.pack(pady=5)

    def vender():
        id_prod = entry_id.get()
        cantidad = int(entry_cant.get())

        for item in inventario:
            if item[0] == id_prod:
                stock = int(item[7])

                if cantidad > stock:
                    messagebox.showerror("Error", "No hay suficiente stock.")
                    return

                item[7] = str(stock - cantidad)
                guardar_inventario()  # SE GUARDA LA VENTA
                messagebox.showinfo("Éxito", "Venta realizada.")
                win.destroy()
                return

        messagebox.showerror("Error", "Producto no encontrado.")

    tk.Button(win, text="Vender", bg="#2196F3", fg="white",
              font=("Arial", 14), width=20, command=vender).pack(pady=20)


# ---------- EDITAR PRODUCTO ----------
def ventana_editar_producto():
    win = tk.Toplevel()
    win.title("Editar Producto")
    win.geometry("450x400")
    win.configure(bg="white")

    tk.Label(win, text="EDITAR PRODUCTO", font=("Arial", 18, "bold"),
             bg="white").pack(pady=10)

    tk.Label(win, text="ID del Producto a editar:", bg="white", font=("Arial", 12)).pack()
    entry_id = tk.Entry(win, font=("Arial", 12))
    entry_id.pack(pady=5)

    def buscar():
        id_prod = entry_id.get()

        for item in inventario:
            if item[0] == id_prod:
                editar_producto(item, win)
                return

        messagebox.showerror("Error", "Producto no encontrado.")

    tk.Button(win, text="Buscar", bg="#FFC107", fg="black",
              font=("Arial", 12), width=20, command=buscar).pack(pady=15)


def editar_producto(producto, ventana_editar):
    ventana_editar.destroy()
    win = tk.Toplevel()
    win.title("Editar Datos del Producto")
    win.geometry("500x600")
    win.configure(bg="white")

    tk.Label(win, text="Editar Producto", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    campos = [
        "ID_Producto", "Descripción/Nombre", "Categoría", "Talla",
        "Color", "Precio_Base", "Precio_Descuento", "Stock/Cantidad",
        "ID_Proveedor"
    ]

    entradas = {}

    for i, campo in enumerate(campos):
        tk.Label(win, text=campo, font=("Arial", 12), bg="white").pack()
        entry = tk.Entry(win, font=("Arial", 12), width=30)
        entry.insert(0, producto[i])
        entry.pack()
        entradas[campo] = entry

    def guardar_cambios():
        for i, campo in enumerate(campos):
            producto[i] = entradas[campo].get()

        guardar_inventario()  # SE GUARDA LA EDICIÓN
        messagebox.showinfo("Éxito", "Cambios guardados.")
        win.destroy()

    tk.Button(win, text="Guardar Cambios", bg="#4CAF50", fg="white",
              font=("Arial", 14), width=20, command=guardar_cambios).pack(pady=30)


# ---------- LOGIN UI ----------
ventana_login = tk.Tk()
ventana_login.title("Login - Mis Trapitos")
ventana_login.geometry("400x350")
ventana_login.configure(bg="#f0f0f0")

frame = tk.Frame(ventana_login, bg="white", padx=20, pady=20, relief="ridge", bd=3)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Iniciar Sesión", font=("Arial", 18, "bold"),
         bg="white").pack(pady=10)

tk.Label(frame, text="Usuario", font=("Arial", 12), bg="white").pack()
entry_usuario = tk.Entry(frame, font=("Arial", 12), width=25)
entry_usuario.pack(pady=5)

tk.Label(frame, text="Contraseña", font=("Arial", 12), bg="white").pack()
entry_password = tk.Entry(frame, font=("Arial", 12), show="*", width=25)
entry_password.pack(pady=5)

tk.Button(frame, text="Entrar", font=("Arial", 12, "bold"),
          bg="#4CAF50", fg="white", width=20, command=verificar_login).pack(pady=15)

ventana_login.mainloop()
