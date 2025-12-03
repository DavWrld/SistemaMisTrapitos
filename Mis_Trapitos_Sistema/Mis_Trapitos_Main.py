import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import csv
from datetime import datetime, date, timedelta

# IMPORTAMOS EL MODULO DE ESTILOS
import estilos

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
                            direccion TEXT,
                            categoria_suministro TEXT)''')

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

        cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fecha TEXT NOT NULL,
                            cliente_nombre TEXT,
                            total REAL,
                            usuario_id INTEGER,
                            cliente_id INTEGER,
                            metodo_pago TEXT, 
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
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS suministros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fecha TEXT NOT NULL,
                            proveedor_id INTEGER,
                            nombre_producto TEXT,
                            categoria_id INTEGER,
                            cantidad INTEGER,
                            precio REAL,
                            FOREIGN KEY(proveedor_id) REFERENCES proveedores(id),
                            FOREIGN KEY(categoria_id) REFERENCES categorias(id))''')

        conn.commit()
        conn.close()

    def actualizar_schema(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        try: cursor.execute("SELECT direccion FROM clientes LIMIT 1")
        except: cursor.execute("ALTER TABLE clientes ADD COLUMN direccion TEXT"); conn.commit()
            
        try: cursor.execute("SELECT cliente_id FROM ventas LIMIT 1")
        except: cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER"); conn.commit()

        try: cursor.execute("SELECT metodo_pago FROM ventas LIMIT 1")
        except: cursor.execute("ALTER TABLE ventas ADD COLUMN metodo_pago TEXT"); conn.commit()

        try: cursor.execute("SELECT categoria_suministro FROM proveedores LIMIT 1")
        except: 
            cursor.execute("ALTER TABLE proveedores ADD COLUMN categoria_suministro TEXT")
            cursor.execute("UPDATE proveedores SET categoria_suministro = 'General' WHERE categoria_suministro IS NULL")
            conn.commit()
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS suministros (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fecha TEXT NOT NULL,
                            proveedor_id INTEGER,
                            nombre_producto TEXT,
                            categoria_id INTEGER,
                            cantidad INTEGER,
                            precio REAL,
                            FOREIGN KEY(proveedor_id) REFERENCES proveedores(id),
                            FOREIGN KEY(categoria_id) REFERENCES categorias(id))''')
        
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

        categorias = ['Camisetas', 'Pantalones', 'Accesorios', 'Calzado', 'Vestidos']
        for cat in categorias:
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (cat,))
        
        cursor.execute("SELECT * FROM proveedores")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO proveedores (nombre, contacto, telefono, categoria_suministro) VALUES (?,?,?,?)",
                           ("Proveedor General", "Juan Perez", "555-0000", "General"))

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

    # --- Productos & Suministros ---
    def agregar_producto(self, nombre, desc, cat_id, precio, talla, color, stock, prov_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, stock FROM productos WHERE nombre=? AND talla=? AND color=? AND proveedor_id=?", 
                       (nombre, talla, color, prov_id))
        producto_existente = cursor.fetchone()
        
        if producto_existente:
            prod_id = producto_existente[0]
            nuevo_stock = producto_existente[1] + stock
            cursor.execute("UPDATE productos SET stock = ?, precio = ? WHERE id = ?", (nuevo_stock, precio, prod_id))
        else:
            cursor.execute('''INSERT INTO productos (nombre, descripcion, categoria_id, precio, talla, color, stock, proveedor_id)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                              (nombre, desc, cat_id, precio, talla, color, stock, prov_id))
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''INSERT INTO suministros (fecha, proveedor_id, nombre_producto, categoria_id, cantidad, precio)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (fecha_actual, prov_id, nombre, cat_id, stock, precio))
        
        conn.commit()
        conn.close()

    def reabastecer_producto(self, prod_id, cantidad, precio_nuevo):
        conn = self.db.conectar()
        cursor = conn.cursor()
        
        cursor.execute("SELECT nombre, categoria_id, stock, proveedor_id FROM productos WHERE id=?", (prod_id,))
        prod = cursor.fetchone()
        if not prod: return
        
        nombre, cat_id, stock_actual, prov_id = prod
        
        nuevo_stock = stock_actual + cantidad
        cursor.execute("UPDATE productos SET stock = ?, precio = ? WHERE id = ?", (nuevo_stock, precio_nuevo, prod_id))
        
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''INSERT INTO suministros (fecha, proveedor_id, nombre_producto, categoria_id, cantidad, precio)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                          (fecha_actual, prov_id, nombre, cat_id, cantidad, precio_nuevo))
        
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
            if filtro.get('proveedor_id'):
                query += " AND p.proveedor_id = ?"
                params.append(filtro['proveedor_id'])
            if filtro.get('proveedor') and filtro['proveedor'] != "Todos":
                query += " AND pr.nombre = ?"
                params.append(filtro['proveedor'])
        
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data
    
    # NUEVO: Eliminar Producto
    def eliminar_producto(self, prod_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
            conn.commit()
            filas_afectadas = cursor.rowcount
            conn.close()
            return filas_afectadas > 0
        except sqlite3.Error:
            conn.close()
            return False

    def obtener_historial_suministros(self, proveedor_id, filtro_texto=None):
        conn = self.db.conectar()
        cursor = conn.cursor()
        query = '''SELECT s.id, s.fecha, s.nombre_producto, c.nombre, s.cantidad, s.precio
                   FROM suministros s
                   LEFT JOIN categorias c ON s.categoria_id = c.id
                   WHERE s.proveedor_id = ?'''
        params = [proveedor_id]
        
        if filtro_texto:
            query += " AND (s.fecha LIKE ? OR s.nombre_producto LIKE ?)"
            params.append(f"%{filtro_texto}%")
            params.append(f"%{filtro_texto}%")
            
        query += " ORDER BY s.fecha DESC"
        
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    # --- Ventas ---
    def registrar_venta(self, usuario_id, cliente_nombre, items_venta, total_final, cliente_id=None, metodo_pago="Efectivo"):
        conn = self.db.conectar()
        cursor = conn.cursor()
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''INSERT INTO ventas (fecha, cliente_nombre, total, usuario_id, cliente_id, metodo_pago) 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (fecha, cliente_nombre, total_final, usuario_id, cliente_id, metodo_pago))
        venta_id = cursor.lastrowid
        
        for item in items_venta:
            cursor.execute('''INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                              VALUES (?, ?, ?, ?, ?)''',
                              (venta_id, item['id'], item['cantidad'], item['precio_unitario_real'], item['subtotal_final']))
            cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['id']))
            
        conn.commit()
        conn.close()
        return venta_id

    def obtener_ventas_por_cliente(self, cliente_id):
        conn = self.db.conectar()
        cursor = conn.cursor()
        query = '''SELECT v.id, v.fecha, v.total, u.username, v.metodo_pago
                   FROM ventas v
                   LEFT JOIN usuarios u ON v.usuario_id = u.id
                   WHERE v.cliente_id = ?
                   ORDER BY v.fecha DESC'''
        cursor.execute(query, (cliente_id,))
        data = cursor.fetchall()
        conn.close()
        return data

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

    # --- REPORTES AVANZADOS ---
    def obtener_reporte_ventas(self, dias=None, metodo=None):
        conn = self.db.conectar()
        cursor = conn.cursor()
        query = '''SELECT v.id, v.fecha, v.cliente_nombre, u.username, v.total, v.metodo_pago 
                   FROM ventas v 
                   LEFT JOIN usuarios u ON v.usuario_id = u.id 
                   WHERE 1=1'''
        params = []
        
        if dias and dias != "Todos":
            try:
                dias_int = int(dias)
                fecha_limite = (datetime.now() - timedelta(days=dias_int)).strftime("%Y-%m-%d")
                query += " AND v.fecha >= ?"
                params.append(fecha_limite)
            except ValueError: pass
            
        if metodo and metodo != "Todos":
            query += " AND v.metodo_pago = ?"
            params.append(metodo)
            
        query += " ORDER BY v.fecha DESC"
        
        cursor.execute(query, params)
        data = cursor.fetchall()
        conn.close()
        return data

    def ejecutar_consulta_reporte(self, tipo_reporte, dias=None, categoria=None):
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
            subquery_sales = """
                SELECT SUM(d.cantidad) 
                FROM detalle_ventas d 
                JOIN ventas v ON d.venta_id = v.id 
                WHERE d.producto_id = p.id
            """
            params = []
            
            if dias and dias != "Total":
                try:
                    dias_int = int(dias)
                    fecha_limite = (datetime.now() - timedelta(days=dias_int)).strftime("%Y-%m-%d")
                    subquery_sales += " AND v.fecha >= ?"
                    params.append(fecha_limite)
                except ValueError: pass
            
            query = f'''
                SELECT p.nombre, 
                       COALESCE(({subquery_sales}), 0) as total_vendido
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                WHERE 1=1
            '''
            
            if categoria and categoria != "Todas":
                query += " AND c.nombre = ?"
                params.append(categoria)
                
            query += " ORDER BY total_vendido DESC"
            
            cursor.execute(query, params)
            columnas = ["Producto", "Unidades Vendidas"]
            data = cursor.fetchall()

        conn.close()
        return columnas, data

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

    # --- Proveedores ---
    def agregar_proveedor(self, nombre, direccion, telefono, email, contacto="N/A", categoria_suministro="General"):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO proveedores (nombre, direccion, telefono, email, contacto, categoria_suministro) 
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (nombre, direccion, telefono, email, contacto, categoria_suministro))
        conn.commit()
        conn.close()

    def obtener_proveedores(self):
        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proveedores")
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
        
        # Inicializar estilo
        self.style = estilos.configurar_estilo()
        
        self.crear_menu_lateral()
        self.crear_area_contenido()
        
        self.mostrar_inventario()
        self.root.mainloop()

    def crear_menu_lateral(self):
        self.frm_menu = tk.Frame(self.root, width=200, bg=estilos.COLOR_SIDEBAR)
        self.frm_menu.pack(side="left", fill="y")
        self.frm_menu.pack_propagate(False)
        
        lbl_logo = tk.Label(self.frm_menu, text="👗\nMis Trapitos", bg=estilos.COLOR_SIDEBAR, fg="white", font=("Arial", 16))
        lbl_logo.pack(pady=20)
        
        btns = [
            ("Inventario", self.mostrar_inventario),
            ("Punto de Venta", self.mostrar_pos),
            ("Clientes", self.mostrar_clientes)
        ]
        
        if self.usuario[3] == "Administrador":
            btns.append(("Proveedores", self.mostrar_proveedores))
            btns.append(("Promociones", self.mostrar_promociones))
            btns.append(("Reportes", self.mostrar_reportes))
            btns.append(("Importar Productos", self.importar_csv_productos))

        for txt, cmd in btns:
            btn = tk.Button(self.frm_menu, text=txt, command=cmd)
            estilos.style_button_sidebar(btn)
            btn.pack(fill="x", pady=2)
            
        btn_salir = tk.Button(self.frm_menu, text="Salir", command=self.root.destroy)
        estilos.style_button_danger(btn_salir)
        btn_salir.pack(side="bottom", fill="x", pady=10)

    def crear_area_contenido(self):
        self.content_area = tk.Frame(self.root, bg=estilos.COLOR_FONDO_APP)
        self.content_area.pack(side="right", fill="both", expand=True)

    def limpiar_contenido(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    # ========================== VISTA: INVENTARIO ==========================
    def mostrar_inventario(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Gestión de Inventario", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        # 1. Filtros
        frm_filtros = tk.Frame(self.content_area, bg=estilos.COLOR_FONDO_APP)
        frm_filtros.pack(fill="x", padx=20)
        
        # Filtro Nombre
        tk.Label(frm_filtros, text="Nombre:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        txt_filtro_nombre = tk.Entry(frm_filtros)
        txt_filtro_nombre.pack(side="left", padx=5)
        
        # Filtro Categoría
        tk.Label(frm_filtros, text="Categoría:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
        cmb_filtro_cat = ttk.Combobox(frm_filtros, values=["Todas"] + [c[1] for c in self.controller.obtener_categorias()])
        cmb_filtro_cat.current(0)
        cmb_filtro_cat.pack(side="left")

        # Filtro Proveedor
        tk.Label(frm_filtros, text="Proveedor:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
        provs = [p[1] for p in self.controller.obtener_proveedores()]
        cmb_filtro_prov = ttk.Combobox(frm_filtros, values=["Todos"] + provs)
        cmb_filtro_prov.current(0)
        cmb_filtro_prov.pack(side="left")
        
        btn_filtrar = tk.Button(frm_filtros, text="Filtrar", command=lambda: cargar_datos())
        estilos.style_button_primary(btn_filtrar)
        btn_filtrar.pack(side="left", padx=10)
        
        # --- NUEVO: Botón Eliminar ---
        def eliminar_seleccionado():
            seleccion = tree.selection()
            if not seleccion:
                messagebox.showwarning("Aviso", "Selecciona un producto para eliminar.")
                return
            
            item = tree.item(seleccion[0])
            prod_id = item['values'][0]
            prod_nombre = item['values'][1]
            
            confirmar = messagebox.askyesno("Confirmar Eliminación", 
                                          f"¿Estás seguro de que deseas eliminar el producto:\n'{prod_nombre}'?\n\nEsta acción no se puede deshacer.",
                                          icon='warning')
            if confirmar:
                try:
                    if self.controller.eliminar_producto(prod_id):
                        messagebox.showinfo("Éxito", "Producto eliminado correctamente.")
                        cargar_datos()
                    else:
                        messagebox.showerror("Error", "No se pudo eliminar el producto.")
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error al eliminar: {e}")

        btn_eliminar = tk.Button(frm_filtros, text="🗑️ Eliminar", command=eliminar_seleccionado)
        estilos.style_button_danger(btn_eliminar)
        btn_eliminar.pack(side="right", padx=10)

        # 2. Etiqueta TOTAL abajo
        self.lbl_total_stock = tk.Label(self.content_area, text="Total Existencias: 0", font=("Arial", 12, "bold"), fg="green", bg=estilos.COLOR_FONDO_APP)
        self.lbl_total_stock.pack(side="bottom", pady=10)

        # 3. Tabla
        cols = ("ID", "Nombre", "Talla", "Color", "Precio", "Stock", "Categoría", "Proveedor")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        tree.pack(side="top", fill="both", expand=True, padx=20, pady=10)
        
        self.orden_actual = {"col": "ID", "reverse": False} 

        def ordenar(col):
            if self.orden_actual["col"] == col:
                self.orden_actual["reverse"] = not self.orden_actual["reverse"]
            else:
                self.orden_actual["col"] = col
                self.orden_actual["reverse"] = False
            
            for c in cols:
                tree.heading(c, text=c, command=lambda _col=c: ordenar(_col) if _col in ["ID", "Precio", "Stock"] else None)
            
            flecha = " ▼" if self.orden_actual["reverse"] else " ▲"
            tree.heading(col, text=col + flecha, command=lambda: ordenar(col))
            
            cargar_datos()

        for col in cols:
            if col in ["ID", "Precio", "Stock"]:
                tree.heading(col, text=col, command=lambda c=col: ordenar(c))
            else:
                tree.heading(col, text=col)

        def cargar_datos():
            for i in tree.get_children(): tree.delete(i)
            
            filtros = {
                "nombre": txt_filtro_nombre.get(),
                "categoria": cmb_filtro_cat.get(),
                "proveedor": cmb_filtro_prov.get() 
            }
            productos = list(self.controller.obtener_productos(filtros))
            
            total_stock_visible = sum(p[7] for p in productos)
            self.lbl_total_stock.config(text=f"Total Existencias: {total_stock_visible}")
            
            col_orden = self.orden_actual["col"]
            reverso = self.orden_actual["reverse"]
            
            if col_orden == "ID":
                productos.sort(key=lambda x: x[0], reverse=reverso)
            elif col_orden == "Precio":
                productos.sort(key=lambda x: float(x[4]), reverse=reverso)
            elif col_orden == "Stock":
                productos.sort(key=lambda x: int(x[7]), reverse=reverso)
            
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
        tk.Label(self.content_area, text="Punto de Venta", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        frm_principal = tk.Frame(self.content_area, bg=estilos.COLOR_FONDO_APP)
        frm_principal.pack(fill="both", expand=True, padx=10)
        
        # Izquierda: Productos
        frm_izq = tk.LabelFrame(frm_principal, text="Productos Disponibles", bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
        frm_izq.pack(side="left", fill="both", expand=True)
        
        frm_filtros_pos = tk.Frame(frm_izq, bg=estilos.COLOR_FONDO_APP)
        frm_filtros_pos.pack(fill="x", padx=5, pady=5)
        
        tk.Label(frm_filtros_pos, text="Nombre:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        txt_filtro_nombre = tk.Entry(frm_filtros_pos, width=15)
        txt_filtro_nombre.pack(side="left", padx=5)
        
        tk.Label(frm_filtros_pos, text="Cat:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
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
        frm_der = tk.LabelFrame(frm_principal, text="Carrito de Compras", width=500, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
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
        
        self.lbl_subtotal = tk.Label(frm_der, text="Subtotal: $0.00", font=("Arial", 10), fg="gray", bg=estilos.COLOR_FONDO_APP)
        self.lbl_subtotal.pack(pady=2)
        
        self.lbl_desc_global = tk.Label(frm_der, text="Desc. Global: -$0.00", font=("Arial", 10), fg="green", bg=estilos.COLOR_FONDO_APP)
        self.lbl_desc_global.pack(pady=2)
        
        self.total_var = tk.StringVar(value="TOTAL A PAGAR: $0.00")
        tk.Label(frm_der, textvariable=self.total_var, font=("Arial", 16, "bold"), fg=estilos.COLOR_PRIMARY, bg=estilos.COLOR_FONDO_APP).pack(pady=10)

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
        estilos.style_button_primary(btn_buscar)
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

        btn_add = tk.Button(frm_izq, text="Agregar al Carrito >>", command=agregar_al_carrito)
        estilos.style_button_success(btn_add)
        btn_add.pack(pady=5)

        btn_cobrar = tk.Button(frm_der, text="Cobrar / Finalizar", command=finalizar_venta)
        estilos.style_button_primary(btn_cobrar)
        btn_cobrar.pack(pady=20, fill="x")

    def popup_seleccionar_cliente(self):
        top = tk.Toplevel(self.root)
        top.title("Seleccionar Cliente")
        top.geometry("600x400")
        top.configure(bg=estilos.COLOR_FONDO_APP)
        
        tk.Label(top, text="Buscar Cliente (ID o Nombre):", bg=estilos.COLOR_FONDO_APP).pack(pady=5)
        
        frm_search = tk.Frame(top, bg=estilos.COLOR_FONDO_APP)
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
        estilos.style_button_primary(btn_search)
        btn_search.pack(side="left", padx=5)
        entry_search.bind("<Return>", buscar_clientes)
        
        buscar_clientes()

        def confirmar_seleccion():
            sel = tree_cli.selection()
            if sel:
                item = tree_cli.item(sel[0])['values']
                cliente_id = item[0]
                cliente_nombre = f"{item[1]} (ID: {cliente_id})"
                self.popup_metodo_pago(top, cliente_nombre, cliente_id)
            else:
                messagebox.showwarning("Aviso", "Seleccione un cliente de la lista")

        def publico_general():
            self.popup_metodo_pago(top, "Público General", None)

        frm_btns = tk.Frame(top, bg=estilos.COLOR_FONDO_APP)
        frm_btns.pack(pady=10)
        
        btn_pg = tk.Button(frm_btns, text="Usar Público General", command=publico_general)
        estilos.style_button_warning(btn_pg)
        btn_pg.pack(side="left", padx=10)
        
        btn_sel = tk.Button(frm_btns, text="Seleccionar Cliente", command=confirmar_seleccion)
        estilos.style_button_success(btn_sel)
        btn_sel.pack(side="left", padx=10)

    # NUEVO: Popup para método de pago CON TRANSFERENCIA
    def popup_metodo_pago(self, parent_window, nombre_cliente, cliente_id):
        win_pago = tk.Toplevel(self.root)
        win_pago.title("Método de Pago")
        win_pago.geometry("350x300")
        win_pago.configure(bg=estilos.COLOR_FONDO_APP)
        
        tk.Label(win_pago, text=f"Cliente: {nombre_cliente}", font=("Arial", 10), bg=estilos.COLOR_FONDO_APP).pack(pady=10)
        tk.Label(win_pago, text=f"Total: {self.total_var.get()}", font=("Arial", 12, "bold"), bg=estilos.COLOR_FONDO_APP).pack(pady=5)
        
        def pagar(metodo):
            try:
                venta_id = self.controller.registrar_venta(
                    self.usuario[0], 
                    nombre_cliente, 
                    self.calculo_actual['items'], 
                    self.calculo_actual['total_final'],
                    cliente_id,
                    metodo 
                )
                messagebox.showinfo("Éxito", f"Venta #{venta_id} registrada ({metodo})")
                
                # Limpieza
                self.carrito_raw = []
                self.calculo_actual = None
                
                for i in self.tree_pos_cart_ref.get_children(): self.tree_pos_cart_ref.delete(i)
                self.lbl_subtotal_ref.config(text="Subtotal: $0.00")
                self.lbl_desc_global_ref.config(text="")
                self.total_var_ref.set("Total: $0.00")
                
                self.mostrar_pos() 
                
                win_pago.destroy()
                parent_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        btn_efectivo = tk.Button(win_pago, text="💵 Efectivo", command=lambda: pagar("Efectivo"), width=20)
        estilos.style_button_success(btn_efectivo)
        btn_efectivo.pack(pady=5)
        
        btn_tarjeta = tk.Button(win_pago, text="💳 Tarjeta", command=lambda: pagar("Tarjeta"), width=20)
        estilos.style_button_primary(btn_tarjeta)
        btn_tarjeta.pack(pady=5)

        # NUEVO BOTÓN
        btn_transf = tk.Button(win_pago, text="🏦 Transferencia", command=lambda: pagar("Transferencia"), width=20)
        estilos.style_button_primary(btn_transf) # Usamos primary o podemos crear uno nuevo
        btn_transf.configure(bg="#9C27B0") # Override color purpura
        btn_transf.pack(pady=5)

    # ========================== VISTA: PROMOCIONES ==========================
    def mostrar_promociones(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Gestión de Promociones", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        frm_form = tk.LabelFrame(self.content_area, text="Nueva Promoción", bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
        frm_form.pack(fill="x", padx=20, pady=5)
        
        f1 = tk.Frame(frm_form, bg=estilos.COLOR_FONDO_APP); f1.pack(fill="x", pady=2)
        tk.Label(f1, text="Nombre Promo:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        entry_nom = tk.Entry(f1, width=20); entry_nom.pack(side="left", padx=5)
        
        tk.Label(f1, text="Inicio (YYYY-MM-DD):", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        entry_ini = tk.Entry(f1, width=12); entry_ini.insert(0, date.today().strftime("%Y-%m-%d")); entry_ini.pack(side="left", padx=5)
        
        tk.Label(f1, text="Fin (YYYY-MM-DD):", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        entry_fin = tk.Entry(f1, width=12); entry_fin.insert(0, "2025-12-31"); entry_fin.pack(side="left", padx=5)

        f2 = tk.Frame(frm_form, bg=estilos.COLOR_FONDO_APP); f2.pack(fill="x", pady=5)
        
        tk.Label(f2, text="Aplica a:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
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
        
        tk.Label(f2, text="Tipo Desc:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        cmb_tipo_desc = ttk.Combobox(f2, values=["Porcentaje", "Monto Fijo", "NxM", "Volumen"], state="readonly", width=12)
        cmb_tipo_desc.current(0)
        cmb_tipo_desc.pack(side="left", padx=5)
        
        f3 = tk.Frame(frm_form, bg=estilos.COLOR_FONDO_APP); f3.pack(fill="x", pady=5)
        lbl_v1 = tk.Label(f3, text="Valor (% o Monto):", bg=estilos.COLOR_FONDO_APP)
        lbl_v1.pack(side="left")
        entry_v1 = tk.Entry(f3, width=10); entry_v1.pack(side="left", padx=5)
        
        lbl_v2 = tk.Label(f3, text="Valor 2 (opcional):", bg=estilos.COLOR_FONDO_APP)
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

        btn_guardar = tk.Button(frm_form, text="Guardar Regla", command=guardar_promo)
        estilos.style_button_success(btn_guardar)
        btn_guardar.pack(pady=5)

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

        btn_eliminar = tk.Button(self.content_area, text="Eliminar Seleccionada", command=eliminar_promo)
        estilos.style_button_danger(btn_eliminar)
        btn_eliminar.pack(pady=5)

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
        tk.Label(self.content_area, text="Directorio de Clientes", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        frm_botones = tk.Frame(self.content_area, bg=estilos.COLOR_FONDO_APP)
        frm_botones.pack(fill="x", padx=20, pady=5)
        
        btn_new = tk.Button(frm_botones, text="+ Nuevo Cliente", command=self.popup_nuevo_cliente)
        estilos.style_button_success(btn_new)
        btn_new.pack(side="left", padx=5)

        btn_hist = tk.Button(frm_botones, text="📜 Historial de Compras", command=self.popup_historial_cliente)
        estilos.style_button_primary(btn_hist)
        btn_hist.pack(side="left", padx=5)
        
        if self.usuario[3] == "Administrador":
            btn_imp = tk.Button(frm_botones, text="Importar CSV Clientes", command=self.importar_csv_clientes)
            estilos.style_button_warning(btn_imp)
            btn_imp.pack(side="left", padx=5)

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

    def popup_historial_cliente(self):
        top = tk.Toplevel(self.root)
        top.title("Historial de Compras por Cliente")
        top.geometry("700x500")
        top.configure(bg=estilos.COLOR_FONDO_APP)
        
        tk.Label(top, text="Buscar Cliente (ID o Nombre):", bg=estilos.COLOR_FONDO_APP).pack(pady=5)
        
        frm_search = tk.Frame(top, bg=estilos.COLOR_FONDO_APP)
        frm_search.pack(fill="x", padx=10)
        
        entry_search = tk.Entry(frm_search)
        entry_search.pack(side="left", fill="x", expand=True)
        
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
        
        btn_search = tk.Button(frm_search, text="Buscar", command=buscar_clientes)
        estilos.style_button_primary(btn_search)
        btn_search.pack(side="left", padx=5)
        entry_search.bind("<Return>", buscar_clientes)
        
        lbl_historial = tk.Label(top, text="Historial de Ventas:", font=("Arial", 12, "bold"), bg=estilos.COLOR_FONDO_APP)
        lbl_historial.pack(pady=10)
        
        cols_v = ("ID Venta", "Fecha", "Total", "Vendedor", "Método")
        tree_ventas = ttk.Treeview(top, columns=cols_v, show="headings", height=6)
        for c in cols_v: tree_ventas.heading(c, text=c)
        tree_ventas.pack(fill="x", padx=10)

        lbl_detalle = tk.Label(top, text="Detalle de Productos (Selecciona una venta):", font=("Arial", 10), bg=estilos.COLOR_FONDO_APP)
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
            
            for i in tree_ventas.get_children(): tree_ventas.delete(i)
            for i in tree_det.get_children(): tree_det.delete(i)
            
            ventas = self.controller.obtener_ventas_por_cliente(cliente_id)
            if not ventas:
                messagebox.showinfo("Info", "Este cliente no tiene compras registradas.")
            
            for v in ventas:
                metodo = v[4] if v[4] else "Desconocido"
                tree_ventas.insert("", "end", values=(v[0], v[1], f"${v[2]:.2f}", v[3], metodo))

        def mostrar_detalle_venta(event):
            sel = tree_ventas.selection()
            if not sel: return
            item = tree_ventas.item(sel[0])['values']
            venta_id = item[0]
            
            for i in tree_det.get_children(): tree_det.delete(i)
            
            detalles = self.controller.obtener_detalle_venta(venta_id)
            for d in detalles:
                tree_det.insert("", "end", values=(d[0], d[1], f"${d[2]:.2f}", f"${d[3]:.2f}"))

        tree_cli.bind("<<TreeviewSelect>>", mostrar_historial_seleccionado)
        tree_ventas.bind("<<TreeviewSelect>>", mostrar_detalle_venta)
        
        buscar_clientes()

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

    # ========================== VISTA: PROVEEDORES ==========================
    def mostrar_proveedores(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Gestión de Proveedores", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        frm_btns = tk.Frame(self.content_area, bg=estilos.COLOR_FONDO_APP)
        frm_btns.pack(fill="x", padx=20, pady=5)
        
        btn_new = tk.Button(frm_btns, text="+ Nuevo Proveedor", command=self.popup_nuevo_proveedor)
        estilos.style_button_success(btn_new)
        btn_new.pack(side="left", padx=5)
        
        btn_asig = tk.Button(frm_btns, text="📦 Asignar Suministro", command=self.popup_asignar_suministro)
        estilos.style_button_warning(btn_asig)
        btn_asig.pack(side="left", padx=5)
        
        btn_reab = tk.Button(frm_btns, text="🔄 Seleccionar Existente", command=self.popup_seleccionar_existente)
        estilos.style_button_primary(btn_reab)
        btn_reab.configure(bg="#009688")
        btn_reab.pack(side="left", padx=5)
        
        btn_imp = tk.Button(frm_btns, text="Importar CSV Proveedores", command=self.importar_csv_proveedores)
        estilos.style_button_sidebar(btn_imp)
        btn_imp.configure(bg="#607D8B")
        btn_imp.pack(side="left", padx=5)
        
        btn_hist = tk.Button(frm_btns, text="📜 Historial Suministros", command=self.popup_historial_suministros)
        estilos.style_button_primary(btn_hist)
        btn_hist.pack(side="left", padx=5)
        
        cols = ("ID", "Empresa", "Suministra", "Dirección", "Teléfono")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        
        tree.column("ID", width=30)
        tree.column("Empresa", width=150)
        tree.column("Suministra", width=100)
        tree.column("Dirección", width=200)
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        def cargar_provs():
            for i in tree.get_children(): tree.delete(i)
            for p in self.controller.obtener_proveedores():
                cat = p[6] if len(p) > 6 else "General"
                tree.insert("", "end", values=(p[0], p[1], cat, p[5], p[3]))
        
        cargar_provs()
        self.loader_proveedores_ref = cargar_provs
        self.tree_proveedores_ref = tree 

    def popup_historial_suministros(self):
        sel = self.tree_proveedores_ref.selection()
        
        top = tk.Toplevel(self.root)
        top.title("Historial de Suministros por Proveedor")
        top.geometry("700x500")
        top.configure(bg=estilos.COLOR_FONDO_APP)
        
        frm_top = tk.Frame(top, bg=estilos.COLOR_FONDO_APP)
        frm_top.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frm_top, text="Proveedor Seleccionado:", bg=estilos.COLOR_FONDO_APP).pack(side="left")
        
        lbl_prov_actual = tk.Label(frm_top, text="Ninguno", font=("Arial", 10, "bold"), fg="blue", bg=estilos.COLOR_FONDO_APP)
        lbl_prov_actual.pack(side="left", padx=10)
        
        provs = self.controller.obtener_proveedores()
        prov_list = [f"{p[0]} - {p[1]}" for p in provs]
        cmb_prov = ttk.Combobox(frm_top, values=prov_list, state="readonly", width=30)
        cmb_prov.pack(side="left", padx=10)
        
        current_prov_id = None
        if sel:
            p_data = self.tree_proveedores_ref.item(sel[0])['values']
            p_str = f"{p_data[0]} - {p_data[1]}"
            if p_str in prov_list:
                cmb_prov.set(p_str)
                lbl_prov_actual.config(text=p_data[1])
                current_prov_id = p_data[0]

        frm_filter = tk.LabelFrame(top, text="Filtrar Historial", bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
        frm_filter.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frm_filter, text="Buscar (Fecha o Producto):", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
        entry_filter = tk.Entry(frm_filter)
        entry_filter.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_filter = tk.Button(frm_filter, text="🔍 Buscar", command=lambda: cargar_historial())
        estilos.style_button_primary(btn_filter)
        btn_filter.pack(side="left", padx=5)
        entry_filter.bind("<Return>", lambda e: cargar_historial())

        cols = ("ID", "Fecha Entrada", "Producto", "Categoría", "Cant", "Costo Unit.")
        tree_hist = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols: tree_hist.heading(c, text=c)
        
        tree_hist.column("ID", width=30)
        tree_hist.column("Fecha Entrada", width=120)
        tree_hist.column("Producto", width=150)
        tree_hist.column("Categoría", width=80)
        tree_hist.column("Cant", width=50)
        tree_hist.column("Costo Unit.", width=70)
        
        tree_hist.pack(fill="both", expand=True, padx=10, pady=10)
        
        def cargar_historial(event=None):
            sel_str = cmb_prov.get()
            if not sel_str: return
            
            p_id = int(sel_str.split(" - ")[0])
            lbl_prov_actual.config(text=sel_str.split(" - ")[1])
            
            filtro = entry_filter.get()
            
            for i in tree_hist.get_children(): tree_hist.delete(i)
            
            datos = self.controller.obtener_historial_suministros(p_id, filtro)
            
            for d in datos:
                tree_hist.insert("", "end", values=(d[0], d[1], d[2], d[3], d[4], f"${d[5]:.2f}"))

        cmb_prov.bind("<<ComboboxSelected>>", cargar_historial)
        
        if current_prov_id:
            cargar_historial()

    def popup_nuevo_proveedor(self):
        top = tk.Toplevel(self.root)
        top.title("Registrar Proveedor")
        top.geometry("400x400")
        
        tk.Label(top, text="Nombre Empresa:").pack(pady=5)
        entry_nom = tk.Entry(top, width=40); entry_nom.pack()
        
        tk.Label(top, text="Categoría Suministro:").pack(pady=5)
        cats = [c[1] for c in self.controller.obtener_categorias()]
        cats.append("Varios") 
        cmb_cat = ttk.Combobox(top, values=cats, state="readonly", width=37)
        cmb_cat.current(0)
        cmb_cat.pack()
        
        tk.Label(top, text="Dirección:").pack(pady=5)
        entry_dir = tk.Entry(top, width=40); entry_dir.pack()
        
        tk.Label(top, text="Teléfono:").pack(pady=5)
        entry_tel = tk.Entry(top, width=40); entry_tel.pack()
        
        tk.Label(top, text="Email:").pack(pady=5)
        entry_email = tk.Entry(top, width=40); entry_email.pack()
        
        def guardar():
            nom = entry_nom.get()
            cat = cmb_cat.get()
            if nom:
                self.controller.agregar_proveedor(nom, entry_dir.get(), entry_tel.get(), entry_email.get(), "N/A", cat)
                messagebox.showinfo("Éxito", "Proveedor registrado")
                top.destroy()
                self.loader_proveedores_ref()
            else:
                messagebox.showwarning("Error", "Nombre es obligatorio")
        
        tk.Button(top, text="Guardar", command=guardar, bg="#2196F3", fg="white").pack(pady=20)

    def popup_asignar_suministro(self):
        sel = self.tree_proveedores_ref.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un proveedor de la lista primero.")
            return
            
        prov_data = self.tree_proveedores_ref.item(sel[0])['values']
        prov_id = prov_data[0]
        prov_nombre = prov_data[1]
        
        top = tk.Toplevel(self.root)
        top.title(f"Suministro de: {prov_nombre}")
        top.geometry("350x450")
        
        tk.Label(top, text="Categoría:").pack(pady=2)
        cats = [f"{c[0]} - {c[1]}" for c in self.controller.obtener_categorias()]
        cmb_cat = ttk.Combobox(top, values=cats, state="readonly")
        cmb_cat.pack()
        
        tk.Label(top, text="Nombre Producto:").pack(pady=2)
        entry_prod = tk.Entry(top); entry_prod.pack()
        
        tk.Label(top, text="Talla:").pack(pady=2)
        entry_talla = tk.Entry(top); entry_talla.pack()
        
        tk.Label(top, text="Color:").pack(pady=2)
        entry_color = tk.Entry(top); entry_color.pack()
        
        tk.Label(top, text="Precio Venta ($):").pack(pady=2)
        entry_precio = tk.Entry(top); entry_precio.pack()
        
        tk.Label(top, text="Stock Inicial (Cantidad):").pack(pady=2)
        entry_stock = tk.Entry(top); entry_stock.pack()
        
        def registrar_suministro():
            try:
                cat_str = cmb_cat.get()
                if not cat_str: raise ValueError("Seleccione una categoría")
                
                cat_id = int(cat_str.split(" - ")[0])
                nombre = entry_prod.get()
                talla = entry_talla.get()
                color = entry_color.get()
                precio = float(entry_precio.get())
                stock = int(entry_stock.get())
                
                if not nombre: raise ValueError("Falta el nombre del producto")
                
                self.controller.agregar_producto(
                    nombre, "Suministro Nuevo", cat_id, precio, talla, color, stock, prov_id
                )
                
                messagebox.showinfo("Éxito", "Producto agregado/actualizado al inventario correctamente.")
                top.destroy()
                
            except ValueError as ve:
                messagebox.showwarning("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error Crítico", str(e))
        
        tk.Button(top, text="Registrar Entrada", command=registrar_suministro, bg="#4CAF50", fg="white").pack(pady=20)

    def popup_seleccionar_existente(self):
        sel = self.tree_proveedores_ref.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un proveedor de la lista primero.")
            return
            
        prov_data = self.tree_proveedores_ref.item(sel[0])['values']
        prov_id = prov_data[0]
        prov_nombre = prov_data[1]
        
        top = tk.Toplevel(self.root)
        top.title(f"Reabastecer de: {prov_nombre}")
        top.geometry("600x400")
        
        tk.Label(top, text=f"Productos suministrados por {prov_nombre}", font=("Arial", 10, "bold")).pack(pady=10)
        
        cols = ("ID", "Producto", "Talla", "Color", "Precio Actual", "Stock Actual")
        tree_prods = ttk.Treeview(top, columns=cols, show="headings")
        for c in cols: tree_prods.heading(c, text=c)
        
        tree_prods.column("ID", width=30)
        tree_prods.column("Producto", width=150)
        tree_prods.column("Talla", width=50)
        tree_prods.column("Color", width=80)
        tree_prods.column("Precio Actual", width=80)
        tree_prods.column("Stock Actual", width=80)
        
        tree_prods.pack(fill="both", expand=True, padx=10, pady=5)
        
        filtros = {'proveedor_id': prov_id}
        productos = self.controller.obtener_productos(filtros)
        
        if not productos:
            tk.Label(top, text="No hay productos registrados de este proveedor.", fg="red").pack()
        
        for p in productos:
            tree_prods.insert("", "end", values=(p[0], p[1], p[5], p[6], f"${p[4]:.2f}", p[7]))
            
        def agregar_stock():
            sel_prod = tree_prods.selection()
            if not sel_prod: return
            
            item = tree_prods.item(sel_prod[0])['values']
            prod_id = item[0]
            prod_nombre = item[1]
            precio_actual_str = item[4].replace("$", "")
            
            cant = simpledialog.askinteger("Reabastecer", f"Cantidad a agregar de:\n{prod_nombre}", parent=top, minvalue=1)
            if not cant: return
            
            precio_nuevo = simpledialog.askfloat("Precio", f"Precio unitario ($):", parent=top, initialvalue=float(precio_actual_str), minvalue=0)
            if precio_nuevo is None: return 
            
            try:
                self.controller.reabastecer_producto(prod_id, cant, precio_nuevo)
                messagebox.showinfo("Éxito", f"Se agregaron {cant} unidades a {prod_nombre}.")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="➕ Agregar Stock al Seleccionado", command=agregar_stock, bg="#009688", fg="white", font=("Arial", 11)).pack(pady=15)

    def importar_csv_proveedores(self):
        archivo_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not archivo_path:
            return

        try:
            with open(archivo_path, newline='', encoding='utf-8') as archivo:
                reader = csv.DictReader(archivo)
                count = 0
                for row in reader:
                    nom = row.get("Empresa", row.get("Nombre", "Proveedor Importado"))
                    dire = row.get("Direccion", "")
                    tel = row.get("Telefono", "")
                    mail = row.get("Email", "")
                    cont = row.get("Contacto", "N/A")
                    cat = row.get("CategoriaSuministro", "Varios") # Nueva columna
                    
                    self.controller.agregar_proveedor(nom, dire, tel, mail, cont, cat)
                    count += 1
            messagebox.showinfo("Éxito", f"Se importaron {count} proveedores correctamente.")
            self.loader_proveedores_ref()
        except Exception as e:
            messagebox.showerror("Error", f"Error al importar CSV Proveedores: {e}")

    # ========================== VISTA: REPORTES ==========================
    def mostrar_reportes(self):
        self.limpiar_contenido()
        tk.Label(self.content_area, text="Reportes Gerenciales", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
        
        frm_btns = tk.Frame(self.content_area, bg=estilos.COLOR_FONDO_APP)
        frm_btns.pack(pady=5)
        
        # Area para mostrar tabla
        self.tree_reportes = ttk.Treeview(self.content_area, show="headings")
        self.tree_reportes.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Etiqueta para totalizador
        self.lbl_total_reporte = tk.Label(self.content_area, text="", font=("Arial", 14, "bold"), fg="blue", bg=estilos.COLOR_FONDO_APP)
        self.lbl_total_reporte.pack(pady=10)

        # Función genérica para mostrar datos
        def mostrar_datos_en_tabla(cols, data):
            for i in self.tree_reportes.get_children(): self.tree_reportes.delete(i)
            self.tree_reportes["columns"] = cols
            
            # --- ORDENAMIENTO REPORTE ---
            self.orden_reporte = {"col": "", "reverse": False}
            
            def ordenar_reporte(col):
                if self.orden_reporte["col"] == col:
                    self.orden_reporte["reverse"] = not self.orden_reporte["reverse"]
                else:
                    self.orden_reporte["col"] = col
                    self.orden_reporte["reverse"] = False
                
                # Actualizar headers
                for c in cols:
                    self.tree_reportes.heading(c, text=c, command=lambda _c=c: ordenar_reporte(_c))
                
                flecha = " ▼" if self.orden_reporte["reverse"] else " ▲"
                self.tree_reportes.heading(col, text=col + flecha, command=lambda: ordenar_reporte(col))
                
                # Obtener items
                items = [(self.tree_reportes.set(k, col), k) for k in self.tree_reportes.get_children('')]
                
                # Intentar ordenar numericamente si es posible
                try:
                    items.sort(key=lambda t: float(t[0].replace("$","").replace(" ","")), reverse=self.orden_reporte["reverse"])
                except ValueError:
                    items.sort(reverse=self.orden_reporte["reverse"])

                for index, (val, k) in enumerate(items):
                    self.tree_reportes.move(k, '', index)

            for c in cols: 
                self.tree_reportes.heading(c, text=c, command=lambda _c=c: ordenar_reporte(_c))
            
            for d in data: self.tree_reportes.insert("", "end", values=d)
            self.lbl_total_reporte.config(text="") # Limpiar total por defecto

        # Reportes Simples
        def ver_simple(tipo):
            cols, data = self.controller.ejecutar_consulta_reporte(tipo)
            mostrar_datos_en_tabla(cols, data)

        btn_bajo = tk.Button(frm_btns, text="Productos Bajo Stock", command=lambda: ver_simple("Bajo Stock"))
        estilos.style_button_warning(btn_bajo)
        btn_bajo.pack(side="left", padx=5)
        
        btn_ventas_dia = tk.Button(frm_btns, text="Ventas del Día", command=lambda: ver_simple("Ventas del Dia"))
        estilos.style_button_success(btn_ventas_dia)
        btn_ventas_dia.pack(side="left", padx=5)
        
        # REPORTE AVANZADO: VENTAS TOTALES
        def mostrar_filtro_ventas():
            self.limpiar_contenido()
            tk.Label(self.content_area, text="Reporte de Ventas Totales", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
            
            frm_filtros = tk.LabelFrame(self.content_area, text="Filtros", bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
            frm_filtros.pack(fill="x", padx=20, pady=5)
            
            # Filtro Período
            tk.Label(frm_filtros, text="Período:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
            cmb_periodo = ttk.Combobox(frm_filtros, values=["Total", "Personalizado"], width=12, state="readonly")
            cmb_periodo.current(0)
            cmb_periodo.pack(side="left", padx=5)
            
            # Entry días (oculto por defecto)
            entry_dias = tk.Entry(frm_filtros, width=5)
            entry_dias.pack(side="left", padx=2)
            entry_dias.config(state="disabled")
            
            lbl_dias_txt = tk.Label(frm_filtros, text="días atrás", bg=estilos.COLOR_FONDO_APP)
            lbl_dias_txt.pack(side="left")

            def toggle_entry(event):
                if cmb_periodo.get() == "Personalizado":
                    entry_dias.config(state="normal")
                    entry_dias.focus()
                else:
                    entry_dias.delete(0, 'end')
                    entry_dias.config(state="disabled")

            cmb_periodo.bind("<<ComboboxSelected>>", toggle_entry)
            
            # Filtro Método Pago
            tk.Label(frm_filtros, text="Método Pago:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=15)
            cmb_metodo = ttk.Combobox(frm_filtros, values=["Todos", "Efectivo", "Tarjeta", "Transferencia"], width=15, state="readonly")
            cmb_metodo.current(0)
            cmb_metodo.pack(side="left", padx=5)
            
            # Tabla resultados
            self.tree_reportes = ttk.Treeview(self.content_area, columns=("ID", "Fecha", "Cliente", "Vendedor", "Total", "Método"), show="headings")
            
            # Agregamos ordenamiento tambien aqui
            def ordenar_ventas(col):
                items = [(self.tree_reportes.set(k, col), k) for k in self.tree_reportes.get_children('')]
                try:
                    items.sort(key=lambda t: float(t[0].replace("$","")), reverse=True) # Default desc
                except:
                    items.sort(reverse=True)
                for index, (val, k) in enumerate(items):
                    self.tree_reportes.move(k, '', index)

            for c in ("ID", "Fecha", "Cliente", "Vendedor", "Total", "Método"): 
                self.tree_reportes.heading(c, text=c, command=lambda _c=c: ordenar_ventas(_c))
            
            self.tree_reportes.pack(fill="both", expand=True, padx=20, pady=10)
            
            self.lbl_total_reporte = tk.Label(self.content_area, text="Total Ventas: $0.00", font=("Arial", 16, "bold"), fg="green", bg=estilos.COLOR_FONDO_APP)
            self.lbl_total_reporte.pack(pady=10)
            
            def aplicar_filtro():
                modo = cmb_periodo.get()
                dias_valor = None
                
                if modo == "Personalizado":
                    d = entry_dias.get()
                    if d and d.isdigit():
                        dias_valor = d
                
                metodo = cmb_metodo.get()
                
                datos = self.controller.obtener_reporte_ventas(dias_valor, metodo)
                
                for i in self.tree_reportes.get_children(): self.tree_reportes.delete(i)
                
                suma_total = 0
                for d in datos:
                    # d: id, fecha, cliente, vendedor, total, metodo
                    suma_total += d[4]
                    met = d[5] if d[5] else "N/A"
                    self.tree_reportes.insert("", "end", values=(d[0], d[1], d[2], d[3], f"${d[4]:.2f}", met))
                
                self.lbl_total_reporte.config(text=f"Total Filtrado: ${suma_total:.2f}")

            btn_aplicar = tk.Button(frm_filtros, text="Aplicar Filtros", command=aplicar_filtro)
            estilos.style_button_primary(btn_aplicar)
            btn_aplicar.pack(side="left", padx=20)
            
            # Botón Volver
            tk.Button(self.content_area, text="< Volver al Menú Reportes", command=self.mostrar_reportes).pack(side="bottom", pady=10)
            
            aplicar_filtro() # Carga inicial

        # REPORTE AVANZADO: TOP PRODUCTOS (ROTACIÓN)
        def mostrar_filtro_top_productos():
            self.limpiar_contenido()
            tk.Label(self.content_area, text="Reporte: Rotación de Productos", font=estilos.FONT_H1, bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO).pack(pady=10)
            
            frm_filtros = tk.LabelFrame(self.content_area, text="Filtros", bg=estilos.COLOR_FONDO_APP, fg=estilos.COLOR_TEXTO)
            frm_filtros.pack(fill="x", padx=20, pady=5)
            
            # Filtro de tiempo
            tk.Label(frm_filtros, text="Período:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=5)
            cmb_periodo = ttk.Combobox(frm_filtros, values=["Total", "Personalizado"], width=12, state="readonly")
            cmb_periodo.current(0)
            cmb_periodo.pack(side="left", padx=5)
            
            entry_dias = tk.Entry(frm_filtros, width=5)
            entry_dias.pack(side="left", padx=2)
            entry_dias.config(state="disabled")
            
            tk.Label(frm_filtros, text="días atrás", bg=estilos.COLOR_FONDO_APP).pack(side="left")

            def toggle_entry(event):
                if cmb_periodo.get() == "Personalizado":
                    entry_dias.config(state="normal"); entry_dias.focus()
                else:
                    entry_dias.delete(0, 'end'); entry_dias.config(state="disabled")

            cmb_periodo.bind("<<ComboboxSelected>>", toggle_entry)
            
            # Filtro de Categoría (NUEVO)
            tk.Label(frm_filtros, text="Categoría:", bg=estilos.COLOR_FONDO_APP).pack(side="left", padx=15)
            cats = [c[1] for c in self.controller.obtener_categorias()]
            cmb_cat = ttk.Combobox(frm_filtros, values=["Todas"] + cats, width=15, state="readonly")
            cmb_cat.current(0)
            cmb_cat.pack(side="left", padx=5)
            
            self.tree_reportes = ttk.Treeview(self.content_area, columns=("Producto", "Unidades Vendidas"), show="headings")
            self.tree_reportes.heading("Producto", text="Producto", command=lambda: ordenar_reporte_rotacion("Producto"))
            self.tree_reportes.heading("Unidades Vendidas", text="Unidades Vendidas", command=lambda: ordenar_reporte_rotacion("Unidades Vendidas"))
            self.tree_reportes.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Logica ordenamiento para este reporte especifico
            self.orden_rotacion = {"col": "", "reverse": True}
            def ordenar_reporte_rotacion(col):
                if self.orden_rotacion["col"] == col:
                    self.orden_rotacion["reverse"] = not self.orden_rotacion["reverse"]
                else:
                    self.orden_rotacion["col"] = col
                    self.orden_rotacion["reverse"] = True
                
                items = [(self.tree_reportes.set(k, col), k) for k in self.tree_reportes.get_children('')]
                
                # Si es numerico
                if col == "Unidades Vendidas":
                     items.sort(key=lambda t: int(t[0]), reverse=self.orden_rotacion["reverse"])
                else:
                     items.sort(reverse=self.orden_rotacion["reverse"])
                     
                for index, (val, k) in enumerate(items):
                    self.tree_reportes.move(k, '', index)

            # Label Totalizador (NUEVO)
            self.lbl_sum_unidades = tk.Label(self.content_area, text="", font=("Arial", 14, "bold"), fg="green", bg=estilos.COLOR_FONDO_APP)
            self.lbl_sum_unidades.pack(pady=10)
            
            def aplicar_filtro_top():
                modo = cmb_periodo.get()
                cat_val = cmb_cat.get()
                dias_valor = None
                if modo == "Personalizado":
                    d = entry_dias.get()
                    if d and d.isdigit(): dias_valor = d
                
                cols, data = self.controller.ejecutar_consulta_reporte("Top Productos", dias_valor, cat_val)
                # Limpiar y llenar
                for i in self.tree_reportes.get_children(): self.tree_reportes.delete(i)
                for d in data: self.tree_reportes.insert("", "end", values=d)
                
                # Calcular suma de la columna "Unidades Vendidas" (índice 1)
                total_units = sum(d[1] for d in data)
                self.lbl_sum_unidades.config(text=f"Total Unidades Filtradas: {total_units}")

            btn_aplicar = tk.Button(frm_filtros, text="Aplicar Filtros", command=aplicar_filtro_top)
            estilos.style_button_primary(btn_aplicar)
            btn_aplicar.pack(side="left", padx=20)
            
            tk.Button(self.content_area, text="< Volver al Menú Reportes", command=self.mostrar_reportes).pack(side="bottom", pady=10)
            
            aplicar_filtro_top()

        # Botón principal para ir al reporte avanzado
        btn_ventas_tot = tk.Button(frm_btns, text="💰 Ventas Totales", command=mostrar_filtro_ventas)
        estilos.style_button_primary(btn_ventas_tot)
        btn_ventas_tot.pack(side="left", padx=5)
        
        btn_top = tk.Button(frm_btns, text="Más Vendidos / Rotación", command=mostrar_filtro_top_productos)
        estilos.style_button_primary(btn_top); btn_top.configure(bg=estilos.COLOR_WARNING)
        btn_top.pack(side="left", padx=5)

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