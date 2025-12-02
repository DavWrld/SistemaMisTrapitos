import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

CATEGORIAS = ["Partes Bajas", "Partes Altas", "Accesorios"]

# ---------- FUNCIONES DE GUARDADO / CARGA INVENTARIO ----------
def guardar_inventario():
    with open("inventario.json", "w") as f:
        json.dump(inventario, f, indent=4)

def cargar_inventario():
    if os.path.exists("inventario.json"):
        with open("inventario.json", "r") as f:
            return json.load(f)
    return []


# ---------- FUNCIONES DE VENTAS ----------
def guardar_venta(venta):
    ventas = cargar_ventas()
    ventas.append(venta)

    with open("ventas.json", "w") as f:
        json.dump(ventas, f, indent=4)

def cargar_ventas():
    if os.path.exists("ventas.json"):
        with open("ventas.json", "r") as f:
            return json.load(f)
    return []


# ---------- FUNCIONES DE CLIENTES ----------
def guardar_clientes():
    with open("clientes.json", "w") as f:
        json.dump(clientes, f, indent=4)

def cargar_clientes():
    if os.path.exists("clientes.json"):
        with open("clientes.json", "r") as f:
            return json.load(f)
    return {}


# ---------- BASE DE DATOS INICIAL ----------
usuarios = {
    "Hector": "1234",
    "Jorge": "pass123",
    "Eduardo": "abc789",
    "David": "0000"
}

inventario = cargar_inventario()  # Se carga al iniciar
clientes = cargar_clientes()     # Se carga la base de clientes

# ---------- LOGIN ----------
def verificar_login():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if usuario in usuarios and usuarios[usuario] == password:
        ventana_login.destroy()
        menu_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


# ---------- MENÚ PRINCIPAL (MODIFICADO) ----------
def menu_principal():
    global ventana_menu
    ventana_menu = tk.Tk()
    ventana_menu.title("Mis Trapitos - Menú Principal")
    ventana_menu.geometry("500x630") # Aumentado el tamaño vertical
    ventana_menu.resizable(False, False)
    ventana_menu.configure(bg="#f5f5f5")

    tk.Label(ventana_menu, text="MIS TRAPITOS",
             font=("Arial", 22, "bold"), bg="#f5f5f5").pack(pady=20)

    tk.Button(ventana_menu, text="Ver Inventario", width=25, height=2,
              font=("Arial", 12), command=ventana_inventario).pack(pady=8)

    tk.Button(ventana_menu, text="Agregar Producto", width=25, height=2,
              font=("Arial", 12), command=ventana_agregar_producto).pack(pady=8)

    tk.Button(ventana_menu, text="Vender", width=25, height=2,
              font=("Arial", 12), command=ventana_vender).pack(pady=8)
    
    tk.Button(ventana_menu, text="Registrar Cliente", width=25, height=2,
              font=("Arial", 12), command=ventana_registrar_cliente).pack(pady=8)
    
    tk.Button(ventana_menu, text="Historial de Cliente", width=25, height=2,
              font=("Arial", 12), command=ventana_historial_cliente).pack(pady=8)

    tk.Button(ventana_menu, text="Editar Producto", width=25, height=2,
              font=("Arial", 12), command=ventana_editar_producto).pack(pady=8)

    # 👇 NUEVO BOTÓN PARA ELIMINAR 👇
    tk.Button(ventana_menu, text="Eliminar Producto", width=25, height=2,
              font=("Arial", 12), command=ventana_eliminar_producto).pack(pady=8)

    tk.Button(ventana_menu, text="Reporte de Ventas", width=25, height=2,
              font=("Arial", 12), command=ventana_reporte_ventas).pack(pady=8)

    ventana_menu.mainloop()


