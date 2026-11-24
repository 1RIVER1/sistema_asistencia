"""Interfaz de escritorio de KRONVIA: consume únicamente las funciones de funciones.py."""
from tkinter import (
    Tk, Toplevel, Frame, Label, Entry, Button, Listbox, Scrollbar,
    Canvas, END, LEFT, RIGHT, BOTH, X, Y, TOP, Checkbutton, BooleanVar,
    filedialog
)
import os
from tkinter.ttk import Combobox, Style
from tkinter import messagebox
from datetime import datetime
import funciones

# Paleta inspirada en el referente compartido por el usuario
FONDO = "#f0f0f2"
BLANCO = "#ffffff"
AZUL_PRINCIPAL = "#9511a8"
AZUL_OSCURO = "#32104f"
AZUL_TEXTO = "#171717"
AZUL_SUAVE = "#f4e7f5"
AZUL_BORDE = "#ded8e2"
GRIS = "#73717a"
GRIS_SUAVE = "#faf9fb"
VERDE = "#ed176a"
AMARILLO = "#ffbf2f"
ROJO = "#e23c38"


def color_a_rgb(color):
    """Convierte un color hexadecimal a una tupla RGB."""
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_a_color(rgb):
    """Convierte una tupla RGB a color hexadecimal."""
    return "#%02x%02x%02x" % rgb


def mezclar_color(a, b, proporcion):
    """Interpola dos colores."""
    return tuple(int(a[i] + (b[i] - a[i]) * proporcion) for i in range(3))


def dibujar_degradado(canvas, texto_principal=None, texto_secundario=None, alineacion="centro"):
    """Dibuja un degradado morado, fucsia y rojo en un Canvas."""
    ancho = max(canvas.winfo_width(), 2)
    alto = max(canvas.winfo_height(), 2)
    canvas.delete("all")

    superior_izq = color_a_rgb("#43108f")
    superior_der = color_a_rgb("#f10a8b")
    inferior_izq = color_a_rgb("#e83b42")
    inferior_der = color_a_rgb("#ff321d")

    columnas = 40
    filas = 60
    for fila in range(filas):
        y0 = fila * alto / filas
        y1 = (fila + 1) * alto / filas + 1
        fy = fila / max(filas - 1, 1)
        for columna in range(columnas):
            x0 = columna * ancho / columnas
            x1 = (columna + 1) * ancho / columnas + 1
            fx = columna / max(columnas - 1, 1)
            arriba = mezclar_color(superior_izq, superior_der, fx)
            abajo = mezclar_color(inferior_izq, inferior_der, fx)
            tono = rgb_a_color(mezclar_color(arriba, abajo, fy))
            canvas.create_rectangle(x0, y0, x1, y1, fill=tono, outline=tono)

    if texto_principal:
        centro_x = ancho / 2 if alineacion == "centro" else 30
        ancla = "center" if alineacion == "centro" else "nw"
        y_titulo = alto * 0.43 if alineacion == "centro" else 34
        canvas.create_text(
            centro_x, y_titulo, text=texto_principal,
            fill=BLANCO, font=("Segoe UI", 27, "bold"),
            anchor=ancla, width=max(ancho - 70, 200)
        )
    if texto_secundario:
        centro_x = ancho / 2 if alineacion == "centro" else 30
        ancla = "center" if alineacion == "centro" else "nw"
        y_texto = alto * 0.53 if alineacion == "centro" else 82
        canvas.create_text(
            centro_x, y_texto, text=texto_secundario,
            fill="#fff4fa", font=("Segoe UI", 10),
            anchor=ancla, width=max(ancho - 90, 180), justify="center" if alineacion == "centro" else "left"
        )


def cargar_usuario_recordado():
    """Lee únicamente el nombre de usuario recordado, nunca la contraseña."""
    try:
        with open("recordarme.txt", "r", encoding="utf-8") as archivo:
            return archivo.read().strip()
    except OSError:
        return ""


def guardar_usuario_recordado(usuario, recordar):
    """Guarda o elimina el nombre de usuario recordado."""
    if recordar:
        try:
            with open("recordarme.txt", "w", encoding="utf-8") as archivo:
                archivo.write(usuario)
        except OSError:
            pass
    else:
        try:
            os.remove("recordarme.txt")
        except OSError:
            pass


def crear_campo_acceso(contenedor, texto, oculto=False):
    """Construye un campo de acceso con borde oscuro y esquinas visualmente suaves."""
    bloque = Frame(
        contenedor, bg=BLANCO, padx=12, pady=7,
        highlightthickness=1, highlightbackground="#171717", highlightcolor="#171717"
    )
    bloque.pack(fill=X, pady=8)
    icono = Canvas(bloque, width=25, height=25, bg=BLANCO, highlightthickness=0)
    icono.pack(side=LEFT, padx=(0, 10))
    if oculto:
        icono.create_arc(5, 1, 20, 17, start=0, extent=180, style="arc", outline="#171717", width=2)
        icono.create_rectangle(3, 10, 22, 23, outline="#171717", width=2)
        icono.create_oval(11, 14, 14, 17, fill="#171717", outline="#171717")
    else:
        icono.create_oval(8, 2, 17, 11, outline="#171717", width=2)
        icono.create_arc(3, 9, 22, 28, start=0, extent=180, style="arc", outline="#171717", width=2)
    entrada = Entry(
        bloque, relief="flat", bd=0, bg=BLANCO, fg=GRIS,
        insertbackground="#171717", font=("Segoe UI", 11), show="", highlightthickness=0
    )
    entrada.pack(side=LEFT, fill=X, expand=True, ipady=6)
    entrada.insert(0, texto)
    entrada._es_placeholder = True

    def activar_campo(event=None):
        if entrada._es_placeholder:
            entrada.delete(0, END)
            entrada.config(fg="#171717", show="*" if oculto else "")
            entrada._es_placeholder = False

    def restaurar_placeholder(event=None):
        if entrada.get() == "":
            entrada.config(show="", fg=GRIS)
            entrada.insert(0, texto)
            entrada._es_placeholder = True

    entrada.bind("<FocusIn>", activar_campo)
    entrada.bind("<FocusOut>", restaurar_placeholder)

    if oculto:
        boton_ojo = Button(
            bloque, text="\u25c9", bg=BLANCO, fg="#171717",
            activebackground=BLANCO, activeforeground="#171717",
            relief="flat", bd=0, cursor="hand2", font=("Segoe UI Symbol", 12)
        )
        boton_ojo.pack(side=RIGHT, padx=(6, 0))

        def alternar_visibilidad():
            if not entrada._es_placeholder:
                entrada.config(show="" if entrada.cget("show") == "*" else "*")

        boton_ojo.config(command=alternar_visibilidad)
    return entrada


# ---------- Utilidades visuales ----------
def limpiar(contenedor):
    """Elimina los controles anteriores antes de dibujar otra pantalla."""
    for objeto in contenedor.winfo_children():
        objeto.destroy()


