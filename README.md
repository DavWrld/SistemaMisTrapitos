# 👕 Sistema de Gestión "Mis Trapitos" (POS & Inventario)

> Una solución de escritorio robusta y offline para la gestión de ventas e inventario, diseñada para optimizar los procesos operativos de la tienda de ropa "Mis Trapitos".

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![GUI](https://img.shields.io/badge/GUI-Tkinter-green)
![Status]

## 📖 Descripción del Proyecto

Este proyecto nace con el objetivo de **reemplazar los procesos manuales y hojas de cálculo** utilizados actualmente en la tienda, centralizando la información para reducir errores de stock y agilizar la atención al cliente.

El sistema es una aplicación de escritorio autocontenida (offline) que gestiona el ciclo completo de venta: desde el alta de productos y control de inventario, hasta la venta en caja (POS) y generación de reportes.

El desarrollo está fundamentado en una **Especificación de Requisitos de Software (ERS) bajo el estándar IEEE 830**, asegurando la calidad técnica y la alineación con las necesidades del negocio.

## 🚀 Características Principales

El sistema cubre los siguientes Requisitos Funcionales (RF) documentados:

** Punto de Venta (POS) Ágil (RF-03):** Interfaz optimizada para registrar ventas rápidas, cálculo automático de totales y cambio, y soporte para múltiples métodos de pago[cite: 555].
** Gestión de Inventario en Tiempo Real (RF-02):** Descuento automático de stock tras cada venta y alertas de productos por agotarse[cite: 551].
** Motor de Promociones (RF-05):** Sistema flexible para aplicar descuentos por porcentaje (%), monto fijo ($) o reglas especiales como "2x1", con vigencia programada[cite: 568, 570].
** Roles y Seguridad (RF-07):** Control de acceso basado en roles (Administrador, Vendedor, Encargado de Inventario) con permisos diferenciados[cite: 576].
** Generación de Tickets:** Emisión de comprobantes de venta listos para impresión térmica[cite: 560].
** Migración de Datos (RF-08):** Módulo ETL personalizado para importar el catálogo histórico y clientes desde archivos Excel existentes hacia la nueva base de datos[cite: 582].

## 🛠️ Stack Tecnológico

El proyecto sigue una arquitectura **MVC (Modelo-Vista-Controlador)** para asegurar la escalabilidad y separación de responsabilidades.

* **Lenguaje:** Python 3.x
* **Frontend (GUI):** Tkinter (con estilos modernos mediante `ttkbootstrap` o `customtkinter`).
* **Backend / Persistencia:** SQLite (Base de datos local relacional).
* **Librerías Clave:**
    * `pandas`: Procesamiento y migración de datos históricos (Excel).
    * `reportlab` / `fpdf`: Generación de reportes y tickets PDF.
    * `bcrypt`: Hashing y seguridad de contraseñas.

## 🗃️ Estructura de Datos

La base de datos ha sido diseñada siguiendo estrictas reglas de integridad y tipado para garantizar la precisión financiera:

* **Precios:** Manejo de datos `DECIMAL(10, 2)` para evitar errores de redondeo en centavos.
* **Integridad Referencial:** Relaciones fuertes (Foreign Keys) entre `Ventas`, `Clientes` y `Productos`.

## 🔧 Instalación y Ejecución

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/mis-trapitos-pos.git](https://github.com/tu-usuario/mis-trapitos-pos.git)
    cd mis-trapitos-pos
    ```

2.  **Crear entorno virtual (Recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicializar Base de Datos:**
    ```bash
    python database/setup_db.py
    ```

5.  **Ejecutar la aplicación:**
    ```bash
    python main.py
    ```

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado siguiendo una metodología ágil con división de roles especializada:

* **David Del Toro** - *Full Stack Dev & Arquitecto*: Integración MVC, Lógica de Negocio (Promociones/Migración) y QA.
* **Eduardo Robles Valverde** - *Backend Dev*: Diseño de Base de Datos, Consultas SQL y Seguridad.
* **Jorge Daniel Flores López** - *Frontend Dev*: Diseño de Interfaces (UI/UX) y Experiencia de Usuario en Tkinter.

---
*Proyecto académico basado en requerimientos reales para la materia de Ingeniería de Software (CUCEI - UdeG).*