# ---------- VENTANA INVENTARIO (MODIFICADO) ----------
def ventana_inventario():
    win = tk.Toplevel()
    win.title("Inventario - Mis Trapitos")
    win.geometry("1200x700")
    win.configure(bg="white")

    tk.Label(win, text="INVENTARIO COMPLETO", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    # Filtro por categoría
    filtro_frame = tk.Frame(win, bg="white")
    filtro_frame.pack(fill="x", padx=20)
    tk.Label(filtro_frame, text="Filtrar por categoría:", bg="white", font=("Arial", 12)).pack(side="left")
    filtro_var = tk.StringVar(value="Todas")
    combofiltro = ttk.Combobox(filtro_frame, textvariable=filtro_var,
                               values=["Todas"] + CATEGORIAS, state="readonly", width=18)
    combofiltro.pack(side="left", padx=10)

    frame_tabla = tk.Frame(win)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
    scroll_x = tk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL)

    columnas = [
        "ID_Producto", "Descripción", "Categoría", "Talla", "Color",
        "Precio_Base", "Precio_Descuento", "Stock", "Nombre_Proveedor" # ¡MODIFICADO!
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

    def actualizar_tabla_inventario():
        tabla.delete(*tabla.get_children())
        cat = filtro_var.get()
        for item in inventario:
            # item is expected to be a list with category at index 2
            try:
                item_cat = item[2]
            except Exception:
                item_cat = ""
            if cat == "Todas" or item_cat == cat:
                tabla.insert("", "end", values=item)

    combofiltro.bind("<<ComboboxSelected>>", lambda e: actualizar_tabla_inventario())

    actualizar_tabla_inventario()


# ---------- AGREGAR PRODUCTO (MODIFICADO) ----------
def ventana_agregar_producto():
    win = tk.Toplevel()
    win.title("Agregar Producto - Mis Trapitos")
    win.geometry("500x650")
    win.configure(bg="white")

    tk.Label(win, text="Agregar Nuevo Producto", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    # ¡MODIFICADO! "ID_Proveedor" cambiado a "Nombre_Proveedor"
    campos = [
        "ID_Producto", "Descripción/Nombre", "Categoría", "Talla",
        "Color", "Precio_Base", "Precio_Descuento", "Stock/Cantidad",
        "Nombre_Proveedor" 
    ]

    entradas = {}

    for campo in campos:
        tk.Label(win, text=campo, font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
        if campo == "Categoría":
            categoria_var = tk.StringVar()
            combocat = ttk.Combobox(win, textvariable=categoria_var, values=CATEGORIAS, state="readonly", width=30)
            combocat.pack(pady=5)
            entradas[campo] = combocat
        else:
            entry = tk.Entry(win, font=("Arial", 12), width=34)
            entry.pack(pady=5)
            entradas[campo] = entry

    def guardar():
        producto = [entradas[c].get() for c in campos]

        if any(v == "" for v in producto):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        # Validaciones básicas: stock y precios numéricos
        try:
            # asegurarse que índice 5 (Precio_Base), 6 (Precio_Descuento) y 7 (Stock) sean números
            float(producto[5])
            float(producto[6])
            int(producto[7])
        except Exception:
            messagebox.showerror("Error", "Precio_Base, Precio_Descuento deben ser números y Stock un entero.")
            return

        # Validación: ID de Producto único
        if any(item[0] == producto[0] for item in inventario):
            messagebox.showerror("Error", f"El ID de Producto '{producto[0]}' ya existe. Por favor, use otro.")
            return
            
        inventario.append(producto)
        guardar_inventario()
        messagebox.showinfo("Éxito", "Producto agregado correctamente.")
        win.destroy()

    tk.Button(win, text="Guardar", bg="#4CAF50", fg="white",
              font=("Arial", 14), width=20, command=guardar).pack(pady=20)


# ---------- VENDER (SIN CAMBIOS FUNCIONALES) ----------
def ventana_vender():
    win = tk.Toplevel()
    win.title("Realizar Venta - Mis Trapitos")
    win.geometry("1000x750")
    win.configure(bg="#F5F5F5")

    # ---- TÍTULO ----
    tk.Label(win, text="PUNTO DE VENTA", font=("Arial", 24, "bold"),
             bg="#F5F5F5", fg="#333").pack(pady=15)

    frame_main = tk.Frame(win, bg="#F5F5F5")
    frame_main.pack(expand=True, fill="both")

    # ========================================
    # IZQUIERDA: FILTRO Y TABLA DE PRODUCTOS
    # ========================================
    left_container = tk.Frame(frame_main, bg="white", bd=2, relief="ridge")
    left_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    tk.Label(left_container, text="Productos Disponibles",
             font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    # Filtro por categoría en vender
    filtro_cat_var = tk.StringVar(value="Todas")
    filtro_combo = ttk.Combobox(left_container, textvariable=filtro_cat_var,
                                 values=["Todas"] + CATEGORIAS, state="readonly", width=20)
    filtro_combo.pack(pady=5)

    columnas = [
        "ID_Producto", "Descripción", "Precio_Base",
        "Precio_Descuento", "Stock"
    ]

    tabla = ttk.Treeview(left_container, columns=columnas, show="headings", height=20)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)

    # Scrollbar
    scroll_y = ttk.Scrollbar(left_container, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll_y.set)
    scroll_y.pack(side="right", fill="y")
    tabla.pack(expand=True, fill="both")

    def actualizar_tabla_vender():
        tabla.delete(*tabla.get_children())
        cat = filtro_cat_var.get()
        for item in inventario:
            try:
                stock = int(item[7])
            except Exception:
                stock = 0
            try:
                item_cat = item[2]
            except Exception:
                item_cat = ""
            if stock > 0 and (cat == "Todas" or item_cat == cat):
                tabla.insert("", "end", values=(item[0], item[1], item[5], item[6], item[7]))

    filtro_combo.bind("<<ComboboxSelected>>", lambda e: actualizar_tabla_vender())
    actualizar_tabla_vender()

    # ========================================
    # DERECHA: PANEL DE INFORMACIÓN Y VENTA
    # ========================================
    panel = tk.Frame(frame_main, bg="white", bd=2, relief="ridge", padx=20, pady=20)
    panel.pack(side="right", fill="y", padx=20, pady=20)

    tk.Label(panel, text="Detalles del Producto",
             font=("Arial", 16, "bold"), bg="white").pack(pady=10)

    info = {
        "ID": tk.Label(panel, text="ID: ---", font=("Arial", 12), bg="white"),
        "Nombre": tk.Label(panel, text="Nombre: ---", font=("Arial", 12), bg="white"),
        "Precio Base": tk.Label(panel, text="Precio Base: ---", font=("Arial", 12), bg="white"),
        "Descuento": tk.Label(panel, text="Precio con Descuento: ---", font=("Arial", 12), bg="white"),
        "Stock": tk.Label(panel, text="Stock disponible: ---", font=("Arial", 12), bg="white"),
    }

    for widget in info.values():
        widget.pack(anchor="w", pady=5)

    # ---- Entrada de cantidad ----
    tk.Label(panel, text="\nCantidad a vender:",
             font=("Arial", 14, "bold"), bg="white").pack(anchor="w")

    entry_cantidad = tk.Entry(panel, font=("Arial", 12), width=10)
    entry_cantidad.pack(pady=5)

    # ---- Total ----
    label_total = tk.Label(panel, text="Total: $0.00",
                           font=("Arial", 18, "bold"), bg="white", fg="#4CAF50")
    label_total.pack(pady=20)
    
    # ---- Selección de Cliente ----
    tk.Label(panel, text="ID Cliente (Opcional):",
             font=("Arial", 12), bg="white").pack(anchor="w", pady=(10,0))
    entry_id_cliente = tk.Entry(panel, font=("Arial", 12), width=20)
    entry_id_cliente.pack(pady=5)
    
    # ---- Método de Pago ----
    tk.Label(panel, text="Método de Pago:",
             font=("Arial", 14, "bold"), bg="white").pack(anchor="w", pady=(15, 5))
    
    metodo_pago_var = tk.StringVar(value="") # Variable de control
    
    frame_pago = tk.Frame(panel, bg="white")
    frame_pago.pack(anchor="w")
    
    tk.Radiobutton(frame_pago, text="Efectivo", variable=metodo_pago_var, value="Efectivo",
                   font=("Arial", 12), bg="white").pack(side="left", padx=10)
    
    tk.Radiobutton(frame_pago, text="Tarjeta", variable=metodo_pago_var, value="Tarjeta",
                   font=("Arial", 12), bg="white").pack(side="left", padx=10)


    seleccionado = {"item": None}

    # ----------------------------------------
    # AL SELECCIONAR PRODUCTO
    # ----------------------------------------
    def seleccionar_producto(event):
        seleccion = tabla.focus()
        if not seleccion:
            return

        datos = tabla.item(seleccion, "values")
        seleccionado["item"] = datos

        info["ID"].config(text=f"ID: {datos[0]}")
        info["Nombre"].config(text=f"Nombre: {datos[1]}")
        info["Precio Base"].config(text=f"Precio Base: ${datos[2]}")
        info["Descuento"].config(text=f"Precio con Descuento: ${datos[3]}")
        info["Stock"].config(text=f"Stock disponible: {datos[4]}")

    tabla.bind("<<TreeviewSelect>>", seleccionar_producto)

    # ----------------------------------------
    # CALCULAR TOTAL AUTOMÁTICAMENTE
    # ----------------------------------------
    def actualizar_total(event):
        try:
            if not seleccionado["item"]:
                return

            precio = float(seleccionado["item"][3])
            cantidad = int(entry_cantidad.get())

            total = precio * cantidad
            label_total.config(text=f"Total: ${total:.2f}")

        except:
            label_total.config(text="Total: $0.00")

    entry_cantidad.bind("<KeyRelease>", actualizar_total)

    # ----------------------------------------
    # CONFIRMAR VENTA
    # ----------------------------------------
    def confirmar_venta():
        if not seleccionado["item"]:
            messagebox.showerror("Error", "Selecciona un producto.")
            return

        try:
            cantidad = int(entry_cantidad.get())
            if cantidad <= 0:
                 messagebox.showerror("Error", "La cantidad debe ser mayor a cero.")
                 return
        except:
            messagebox.showerror("Error", "Cantidad inválida.")
            return
        
        metodo_pago = metodo_pago_var.get()
        if metodo_pago == "":
            messagebox.showerror("Error", "Selecciona un método de pago (Efectivo o Tarjeta).")
            return

        id_prod = seleccionado["item"][0]
        id_cliente = entry_id_cliente.get().strip()
        
        # Validar Cliente si se proporciona un ID
        if id_cliente and id_cliente not in clientes:
             messagebox.showerror("Error", f"El ID de Cliente '{id_cliente}' no está registrado.")
             return


        for item in inventario:
            if item[0] == id_prod:
                try:
                    stock = int(item[7])
                except:
                    stock = 0

                if cantidad > stock:
                    messagebox.showerror("Error", "No hay suficiente stock.")
                    return

                # Reducir stock
                item[7] = str(stock - cantidad)
                guardar_inventario()

                # Registrar venta
                venta = {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "id_producto": seleccionado["item"][0],
                    "descripcion": seleccionado["item"][1],
                    "precio_unitario": float(seleccionado["item"][3]),
                    "cantidad": cantidad,
                    "total": float(seleccionado["item"][3]) * cantidad,
                    "id_cliente": id_cliente if id_cliente else "N/A",
                    "metodo_pago": metodo_pago 
                }

                guardar_venta(venta)

                messagebox.showinfo("Venta Exitosa", "La venta fue registrada correctamente.")
                win.destroy()
                return

    tk.Button(panel, text="CONFIRMAR VENTA", font=("Arial", 16, "bold"),
              bg="#4CAF50", fg="white", width=20, height=2,
              command=confirmar_venta).pack(pady=30)


# ---------- REGISTRAR CLIENTE (SIN CAMBIOS) ----------
def ventana_registrar_cliente():
    win = tk.Toplevel()
    win.title("Registrar Cliente - Mis Trapitos")
    win.geometry("450x450")
    win.configure(bg="white")

    tk.Label(win, text="REGISTRAR NUEVO CLIENTE", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    campos = ["ID Cliente", "Nombre", "Apellido", "Teléfono", "Email"]
    entradas = {}

    for campo in campos:
        tk.Label(win, text=campo + ":", font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
        entry = tk.Entry(win, font=("Arial", 12), width=34)
        entry.pack(pady=5)
        entradas[campo] = entry

    def guardar_cliente():
        id_cliente = entradas["ID Cliente"].get().strip()
        nombre = entradas["Nombre"].get().strip()
        apellido = entradas["Apellido"].get().strip()
        telefono = entradas["Teléfono"].get().strip()
        email = entradas["Email"].get().strip()

        if not all([id_cliente, nombre, apellido]):
            messagebox.showerror("Error", "ID Cliente, Nombre y Apellido son obligatorios.")
            return

        if id_cliente in clientes:
            messagebox.showerror("Error", f"El ID de Cliente '{id_cliente}' ya existe.")
            return

        clientes[id_cliente] = {
            "nombre": nombre,
            "apellido": apellido,
            "telefono": telefono,
            "email": email
        }

        guardar_clientes()
        messagebox.showinfo("Éxito", f"Cliente {nombre} {apellido} registrado con ID: {id_cliente}")
        win.destroy()

    tk.Button(win, text="Registrar", bg="#00BCD4", fg="white",
              font=("Arial", 14), width=20, command=guardar_cliente).pack(pady=20)


# ---------- HISTORIAL DE CLIENTE (SIN CAMBIOS) ----------
def ventana_historial_cliente():
    win = tk.Toplevel()
    win.title("Historial de Compras por Cliente")
    win.geometry("900x600")
    win.configure(bg="white")

    tk.Label(win, text="HISTORIAL DE COMPRAS DE CLIENTE", font=("Arial", 18, "bold"),
             bg="white").pack(pady=10)

    # Frame de Búsqueda
    frame_busqueda = tk.Frame(win, bg="white")
    frame_busqueda.pack(pady=10)

    tk.Label(frame_busqueda, text="ID del Cliente:", bg="white", font=("Arial", 12)).pack(side="left", padx=5)
    entry_id = tk.Entry(frame_busqueda, font=("Arial", 12), width=20)
    entry_id.pack(side="left", padx=5)
    
    # Etiqueta de información del cliente (vacía inicialmente)
    label_info_cliente = tk.Label(win, text="Cliente: ---", font=("Arial", 14, "bold"), bg="white", fg="#00796B")
    label_info_cliente.pack(pady=5)
    
    # Frame para la tabla
    frame_tabla = tk.Frame(win)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
    scroll_y.pack(side="right", fill="y")

    columnas = ["Fecha", "ID Producto", "Descripción", "Precio Unitario", "Cantidad", "Total", "Método Pago"] 

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings",
                         yscrollcommand=scroll_y.set)

    scroll_y.config(command=tabla.yview)
    tabla.pack(fill="both", expand=True)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150)

    def buscar_historial():
        tabla.delete(*tabla.get_children())
        id_buscado = entry_id.get().strip()
        ventas = cargar_ventas()
        
        # 1. Validar y mostrar información del cliente
        if id_buscado in clientes:
            info = clientes[id_buscado]
            label_info_cliente.config(text=f"Cliente: {info['nombre']} {info['apellido']} (Tel: {info['telefono']})")
        else:
            messagebox.showerror("Error", "ID de Cliente no encontrado.")
            label_info_cliente.config(text="Cliente: ---")
            return

        # 2. Filtrar ventas
        compras_cliente = [v for v in ventas if v.get("id_cliente") == id_buscado]
        
        if not compras_cliente:
            messagebox.showinfo("Información", f"El cliente {id_buscado} no tiene ventas registradas.")
            return

        # 3. Insertar en la tabla
        for v in compras_cliente:
            total_venta = v.get("total", 0.0)
            cantidad_vendida = v.get("cantidad", 0)
            
            tabla.insert("", "end", values=(
                v.get("fecha", "N/A"),
                v.get("id_producto", "N/A"),
                v.get("descripcion", "N/A"),
                f"${v.get('precio_unitario', 0.0):.2f}",
                cantidad_vendida,
                f"${total_venta:.2f}",
                v.get("metodo_pago", "N/A") 
            ))

    tk.Button(frame_busqueda, text="Buscar Historial", bg="#008CBA", fg="white",
              font=("Arial", 12), command=buscar_historial).pack(side="left", padx=10)


# ---------- EDITAR PRODUCTO (MODIFICADO) ----------
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
    win.geometry("500x650")
    win.configure(bg="white")

    tk.Label(win, text="Editar Producto", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    # ¡MODIFICADO! "ID_Proveedor" cambiado a "Nombre_Proveedor"
    campos = [
        "ID_Producto", "Descripción/Nombre", "Categoría", "Talla",
        "Color", "Precio_Base", "Precio_Descuento", "Stock/Cantidad",
        "Nombre_Proveedor" 
    ]

    entradas = {}

    for i, campo in enumerate(campos):
        tk.Label(win, text=campo, font=("Arial", 12), bg="white").pack(anchor="w", padx=20)
        if campo == "Categoría":
            categoria_var = tk.StringVar()
            combocat = ttk.Combobox(win, textvariable=categoria_var, values=CATEGORIAS, state="readonly", width=30)
            # intentar seleccionar la categoría actual si existe
            try:
                if producto[2] in CATEGORIAS:
                    combocat.set(producto[2])
            except Exception:
                pass
            combocat.pack(pady=5)
            entradas[campo] = combocat
        else:
            entry = tk.Entry(win, font=("Arial", 12), width=34)
            try:
                entry.insert(0, producto[i])
            except Exception:
                entry.insert(0, "")
            # Deshabilitar la edición del ID para prevenir inconsistencias
            if campo == "ID_Producto":
                entry.config(state="readonly") 
            entry.pack(pady=5)
            entradas[campo] = entry

    def guardar_cambios():
        # Validaciones de la edición (secciones 5, 6, 7 deben ser números)
        try:
            float(entradas["Precio_Base"].get())
            float(entradas["Precio_Descuento"].get())
            int(entradas["Stock/Cantidad"].get())
        except Exception:
            messagebox.showerror("Error", "Precio_Base, Precio_Descuento deben ser números y Stock un entero.")
            return

        for i, campo in enumerate(campos):
             if campo != "ID_Producto": # No se edita el ID
                 producto[i] = entradas[campo].get()

        guardar_inventario()
        messagebox.showinfo("Éxito", "Cambios guardados.")
        win.destroy()

    tk.Button(win, text="Guardar Cambios", bg="#4CAF50", fg="white",
              font=("Arial", 14), width=20, command=guardar_cambios).pack(pady=30)


# 👇 NUEVA FUNCIÓN PARA ELIMINAR PRODUCTOS 👇
# ----------------------------------------------------
def ventana_eliminar_producto():
    win = tk.Toplevel()
    win.title("Eliminar Producto")
    win.geometry("400x250")
    win.configure(bg="white")

    tk.Label(win, text="ELIMINAR PRODUCTO", font=("Arial", 18, "bold"),
             bg="white").pack(pady=15)

    tk.Label(win, text="ID del Producto a eliminar:", bg="white", font=("Arial", 12)).pack()
    entry_id = tk.Entry(win, font=("Arial", 12))
    entry_id.pack(pady=5)

    def eliminar():
        global inventario
        id_prod = entry_id.get().strip()

        if not id_prod:
            messagebox.showerror("Error", "Debes ingresar el ID del producto.")
            return

        # Buscar el producto en el inventario
        producto_a_eliminar = None
        for item in inventario:
            if item[0] == id_prod:
                producto_a_eliminar = item
                break

        if producto_a_eliminar:
            # Confirmación antes de eliminar
            confirmar = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Estás seguro de que deseas eliminar '{producto_a_eliminar[1]}' (ID: {id_prod}) permanentemente?"
            )
            
            if confirmar:
                try:
                    # Eliminar el producto de la lista global
                    inventario.remove(producto_a_eliminar)
                    
                    # Guardar el inventario modificado en el archivo JSON
                    guardar_inventario() 
                    
                    messagebox.showinfo("Éxito", f"Producto '{id_prod}' eliminado correctamente.")
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error al guardar los cambios: {e}")
            
        else:
            messagebox.showerror("Error", f"Producto con ID '{id_prod}' no encontrado.")


    tk.Button(win, text="Eliminar Producto", bg="#D32F2F", fg="white",
              font=("Arial", 12, "bold"), width=20, command=eliminar).pack(pady=20)
# ----------------------------------------------------
# 👆 FIN DE LA NUEVA FUNCIÓN 👆


# ---------- REPORTE DE VENTAS (SIN CAMBIOS FUNCIONALES) ----------
def ventana_reporte_ventas():
    win = tk.Toplevel()
    win.title("Reporte de Ventas - Mis Trapitos")
    win.geometry("1100x750")
    win.configure(bg="white")

    tk.Label(win, text="REPORTE DE VENTAS", font=("Arial", 18, "bold"),
             bg="white").pack(pady=10)
    
    # ----------------------------------------
    # CONTROLES DE FILTRO POR FECHA
    # ----------------------------------------
    filtro_frame = tk.Frame(win, bg="white", padx=10, pady=10)
    filtro_frame.pack(fill="x", padx=20)
    
    tk.Label(filtro_frame, text="Filtrar por Rango de Fechas (AAAA-MM-DD):", 
             bg="white", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=5, pady=5, sticky="w")
    
    tk.Label(filtro_frame, text="Desde:", bg="white", font=("Arial", 11)).grid(row=1, column=0, padx=5, sticky="w")
    entry_desde = tk.Entry(filtro_frame, font=("Arial", 11), width=15)
    entry_desde.grid(row=1, column=1, padx=5)
    entry_desde.insert(0, "2020-01-01") 
    
    tk.Label(filtro_frame, text="Hasta:", bg="white", font=("Arial", 11)).grid(row=1, column=2, padx=5, sticky="w")
    entry_hasta = tk.Entry(filtro_frame, font=("Arial", 11), width=15)
    entry_hasta.grid(row=1, column=3, padx=5)
    entry_hasta.insert(0, datetime.now().strftime("%Y-%m-%d")) 
    
    # Nuevo filtro de pago
    tk.Label(filtro_frame, text="Método de Pago:", bg="white", font=("Arial", 11)).grid(row=2, column=0, padx=5, sticky="w", pady=5)
    metodo_pago_filtro_var = tk.StringVar(value="Todos")
    combofiltro_pago = ttk.Combobox(filtro_frame, textvariable=metodo_pago_filtro_var,
                                 values=["Todos", "Efectivo", "Tarjeta"], state="readonly", width=12)
    combofiltro_pago.grid(row=2, column=1, padx=5, sticky="w")


    # ----------------------------------------
    # TABLA Y TOTALES
    # ----------------------------------------
    
    frame_tabla = tk.Frame(win)
    frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

    scroll_y = tk.Scrollbar(frame_tabla, orient=tk.VERTICAL)
    scroll_y.pack(side="right", fill="y")

    columnas = ["Fecha", "ID Producto", "Descripción", "Precio Unitario", "Cantidad", "Total", "ID Cliente", "Método Pago"] 

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings",
                         yscrollcommand=scroll_y.set)

    scroll_y.config(command=tabla.yview)
    tabla.pack(fill="both", expand=True)

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=110)

    # Frame para mostrar los totales
    frame_totales = tk.Frame(win, bg="#f0f0f0", bd=1, relief="solid")
    frame_totales.pack(fill="x", padx=20, pady=10)
    
    label_total_monetario = tk.Label(frame_totales, 
                                     text="Total de Ventas Generales: $0.00",
                                     font=("Arial", 14, "bold"), 
                                     bg="#f0f0f0", 
                                     fg="#00796B", 
                                     anchor="w")
    label_total_monetario.pack(pady=5, padx=10, fill="x")

    label_total_unidades = tk.Label(frame_totales, 
                                     text="Total de Unidades Vendidas: 0",
                                     font=("Arial", 14, "bold"), 
                                     bg="#f0f0f0", 
                                     fg="#00796B", 
                                     anchor="w")
    label_total_unidades.pack(pady=5, padx=10, fill="x")

    def actualizar_reporte():
        tabla.delete(*tabla.get_children())
        ventas = cargar_ventas()
        total_ventas_monetario = 0.0
        total_unidades_vendidas = 0
        
        fecha_desde_str = entry_desde.get().strip()
        fecha_hasta_str = entry_hasta.get().strip()
        filtro_pago = metodo_pago_filtro_var.get()

        try:
            fecha_desde = datetime.strptime(fecha_desde_str, "%Y-%m-%d")
            fecha_hasta = datetime.strptime(fecha_hasta_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        except ValueError:
            messagebox.showerror("Error de Fecha", "Formato de fecha inválido. Use AAAA-MM-DD.")
            return

        for v in ventas:
            try:
                fecha_venta = datetime.strptime(v["fecha"], "%Y-%m-%d %H:%M:%S")
                metodo_venta = v.get("metodo_pago", "N/A")
                
                # Aplicar filtro de fecha
                if not (fecha_desde <= fecha_venta <= fecha_hasta):
                    continue
                
                # Aplicar filtro de método de pago
                if filtro_pago != "Todos" and metodo_venta != filtro_pago:
                    continue


                total_venta = v.get("total", 0.0)
                cantidad_vendida = v.get("cantidad", 0)
                
                # Sumar totales de las ventas filtradas
                total_ventas_monetario += total_venta
                total_unidades_vendidas += cantidad_vendida
                
                # Insertar en la tabla
                tabla.insert("", "end", values=(
                    v.get("fecha", "N/A"),
                    v.get("id_producto", "N/A"),
                    v.get("descripcion", "N/A"),
                    f"${v.get('precio_unitario', 0.0):.2f}",
                    cantidad_vendida,
                    f"${total_venta:.2f}",
                    v.get("id_cliente", "N/A"),
                    metodo_venta
                ))

            except (KeyError, ValueError) as e:
                pass

        # Actualizar etiquetas de totales
        label_total_monetario.config(text=f"Total de Ventas Generales: ${total_ventas_monetario:.2f}")
        label_total_unidades.config(text=f"Total de Unidades Vendidas: {total_unidades_vendidas}")


    # Botón para aplicar el filtro
    tk.Button(filtro_frame, text="Aplicar Filtro", bg="#008CBA", fg="white",
              font=("Arial", 11, "bold"), command=actualizar_reporte).grid(row=2, column=4, padx=15, sticky="e")
    
    # Cargar reporte inicial
    actualizar_reporte()


# ---------- LOGIN UI (SIN CAMBIOS) ----------
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