def aplicar_estilo_ttk(raiz):
    """Configura estilos básicos de ttk."""
    estilo = Style(raiz)
    try:
        estilo.theme_use("clam")
    except Exception:
        pass
    estilo.configure(
        "TCombobox",
        fieldbackground=BLANCO,
        background=BLANCO,
        foreground=AZUL_TEXTO,
        padding=8,
        arrowsize=14,
        borderwidth=0,
        relief="flat"
    )
    estilo.map("TCombobox", fieldbackground=[("readonly", BLANCO)])


def caja_blanca(contenedor, padx=18, pady=18):
    """Devuelve una caja blanca estándar."""
    caja = Frame(
        contenedor,
        bg=BLANCO,
        padx=padx,
        pady=pady,
        highlightthickness=1,
        highlightbackground=AZUL_BORDE
    )
    return caja


def mensaje_ayuda(contenedor, texto, color=GRIS, pady=(3, 8)):
    Label(
        contenedor,
        text=texto,
        bg=contenedor.cget("bg"),
        fg=color,
        font=("Segoe UI", 9),
        justify="left",
        wraplength=700
    ).pack(anchor="w", pady=pady)


def etiqueta_campo(contenedor, texto, valor="", ancho=32, oculto=False):
    """Campo de formulario con estilo uniforme."""
    fila = Frame(contenedor, bg=BLANCO)
    fila.pack(fill=X, pady=5)
    Label(
        fila, text=texto, width=24, anchor="w",
        bg=BLANCO, fg=AZUL_TEXTO, font=("Segoe UI", 9, "bold")
    ).pack(side=LEFT)
    entrada = Entry(
        fila, width=ancho, show="*" if oculto else "",
        font=("Segoe UI", 10), relief="flat", bg=GRIS_SUAVE,
        fg=AZUL_TEXTO, insertbackground=AZUL_PRINCIPAL,
        highlightthickness=1, highlightbackground="#e7eef7"
    )
    entrada.pack(side=LEFT, padx=5, ipady=6)
    if valor != "":
        entrada.insert(0, valor)
    return entrada


def etiqueta_opciones(contenedor, texto, opciones, valor):
    """Lista desplegable con estilo uniforme."""
    fila = Frame(contenedor, bg=BLANCO)
    fila.pack(fill=X, pady=5)
    Label(
        fila, text=texto, width=24, anchor="w",
        bg=BLANCO, fg=AZUL_TEXTO, font=("Segoe UI", 9, "bold")
    ).pack(side=LEFT)
    campo = Combobox(fila, values=opciones, state="readonly", width=29)
    campo.pack(side=LEFT, padx=5)
    if len(opciones) > 0:
        campo.set(valor)
    return campo


def boton(contenedor, texto, comando, color=AZUL_PRINCIPAL, expandir=False):
    """Botón estándar de KRONVIA."""
    control = Button(
        contenedor,
        text=texto,
        command=comando,
        bg=color,
        fg=BLANCO,
        activebackground=color,
        activeforeground=BLANCO,
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        padx=14,
        pady=9,
        cursor="hand2"
    )
    control.pack(fill=X if expandir else None, side=LEFT if not expandir else TOP, padx=4, pady=4)
    return control


def lista_con_scroll(contenedor, ancho=100, alto=18):
    """Prepara una lista visual y su desplazamiento vertical."""
    marco = Frame(contenedor, bg=BLANCO)
    marco.pack(fill=BOTH, expand=True, pady=8)
    barra = Scrollbar(marco)
    barra.pack(side=RIGHT, fill=Y)
    lista = Listbox(
        marco,
        width=ancho,
        height=alto,
        font=("Consolas", 10),
        yscrollcommand=barra.set,
        selectbackground=AZUL_PRINCIPAL,
        selectforeground=BLANCO,
        bg=BLANCO,
        fg=AZUL_TEXTO,
        relief="flat",
        highlightthickness=1,
        highlightbackground=AZUL_BORDE
    )
    lista.pack(side=LEFT, fill=BOTH, expand=True)
    barra.config(command=lista.yview)
    return lista


def mostrar_resultado(correcto, mensaje):
    """Muestra respuesta del módulo de lógica."""
    if correcto:
        messagebox.showinfo("KRONVIA", mensaje)
    else:
        messagebox.showerror("KRONVIA", mensaje)


def configurar_toplevel(ventana, titulo, geometria, subtitulo=""):
    """Aplica apariencia uniforme a ventanas secundarias."""
    ventana.title("KRONVIA | " + titulo)
    ventana.geometry(geometria)
    ventana.configure(bg=FONDO)
    contenedor = Frame(ventana, bg=FONDO, padx=18, pady=18)
    contenedor.pack(fill=BOTH, expand=True)

    cabecera = Frame(contenedor, bg=AZUL_PRINCIPAL, padx=24, pady=18)
    cabecera.pack(fill=X)
    Label(cabecera, text=titulo, bg=AZUL_PRINCIPAL, fg=BLANCO,
          font=("Segoe UI", 18, "bold")).pack(anchor="w")
    if subtitulo:
        Label(cabecera, text=subtitulo, bg=AZUL_PRINCIPAL, fg="#dbe7ff",
              font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))

    cuerpo = caja_blanca(contenedor, padx=18, pady=18)
    cuerpo.pack(fill=BOTH, expand=True)
    return cuerpo



def barra_lateral_boton(contenedor, nombre, funcion, activo=False):
    """Botones del menú lateral."""
    return Button(
        contenedor,
        text=nombre,
        command=funcion,
        bg="#a3158d" if activo else AZUL_OSCURO,
        fg=BLANCO,
        activebackground=AZUL_PRINCIPAL,
        activeforeground=BLANCO,
        relief="flat",
        anchor="w",
        padx=18,
        pady=11,
        font=("Segoe UI", 10, "bold" if activo else "normal"),
        cursor="hand2"
    )


def tarjeta_indicador(contenedor, titulo, valor):
    """Tarjeta resumen del dashboard."""
    tarjeta = caja_blanca(contenedor, padx=16, pady=14)
    tarjeta.pack(side=LEFT, fill=X, expand=True, padx=6)
    Label(tarjeta, text=valor, font=("Segoe UI", 18, "bold"), bg=BLANCO, fg=AZUL_PRINCIPAL).pack(anchor="w")
    Label(tarjeta, text=titulo, font=("Segoe UI", 9), bg=BLANCO, fg=GRIS).pack(anchor="w", pady=(4, 0))
    return tarjeta


# ---------- Inicio ----------
def iniciar_interfaz():
    """Crea la única raíz Tk y ejecuta el sistema."""
    correcto, mensaje = funciones.inicializar_archivos()
    raiz = Tk()
    raiz.title("KRONVIA | Gestión Inteligente de Asistencia")
    raiz.geometry("1280x800")
    raiz.minsize(1040, 700)
    raiz.configure(bg=FONDO)
    aplicar_estilo_ttk(raiz)
    if correcto:
        ventana_login(raiz)
    else:
        Label(raiz, text=mensaje, bg=FONDO, fg=ROJO).pack(pady=60)
    raiz.mainloop()


