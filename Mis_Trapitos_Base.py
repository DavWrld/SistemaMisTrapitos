import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import csv
from datetime import datetime, date

# =============================================================================
# CAPA DE DATOS (MODELO)
# =============================================================================

class DatabaseManager:
    def __init__(self, db_name="mis_trapitos.db"):
        self.db_name = db_name
        self.crear_tablas()
        self.sembrar_datos_iniciales()
        self.actualizar_schema() 

    def conectar(self):
        return sqlite3.connect(self.db_name)

    def crear_tablas(self):
        conn = self.conectar()
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            rol TEXT NOT NULL)''') 

        cursor.execute('''CREATE TABLE IF NOT EXISTS proveedores (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            contacto TEXT,
                            telefono TEXT,
                            email TEXT,
                            direccion TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS categorias (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT UNIQUE NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            descripcion TEXT,
                            categoria_id INTEGER,
                            precio REAL NOT NULL,
                            talla TEXT,
                            color TEXT,
                            stock INTEGER NOT NULL,
                            stock_minimo INTEGER DEFAULT 5,
                            proveedor_id INTEGER,
                            FOREIGN KEY(categoria_id) REFERENCES categorias(id),
                            FOREIGN KEY(proveedor_id) REFERENCES proveedores(id))''')

        # NOTA: Se agrega cliente_id para vincular historial
        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fecha TEXT NOT NULL,
                            cliente_nombre TEXT,
                            total REAL,
                            usuario_id INTEGER,
                            cliente_id INTEGER, 
                            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                            FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS detalle_ventas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            venta_id INTEGER,
                            producto_id INTEGER,
                            cantidad INTEGER,
                            precio_unitario REAL,
                            subtotal REAL,
                            FOREIGN KEY(venta_id) REFERENCES ventas(id),
                            FOREIGN KEY(producto_id) REFERENCES productos(id))''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            direccion TEXT,
                            telefono TEXT,
                            email TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS promociones (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            tipo_entidad TEXT, 
                            entidad_id INTEGER,
                            tipo_descuento TEXT,
                            valor1 REAL,
                            valor2 REAL,
                            fecha_inicio TEXT,
                            fecha_fin TEXT)''')

        conn.commit()
        conn.close()

    def actualizar_schema(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        # 1. Revisar columna direccion en clientes
        try:
            cursor.execute("SELECT direccion FROM clientes LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE clientes ADD COLUMN direccion TEXT")
            conn.commit()
            
        # 2. Revisar columna cliente_id en ventas (NUEVO PARA HISTORIAL)
        try:
            cursor.execute("SELECT cliente_id FROM ventas LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER")
            conn.commit()
            
        conn.close()

    def sembrar_datos_iniciales(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", 
                           ('admin', 'admin123', 'Administrador'))
            cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", 
                           ('vendedor', '1234', 'Vendedor'))

        categorias = ['Camisetas', 'Pantalones', 'Accesorios', 'Zapatos', 'Vestidos']
        for cat in categorias:
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (cat,))
        
        cursor.execute("SELECT * FROM proveedores")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?,?,?)",
                           ("Proveedor General", "Juan Perez", "555-0000"))

        conn.commit()
        conn.close()

# =============================================================================
# CAPA DE LÓGICA (CONTROLADOR)
# =============================================================================

