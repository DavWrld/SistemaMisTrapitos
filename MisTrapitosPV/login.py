import tkinter as tk
from tkinter import messagebox

# Credenciales
USUARIOS = {
    "Hector": "1234",
    "Jorge": "pass123",
    "Eduardo": "abc789",
    "David": "0000"
}

def login():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if usuario in USUARIOS and USUARIOS[usuario] == password:
        messagebox.showinfo("Login", f"¡Bienvenido {usuario}!")
    else:
        messagebox.showerror("Login", "Usuario o contraseña incorrectos")
        
def toggle_password():
    if entry_password.cget("show") == "":
        entry_password.config(show="*")
        btn_toggle.config(text="👁")
    else:
        entry_password.config(show="")
        btn_toggle.config(text="🙈")

def on_enter(e):
    btn_login.config(bg="#1976D2")

def on_leave(e):
    btn_login.config(bg="#2196F3")

# Ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Login")
ventana.geometry("380x350")
ventana.resizable(False, False)
ventana.configure(bg="#ECEFF1")

# Marco estilizado
frame = tk.Frame(ventana, bg="white", padx=30, pady=30, bd=0, relief="flat")
frame.place(relx=0.5, rely=0.5, anchor="center")

# Título
label_titulo = tk.Label(frame, text="Iniciar Sesión",
                        font=("Segoe UI", 18, "bold"), bg="white", fg="#263238")
label_titulo.pack(pady=(0, 20))

# Usuario
label_usuario = tk.Label(frame, text="Usuario", font=("Segoe UI", 11),
                         bg="white", fg="#455A64")
label_usuario.pack(anchor="w")

entry_usuario = tk.Entry(frame, font=("Segoe UI", 11), width=28,
                         relief="solid", bd=1)
entry_usuario.pack(pady=5)

# Contraseña
label_password = tk.Label(frame, text="Contraseña", font=("Segoe UI", 11),
                          bg="white", fg="#455A64")
label_password.pack(anchor="w")

password_frame = tk.Frame(frame, bg="white")
password_frame.pack(pady=5)

entry_password = tk.Entry(password_frame, font=("Segoe UI", 11), width=23,
                          relief="solid", bd=1, show="*")
entry_password.grid(row=0, column=0)

btn_toggle = tk.Button(password_frame, text="👁", font=("Arial", 10),
                       bg="white", bd=0, command=toggle_password)
btn_toggle.grid(row=0, column=1, padx=5)

# Botón Login
btn_login = tk.Button(frame, text="Entrar", font=("Segoe UI", 12, "bold"),
                      bg="#2196F3", fg="white", width=20, pady=5,
                      bd=0, activebackground="#1976D2",
                      command=login)
btn_login.pack(pady=25)

# Efecto hover
btn_login.bind("<Enter>", on_enter)
btn_login.bind("<Leave>", on_leave)

ventana.mainloop()