def ventana_login(raiz):
    """Pantalla de acceso KRONVIA, basada en el referente visual compartido."""
    limpiar(raiz)
    raiz.configure(bg=FONDO)

    exterior = Frame(raiz, bg=FONDO, padx=38, pady=34)
    exterior.pack(fill=BOTH, expand=True)

    tarjeta = Frame(
        exterior, bg=BLANCO, bd=0, relief="flat",
        highlightthickness=1, highlightbackground="#e4e1e7"
    )
    tarjeta.pack(fill=BOTH, expand=True, padx=52, pady=24)

    izquierda = Frame(tarjeta, bg=BLANCO, padx=54, pady=32)
    izquierda.pack(side=LEFT, fill=BOTH, expand=True)
    derecha = Canvas(tarjeta, bg="#8c0e9f", highlightthickness=0, bd=0, width=440)
    derecha.pack(side=LEFT, fill=BOTH)

    Label(
        izquierda, text="KRONVIA", bg=BLANCO, fg=AZUL_PRINCIPAL,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", pady=(8, 0))

    formulario = Frame(izquierda, bg=BLANCO, width=390)
    formulario.place(relx=0.5, rely=0.51, anchor="center", width=390)

    Label(formulario, text="Hola...", bg=BLANCO, fg="#111111",
          font=("Segoe UI", 26, "bold")).pack(anchor="center", pady=(0, 0))
    Label(formulario, text="Inicia sesión en tu cuenta", bg=BLANCO, fg="#171717",
          font=("Segoe UI", 13)).pack(anchor="center", pady=(0, 25))

    usuario = crear_campo_acceso(formulario, "Usuario")
    clave = crear_campo_acceso(formulario, "Contraseña", oculto=True)

    fila_opciones = Frame(formulario, bg=BLANCO)
    fila_opciones.pack(fill=X, pady=(2, 18))
    usuario_recordado = cargar_usuario_recordado()
    recordar = BooleanVar(value=bool(usuario_recordado))
    if usuario_recordado:
        usuario.delete(0, END)
        usuario.insert(0, usuario_recordado)
        usuario.config(fg="#171717")
        usuario._es_placeholder = False

    Checkbutton(
        fila_opciones, text="Recordarme", variable=recordar,
        bg=BLANCO, fg="#171717", activebackground=BLANCO,
        activeforeground="#171717", selectcolor=BLANCO,
        font=("Segoe UI", 9), bd=0, highlightthickness=0
    ).pack(side=LEFT)

    def recuperar_acceso():
        messagebox.showinfo(
            "Recuperar contraseña",
            "Para restablecer tu contraseña, solicita ayuda al administrador del sistema."
        )

    Button(
        fila_opciones, text="¿Olvidaste tu contraseña?", command=recuperar_acceso,
        bg=BLANCO, fg="#171717", activebackground=BLANCO,
        activeforeground=AZUL_PRINCIPAL, relief="flat", bd=0, highlightthickness=0,
        font=("Segoe UI", 9), cursor="hand2"
    ).pack(side=RIGHT)

    estado = Label(
        formulario, text="", bg=BLANCO, fg=ROJO,
        font=("Segoe UI", 9), justify="left", wraplength=370
    )
    estado.pack(anchor="w", pady=(0, 5))

    def ingresar(event=None):
        nombre = "" if getattr(usuario, "_es_placeholder", False) else usuario.get().strip()
        contrasena = "" if getattr(clave, "_es_placeholder", False) else clave.get()
        if not nombre or not contrasena:
            estado.config(text="Escribe tu usuario y contraseña para continuar.")
            return
        fecha = funciones.fecha_actual()
        hora = funciones.hora_actual()
        correcto, mensaje, rol = funciones.iniciar_sesion(nombre, contrasena, fecha, hora)
        if correcto:
            guardar_usuario_recordado(nombre, recordar.get())
            sesion = {"usuario": nombre, "rol": rol, "fecha": fecha, "hora": hora}
            ventana_panel(raiz, sesion)
        else:
            estado.config(text=mensaje)
            clave.delete(0, END)
            clave._es_placeholder = False
            clave.config(show="*")
            clave.focus_set()

    acceso = Button(
        formulario, text="Iniciar sesión", command=ingresar,
        bg=BLANCO, fg="#111111", activebackground="#f5f2f6",
        activeforeground="#111111", relief="solid", bd=1,
        font=("Segoe UI", 11, "bold"), cursor="hand2", pady=11
    )
    acceso.pack(fill=X, pady=(5, 25))

    fila_cuenta = Frame(formulario, bg=BLANCO)
    fila_cuenta.pack(anchor="center")
    Label(fila_cuenta, text="¿No eres tú?", bg=BLANCO, fg="#171717",
          font=("Segoe UI", 9)).pack(side=LEFT)

    def cambiar_cuenta():
        usuario.delete(0, END)
        clave.delete(0, END)
        usuario._es_placeholder = False
        clave._es_placeholder = False
        clave.config(show="*")
        recordar.set(False)
        guardar_usuario_recordado("", False)
        estado.config(text="")
        usuario.focus_set()

    Button(
        fila_cuenta, text="Usar otra cuenta", command=cambiar_cuenta,
        bg=BLANCO, fg="#171717", activebackground=BLANCO,
        activeforeground=AZUL_PRINCIPAL, relief="flat", bd=0, highlightthickness=0,
        font=("Segoe UI", 9, "bold"), cursor="hand2"
    ).pack(side=LEFT, padx=(4, 0))

    reloj = Label(izquierda, text="", bg=BLANCO, fg=GRIS,
                  font=("Segoe UI", 9))
    reloj.pack(side="bottom", anchor="center", pady=(8, 2))

    def actualizar_reloj():
        ahora = datetime.now()
        dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        reloj.config(
            text=dias[ahora.weekday()].capitalize() + ", " + str(ahora.day) +
            " de " + meses[ahora.month - 1] + " de " + str(ahora.year) +
            "   ·   " + ahora.strftime("%H:%M:%S")
        )
        if raiz.winfo_exists():
            raiz.after(1000, actualizar_reloj)

    def actualizar_degradado(event=None):
        dibujar_degradado(
            derecha,
            "¡Bienvenido!",
            "Nos alegra tenerte de vuelta. Administra la asistencia y consulta la jornada de tu equipo desde un solo lugar."
        )

    derecha.bind("<Configure>", actualizar_degradado)
    actualizar_reloj()
    usuario.bind("<Return>", ingresar)
    clave.bind("<Return>", ingresar)


# ---------- Dashboard principal ----------
def ventana_panel(raiz, sesion):
    """Dashboard principal con apariencia renovada."""
    limpiar(raiz)

    fondo = Frame(raiz, bg=FONDO)
    fondo.pack(fill=BOTH, expand=True)

    lateral = Frame(fondo, bg=AZUL_OSCURO, width=245)
    lateral.pack(side=LEFT, fill=Y)
    lateral.pack_propagate(False)

    principal = Frame(fondo, bg=FONDO, padx=22, pady=18)
    principal.pack(side=LEFT, fill=BOTH, expand=True)

    Label(lateral, text="KRONVIA", font=("Segoe UI", 22, "bold"), bg=AZUL_OSCURO, fg=BLANCO).pack(anchor="w", padx=24, pady=(28, 2))
    Label(lateral, text="GESTIÓN INTELIGENTE DE ASISTENCIA", bg=AZUL_OSCURO,
          fg="#9fc4ff", font=("Segoe UI", 8, "bold"),
          wraplength=190, justify="left").pack(anchor="w", padx=24)

    caja_usuario = Frame(lateral, bg="#1c447e", padx=16, pady=14)
    caja_usuario.pack(fill=X, padx=16, pady=22)
    Label(caja_usuario, text=sesion["usuario"], bg="#1c447e", fg=BLANCO,
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    Label(caja_usuario, text=sesion["rol"], bg="#1c447e", fg="#cfe1ff",
          font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

    def volver_inicio():
        ventana_panel(raiz, sesion)

    def abrir_empleados():
        ventana_empleados(raiz, sesion)

    def abrir_usuarios():
        ventana_usuarios(raiz, sesion)

    def abrir_horario():
        ventana_horario(raiz, sesion)

    def abrir_registro():
        ventana_asistencia(raiz, sesion)

    def abrir_historial():
        ventana_historial(raiz, sesion)

    def abrir_justificaciones():
        ventana_justificaciones(raiz, sesion)

    def abrir_estadisticas():
        ventana_estadisticas(raiz, sesion)

    def abrir_reportes():
        ventana_reportes(raiz, sesion)

    def abrir_bitacora():
        ventana_bitacora(raiz, sesion)

    def abrir_respaldo():
        ventana_respaldo(raiz, sesion)

    def salir():
        funciones.cerrar_sesion(sesion["usuario"], funciones.fecha_actual(), funciones.hora_actual())
        ventana_login(raiz)

    menu = []
    menu.append(("Inicio", volver_inicio))
    if sesion["rol"] == "Administrador":
        menu.extend([
            ("Empleados", abrir_empleados),
            ("Usuarios", abrir_usuarios),
            ("Horario", abrir_horario),
            ("Historial", abrir_historial),
            ("Estadísticas", abrir_estadisticas),
            ("Reportes", abrir_reportes),
            ("Bitácora", abrir_bitacora),
            ("Respaldo", abrir_respaldo),
        ])
    elif sesion["rol"] == "Supervisor":
        menu.extend([
            ("Empleados", abrir_empleados),
            ("Historial", abrir_historial),
            ("Justificaciones", abrir_justificaciones),
            ("Estadísticas", abrir_estadisticas),
            ("Reportes", abrir_reportes),
        ])
    else:
        menu.extend([
            ("Registrar entrada / salida", abrir_registro),
            ("Mi historial", abrir_historial),
            ("Mis justificaciones", abrir_justificaciones),
        ])
    menu.append(("Cerrar sesión", salir))

    for indice, (nombre, funcion) in enumerate(menu):
        barra_lateral_boton(lateral, nombre, funcion, activo=(indice == 0)).pack(fill=X, padx=12, pady=2)

    # Banner superior con el mismo degradado de la pantalla de acceso
    banner = Canvas(principal, height=150, bg=AZUL_OSCURO, highlightthickness=0)
    banner.pack(fill=X)

    def actualizar_banner(event=None):
        dibujar_degradado(banner)
        ancho = max(banner.winfo_width(), 300)
        if sesion["rol"] == "Empleado":
            titulo = "Mi jornada"
            descripcion = "Consulta tu asistencia y registra cada marcación con su fotografía de evidencia."
        elif sesion["rol"] == "Supervisor":
            titulo = "Panel de supervisión"
            descripcion = "Consulta el estado de asistencia y realiza seguimiento a las novedades del equipo."
        else:
            titulo = "Panel de administración"
            descripcion = "Supervisa asistencia, puntualidad y seguimiento diario desde una sola vista."
        banner.create_text(26, 28, text=titulo, anchor="nw",
                           fill=BLANCO, font=("Segoe UI", 23, "bold"))
        banner.create_text(27, 70, text=descripcion,
                           anchor="nw", fill="#fff4fa", font=("Segoe UI", 10),
                           width=max(ancho - 55, 250))
        banner.create_text(27, 112,
                           text="Fecha: " + funciones.fecha_actual() + "   ·   Hora: " + funciones.hora_actual() + "   ·   Rol: " + sesion["rol"],
                           anchor="nw", fill=BLANCO, font=("Segoe UI", 9, "bold"))

    banner.bind("<Configure>", actualizar_banner)

    # La cuenta de empleado tiene una pantalla personal, sin indicadores ni
    # estadísticas globales que corresponden al administrador.
    if sesion["rol"] == "Empleado":
        ficha = funciones.buscar_empleado(sesion["usuario"])
        nombre_empleado = sesion["usuario"]
        if ficha is not None:
            nombre_empleado = ficha[2] + " " + ficha[3]
        Label(principal, text="Hola, " + nombre_empleado,
              bg=FONDO, fg=AZUL_TEXTO, font=("Segoe UI", 19, "bold")).pack(anchor="w", pady=(18, 4))
        Label(principal, text="Este es tu espacio personal para consultar y registrar tu jornada.",
              bg=FONDO, fg=GRIS, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))

        hoy = funciones.fecha_actual()
        registros_hoy = funciones.historial_empleado(
            sesion["usuario"], sesion["usuario"], hoy, hoy
        )
        registro_hoy = registros_hoy[0] if len(registros_hoy) > 0 else None
        hora_entrada = "Pendiente"
        hora_salida = "Pendiente"
        estado_jornada = "Sin entrada registrada"
        if registro_hoy is not None:
            if registro_hoy[2] != "":
                hora_entrada = registro_hoy[2]
                estado_jornada = "Entrada registrada"
            if registro_hoy[3] != "":
                hora_salida = registro_hoy[3]
                estado_jornada = "Jornada completada"
            elif registro_hoy[2] != "":
                estado_jornada = "Pendiente de registrar salida"

        resumen_personal = caja_blanca(principal, padx=20, pady=18)
        resumen_personal.pack(fill=X, pady=(4, 14))
        Label(resumen_personal, text="ESTADO DE TU JORNADA", bg=BLANCO,
              fg=GRIS, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        Label(resumen_personal, text=estado_jornada, bg=BLANCO,
              fg=AZUL_PRINCIPAL, font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(5, 14))
        tiempos = Frame(resumen_personal, bg=BLANCO)
        tiempos.pack(fill=X)
        tarjeta_indicador(tiempos, "Mi entrada", hora_entrada)
        tarjeta_indicador(tiempos, "Mi salida", hora_salida)

        acciones = caja_blanca(principal, padx=20, pady=16)
        acciones.pack(fill=X)
        Label(acciones, text="Accesos rápidos", bg=BLANCO, fg=AZUL_TEXTO,
              font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))
        fila_acciones = Frame(acciones, bg=BLANCO)
        fila_acciones.pack(fill=X)
        boton(fila_acciones, "Registrar entrada / salida", abrir_registro, VERDE)
        boton(fila_acciones, "Mi historial", abrir_historial, AZUL_PRINCIPAL)
        boton(fila_acciones, "Mis justificaciones", abrir_justificaciones, AZUL_OSCURO)
        mensaje_ayuda(acciones, "Para cada marcación debes adjuntar una fotografía: una para la entrada y otra para la salida.")
        return

    datos = funciones.resumen_dashboard(sesion["usuario"], funciones.fecha_actual())
    if datos == {}:
        Label(principal, text="No hay datos disponibles", bg=FONDO, fg=ROJO).pack(anchor="w", pady=16)
        return

    tarjetas = Frame(principal, bg=FONDO)
    tarjetas.pack(fill=X, pady=16)
    tarjeta_indicador(tarjetas, "Empleados activos", str(datos["activos"]))
    tarjeta_indicador(tarjetas, "Presentes hoy", str(datos["presentes"]))
    tarjeta_indicador(tarjetas, "Ausentes hoy", str(datos["ausentes"]))
    tarjeta_indicador(tarjetas, "Retardos", str(datos["retardos"]))
    tarjeta_indicador(tarjetas, "Horas extra", funciones.minutos_a_texto(datos["extra"]))

    panel_grafico = caja_blanca(principal, padx=20, pady=18)
    panel_grafico.pack(fill=BOTH, expand=True)
    Label(panel_grafico, text="Comparativo de puntualidad y ausencias",
          bg=BLANCO, fg=AZUL_TEXTO, font=("Segoe UI", 15, "bold")).pack(anchor="w")
    mensaje_ayuda(panel_grafico, "Resumen visual del comportamiento del día según los registros almacenados.")

    grafico = Canvas(panel_grafico, height=300, bg=BLANCO, highlightthickness=0)
    grafico.pack(fill=X, pady=(6, 10))
    cantidades = [datos["puntuales"], datos["retardos"], datos["ausentes"]]
    nombres = ["Puntuales", "Retardos", "Ausencias"]
    colores = ["#8f20b2", "#ff2c83", "#f04438"]
    maximo = max(max(cantidades), 1)

    ancho = 920
    separacion = 220
    inicio_x = 120
    base_y = 225
    grafico.create_line(60, base_y, ancho, base_y, fill="#dbe5f0", width=2)
    for i in range(5):
        y = base_y - i * 40
        grafico.create_line(60, y, ancho, y, fill="#eef3f8")

    indice = 0
    while indice < 3:
        izquierda = inicio_x + indice * separacion
        alto = cantidades[indice] * 135 // maximo
        grafico.create_rectangle(
            izquierda, base_y - alto, izquierda + 90, base_y,
            fill=colores[indice], outline=""
        )
        grafico.create_text(izquierda + 45, base_y - alto - 16, text=str(cantidades[indice]),
                            font=("Segoe UI", 12, "bold"), fill=AZUL_TEXTO)
        grafico.create_text(izquierda + 45, base_y + 22, text=nombres[indice],
                            font=("Segoe UI", 10), fill=GRIS)
        indice = indice + 1

    mensaje_ayuda(panel_grafico, "Las ausencias del día se calculan frente a los empleados activos que debían asistir.")


# ---------- Ventanas secundarias ----------
def ventana_empleados(raiz, sesion):
    ventana = Toplevel(raiz)
    contenido = configurar_toplevel(
        ventana, "Gestión de empleados", "1100x740",
        "Consulta, creación y actualización de fichas del personal"
    )

    columnas = Frame(contenido, bg=BLANCO)
    columnas.pack(fill=BOTH, expand=True)
    izquierda = caja_blanca(columnas, padx=14, pady=14)
    izquierda.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
    derecha = caja_blanca(columnas, padx=14, pady=14)
    derecha.pack(side=LEFT, fill=BOTH, expand=True)

    Label(izquierda, text="Seleccione un empleado", bg=BLANCO, fg=AZUL_TEXTO,
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    mensaje_ayuda(izquierda, "Haz clic en un registro para cargar sus datos en el formulario.")
    listado = lista_con_scroll(izquierda, 45, 24)
    filas = []

    nombres_campos = ["ID", "Documento", "Nombre", "Apellido", "Cargo", "Departamento",
                      "Correo", "Teléfono", "Fecha de ingreso", "Estado"]
    campos = []
    Label(derecha, text="Formulario", bg=BLANCO, fg=AZUL_TEXTO,
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    mensaje_ayuda(derecha, "Completa la información del colaborador y guarda los cambios.")
    for nombre in nombres_campos:
        if nombre == "Estado":
            control = etiqueta_opciones(derecha, nombre, ["Activo", "Inactivo"], "Activo")
        else:
            control = etiqueta_campo(derecha, nombre)
        campos.append(control)
    botones = Frame(derecha, bg=BLANCO)
    botones.pack(fill=X, pady=12)

    def actualizar():
        filas.clear()
        listado.delete(0, END)
        for empleado in funciones.consultar_empleados(sesion["usuario"]):
            filas.append(empleado)
            listado.insert(END, empleado[0] + " | " + empleado[2] + " " + empleado[3] + " | " + empleado[9])

    def seleccionar(event=None):
        indices = listado.curselection()
        if len(indices) == 0:
            return
        fila = filas[indices[0]]
        indice = 0
        while indice < 10:
            if indice == 9:
                campos[indice].set(fila[indice])
            else:
                campos[indice].delete(0, END)
                campos[indice].insert(0, fila[indice])
            indice += 1

    def obtener_datos():
        datos = []
        indice = 1
        while indice < 10:
            datos.append(campos[indice].get().strip())
            indice += 1
        return campos[0].get().strip(), datos

    def crear():
        identificador, datos = obtener_datos()
        correcto, mensaje = funciones.crear_empleado(sesion["usuario"], identificador, datos, funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            actualizar()

    def editar():
        identificador, datos = obtener_datos()
        correcto, mensaje = funciones.editar_empleado(sesion["usuario"], identificador, datos, funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            actualizar()

    def desactivar():
        identificador = campos[0].get().strip()
        correcto, mensaje = funciones.desactivar_empleado(sesion["usuario"], identificador, funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            actualizar()

    listado.bind("<<ListboxSelect>>", seleccionar)
    if sesion["rol"] == "Administrador":
        boton(botones, "Crear empleado", crear, VERDE)
        boton(botones, "Guardar cambios", editar, AZUL_PRINCIPAL)
        boton(botones, "Desactivar", desactivar, ROJO)
    else:
        mensaje_ayuda(botones, "Modo consulta: solo el administrador modifica fichas.", color=AZUL_PRINCIPAL)
    actualizar()


def ventana_usuarios(raiz, sesion):
    ventana = Toplevel(raiz)
    contenido = configurar_toplevel(
        ventana, "Usuarios y permisos", "960x670",
        "Administración de cuentas, roles y accesos"
    )

    columnas = Frame(contenido, bg=BLANCO)
    columnas.pack(fill=BOTH, expand=True)
    izquierda = caja_blanca(columnas, padx=14, pady=14)
    izquierda.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
    derecha = caja_blanca(columnas, padx=14, pady=14)
    derecha.pack(side=LEFT, fill=BOTH, expand=True)

    Label(izquierda, text="Cuentas registradas", bg=BLANCO, fg=AZUL_TEXTO,
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    listado = lista_con_scroll(izquierda, 44, 19)
    filas = []

    Label(derecha, text="Configuración de cuenta", bg=BLANCO, fg=AZUL_TEXTO,
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
    nombre = etiqueta_campo(derecha, "Usuario / ID")
    clave = etiqueta_campo(derecha, "Contraseña nueva", oculto=True)
    rol = etiqueta_opciones(derecha, "Rol", ["Administrador", "Supervisor", "Empleado"], "Empleado")
    mensaje_ayuda(derecha, "Para Empleado, el usuario debe coincidir con el ID del empleado.", color="#9b6a09")

    def actualizar():
        filas.clear()
        listado.delete(0, END)
        for fila in funciones.consultar_usuarios(sesion["usuario"]):
            filas.append(fila)
            listado.insert(END, fila[0] + " | " + fila[2] + " | " + fila[3] + " | intentos " + fila[4])

    def seleccionar(event=None):
        seleccion = listado.curselection()
        if len(seleccion) == 0:
            return
        fila = filas[seleccion[0]]
        nombre.delete(0, END)
        nombre.insert(0, fila[0])
        clave.delete(0, END)
        rol.set(fila[2])

    def crear():
        correcto, mensaje = funciones.crear_usuario(sesion["usuario"], nombre.get().strip(), clave.get(), rol.get(), funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            actualizar()

    def ejecutar(accion, valor):
        correcto, mensaje = funciones.modificar_usuario(sesion["usuario"], nombre.get().strip(), accion, valor, funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            actualizar()

    botones = Frame(derecha, bg=BLANCO)
    botones.pack(fill=X, pady=10)
    boton(botones, "Crear usuario", crear, VERDE)
    boton(botones, "Cambiar contraseña", lambda: ejecutar("clave", clave.get()), AZUL_PRINCIPAL)
    boton(botones, "Asignar rol", lambda: ejecutar("rol", rol.get()), AZUL_PRINCIPAL)

    botones2 = Frame(derecha, bg=BLANCO)
    botones2.pack(fill=X, pady=2)
    boton(botones2, "Activar", lambda: ejecutar("estado", "Activo"), VERDE)
    boton(botones2, "Desactivar", lambda: ejecutar("estado", "Inactivo"), ROJO)
    boton(botones2, "Desbloquear", lambda: ejecutar("desbloquear", ""), AMARILLO)

    listado.bind("<<ListboxSelect>>", seleccionar)
    actualizar()


def ventana_horario(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Horario laboral", "720x500",
        "Configura entrada, salida, tolerancias y plazos del sistema"
    )
    horarios = funciones.obtener_horario()
    etiquetas = ["Entrada HH:MM", "Salida HH:MM", "Tolerancia (minutos)",
                 "Inicio horas extra HH:MM", "Plazo para justificar (días)"]
    campos = []
    for indice in range(5):
        campos.append(etiqueta_campo(marco, etiquetas[indice], horarios[indice]))

    def guardar():
        nuevos = [campo.get().strip() for campo in campos]
        correcto, mensaje = funciones.configurar_horario(sesion["usuario"], nuevos, funciones.fecha_actual(), funciones.hora_actual())
        mostrar_resultado(correcto, mensaje)

    fila = Frame(marco, bg=BLANCO)
    fila.pack(fill=X, pady=12)
    boton(fila, "Guardar horario", guardar, VERDE)


def ventana_asistencia(raiz, sesion):
    """Registra entrada/salida usando exclusivamente la hora capturada por la lógica."""
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Registro de asistencia", "980x720",
        "Registra entrada y salida del trabajador autenticado"
    )

    # La fecha y la hora son etiquetas informativas, nunca campos editables.
    bloque_tiempo = Frame(marco, bg=BLANCO)
    bloque_tiempo.pack(fill=X, pady=(4, 16))

    tarjeta_fecha = Frame(
        bloque_tiempo, bg=GRIS_SUAVE, padx=16, pady=13,
        highlightthickness=1, highlightbackground=AZUL_BORDE
    )
    tarjeta_fecha.pack(side=LEFT, fill=X, expand=True, padx=(0, 8))
    Label(tarjeta_fecha, text="FECHA DE REGISTRO", bg=GRIS_SUAVE,
          fg=GRIS, font=("Segoe UI", 8, "bold")).pack(anchor="w")
    valor_fecha = Label(tarjeta_fecha, text="", bg=GRIS_SUAVE,
                        fg=AZUL_TEXTO, font=("Segoe UI", 16, "bold"))
    valor_fecha.pack(anchor="w", pady=(4, 0))

    tarjeta_hora = Frame(
        bloque_tiempo, bg=GRIS_SUAVE, padx=16, pady=13,
        highlightthickness=1, highlightbackground=AZUL_BORDE
    )
    tarjeta_hora.pack(side=LEFT, fill=X, expand=True, padx=(8, 0))
    Label(tarjeta_hora, text="HORA ACTUAL", bg=GRIS_SUAVE,
          fg=GRIS, font=("Segoe UI", 8, "bold")).pack(anchor="w")
    valor_hora = Label(tarjeta_hora, text="", bg=GRIS_SUAVE,
                       fg=AZUL_PRINCIPAL, font=("Segoe UI", 16, "bold"))
    valor_hora.pack(anchor="w", pady=(4, 0))

    mensaje_ayuda(
        marco,
        "La fotografía es obligatoria en cada marcación. Selecciona una imagen distinta para la entrada y para la salida.",
        color=AZUL_PRINCIPAL,
        pady=(0, 10)
    )

    contenedor_fotos = Frame(marco, bg=BLANCO)
    contenedor_fotos.pack(fill=X, pady=4)
    foto_entrada = {"ruta": ""}
    foto_salida = {"ruta": ""}

    def crear_selector_foto(padre, titulo, estado_foto):
        tarjeta = caja_blanca(padre, padx=14, pady=12)
        tarjeta.pack(side=LEFT, fill=X, expand=True, padx=5)
        Label(tarjeta, text=titulo, bg=BLANCO, fg=AZUL_TEXTO,
              font=("Segoe UI", 10, "bold")).pack(anchor="w")
        etiqueta_archivo = Label(
            tarjeta, text="Ninguna fotografía seleccionada",
            bg=BLANCO, fg=GRIS, font=("Segoe UI", 9),
            wraplength=300, justify="left"
        )
        etiqueta_archivo.pack(anchor="w", pady=(7, 9))

        def seleccionar_foto():
            ruta = filedialog.askopenfilename(
                parent=ventana,
                title="Seleccionar fotografía de " + titulo.lower(),
                filetypes=[
                    ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
                    ("Todos los archivos", "*.*")
                ]
            )
            if ruta:
                estado_foto["ruta"] = ruta
                etiqueta_archivo.config(text=os.path.basename(ruta), fg=VERDE)

        boton(tarjeta, "Adjuntar fotografía", seleccionar_foto, AZUL_PRINCIPAL, expandir=True)
        return etiqueta_archivo

    etiqueta_foto_entrada = crear_selector_foto(
        contenedor_fotos, "FOTO DE ENTRADA *", foto_entrada
    )
    etiqueta_foto_salida = crear_selector_foto(
        contenedor_fotos, "FOTO DE SALIDA *", foto_salida
    )

    botones = Frame(marco, bg=BLANCO)
    botones.pack(fill=X, pady=8)

    historial = lista_con_scroll(marco, 100, 12)

    def actualizar_reloj():
        """Actualiza la vista con la misma precisión que se almacena en el registro."""
        if ventana.winfo_exists():
            ahora = datetime.now()
            valor_fecha.config(text=ahora.strftime("%d/%m/%Y"))
            valor_hora.config(text=ahora.strftime("%H:%M"))
            ventana.after(1000, actualizar_reloj)

    def actualizar():
        historial.delete(0, END)
        registros = funciones.historial_empleado(
            sesion["usuario"], sesion["usuario"], "0001-01-01", "9999-12-31"
        )
        for registro in registros:
            historial.insert(
                END,
                registro[1] + " | E: " + registro[2] + " | S: " + registro[3] +
                " | " + registro[4] + " | " + registro[5]
            )

    def registrar(tipo):
        # Cada marcación utiliza su propio archivo. La lógica valida la imagen,
        # la copia a evidencias/ y captura la fecha/hora al momento del clic.
        seleccion = foto_entrada if tipo == "Entrada" else foto_salida
        etiqueta = etiqueta_foto_entrada if tipo == "Entrada" else etiqueta_foto_salida
        if not seleccion["ruta"]:
            messagebox.showwarning(
                "Fotografía obligatoria",
                "Adjunta la fotografía de " + tipo.lower() + " antes de registrar."
            )
            return
        correcto, mensaje = funciones.registrar_asistencia(
            sesion["usuario"], tipo, seleccion["ruta"]
        )
        mostrar_resultado(correcto, mensaje)
        if correcto:
            seleccion["ruta"] = ""
            etiqueta.config(text="Ninguna fotografía seleccionada", fg=GRIS)
            actualizar()

    boton(botones, "Registrar entrada", lambda: registrar("Entrada"), VERDE)
    boton(botones, "Registrar salida", lambda: registrar("Salida"), AZUL_PRINCIPAL)
    actualizar_reloj()
    actualizar()


def ventana_historial(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Historial de asistencias", "1100x700",
        "Consulta registros por periodo y revisa evidencias"
    )
    empleados = funciones.consultar_empleados(sesion["usuario"])
    ids = [empleado[0] for empleado in empleados]
    identificador = sesion["usuario"] if len(ids) == 0 else ids[0]
    campo_id = etiqueta_opciones(marco, "Empleado (ID)", ids, identificador)
    periodo = etiqueta_opciones(marco, "Período", ["Diario", "Semanal", "Mensual", "Anual"], "Mensual")
    fecha = etiqueta_campo(marco, "Fecha de referencia", funciones.fecha_actual())
    listado = lista_con_scroll(marco, 125, 15)
    resumen = Label(marco, text="", justify="left", bg=BLANCO, fg=AZUL_TEXTO, font=("Segoe UI", 10, "bold"))
    resumen.pack(anchor="w", pady=6)
    filas = []

    def consultar():
        inicio, fin = funciones.rango_periodo(periodo.get(), fecha.get().strip())
        if inicio == "":
            mostrar_resultado(False, "Fecha o periodo inválido")
            return
        filas.clear()
        listado.delete(0, END)
        registros = funciones.historial_empleado(sesion["usuario"], campo_id.get(), inicio, fin)
        for fila in registros:
            filas.append(fila)
            listado.insert(END, fila[1] + " | " + fila[2] + " - " + fila[3] + " | " + fila[4] + " | " + fila[5] + " | " + funciones.minutos_a_texto(int(fila[6])) + " | extra " + funciones.minutos_a_texto(int(fila[7])))
        indicadores = funciones.calcular_estadisticas(registros)
        resumen.config(text="Trabajadas: " + funciones.minutos_a_texto(indicadores["minutos"]) + " | Extras: " + funciones.minutos_a_texto(indicadores["extras"]) + " | Retardos: " + str(indicadores["retardos"]) + " | Ausencias: " + str(indicadores["ausencias"]) + " | Puntualidad: " + str(indicadores["puntualidad"]) + "%")

    def ver_evidencia():
        seleccion = listado.curselection()
        if len(seleccion) == 0:
            messagebox.showwarning("KRONVIA", "Selecciona primero un registro del historial.")
            return
        fila = filas[seleccion[0]]
        ventana_evidencia = Toplevel(ventana)
        cuerpo = configurar_toplevel(
            ventana_evidencia, "Fotografías de evidencia", "620x330",
            "Evidencias adjuntas al registro seleccionado"
        )

        def abrir_fotografia(ruta, tipo):
            if not ruta:
                messagebox.showwarning("KRONVIA", "Este registro no tiene fotografía de " + tipo.lower() + ".")
                return
            if not os.path.isfile(ruta):
                messagebox.showerror("KRONVIA", "No se encontró el archivo de evidencia:\n" + ruta)
                return
            try:
                if hasattr(os, "startfile"):
                    os.startfile(os.path.abspath(ruta))
                else:
                    messagebox.showinfo("KRONVIA", "La fotografía está guardada en:\n" + os.path.abspath(ruta))
            except OSError:
                messagebox.showerror("KRONVIA", "No fue posible abrir la fotografía.")

        for tipo, ruta in [("Entrada", fila[10]), ("Salida", fila[11])]:
            tarjeta = caja_blanca(cuerpo, padx=14, pady=12)
            tarjeta.pack(fill=X, pady=6)
            Label(tarjeta, text="FOTO DE " + tipo.upper(), bg=BLANCO,
                  fg=AZUL_TEXTO, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            nombre_archivo = os.path.basename(ruta) if ruta else "Sin fotografía adjunta"
            Label(tarjeta, text=nombre_archivo, bg=BLANCO, fg=GRIS,
                  font=("Segoe UI", 9)).pack(anchor="w", pady=4)
            boton(tarjeta, "Abrir fotografía", lambda r=ruta, t=tipo: abrir_fotografia(r, t), AZUL_PRINCIPAL)

    fila_botones = Frame(marco, bg=BLANCO)
    fila_botones.pack(fill=X, pady=6)
    boton(fila_botones, "Consultar historial", consultar, VERDE)
    boton(fila_botones, "Ver evidencia", ver_evidencia, AZUL_PRINCIPAL)
    consultar()


def ventana_justificaciones(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Gestión de justificaciones", "1080x710",
        "Envía, revisa y resuelve ausencias justificadas"
    )
    filas = []
    if sesion["rol"] == "Empleado":
        tipo = etiqueta_opciones(marco, "Tipo", ["Incapacidad médica", "Vacaciones", "Permiso personal", "Comisión laboral"], "Permiso personal")
        ausencia = etiqueta_campo(marco, "Fecha de ausencia", funciones.fecha_actual())
        descripcion = etiqueta_campo(marco, "Descripción")
        soporte = etiqueta_campo(marco, "Nombre archivo soporte")
        fecha = etiqueta_campo(marco, "Fecha de radicación", funciones.fecha_actual())
        hora = etiqueta_campo(marco, "Hora de radicación", funciones.hora_actual())
        listado = lista_con_scroll(marco, 115, 11)

        def actualizar():
            listado.delete(0, END)
            for fila in funciones.consultar_justificaciones(sesion["usuario"]):
                listado.insert(END, fila[0] + " | " + fila[2] + " | " + fila[3] + " | " + fila[6] + " | " + fila[7])

        def enviar():
            correcto, mensaje = funciones.registrar_justificacion(sesion["usuario"], ausencia.get().strip(), tipo.get(), descripcion.get().strip(), soporte.get().strip(), fecha.get().strip(), hora.get().strip())
            mostrar_resultado(correcto, mensaje)
            if correcto:
                actualizar()

        fila_botones = Frame(marco, bg=BLANCO)
        fila_botones.pack(fill=X, pady=6)
        boton(fila_botones, "Enviar justificación", enviar, VERDE)
        actualizar()
    else:
        mensaje_ayuda(marco, "Seleccione una justificación pendiente y escriba un comentario.")
        listado = lista_con_scroll(marco, 120, 20)
        comentario = etiqueta_campo(marco, "Comentario del supervisor")

        def actualizar():
            filas.clear()
            listado.delete(0, END)
            for fila in funciones.consultar_justificaciones(sesion["usuario"]):
                filas.append(fila)
                listado.insert(END, fila[0] + " | " + fila[1] + " | " + fila[2] + " | " + fila[3] + " | " + fila[6] + " | " + fila[4])

        def resolver(decision):
            seleccion = listado.curselection()
            if len(seleccion) == 0:
                mostrar_resultado(False, "Seleccione una justificación")
                return
            fila = filas[seleccion[0]]
            correcto, mensaje = funciones.resolver_justificacion(sesion["usuario"], fila[0], decision, comentario.get().strip(), funciones.fecha_actual(), funciones.hora_actual())
            mostrar_resultado(correcto, mensaje)
            if correcto:
                actualizar()

        fila_botones = Frame(marco, bg=BLANCO)
        fila_botones.pack(fill=X, pady=6)
        boton(fila_botones, "Aprobar selección", lambda: resolver("Aprobado"), VERDE)
        boton(fila_botones, "Rechazar selección", lambda: resolver("Rechazado"), ROJO)
        actualizar()


def ventana_estadisticas(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Estadísticas generales", "920x660",
        "Comparativos globales por periodo"
    )
    periodo = etiqueta_opciones(marco, "Período", ["Diario", "Semanal", "Mensual", "Anual"], "Mensual")
    fecha = etiqueta_campo(marco, "Fecha de referencia", funciones.fecha_actual())
    listado = lista_con_scroll(marco, 100, 17)

    def consultar():
        inicio, fin = funciones.rango_periodo(periodo.get(), fecha.get().strip())
        if inicio == "":
            mostrar_resultado(False, "Fecha inválida")
            return
        datos = funciones.estadisticas_generales(sesion["usuario"], inicio, fin)
        listado.delete(0, END)
        if datos == {}:
            mostrar_resultado(False, "Sin permiso o datos disponibles")
            return
        listado.insert(END, "Periodo: " + inicio + " a " + fin)
        listado.insert(END, "Empleado más puntual: " + datos["mas_puntual"])
        listado.insert(END, "Empleado con más minutos trabajados: " + datos["mas_horas"])
        listado.insert(END, "Empleado con más retardos: " + datos["mas_retardos"])
        listado.insert(END, "")
        listado.insert(END, "ARREGLO BIDIMENSIONAL: REGISTROS POR DÍA")
        nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        indice = 0
        while indice < 7:
            listado.insert(END, nombres[indice] + ": " + str(len(datos["por_dia"][indice])) + " registros")
            indice += 1

    fila_botones = Frame(marco, bg=BLANCO)
    fila_botones.pack(fill=X, pady=6)
    boton(fila_botones, "Calcular estadísticas", consultar, VERDE)
    consultar()


def ventana_reportes(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Reportes de asistencia", "1100x720",
        "Generación y vista previa de reportes del sistema"
    )
    periodo = etiqueta_opciones(marco, "Tipo de reporte", ["Diario", "Semanal", "Mensual", "Individual"], "Diario")
    fecha = etiqueta_campo(marco, "Fecha de referencia", funciones.fecha_actual())
    ids = [empleado[0] for empleado in funciones.consultar_empleados(sesion["usuario"])]
    identificador = "" if len(ids) == 0 else ids[0]
    campo_id = etiqueta_opciones(marco, "ID (reporte individual)", ids, identificador)
    listado = lista_con_scroll(marco, 150, 22)

    def generar():
        correcto, mensaje, contenido = funciones.crear_reporte(sesion["usuario"], periodo.get(), fecha.get().strip(), campo_id.get(), funciones.hora_actual())
        listado.delete(0, END)
        for linea in contenido.split("\n"):
            listado.insert(END, linea)
        mostrar_resultado(correcto, mensaje)

    fila_botones = Frame(marco, bg=BLANCO)
    fila_botones.pack(fill=X, pady=6)
    boton(fila_botones, "Generar reporte .txt", generar, VERDE)


def ventana_bitacora(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Bitácora del sistema", "1040x620",
        "Historial de acciones registradas por el sistema"
    )
    lista = lista_con_scroll(marco, 130, 25)

    def actualizar():
        lista.delete(0, END)
        for fila in funciones.consultar_bitacora(sesion["usuario"]):
            lista.insert(END, " | ".join(fila))

    fila_botones = Frame(marco, bg=BLANCO)
    fila_botones.pack(fill=X, pady=6)
    boton(fila_botones, "Actualizar bitácora", actualizar, AZUL_PRINCIPAL)
    actualizar()


def ventana_respaldo(raiz, sesion):
    ventana = Toplevel(raiz)
    marco = configurar_toplevel(
        ventana, "Respaldo y restauración", "820x560",
        "Copia y recuperación de los archivos base del sistema"
    )
    fecha = etiqueta_campo(marco, "Fecha de respaldo", funciones.fecha_actual())
    fecha_actual = etiqueta_campo(marco, "Fecha del registro", funciones.fecha_actual())
    hora = etiqueta_campo(marco, "Hora del registro", funciones.hora_actual())
    mensaje_ayuda(marco, "Se copian usuarios, empleados, asistencias, justificaciones, horario y bitácora.")

    def copiar():
        correcto, mensaje = funciones.crear_respaldo(sesion["usuario"], fecha.get().strip(), hora.get().strip())
        mostrar_resultado(correcto, mensaje)

    def restaurar():
        confirmar = messagebox.askyesno("Confirmar restauración", "¿Restaurar los seis archivos? Se reemplazarán los datos actuales.")
        if not confirmar:
            return
        correcto, mensaje = funciones.restaurar_respaldo(sesion["usuario"], fecha.get().strip(), fecha_actual.get().strip(), hora.get().strip())
        mostrar_resultado(correcto, mensaje)
        if correcto:
            ventana.destroy()
            ventana_login(raiz)

    fila = Frame(marco, bg=BLANCO)
    fila.pack(fill=X, pady=12)
    boton(fila, "Crear respaldo", copiar, VERDE)
    boton(fila, "Restaurar respaldo", restaurar, ROJO)
    mensaje_ayuda(marco, "Nota: un respaldo existente no se sobrescribe. Guarda los reportes por separado.", color="#9b6a09")


if __name__ == "__main__":
    iniciar_interfaz()