class Controller:
    def __init__(self):
        self.db = DatabaseManager()

    def login(self, user, pwd):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
        usuario = cursor.fetchone()
        conn.close()
        return usuario

    # --- Productos ---
    def agregar_producto(self, nombre, desc, cat_id, precio, talla, color, stock, prov_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO productos (nombre, descripcion, categoria_id, precio, talla, color, stock, proveedor_id)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (nombre, desc, cat_id, precio, talla, color, stock, prov_id))
        conn.commit()
        conn.close()

    def obtener_productos(self, filtro=None):
        conn = self.db.conectar()
        cursor = conn.cursor()
        query = '''SELECT p.id, p.nombre, p.descripcion, p.categoria_id, p.precio, p.talla, p.color, p.stock, p.proveedor_id, c.nombre, pr.nombre 
                   FROM productos p
                   LEFT JOIN categorias c ON p.categoria_id = c.id
                   LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
                   WHERE 1=1'''
        params = []
        if filtro:
            if filtro.get('nombre'):
                query += " AND p.nombre LIKE ?"
                params.append(f"%{filtro['nombre']}%")
            if filtro.get('categoria') and filtro['categoria'] != "Todas":
                query += " AND c.nombre = ?"
                params.append(filtro['categoria'])
        
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    # --- Ventas ---
    def registrar_venta(self, usuario_id, cliente_nombre, items_venta, total_final, cliente_id=None):
        conn = self.db.conectar()
        cursor = conn.cursor()
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertamos también el cliente_id si existe
        cursor.execute("INSERT INTO ventas (fecha, cliente_nombre, total, usuario_id, cliente_id) VALUES (?, ?, ?, ?, ?)",
                       (fecha, cliente_nombre, total_final, usuario_id, cliente_id))
        venta_id = cursor.lastrowid
        
        for item in items_venta:
            cursor.execute('''INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                              VALUES (?, ?, ?, ?, ?)''',
                              (venta_id, item['id'], item['cantidad'], item['precio_unitario_real'], item['subtotal_final']))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['id']))
            
        conn.commit()
        conn.close()
        return venta_id

    # NUEVO: Obtener historial de ventas de un cliente
    def obtener_ventas_por_cliente(self, cliente_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        # Traemos fecha, total y el usuario que vendió
        query = '''SELECT v.id, v.fecha, v.total, u.username 
                   FROM ventas v
                   LEFT JOIN usuarios u ON v.usuario_id = u.id
                   WHERE v.cliente_id = ?
                   ORDER BY v.fecha DESC'''
        cursor.execute(query, (cliente_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    # NUEVO: Obtener detalle de una venta específica para el historial
    def obtener_detalle_venta(self, venta_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        query = '''SELECT p.nombre, d.cantidad, d.precio_unitario, d.subtotal
                   FROM detalle_ventas d
                   JOIN productos p ON d.producto_id = p.id
                   WHERE d.venta_id = ?'''
        cursor.execute(query, (venta_id,))
        data = cursor.fetchall()
        conn.close()
        return data

    # --- Clientes ---
    def agregar_cliente(self, nombre, direccion, telefono, email):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (?, ?, ?, ?)",
                       (nombre, direccion, telefono, email))
        conn.commit()
        conn.close()

    def obtener_clientes(self, busqueda=None):
        conn = self.db.conectar()
        cursor = conn.cursor()
        
        query = "SELECT * FROM clientes WHERE 1=1"
        params = []
        
        if busqueda:
            query += " AND (nombre LIKE ? OR id LIKE ?)"
            params.append(f"%{busqueda}%")
            params.append(f"{busqueda}%")
            
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    # --- Promociones ---
    def agregar_promocion(self, nombre, tipo_ent, ent_id, tipo_desc, v1, v2, f_inicio, f_fin):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO promociones (nombre, tipo_entidad, entidad_id, tipo_descuento, valor1, valor2, fecha_inicio, fecha_fin)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                          (nombre, tipo_ent, ent_id, tipo_desc, v1, v2, f_inicio, f_fin))
        conn.commit()
        conn.close()
    
    def obtener_promociones_activas(self):
        conn = self.db.conectar()
        cursor = conn.cursor()
        hoy = date.today().strftime("%Y-%m-%d")
        query = "SELECT * FROM promociones WHERE fecha_inicio <= ? AND fecha_fin >= ?"
        cursor.execute(query, (hoy, hoy))
        data = cursor.fetchall()
        conn.close()
        return data

    def obtener_todas_promociones(self):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM promociones")
        data = cursor.fetchall()
        conn.close()
        return data
    
    def eliminar_promocion(self, promo_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM promociones WHERE id=?", (promo_id,))
        conn.commit()
        conn.close()

    # --- MOTOR DE CÁLCULO ---
    def calcular_carrito_con_descuentos(self, carrito):
        promos = self.obtener_promociones_activas()
        
        subtotal_bruto = 0
        total_neto = 0
        items_procesados = []
        
        for item in carrito:
            pid = item['id']
            p_cat = item['cat_id']
            cant = item['cantidad']
            precio = item['precio_base']
            
            subtotal_bruto += (cant * precio)
            
            mejor_descuento = 0
            tipo_aplicado = ""
            
            for prom in promos:
                p_tipo_ent = prom[2]
                p_ent_id = prom[3]
                p_tipo_desc = prom[4]
                v1 = prom[5]
                v2 = prom[6]
                
                aplica = False
                if p_tipo_ent == "Producto" and p_ent_id == pid:
                    aplica = True
                elif p_tipo_ent == "Categoria" and p_ent_id == p_cat:
                    aplica = True
                
                if aplica:
                    desc_calculado = 0
                    if p_tipo_desc == "Porcentaje":
                        desc_calculado = (precio * cant) * (v1 / 100)
                    elif p_tipo_desc == "Monto Fijo":
                        desc_calculado = v1 * cant
                    elif p_tipo_desc == "NxM":
                        n = int(v1); m = int(v2)
                        grupos = cant // n
                        resto = cant % n
                        pagar = (grupos * m) + resto
                        total_linea_sin_desc = cant * precio
                        total_linea_con_desc = pagar * precio
                        desc_calculado = total_linea_sin_desc - total_linea_con_desc
                    
                    if desc_calculado > mejor_descuento:
                        mejor_descuento = desc_calculado
                        tipo_aplicado = prom[1]

            subtotal_linea_final = (cant * precio) - mejor_descuento
            items_procesados.append({
                'id': pid,
                'nombre': item['nombre'],
                'cantidad': cant,
                'precio_base': precio,
                'precio_unitario_real': subtotal_linea_final / cant if cant > 0 else 0, 
                'subtotal_final': subtotal_linea_final,
                'promo_nombre': tipo_aplicado,
                'descuento_monto': mejor_descuento
            })
            total_neto += subtotal_linea_final

        descuento_global = 0
        nombre_promo_global = ""
        
        for prom in promos:
            if prom[2] == "Global" and prom[4] == "Volumen":
                umbral = prom[5]
                desc = prom[6]
                
                if total_neto >= umbral:
                    if desc > descuento_global:
                        descuento_global = desc
                        nombre_promo_global = prom[1]

        total_final = total_neto - descuento_global
        if total_final < 0: total_final = 0
        
        return {
            'items': items_procesados,
            'subtotal_bruto': subtotal_bruto,
            'descuento_global': descuento_global,
            'promo_global_nombre': nombre_promo_global,
            'total_final': total_final
        }

    # --- Auxiliares ---
    def obtener_categorias(self):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categorias")
        data = cursor.fetchall()
        conn.close()
        return data

    def ejecutar_consulta_reporte(self, tipo_reporte):
        conn = self.db.conectar()
        cursor = conn.cursor()
        columnas = []
        data = []
        
        if tipo_reporte == "Bajo Stock":
            cursor.execute("SELECT nombre, stock, stock_minimo FROM productos WHERE stock <= stock_minimo")
            columnas = ["Producto", "Stock Actual", "Mínimo"]
            data = cursor.fetchall()
            
        elif tipo_reporte == "Ventas del Dia":
            hoy = date.today().strftime("%Y-%m-%d")
            cursor.execute('''SELECT v.id, v.fecha, v.cliente_nombre, v.total, u.username 
                              FROM ventas v 
                              JOIN usuarios u ON v.usuario_id = u.id 
                              WHERE v.fecha LIKE ?''', (f"{hoy}%",))
            columnas = ["ID Venta", "Fecha", "Cliente", "Total", "Vendedor"]
            data = cursor.fetchall()
            
        elif tipo_reporte == "Top Productos":
            cursor.execute('''SELECT p.nombre, SUM(d.cantidad) as total_vendido 
                              FROM detalle_ventas d
                              JOIN productos p ON d.producto_id = p.id
                              GROUP BY p.id
                              ORDER BY total_vendido DESC LIMIT 5''')
            columnas = ["Producto", "Unidades Vendidas"]
            data = cursor.fetchall()

        conn.close()
        return columnas, data

# =============================================================================
# CAPA DE VISTA (INTERFAZ GRÁFICA)
# =============================================================================

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("Login - Mis Trapitos")
        self.root.geometry("300x250")
        self.controller = Controller()
        
        tk.Label(root, text="INICIAR SESIÓN", font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(root, text="Usuario:").pack()
        self.entry_user = tk.Entry(root)
        self.entry_user.pack()
        
        tk.Label(root, text="Contraseña:").pack()
        self.entry_pass = tk.Entry(root, show="*")
        self.entry_pass.pack()
        
        tk.Button(root, text="Ingresar", command=self.validar, bg="#4CAF50", fg="white").pack(pady=20)

    def validar(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        usuario = self.controller.login(user, pwd)
        if usuario:
            self.root.destroy()
            self.on_login_success(usuario)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

class VistaPrincipal:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = tk.Tk()
        self.root.title(f"Sistema Mis Trapitos - Usuario: {usuario[1]} ({usuario[3]})")
        self.root.state('zoomed')
        self.controller = Controller()
        
        self.crear_menu_lateral()
        self.crear_area_contenido()
        
        self.mostrar_inventario()
        self.root.mainloop()

    def crear_menu_lateral(self):
        self.frm_menu = tk.Frame(self.root, width=200, bg="#333")
        self.frm_menu.pack(side="left", fill="y")
        self.frm_menu.pack_propagate(False)
        
        lbl_logo = tk.Label(self.frm_menu, text="👗\nMis Trapitos", bg="#333", fg="white", font=("Arial", 16))
        lbl_logo.pack(pady=20)
        
        btns = [
            ("Inventario", self.mostrar_inventario),
            ("Punto de Venta", self.mostrar_pos),
            ("Clientes", self.mostrar_clientes)
        ]
        
        if self.usuario[3] == "Administrador":
            btns.append(("Promociones", self.mostrar_promociones))
            btns.append(("Reportes", self.mostrar_reportes))
            btns.append(("Importar Productos", self.importar_csv_productos))

        for txt, cmd in btns:
            tk.Button(self.frm_menu, text=txt, command=cmd, bg="#555", fg="white", bd=0, pady=10).pack(fill="x", pady=2)
            
        tk.Button(self.frm_menu, text="Salir", command=self.root.destroy, bg="#d9534f", fg="white").pack(side="bottom", fill="x", pady=10)

    def crear_area_contenido(self):
        self.content_area = tk.Frame(self.root, bg="#f4f4f4")
        self.content_area.pack(side="right", fill="both", expand=True)

    def limpiar_contenido(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ========================== VISTA: INVENTARIO ==========================
    def mostrar_inventario(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Gestión de Inventario", font=("Arial", 18)).pack(pady=10)
        
        frm_filtros = tk.Frame(self.content_area)
        frm_filtros.pack(fill="x", padx=20)
        
        tk.Label(frm_filtros, text="Buscar por Nombre:").pack(side="left")
        txt_filtro_nombre = tk.Entry(frm_filtros)
        txt_filtro_nombre.pack(side="left", padx=5)
        
        tk.Label(frm_filtros, text="Categoría:").pack(side="left", padx=10)
        cmb_filtro_cat = ttk.Combobox(frm_filtros, values=["Todas"] + [c[1] for c in self.controller.obtener_categorias()])
        cmb_filtro_cat.current(0)
        cmb_filtro_cat.pack(side="left")
        
        tk.Button(frm_filtros, text="Filtrar", command=lambda: cargar_datos()).pack(side="left", padx=10)
        
        cols = ("ID", "Nombre", "Talla", "Color", "Precio", "Stock", "Categoría", "Proveedor")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for col in cols: tree.heading(col, text=col)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        def cargar_datos():
            for i in tree.get_children(): tree.delete(i)
            
            filtros = {
                "nombre": txt_filtro_nombre.get(),
                "categoria": cmb_filtro_cat.get()
            }
            productos = self.controller.obtener_productos(filtros)
            
            for p in productos:
                try:
                    precio_val = float(p[4])
                    precio_formato = f"${precio_val:.2f}"
                except (ValueError, TypeError):
                    precio_formato = "$0.00"

                cat_nombre = p[9] if p[9] else "Sin Categoría"
                prov_nombre = p[10] if p[10] else "Sin Proveedor"

                tree.insert("", "end", values=(
                    p[0], p[1], p[5], p[6], precio_formato,
                    p[7], cat_nombre, prov_nombre
                ))
        
        cargar_datos()

    # ========================== VISTA: PUNTO DE VENTA (POS) ==========================
    def mostrar_pos(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Punto de Venta", font=("Arial", 18)).pack(pady=10)
        
        frm_principal = tk.Frame(self.content_area)
        frm_principal.pack(fill="both", expand=True, padx=10)
        
        # Izquierda: Productos
        frm_izq = tk.LabelFrame(frm_principal, text="Productos Disponibles")
        frm_izq.pack(side="left", fill="both", expand=True)
        
        frm_filtros_pos = tk.Frame(frm_izq)
        frm_filtros_pos.pack(fill="x", padx=5, pady=5)
        
        tk.Label(frm_filtros_pos, text="Nombre:").pack(side="left")
        txt_filtro_nombre = tk.Entry(frm_filtros_pos, width=15)
        txt_filtro_nombre.pack(side="left", padx=5)
        
        tk.Label(frm_filtros_pos, text="Cat:").pack(side="left", padx=5)
        cmb_filtro_cat = ttk.Combobox(frm_filtros_pos, values=["Todas"] + [c[1] for c in self.controller.obtener_categorias()], width=12)
        cmb_filtro_cat.current(0)
        cmb_filtro_cat.pack(side="left")
        
        cols_prod = ("ID", "Nombre", "Precio", "Stock")
        tree_prods = ttk.Treeview(frm_izq, columns=cols_prod, show="headings")
        for col in cols_prod: tree_prods.heading(col, text=col)
        
        tree_prods.column("ID", width=30)
        tree_prods.column("Nombre", width=120)
        tree_prods.column("Precio", width=60)
        tree_prods.column("Stock", width=40)
        tree_prods.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Derecha: Carrito
        frm_der = tk.LabelFrame(frm_principal, text="Carrito de Compras", width=500)
        frm_der.pack(side="right", fill="both", padx=10)
        
        cols_cart = ("Prod", "Cant", "P.Unit", "Desc", "Total")
        tree_cart = ttk.Treeview(frm_der, columns=cols_cart, show="headings", height=15)
        tree_cart.heading("Prod", text="Producto")
        tree_cart.heading("Cant", text="Cant")
        tree_cart.heading("P.Unit", text="$ Unit")
        tree_cart.heading("Desc", text="Promo")
        tree_cart.heading("Total", text="Total")
        
        tree_cart.column("Prod", width=120)
        tree_cart.column("Cant", width=40)
        tree_cart.column("P.Unit", width=60)
        tree_cart.column("Desc", width=80)
        tree_cart.column("Total", width=70)
        tree_cart.pack(fill="x")
        
        self.carrito_raw = [] 
        self.calculo_actual = None 
        
        self.lbl_subtotal = tk.Label(frm_der, text="Subtotal: $0.00", font=("Arial", 10), fg="gray")
        self.lbl_subtotal.pack(pady=2)
        
        self.lbl_desc_global = tk.Label(frm_der, text="Desc. Global: -$0.00", font=("Arial", 10), fg="green")
        self.lbl_desc_global.pack(pady=2)
        
        self.total_var = tk.StringVar(value="TOTAL A PAGAR: $0.00")
        tk.Label(frm_der, textvariable=self.total_var, font=("Arial", 16, "bold"), fg="blue").pack(pady=10)

        # Referencias visuales
        self.tree_pos_cart_ref = tree_cart
        self.lbl_subtotal_ref = self.lbl_subtotal
        self.lbl_desc_global_ref = self.lbl_desc_global
        self.total_var_ref = self.total_var

        # Logica de carga
        def cargar_prods_pos():
            for i in tree_prods.get_children(): tree_prods.delete(i)
            filtros = {"nombre": txt_filtro_nombre.get(), "categoria": cmb_filtro_cat.get()}
            productos = self.controller.obtener_productos(filtros)
            for p in productos:
                if p[7] > 0: tree_prods.insert("", "end", values=(p[0], p[1], p[4], p[7]))
        
        btn_buscar = tk.Button(frm_filtros_pos, text="🔍", command=cargar_prods_pos)
        btn_buscar.pack(side="left", padx=5)
        txt_filtro_nombre.bind("<Return>", lambda e: cargar_prods_pos())
        cmb_filtro_cat.bind("<<ComboboxSelected>>", lambda e: cargar_prods_pos())
        cargar_prods_pos()
        
        def agregar_al_carrito():
            sel = tree_prods.selection()
            if not sel: return
            item = tree_prods.item(sel[0])['values']
            pid, nombre, precio, stock = item[0], item[1], float(item[2]), int(item[3])
            
            prod_full = [p for p in self.controller.obtener_productos() if p[0] == pid][0]
            cat_id = prod_full[3]

            cant = simpledialog.askinteger("Cantidad", f"¿Cuántos {nombre} desea llevar?", minvalue=1, maxvalue=stock)
            if cant:
                self.carrito_raw.append({
                    'id': pid, 
                    'nombre': nombre, 
                    'cantidad': cant, 
                    'precio_base': precio, 
                    'cat_id': cat_id
                })
                actualizar_carrito()

        def actualizar_carrito():
            for i in tree_cart.get_children(): tree_cart.delete(i)
            res = self.controller.calcular_carrito_con_descuentos(self.carrito_raw)
            self.calculo_actual = res 
            
            for item in res['items']:
                promo_txt = item['promo_nombre'] if item['promo_nombre'] else "-"
                tree_cart.insert("", "end", values=(
                    item['nombre'], 
                    item['cantidad'], 
                    f"${item['precio_base']:.2f}",
                    promo_txt,
                    f"${item['subtotal_final']:.2f}"
                ))
            
            self.lbl_subtotal.config(text=f"Subtotal: ${res['subtotal_bruto']:.2f}")
            if res['descuento_global'] > 0:
                self.lbl_desc_global.config(text=f"Desc. Volumen ({res['promo_global_nombre']}): -${res['descuento_global']:.2f}")
            else:
                self.lbl_desc_global.config(text="")
                
            self.total_var.set(f"TOTAL: ${res['total_final']:.2f}")

        def finalizar_venta():
            if not self.carrito_raw: return
            self.popup_seleccionar_cliente()

        tk.Button(frm_izq, text="Agregar al Carrito >>", command=agregar_al_carrito, bg="#4CAF50", fg="white").pack(pady=5)
        tk.Button(frm_der, text="Cobrar / Finalizar", command=finalizar_venta, bg="#2196F3", fg="white", font=("Arial", 12)).pack(pady=20, fill="x")

    def popup_seleccionar_cliente(self):
        top = tk.Toplevel(self.root)
        top.title("Seleccionar Cliente")
        top.geometry("600x400")
        
        tk.Label(top, text="Buscar Cliente (ID o Nombre):").pack(pady=5)
        
        frm_search = tk.Frame(top)
        frm_search.pack(fill="x", padx=10)
        
        entry_search = tk.Entry(frm_search)
        entry_search.pack(side="left", fill="x", expand=True)
        
        cols = ("ID", "Nombre", "Email")
        tree_cli = ttk.Treeview(top, columns=cols, show="headings")
        tree_cli.heading("ID", text="ID"); tree_cli.column("ID", width=50)
        tree_cli.heading("Nombre", text="Nombre")
        tree_cli.heading("Email", text="Email")
        tree_cli.pack(fill="both", expand=True, padx=10, pady=5)
        
        def buscar_clientes(event=None):
            busqueda = entry_search.get()
            for i in tree_cli.get_children(): tree_cli.delete(i)
            clientes = self.controller.obtener_clientes(busqueda)
            for c in clientes:
                if len(c) == 5:
                    tree_cli.insert("", "end", values=(c[0], c[1], c[4]))
                else:
                    tree_cli.insert("", "end", values=(c[0], c[1], c[3]))
        
        btn_search = tk.Button(frm_search, text="Buscar", command=buscar_clientes)
        btn_search.pack(side="left", padx=5)
        entry_search.bind("<Return>", buscar_clientes)
        
        buscar_clientes()

        def confirmar_seleccion():
            sel = tree_cli.selection()
            if sel:
                item = tree_cli.item(sel[0])['values']
                # Guardamos ID y nombre
                cliente_id = item[0]
                cliente_nombre = f"{item[1]} (ID: {cliente_id})"
                procesar_pago(cliente_nombre, cliente_id)
                top.destroy()
            else:
                messagebox.showwarning("Aviso", "Seleccione un cliente de la lista")

        def publico_general():
            procesar_pago("Público General", None)
            top.destroy()

        def procesar_pago(nombre_cliente, cliente_id):
            try:
                # Actualizado para pasar cliente_id
                venta_id = self.controller.registrar_venta(
                    self.usuario[0], 
                    nombre_cliente, 
                    self.calculo_actual['items'], 
                    self.calculo_actual['total_final'],
                    cliente_id
                )
                messagebox.showinfo("Éxito", f"Venta #{venta_id} registrada con éxito para: {nombre_cliente}")
                self.carrito_raw = []
                self.calculo_actual = None
                
                # Recargar UI
                for i in self.tree_pos_cart_ref.get_children(): self.tree_pos_cart_ref.delete(i)
                self.lbl_subtotal_ref.config(text="Subtotal: $0.00")
                self.lbl_desc_global_ref.config(text="")
                self.total_var_ref.set("Total: $0.00")
                
                self.mostrar_pos()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))

        frm_btns = tk.Frame(top)
        frm_btns.pack(pady=10)
        
        tk.Button(frm_btns, text="Usar Público General", command=publico_general, bg="#777", fg="white").pack(side="left", padx=10)
        tk.Button(frm_btns, text="Seleccionar Cliente", command=confirmar_seleccion, bg="#2196F3", fg="white").pack(side="left", padx=10)

    # ========================== VISTA: PROMOCIONES ==========================
    def mostrar_promociones(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Gestión de Promociones", font=("Arial", 18)).pack(pady=10)
        
        frm_form = tk.LabelFrame(self.content_area, text="Nueva Promoción")
        frm_form.pack(fill="x", padx=20, pady=5)
        
        f1 = tk.Frame(frm_form); f1.pack(fill="x", pady=2)
        tk.Label(f1, text="Nombre Promo:").pack(side="left")
        entry_nom = tk.Entry(f1, width=20); entry_nom.pack(side="left", padx=5)
        
        tk.Label(f1, text="Inicio (YYYY-MM-DD):").pack(side="left")
        entry_ini = tk.Entry(f1, width=12); entry_ini.insert(0, date.today().strftime("%Y-%m-%d")); entry_ini.pack(side="left", padx=5)
        
        tk.Label(f1, text="Fin (YYYY-MM-DD):").pack(side="left")
        entry_fin = tk.Entry(f1, width=12); entry_fin.insert(0, "2025-12-31"); entry_fin.pack(side="left", padx=5)

        f2 = tk.Frame(frm_form); f2.pack(fill="x", pady=5)
        
        tk.Label(f2, text="Aplica a:").pack(side="left")
        cmb_tipo_ent = ttk.Combobox(f2, values=["Categoria", "Producto", "Global"], state="readonly", width=10)
        cmb_tipo_ent.current(0)
        cmb_tipo_ent.pack(side="left", padx=5)
        
        cmb_entidad = ttk.Combobox(f2, state="readonly", width=20)
        cmb_entidad.pack(side="left", padx=5)
        
        def actualizar_combo_entidad(event):
            tipo = cmb_tipo_ent.get()
            vals = []
            if tipo == "Categoria":
                vals = [f"{c[0]} - {c[1]}" for c in self.controller.obtener_categorias()]
                cmb_entidad.config(state="readonly")
            elif tipo == "Producto":
                vals = [f"{p[0]} - {p[1]}" for p in self.controller.obtener_productos()]
                cmb_entidad.config(state="readonly")
            else: 
                vals = ["Volumen de Compra Total"]
                cmb_entidad.current(0)
                cmb_entidad.config(state="disabled")
            
            cmb_entidad['values'] = vals
            if vals: cmb_entidad.current(0)
            
        cmb_tipo_ent.bind("<<ComboboxSelected>>", actualizar_combo_entidad)
        actualizar_combo_entidad(None) 
        
        tk.Label(f2, text="Tipo Desc:").pack(side="left")
        cmb_tipo_desc = ttk.Combobox(f2, values=["Porcentaje", "Monto Fijo", "NxM", "Volumen"], state="readonly", width=12)
        cmb_tipo_desc.current(0)
        cmb_tipo_desc.pack(side="left", padx=5)
        
        f3 = tk.Frame(frm_form); f3.pack(fill="x", pady=5)
        lbl_v1 = tk.Label(f3, text="Valor (% o Monto):")
        lbl_v1.pack(side="left")
        entry_v1 = tk.Entry(f3, width=10); entry_v1.pack(side="left", padx=5)
        
        lbl_v2 = tk.Label(f3, text="Valor 2 (opcional):")
        lbl_v2.pack(side="left")
        entry_v2 = tk.Entry(f3, width=10); entry_v2.pack(side="left", padx=5)
        
        def actualizar_labels_valores(event):
            t = cmb_tipo_desc.get()
            if t == "Porcentaje":
                lbl_v1.config(text="Porcentaje (%):"); lbl_v2.config(text="N/A"); entry_v2.config(state="disabled")
            elif t == "Monto Fijo":
                lbl_v1.config(text="Monto ($):"); lbl_v2.config(text="N/A"); entry_v2.config(state="disabled")
            elif t == "NxM":
                lbl_v1.config(text="Llevas (N):"); lbl_v2.config(text="Pagas (M):"); entry_v2.config(state="normal")
            elif t == "Volumen":
                lbl_v1.config(text="Si gastas más de:"); lbl_v2.config(text="Descuento ($):"); entry_v2.config(state="normal")
                cmb_tipo_ent.set("Global"); actualizar_combo_entidad(None)

        cmb_tipo_desc.bind("<<ComboboxSelected>>", actualizar_labels_valores)
        actualizar_labels_valores(None)

        def guardar_promo():
            try:
                nom = entry_nom.get()
                t_ent = cmb_tipo_ent.get()
                t_desc = cmb_tipo_desc.get()
                v1 = float(entry_v1.get())
                v2 = float(entry_v2.get()) if entry_v2.get() else 0.0
                ini = entry_ini.get()
                fin = entry_fin.get()
                
                ent_id = 0
                if t_ent != "Global":
                    sel = cmb_entidad.get()
                    if not sel: raise ValueError("Seleccione Categoria/Producto")
                    ent_id = int(sel.split(" - ")[0])
                
                self.controller.agregar_promocion(nom, t_ent, ent_id, t_desc, v1, v2, ini, fin)
                messagebox.showinfo("Éxito", "Promoción creada")
                cargar_lista_promos()
            except ValueError:
                messagebox.showerror("Error", "Revise los campos numéricos")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(frm_form, text="Guardar Regla", bg="#4CAF50", fg="white", command=guardar_promo).pack(pady=5)

        tree = ttk.Treeview(self.content_area, columns=("ID", "Nombre", "Regla", "Valores", "Vigencia"), show="headings")
        tree.heading("ID", text="ID"); tree.column("ID", width=30)
        tree.heading("Nombre", text="Nombre")
        tree.heading("Regla", text="Aplica a")
        tree.heading("Valores", text="Detalle")
        tree.heading("Vigencia", text="Fin")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        def eliminar_promo():
            sel = tree.selection()
            if not sel: return
            pid = tree.item(sel[0])['values'][0]
            if messagebox.askyesno("Confirmar", "¿Eliminar esta promoción?"):
                self.controller.eliminar_promocion(pid)
                cargar_lista_promos()

        tk.Button(self.content_area, text="Eliminar Seleccionada", bg="#d9534f", fg="white", command=eliminar_promo).pack(pady=5)

        def cargar_lista_promos():
            for i in tree.get_children(): tree.delete(i)
            promos = self.controller.obtener_todas_promociones()
            for p in promos:
                detalle = ""
                if p[4] == "Porcentaje": detalle = f"{p[5]}% Off"
                elif p[4] == "Monto Fijo": detalle = f"-${p[5]}"
                elif p[4] == "NxM": detalle = f"{int(p[5])}x{int(p[6])}"
                elif p[4] == "Volumen": detalle = f"Gastas > {p[5]} -> -${p[6]}"
                
                regla = f"{p[2]} (ID: {p[3]})" if p[2] != "Global" else "Global/Carrito"
                tree.insert("", "end", values=(p[0], p[1], regla, detalle, p[8]))
        
        cargar_lista_promos()

    # ========================== VISTA: CLIENTES ==========================
    def mostrar_clientes(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Directorio de Clientes", font=("Arial", 18)).pack(pady=10)
        
        frm_botones = tk.Frame(self.content_area)
        frm_botones.pack(fill="x", padx=20, pady=5)
        
        tk.Button(frm_botones, text="+ Nuevo Cliente", command=self.popup_nuevo_cliente, 
                  bg="#4CAF50", fg="white").pack(side="left", padx=5)

        # NUEVO BOTÓN DE HISTORIAL
        tk.Button(frm_botones, text="📜 Historial de Compras", command=self.popup_historial_cliente, 
                  bg="#2196F3", fg="white").pack(side="left", padx=5)
        
        if self.usuario[3] == "Administrador":
            tk.Button(frm_botones, text="Importar CSV Clientes", command=self.importar_csv_clientes, 
                      bg="#FF9800", fg="white").pack(side="left", padx=5)

        cols = ("ID", "Nombre", "Dirección", "Teléfono", "Email")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.column("ID", width=50)
        tree.column("Nombre", width=150)
        tree.column("Dirección", width=200)
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def load_cli():
            for i in tree.get_children(): tree.delete(i)
            for c in self.controller.obtener_clientes():
                if len(c) == 5:
                    tree.insert("", "end", values=(c[0], c[1], c[2], c[3], c[4]))
                else:
                    tree.insert("", "end", values=(c[0], c[1], "N/A", c[2], c[3]))
        load_cli()
        self.loader_clientes_func = load_cli

    # NUEVO: Popup para buscar cliente y ver historial
    def popup_historial_cliente(self):
        top = tk.Toplevel(self.root)
        top.title("Historial de Compras por Cliente")
        top.geometry("700x500")
        
        # --- SECCIÓN 1: BUSCADOR ---
        tk.Label(top, text="Buscar Cliente (ID o Nombre):").pack(pady=5)
        
        frm_search = tk.Frame(top)
        frm_search.pack(fill="x", padx=10)
        
        entry_search = tk.Entry(frm_search)
        entry_search.pack(side="left", fill="x", expand=True)
        
        # Tabla resultados de búsqueda
        cols = ("ID", "Nombre", "Email")
        tree_cli = ttk.Treeview(top, columns=cols, show="headings", height=5)
        tree_cli.heading("ID", text="ID"); tree_cli.column("ID", width=50)
        tree_cli.heading("Nombre", text="Nombre")
        tree_cli.heading("Email", text="Email")
        tree_cli.pack(fill="x", padx=10, pady=5)
        
        def buscar_clientes(event=None):
            busqueda = entry_search.get()
            for i in tree_cli.get_children(): tree_cli.delete(i)
            clientes = self.controller.obtener_clientes(busqueda)
            for c in clientes:
                if len(c) == 5:
                    tree_cli.insert("", "end", values=(c[0], c[1], c[4]))
                else:
                    tree_cli.insert("", "end", values=(c[0], c[1], c[3]))
        
        tk.Button(frm_search, text="Buscar", command=buscar_clientes).pack(side="left", padx=5)
        entry_search.bind("<Return>", buscar_clientes)
        
        # --- SECCIÓN 2: HISTORIAL DE VENTAS ---
        lbl_historial = tk.Label(top, text="Historial de Ventas:", font=("Arial", 12, "bold"))
        lbl_historial.pack(pady=10)
        
        # Tabla de Ventas
        cols_v = ("ID Venta", "Fecha", "Total", "Vendedor")
        tree_ventas = ttk.Treeview(top, columns=cols_v, show="headings", height=6)
        for c in cols_v: tree_ventas.heading(c, text=c)
        tree_ventas.pack(fill="x", padx=10)

        # --- SECCIÓN 3: DETALLE DE PRODUCTOS ---
        lbl_detalle = tk.Label(top, text="Detalle de Productos (Selecciona una venta):", font=("Arial", 10))
        lbl_detalle.pack(pady=5)
        
        cols_d = ("Producto", "Cant", "P.Unit", "Subtotal")
        tree_det = ttk.Treeview(top, columns=cols_d, show="headings", height=6)
        for c in cols_d: tree_det.heading(c, text=c)
        tree_det.pack(fill="both", expand=True, padx=10, pady=5)

        def mostrar_historial_seleccionado(event):
            sel = tree_cli.selection()
            if not sel: return
            item = tree_cli.item(sel[0])['values']
            cliente_id = item[0]
            cliente_nom = item[1]
            
            lbl_historial.config(text=f"Historial de: {cliente_nom}")
            
            # Limpiar tablas inferiores
            for i in tree_ventas.get_children(): tree_ventas.delete(i)
            for i in tree_det.get_children(): tree_det.delete(i)
            
            # Cargar ventas
            ventas = self.controller.obtener_ventas_por_cliente(cliente_id)
            if not ventas:
                messagebox.showinfo("Info", "Este cliente no tiene compras registradas.")
            
            for v in ventas:
                tree_ventas.insert("", "end", values=(v[0], v[1], f"${v[2]:.2f}", v[3]))

        def mostrar_detalle_venta(event):
            sel = tree_ventas.selection()
            if not sel: return
            item = tree_ventas.item(sel[0])['values']
            venta_id = item[0]
            
            # Limpiar detalle
            for i in tree_det.get_children(): tree_det.delete(i)
            
            # Cargar productos
            detalles = self.controller.obtener_detalle_venta(venta_id)
            for d in detalles:
                tree_det.insert("", "end", values=(d[0], d[1], f"${d[2]:.2f}", f"${d[3]:.2f}"))

        # Bindings
        tree_cli.bind("<<TreeviewSelect>>", mostrar_historial_seleccionado)
        tree_ventas.bind("<<TreeviewSelect>>", mostrar_detalle_venta)
        
        buscar_clientes() # Carga inicial todos

    def popup_nuevo_cliente(self):
        top = tk.Toplevel(self.root)
        top.title("Registrar Nuevo Cliente")
        top.geometry("400x300")
        
        tk.Label(top, text="Nombre Completo:").pack(pady=5)
        entry_nombre = tk.Entry(top, width=40)
        entry_nombre.pack()
        
        tk.Label(top, text="Dirección:").pack(pady=5)
        entry_dir = tk.Entry(top, width=40)
        entry_dir.pack()
        
        tk.Label(top, text="Teléfono:").pack(pady=5)
        entry_tel = tk.Entry(top, width=40)
        entry_tel.pack()
        
        tk.Label(top, text="Email:").pack(pady=5)
        entry_email = tk.Entry(top, width=40)
        entry_email.pack()
        
        def guardar():
            nom = entry_nombre.get()
            dire = entry_dir.get()
            tel = entry_tel.get()
            mail = entry_email.get()
            
            if nom:
                self.controller.agregar_cliente(nom, dire, tel, mail)
                messagebox.showinfo("Éxito", "Cliente registrado")
                top.destroy()
                self.loader_clientes_func()
            else:
                messagebox.showwarning("Faltan datos", "El nombre es obligatorio")
        
        tk.Button(top, text="Guardar Cliente", command=guardar, bg="#2196F3", fg="white").pack(pady=20)

    def importar_csv_clientes(self):
        archivo_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not archivo_path:
            return

        try:
            with open(archivo_path, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                count = 0
                for row in reader:
                    nom = row.get("Nombre", "Cliente Importado")
                    dire = row.get("Direccion", "")
                    tel = row.get("Telefono", "")
                    mail = row.get("Email", "")
                    self.controller.agregar_cliente(nom, dire, tel, mail)
                    count += 1
            messagebox.showinfo("Éxito", f"Se importaron {count} clientes.")
            self.loader_clientes_func()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar CSV Clientes: {e}")

    # ========================== VISTA: REPORTES ==========================
    def mostrar_reportes(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Reportes Gerenciales", font=("Arial", 18)).pack(pady=10)
        
        frm_btns = tk.Frame(self.content_area)
        frm_btns.pack()
        
        tree = ttk.Treeview(self.content_area, show="headings")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def ver(tipo):
            cols, data = self.controller.ejecutar_consulta_reporte(tipo)
            for i in tree.get_children(): tree.delete(i)
            tree["columns"] = cols
            for c in cols: tree.heading(c, text=c)
            for d in data: tree.insert("", "end", values=d)

        ttk.Button(frm_btns, text="Productos Bajo Stock", command=lambda: ver("Bajo Stock")).pack(side="left", padx=10)
        ttk.Button(frm_btns, text="Ventas del Día", command=lambda: ver("Ventas del Dia")).pack(side="left", padx=10)
        ttk.Button(frm_btns, text="Más Vendidos", command=lambda: ver("Top Productos")).pack(side="left", padx=10)

    def importar_csv_productos(self):
        archivo_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not archivo_path:
            return

        try:
            with open(archivo_path, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                for row in reader:
                    self.controller.agregar_producto(
                        row["Nombre"],
                        row["Descripcion"],
                        int(row["CategoriaID"]),
                        float(row["Precio"]),
                        row["Talla"],
                        row["Color"],
                        int(row["Stock"]),
                        int(row["ProveedorID"])
                    )
            messagebox.showinfo("Éxito", "Carga masiva de productos completada.")
            self.mostrar_inventario()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar CSV: {e}")

if __name__ == "__main__":
    def iniciar_app(usuario):
        VistaPrincipal(usuario)

    root_login = tk.Tk()
    app = LoginWindow(root_login, iniciar_app)
    root_login.mainloop()