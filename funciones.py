"""Lógica de asistencia de KRONVIA. Conserva archivos de texto y estructuras básicas."""

from datetime import datetime
import os
import shutil
import hashlib

def fecha_actual():
    """Fecha local del equipo en formato AAAA-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def hora_actual():
    """Hora local del equipo en formato HH:MM."""
    return datetime.now().strftime("%H:%M")

ARCHIVOS = {
    "usuarios": "usuarios.txt",
    "empleados": "empleados.txt",
    "asistencias": "asistencias.txt",
    "justificaciones": "justificaciones.txt",
    "horario": "horario.txt",
    "bitacora": "bitacora.txt"
}

# Las contraseñas están en texto simple por limitación académica del curso.
# No usar este mecanismo para datos reales o producción.
FECHA_SUGERIDA = fecha_actual()


def leer_registros(nombre):
    """Lee registros separados por punto y coma; tolera un archivo inexistente."""
    registros = []
    try:
        archivo = open(ARCHIVOS[nombre], "r", encoding="utf-8")
        lineas = archivo.readlines()
        archivo.close()
        for linea in lineas:
            linea = linea.strip()
            if linea != "":
                registros.append(linea.split(";"))
    except (OSError, KeyError):
        return []
    return registros


def guardar_registros(nombre, registros):
    """Reescribe un archivo de registros y devuelve éxito o error."""
    try:
        archivo = open(ARCHIVOS[nombre], "w", encoding="utf-8")
        for registro in registros:
            archivo.write(";".join(registro) + "\n")
        archivo.close()
        return True
    except (OSError, KeyError):
        return False


def agregar_registro(nombre, registro):
    """Anexa una fila al final de un archivo."""
    try:
        archivo = open(ARCHIVOS[nombre], "a", encoding="utf-8")
        archivo.write(";".join(registro) + "\n")
        archivo.close()
        return True
    except (OSError, KeyError):
        return False


def texto_valido(valor):
    """Impide campos vacíos y delimitadores que dañen el archivo."""
    return str(valor).strip() != "" and ";" not in str(valor) and "\n" not in str(valor) and "\r" not in str(valor)


def solo_digitos(texto):
    """Comprueba números sin usar funciones avanzadas ni expresiones regulares."""
    if len(texto) == 0:
        return False
    for caracter in texto:
        if caracter not in "0123456789":
            return False
    return True


def validar_identificador(texto):
    """Admite únicamente letras, cifras, guion y guion bajo en ID o usuario."""
    if not texto_valido(texto) or len(texto) > 30:
        return False
    permitidos = "abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ0123456789_-"
    for caracter in texto:
        if caracter not in permitidos:
            return False
    return True


def validar_fecha(fecha):
    """Comprueba formato AAAA-MM-DD y fechas posibles."""
    try:
        partes = fecha.split("-")
        if len(partes) != 3 or len(partes[0]) != 4 or len(partes[1]) != 2 or len(partes[2]) != 2:
            return False
        for parte in partes:
            if not solo_digitos(parte):
                return False
        anio = int(partes[0])
        mes = int(partes[1])
        dia = int(partes[2])
        if anio < 1 or anio > 9999 or mes < 1 or mes > 12:
            return False
        return dia >= 1 and dia <= dias_del_mes(anio, mes)
    except (ValueError, TypeError):
        return False


def es_bisiesto(anio):
    """Indica si un año tiene 366 días."""
    return anio % 400 == 0 or (anio % 4 == 0 and anio % 100 != 0)


def dias_del_mes(anio, mes):
    """Devuelve la cantidad de días de un mes."""
    if mes == 2:
        if es_bisiesto(anio):
            return 29
        return 28
    if mes == 4 or mes == 6 or mes == 9 or mes == 11:
        return 30
    return 31


def numero_de_dia(fecha):
    """Convierte una fecha válida en cantidad de días desde el año 1."""
    if not validar_fecha(fecha):
        return -1
    partes = fecha.split("-")
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
    total = 0
    actual = 1
    while actual < anio:
        if es_bisiesto(actual):
            total = total + 366
        else:
            total = total + 365
        actual = actual + 1
    actual = 1
    while actual < mes:
        total = total + dias_del_mes(anio, actual)
        actual = actual + 1
    return total + dia - 1


def fecha_de_numero(numero):
    """Convierte un número de día a fecha AAAA-MM-DD."""
    if numero < 0:
        return ""
    anio = 1
    while True:
        cantidad = 365
        if es_bisiesto(anio):
            cantidad = 366
        if numero < cantidad:
            break
        numero = numero - cantidad
        anio = anio + 1
        if anio > 9999:
            return ""
    mes = 1
    while numero >= dias_del_mes(anio, mes):
        numero = numero - dias_del_mes(anio, mes)
        mes = mes + 1
    dia = numero + 1
    texto_anio = str(anio)
    while len(texto_anio) < 4:
        texto_anio = "0" + texto_anio
    texto_mes = str(mes)
    if mes < 10:
        texto_mes = "0" + texto_mes
    texto_dia = str(dia)
    if dia < 10:
        texto_dia = "0" + texto_dia
    return texto_anio + "-" + texto_mes + "-" + texto_dia


def sumar_dias(fecha, dias):
    """Suma o resta días, incluso al cambiar de mes o de año."""
    numero = numero_de_dia(fecha)
    if numero < 0:
        return ""
    return fecha_de_numero(numero + dias)


def dias_entre(fechainicio, fechafin):
    """Cuenta días entre dos fechas; puede devolver un valor negativo."""
    primero = numero_de_dia(fechainicio)
    segundo = numero_de_dia(fechafin)
    if primero < 0 or segundo < 0:
        return -999999
    return segundo - primero


def dia_de_la_semana(fecha):
    """Devuelve lunes=0, ..., domingo=6; 0001-01-01 fue lunes."""
    numero = numero_de_dia(fecha)
    if numero < 0:
        return -1
    return numero % 7


def es_laborable(fecha):
    """Comprueba si una fecha es lunes, martes, miércoles, jueves o viernes."""
    dia = dia_de_la_semana(fecha)
    return dia >= 0 and dia <= 4


def validar_hora(hora):
    """Valida una hora de 00:00 a 23:59."""
    try:
        partes = hora.split(":")
        if len(partes) != 2 or len(partes[0]) != 2 or len(partes[1]) != 2:
            return False
        for parte in partes:
            if not solo_digitos(parte):
                return False
        horas = int(partes[0])
        minutos = int(partes[1])
        return horas >= 0 and horas <= 23 and minutos >= 0 and minutos <= 59
    except (ValueError, TypeError):
        return False


def a_minutos(hora):
    """Convierte HH:MM a minutos desde medianoche."""
    if not validar_hora(hora):
        return -1
    partes = hora.split(":")
    return int(partes[0]) * 60 + int(partes[1])


def inicializar_archivos():
    """Crea archivos base y garantiza una cuenta de demostración."""
    faltantes = []
    for nombre in ARCHIVOS:
        try:
            archivo = open(ARCHIVOS[nombre], "r", encoding="utf-8")
            archivo.close()
        except OSError:
            faltantes.append(nombre)
    for nombre in faltantes:
        if nombre == "usuarios":
            datos = [
                ["admin", "admin123", "Administrador", "Activo", "0"],
                ["supervisor", "super123", "Supervisor", "Activo", "0"],
                ["E001", "empleado123", "Empleado", "Activo", "0"],
                ["E002", "empleado123", "Empleado", "Activo", "0"]
            ]
        elif nombre == "empleados":
            datos = [
                ["E001", "100000001", "Ana", "Rojas", "Analista", "Operaciones", "ana@ejemplo.com", "3001111111", "2026-11-16", "Activo"],
                ["E002", "100000002", "Luis", "Pérez", "Auxiliar", "Administración", "luis@ejemplo.com", "3002222222", "2026-11-16", "Activo"]
            ]
        elif nombre == "horario":
            datos = [["08:00", "17:00", "5", "18:00", "3"]]
        else:
            datos = []
        if not guardar_registros(nombre, datos):
            return False, "No fue posible crear " + nombre

    # Se agrega también cuando usuarios.txt ya existía de una ejecución anterior.
    usuarios = leer_registros("usuarios")
    existe_prueba = False
    for fila in usuarios:
        if len(fila) >= 5 and fila[0] == "prueba":
            existe_prueba = True
            break
    if not existe_prueba:
        usuarios.append(["prueba", "prueba123", "Administrador", "Activo", "0"])

    # Garantiza una cuenta de empleado para probar el panel personal y las fotos.
    existe_empleado_demo = False
    for fila in usuarios:
        if len(fila) >= 5 and fila[0] == "E001":
            existe_empleado_demo = True
            break
    if not existe_empleado_demo:
        for empleado in leer_registros("empleados"):
            if len(empleado) >= 10 and empleado[0] == "E001" and empleado[9] == "Activo":
                usuarios.append(["E001", "empleado123", "Empleado", "Activo", "0"])
                break

    if not guardar_registros("usuarios", usuarios):
        return False, "No fue posible actualizar las cuentas de demostración"

    return True, "Archivos preparados"


def obtener_horario():
    """Obtiene la configuración del primer registro de horario.txt."""
    registros = leer_registros("horario")
    if len(registros) > 0 and len(registros[0]) == 5:
        return registros[0]
    return ["08:00", "17:00", "5", "18:00", "3"]


def clasificar_entrada(hora, hora_entrada="08:00", tolerancia=5):
    """Determina si una entrada fue Puntual o Retardo."""
    entrada = a_minutos(hora)
    limite = a_minutos(hora_entrada)
    if entrada < 0 or limite < 0:
        return "Error"
    try:
        tolerancia = int(tolerancia)
        if tolerancia < 0:
            return "Error"
    except (ValueError, TypeError):
        return "Error"
    if entrada <= limite + tolerancia:
        return "Puntual"
    return "Retardo"


def calcular_hora_extra(hora_salida, inicio_extra="18:00"):
    """Devuelve minutos extraordinarios después del umbral establecido."""
    salida = a_minutos(hora_salida)
    inicio = a_minutos(inicio_extra)
    if salida < 0 or inicio < 0:
        return -1
    if salida > inicio:
        return salida - inicio
    return 0


def clasificar_salida(hora, fin_normal="17:00", inicio_extra="18:00"):
    """Identifica salida Anticipada, Normal o Con extra."""
    salida = a_minutos(hora)
    fin = a_minutos(fin_normal)
    extra = a_minutos(inicio_extra)
    if salida < 0 or fin < 0 or extra < 0:
        return "Error"
    if salida < fin:
        return "Anticipada"
    if salida <= extra:
        return "Normal"
    return "Con extra"


def estado_ausencia(fecha_ausencia, fecha_consulta, aprobada=False, rechazada=False, plazo=3):
    """Recalcula justificación según decisión y plazo calendario."""
    dias = dias_entre(fecha_ausencia, fecha_consulta)
    try:
        plazo = int(plazo)
    except (ValueError, TypeError):
        return "Fecha inválida"
    if dias == -999999 or plazo < 0:
        return "Fecha inválida"
    if aprobada:
        return "Justificada"
    if rechazada or dias > plazo:
        return "Injustificada"
    return "Pendiente de justificar"


def buscar_usuario(usuario):
    """Busca un usuario y retorna su fila o None."""
    for fila in leer_registros("usuarios"):
        if len(fila) >= 5 and fila[0] == usuario:
            return fila
    return None


def buscar_empleado(identificador):
    """Busca un empleado por ID y devuelve su fila o None."""
    for fila in leer_registros("empleados"):
        if len(fila) >= 10 and fila[0] == identificador:
            return fila
    return None


def tiene_permiso(usuario, roles):
    """Comprueba que el usuario está activo, sin bloqueo y autorizado."""
    fila = buscar_usuario(usuario)
    if fila is None:
        return False
    return fila[2] in roles and fila[3] == "Activo" and int(fila[4]) < 3


def registrar_bitacora(usuario, fecha, hora, accion):
    """Registra quién hizo qué y cuándo, según fecha y hora digitadas."""
    if not validar_fecha(fecha) or not validar_hora(hora):
        return False
    if not texto_valido(usuario) or not texto_valido(accion):
        return False
    return agregar_registro("bitacora", [usuario, fecha, hora, accion])


def iniciar_sesion(usuario, contrasena, fecha=None, hora=None):
    """Verifica credenciales; fecha y hora se obtienen automáticamente si se omiten."""
    if fecha is None:
        fecha = fecha_actual()
    if hora is None:
        hora = hora_actual()
    if not validar_fecha(fecha) or not validar_hora(hora):
        return False, "Fecha u hora inválida", ""
    filas = leer_registros("usuarios")
    for fila in filas:
        if len(fila) >= 5 and fila[0] == usuario:
            if fila[3] == "Inactivo":
                return False, "Usuario desactivado", ""
            if fila[3] == "Bloqueado" or int(fila[4]) >= 3:
                return False, "Usuario bloqueado. Contacte al administrador", ""
            if fila[1] != contrasena:
                fila[4] = str(int(fila[4]) + 1)
                if int(fila[4]) >= 3:
                    fila[3] = "Bloqueado"
                    mensaje = "Usuario bloqueado tras 3 intentos"
                else:
                    mensaje = "Contraseña incorrecta. Intento " + fila[4] + " de 3"
                if not guardar_registros("usuarios", filas):
                    return False, "Error al guardar intentos", ""
                registrar_bitacora(usuario, fecha, hora, "Acceso fallido")
                return False, mensaje, ""
            if fila[2] == "Empleado":
                empleado = buscar_empleado(usuario)
                if empleado is None or empleado[9] != "Activo":
                    return False, "Empleado desactivado o sin ficha", ""
            fila[4] = "0"
            if not guardar_registros("usuarios", filas):
                return False, "Error al guardar sesión", ""
            registrar_bitacora(usuario, fecha, hora, "Inicio de sesión")
            recalcular_estados(fecha)
            return True, "Acceso correcto", fila[2]
    return False, "Usuario inexistente", ""


def cerrar_sesion(usuario, fecha, hora):
    """Anota la salida del sistema en la bitácora."""
    return registrar_bitacora(usuario, fecha, hora, "Cierre de sesión")


def validar_datos_empleado(datos):
    """Comprueba los nueve datos editables de cada empleado."""
    if len(datos) != 9:
        return False, "Se necesitan nueve campos"
    for dato in datos:
        if not texto_valido(dato):
            return False, "No se permiten campos vacíos ni punto y coma"
    if "@" not in datos[5] or "." not in datos[5].split("@")[1]:
        return False, "Correo electrónico inválido"
    if not validar_fecha(datos[7]):
        return False, "Fecha de ingreso inválida"
    if datos[8] != "Activo" and datos[8] != "Inactivo":
        return False, "Estado inválido"
    return True, "Datos válidos"


def consultar_empleados(operador):
    """Devuelve empleados para administrador o supervisor, o su propia ficha."""
    if tiene_permiso(operador, ["Administrador", "Supervisor"]):
        return leer_registros("empleados")
    if tiene_permiso(operador, ["Empleado"]):
        empleado = buscar_empleado(operador)
        if empleado is not None:
            return [empleado]
    return []


def crear_empleado(operador, identificador, datos, fecha, hora):
    """Crea un empleado si el documento y el ID no están registrados."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    if not validar_identificador(identificador):
        return False, "ID inválido: use solo letras, números, _ y -"
    valido, mensaje = validar_datos_empleado(datos)
    if not valido:
        return False, mensaje
    empleados = leer_registros("empleados")
    for fila in empleados:
        if fila[0] == identificador or fila[1] == datos[0]:
            return False, "ID o documento repetido"
    empleados.append([identificador] + datos)
    if not guardar_registros("empleados", empleados):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Creó empleado " + identificador)
    return True, "Empleado creado"


def editar_empleado(operador, identificador, datos, fecha, hora):
    """Actualiza datos sin eliminar el historial del trabajador."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    valido, mensaje = validar_datos_empleado(datos)
    if not valido:
        return False, mensaje
    empleados = leer_registros("empleados")
    encontrado = False
    for fila in empleados:
        if fila[0] != identificador and fila[1] == datos[0]:
            return False, "Documento repetido"
        if fila[0] == identificador:
            encontrado = True
    if not encontrado:
        return False, "Empleado inexistente"
    for fila in empleados:
        if fila[0] == identificador:
            indice = 0
            while indice < 9:
                fila[indice + 1] = datos[indice]
                indice = indice + 1
    if not guardar_registros("empleados", empleados):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Editó empleado " + identificador)
    return True, "Empleado actualizado"


def desactivar_empleado(operador, identificador, fecha, hora):
    """Desactiva una ficha y conserva registros anteriores."""
    fila = buscar_empleado(identificador)
    if fila is None:
        return False, "Empleado inexistente"
    datos = []
    indice = 1
    while indice < 10:
        datos.append(fila[indice])
        indice = indice + 1
    datos[8] = "Inactivo"
    correcto, mensaje = editar_empleado(operador, identificador, datos, fecha, hora)
    if correcto:
        registrar_bitacora(operador, fecha, hora, "Desactivó empleado " + identificador)
    return correcto, mensaje


def consultar_usuarios(operador):
    """Entrega la lista de cuentas solo al administrador."""
    if not tiene_permiso(operador, ["Administrador"]):
        return []
    return leer_registros("usuarios")


def crear_usuario(operador, usuario, contrasena, rol, fecha, hora):
    """Crea una cuenta; el usuario de empleado debe ser su ID."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    if not validar_identificador(usuario) or not texto_valido(contrasena):
        return False, "Usuario inválido o contraseña vacía"
    if rol not in ["Administrador", "Supervisor", "Empleado"]:
        return False, "Rol inválido"
    if buscar_usuario(usuario) is not None:
        return False, "El usuario ya existe"
    if rol == "Empleado":
        ficha = buscar_empleado(usuario)
        if ficha is None or ficha[9] != "Activo":
            return False, "La cuenta Empleado debe usar el ID de un empleado activo"
    if not agregar_registro("usuarios", [usuario, contrasena, rol, "Activo", "0"]):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Creó cuenta " + usuario)
    return True, "Usuario creado"


def modificar_usuario(operador, usuario, accion, valor, fecha, hora):
    """Cambia clave, rol, activación o bloqueo de una cuenta."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    filas = leer_registros("usuarios")
    encontrada = False
    for fila in filas:
        if len(fila) >= 5 and fila[0] == usuario:
            encontrada = True
            if accion == "clave":
                if not texto_valido(valor):
                    return False, "Clave inválida"
                fila[1] = valor
            elif accion == "rol":
                if valor not in ["Administrador", "Supervisor", "Empleado"]:
                    return False, "Rol inválido"
                if usuario == operador and valor != "Administrador":
                    return False, "No puede retirarse su propio rol administrador"
                if valor == "Empleado" and buscar_empleado(usuario) is None:
                    return False, "El nombre de la cuenta debe coincidir con un ID de empleado"
                fila[2] = valor
            elif accion == "estado":
                if valor not in ["Activo", "Inactivo"]:
                    return False, "Estado inválido"
                if usuario == operador and valor == "Inactivo":
                    return False, "No puede desactivar su propia cuenta"
                fila[3] = valor
                if valor == "Activo":
                    fila[4] = "0"
            elif accion == "desbloquear":
                fila[3] = "Activo"
                fila[4] = "0"
            else:
                return False, "Acción no permitida"
    if not encontrada:
        return False, "Usuario inexistente"
    if not guardar_registros("usuarios", filas):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Cuenta " + usuario + ": " + accion)
    return True, "Cuenta actualizada"


def configurar_horario(operador, datos, fecha, hora):
    """Valida y guarda entrada, salida, tolerancia, extra y plazo."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    if len(datos) != 5:
        return False, "Configuración incompleta"
    if not validar_hora(datos[0]) or not validar_hora(datos[1]) or not validar_hora(datos[3]):
        return False, "Hora inválida"
    try:
        tolerancia = int(datos[2])
        plazo = int(datos[4])
        if tolerancia < 0 or tolerancia > 120 or plazo < 0 or plazo > 60:
            return False, "Tolerancia o plazo fuera de rango"
    except ValueError:
        return False, "Tolerancia y plazo deben ser enteros"
    if a_minutos(datos[0]) >= a_minutos(datos[1]) or a_minutos(datos[1]) > a_minutos(datos[3]):
        return False, "El orden de las horas es incorrecto"
    if not guardar_registros("horario", datos_en_lista(datos)):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Cambió horario")
    return True, "Horario actualizado"


def datos_en_lista(datos):
    """Convierte una fila en una lista de filas para guardarla."""
    return [datos]


def buscar_asistencia(identificador, fecha):
    """Obtiene el registro diario de asistencia, o None."""
    for fila in leer_registros("asistencias"):
        if len(fila) >= 12 and fila[0] == identificador and fila[1] == fecha:
            return fila
    return None


def buscar_justificacion(identificador, fecha):
    """Encuentra una justificación enviada para una ausencia."""
    for fila in leer_registros("justificaciones"):
        if len(fila) >= 9 and fila[1] == identificador and fila[2] == fecha:
            return fila
    return None


CARPETA_EVIDENCIAS = "evidencias"
EXTENSIONES_IMAGEN = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]


def es_fotografia_valida(ruta):
    """Comprueba que exista un archivo de imagen con extensión y firma válidas."""
    if not ruta or not os.path.isfile(ruta):
        return False
    extension = os.path.splitext(ruta)[1].lower()
    if extension not in EXTENSIONES_IMAGEN:
        return False
    try:
        archivo = open(ruta, "rb")
        encabezado = archivo.read(12)
        archivo.close()
    except OSError:
        return False
    if extension in [".jpg", ".jpeg"]:
        return len(encabezado) >= 3 and encabezado[:3] == b"\xff\xd8\xff"
    if extension == ".png":
        return encabezado[:8] == b"\x89PNG\r\n\x1a\n"
    if extension == ".bmp":
        return encabezado[:2] == b"BM"
    if extension == ".gif":
        return encabezado[:6] in [b"GIF87a", b"GIF89a"]
    if extension == ".webp":
        return len(encabezado) >= 12 and encabezado[:4] == b"RIFF" and encabezado[8:12] == b"WEBP"
    return False


def fotografias_iguales(ruta_a, ruta_b):
    """Compara el contenido de dos archivos para impedir reutilizar la misma foto."""
    try:
        if not os.path.isfile(ruta_a) or not os.path.isfile(ruta_b):
            return False
        if os.path.getsize(ruta_a) != os.path.getsize(ruta_b):
            return False
        hash_a = hashlib.sha256()
        hash_b = hashlib.sha256()
        with open(ruta_a, "rb") as archivo_a, open(ruta_b, "rb") as archivo_b:
            bloque_a = archivo_a.read(65536)
            bloque_b = archivo_b.read(65536)
            while bloque_a != b"" or bloque_b != b"":
                hash_a.update(bloque_a)
                hash_b.update(bloque_b)
                bloque_a = archivo_a.read(65536)
                bloque_b = archivo_b.read(65536)
        return hash_a.digest() == hash_b.digest()
    except OSError:
        return False


def guardar_fotografia_evidencia(operador, tipo, ruta_origen, instante):
    """Copia la fotografía seleccionada a la carpeta interna de evidencias."""
    if not es_fotografia_valida(ruta_origen):
        return False, "Debes adjuntar una fotografía válida en JPG, PNG, BMP, GIF o WEBP."
    try:
        if not os.path.isdir(CARPETA_EVIDENCIAS):
            os.makedirs(CARPETA_EVIDENCIAS)
        extension = os.path.splitext(ruta_origen)[1].lower()
        sello = instante.strftime("%Y%m%d_%H%M%S_%f")
        nombre_archivo = operador + "_" + tipo.lower() + "_" + sello + extension
        destino = os.path.join(CARPETA_EVIDENCIAS, nombre_archivo)
        shutil.copy2(ruta_origen, destino)
        return True, destino
    except OSError:
        return False, "No fue posible guardar la fotografía en la carpeta de evidencias."


def evidencia_de(nombre, fecha, hora, tipo, foto):
    """Arma el texto de evidencia asociado al archivo de imagen guardado."""
    return nombre + " | " + fecha + " | " + hora + " | " + tipo + " | Foto: " + foto


def registrar_asistencia(operador, tipo, foto=""):
    """Registra entrada o salida con foto obligatoria y hora capturada internamente."""
    # Fecha y hora se capturan dentro de la lógica, nunca desde un campo editable.
    instante = datetime.now()
    fecha = instante.strftime("%Y-%m-%d")
    hora = instante.strftime("%H:%M")
    if not tiene_permiso(operador, ["Empleado"]):
        return False, "Solo el empleado puede registrar su asistencia"
    ficha = buscar_empleado(operador)
    if ficha is None or ficha[9] != "Activo":
        return False, "Empleado inexistente o inactivo"
    if not validar_fecha(fecha) or not validar_hora(hora):
        return False, "Fecha u hora inválida"
    if fecha < ficha[8]:
        return False, "La fecha es anterior al ingreso"
    if not es_laborable(fecha):
        return False, "El horario contempla lunes a viernes"
    if tipo not in ["Entrada", "Salida"]:
        return False, "Tipo de registro inválido"
    if not foto:
        return False, "Debes adjuntar una fotografía para registrar la " + tipo.lower() + "."

    horario = obtener_horario()
    registros = leer_registros("asistencias")
    fila = None
    for registro in registros:
        if len(registro) >= 12 and registro[0] == operador and registro[1] == fecha:
            fila = registro
            break

    # Verifica las reglas de la marcación antes de copiar el archivo.
    if tipo == "Entrada":
        if fila is not None and fila[2] != "":
            return False, "No se permite doble entrada el mismo día"
        if fila is None:
            fila = [operador, fecha, "", "", "", "", "0", "0", "", "", "", ""]
            registros.append(fila)
    else:
        if fila is None or fila[2] == "":
            return False, "No se permite salida sin entrada"
        if fila[3] != "":
            return False, "No se permite doble salida el mismo día"
        if fila[10] != "" and fotografias_iguales(foto, fila[10]):
            return False, "La fotografía de salida debe ser diferente a la fotografía de entrada."
        minutos = a_minutos(hora) - a_minutos(fila[2])
        if minutos < 0:
            return False, "La salida no puede ser anterior a la entrada"

    correcto_foto, ruta_guardada = guardar_fotografia_evidencia(operador, tipo, foto, instante)
    if not correcto_foto:
        return False, ruta_guardada

    nombre = ficha[2] + " " + ficha[3]
    evidencia = evidencia_de(nombre, fecha, hora, tipo, ruta_guardada)
    if tipo == "Entrada":
        fila[2] = hora
        fila[4] = clasificar_entrada(hora, horario[0], horario[2])
        fila[5] = "Pendiente"
        fila[8] = evidencia
        fila[10] = ruta_guardada
    else:
        fila[3] = hora
        fila[5] = clasificar_salida(hora, horario[1], horario[3])
        fila[6] = str(minutos)
        fila[7] = str(calcular_hora_extra(hora, horario[3]))
        fila[9] = evidencia
        fila[11] = ruta_guardada

    if not guardar_registros("asistencias", registros):
        try:
            os.remove(ruta_guardada)
        except OSError:
            pass
        return False, "No se pudo guardar la asistencia. La fotografía no se conservó."
    registrar_bitacora(operador, fecha, hora, "Registró " + tipo)
    return True, tipo + " guardada correctamente con fotografía de evidencia."


def nueva_ausencia(identificador, fecha, estado):
    """Construye la fila de ausencia compatible con asistencias.txt."""
    return [identificador, fecha, "", "", estado, "No aplica", "0", "0", "", "", "", ""]


def recalcular_estados(fecha_consulta):
    """Completa ausencias y marca salidas omitidas de días anteriores."""
    if not validar_fecha(fecha_consulta):
        return False, "Fecha inválida"
    filas = leer_registros("asistencias")
    justificantes = leer_registros("justificaciones")
    empleados = leer_registros("empleados")
    horario = obtener_horario()
    por_dia = {}
    decisiones = {}
    for fila in filas:
        if len(fila) >= 12:
            clave = fila[0] + "|" + fila[1]
            por_dia[clave] = fila
            if fila[2] != "" and fila[3] == "" and fila[1] < fecha_consulta:
                fila[5] = "Sin salida"
    for justificacion in justificantes:
        if len(justificacion) >= 9:
            clave = justificacion[1] + "|" + justificacion[2]
            decisiones[clave] = justificacion[6]
    for empleado in empleados:
        if len(empleado) < 10 or empleado[9] != "Activo":
            continue
        inicio = empleado[8]
        if not validar_fecha(inicio) or inicio > fecha_consulta:
            continue
        fecha = inicio
        while fecha != "" and fecha <= fecha_consulta:
            if es_laborable(fecha):
                clave = empleado[0] + "|" + fecha
                if clave in por_dia:
                    existente = por_dia[clave]
                else:
                    existente = nueva_ausencia(empleado[0], fecha, "Pendiente de justificar")
                    filas.append(existente)
                    por_dia[clave] = existente
                if existente[2] == "":
                    decision = ""
                    if clave in decisiones:
                        decision = decisiones[clave]
                    existente[4] = estado_ausencia(fecha, fecha_consulta, decision == "Aprobado", decision == "Rechazado", horario[4])
            fecha = sumar_dias(fecha, 1)
    if not guardar_registros("asistencias", filas):
        return False, "Error al actualizar asistencias"
    return True, "Estados actualizados"


def registrar_justificacion(operador, fecha_ausencia, tipo, descripcion, soporte, fecha_actual, hora_actual):
    """Registra excusa dentro de plazo para una ausencia laborable."""
    if not tiene_permiso(operador, ["Empleado"]):
        return False, "Permiso denegado"
    if not validar_fecha(fecha_ausencia) or not validar_fecha(fecha_actual) or not validar_hora(hora_actual):
        return False, "Fecha u hora inválida"
    if tipo not in ["Incapacidad médica", "Vacaciones", "Permiso personal", "Comisión laboral"]:
        return False, "Tipo de justificación inválido"
    if not texto_valido(descripcion):
        return False, "Descripción obligatoria"
    if ";" in soporte or "\n" in soporte:
        return False, "Soporte inválido"
    empleado = buscar_empleado(operador)
    if empleado is None or empleado[9] != "Activo" or fecha_ausencia < empleado[8] or not es_laborable(fecha_ausencia):
        return False, "La ausencia debe ser laborable y posterior al ingreso"
    dias = dias_entre(fecha_ausencia, fecha_actual)
    plazo = int(obtener_horario()[4])
    if dias < 0:
        return False, "No se justifican fechas futuras"
    if dias > plazo:
        return False, "Plazo vencido: máximo " + str(plazo) + " días"
    registro = buscar_asistencia(operador, fecha_ausencia)
    if registro is not None and registro[2] != "":
        return False, "Ya hay una entrada registrada ese día"
    if buscar_justificacion(operador, fecha_ausencia) is not None:
        return False, "Ya existe una justificación para esa fecha"
    existentes = leer_registros("justificaciones")
    identificador = "J" + str(len(existentes) + 1)
    while True:
        repetido = False
        for fila in existentes:
            if fila[0] == identificador:
                repetido = True
                break
        if not repetido:
            break
        identificador = identificador + "1"
    nueva = [identificador, operador, fecha_ausencia, tipo, descripcion, soporte, "Pendiente", "", fecha_actual]
    if not agregar_registro("justificaciones", nueva):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha_actual, hora_actual, "Radicó justificación " + identificador)
    recalcular_estados(fecha_actual)
    return True, "Justificación enviada: " + identificador


def consultar_justificaciones(operador):
    """Supervisor revisa todas; empleado ve las propias."""
    if tiene_permiso(operador, ["Supervisor", "Administrador"]):
        return leer_registros("justificaciones")
    if tiene_permiso(operador, ["Empleado"]):
        resultado = []
        for fila in leer_registros("justificaciones"):
            if len(fila) >= 9 and fila[1] == operador:
                resultado.append(fila)
        return resultado
    return []


def resolver_justificacion(operador, identificador, decision, comentario, fecha, hora):
    """Supervisor aprueba o rechaza una justificación pendiente."""
    if not tiene_permiso(operador, ["Supervisor"]):
        return False, "Solo un supervisor puede resolver justificaciones"
    if decision not in ["Aprobado", "Rechazado"]:
        return False, "Decisión inválida"
    if ";" in comentario or "\n" in comentario:
        return False, "Comentario inválido"
    filas = leer_registros("justificaciones")
    encontrada = False
    for fila in filas:
        if len(fila) >= 9 and fila[0] == identificador:
            if fila[6] != "Pendiente":
                return False, "La justificación ya fue resuelta"
            fila[6] = decision
            fila[7] = comentario
            encontrada = True
    if not encontrada:
        return False, "Justificación inexistente"
    if not guardar_registros("justificaciones", filas):
        return False, "Error de archivo"
    registrar_bitacora(operador, fecha, hora, "Justificación " + identificador + " " + decision)
    recalcular_estados(fecha)
    return True, "Justificación " + decision


def rango_periodo(periodo, fecha):
    """Devuelve fechas de inicio y fin para día, semana, mes o año."""
    if not validar_fecha(fecha):
        return "", ""
    if periodo == "Diario":
        return fecha, fecha
    if periodo == "Semanal":
        inicio = sumar_dias(fecha, 0 - dia_de_la_semana(fecha))
        return inicio, sumar_dias(inicio, 6)
    if periodo == "Mensual":
        partes = fecha.split("-")
        inicio = partes[0] + "-" + partes[1] + "-01"
        fin = fecha_de_numero(numero_de_dia(inicio) + dias_del_mes(int(partes[0]), int(partes[1])) - 1)
        return inicio, fin
    if periodo == "Anual":
        anio = fecha.split("-")[0]
        return anio + "-01-01", anio + "-12-31"
    return "", ""


def historial_empleado(operador, identificador, inicio, fin):
    """Filtra asistencias por ID y rango con controles de permiso."""
    if not tiene_permiso(operador, ["Administrador", "Supervisor"]):
        if not tiene_permiso(operador, ["Empleado"]) or operador != identificador:
            return []
    if not validar_fecha(inicio) or not validar_fecha(fin) or inicio > fin:
        return []
    resultado = []
    for fila in leer_registros("asistencias"):
        if len(fila) >= 12 and fila[0] == identificador and inicio <= fila[1] <= fin:
            resultado.append(fila)
    return resultado


def calcular_estadisticas(filas):
    """Suma minutos trabajados, extra, retardos, ausencias y puntualidad."""
    normales = 0
    extras = 0
    puntuales = 0
    retardos = 0
    ausencias = 0
    justificadas = 0
    sin_salida = 0
    for fila in filas:
        if len(fila) < 12:
            continue
        if fila[4] == "Puntual":
            puntuales = puntuales + 1
        elif fila[4] == "Retardo":
            retardos = retardos + 1
        elif fila[2] == "":
            ausencias = ausencias + 1
            if fila[4] == "Justificada":
                justificadas = justificadas + 1
        if fila[5] == "Sin salida":
            sin_salida = sin_salida + 1
        try:
            normales = normales + int(fila[6])
            extras = extras + int(fila[7])
        except ValueError:
            pass
    porcentaje = 0
    if puntuales + retardos > 0:
        porcentaje = puntuales * 100 // (puntuales + retardos)
    return {"minutos": normales, "extras": extras, "puntuales": puntuales,
            "retardos": retardos, "ausencias": ausencias,
            "justificadas": justificadas, "sin_salida": sin_salida,
            "puntualidad": porcentaje}


def estadisticas_empleado(operador, identificador, inicio, fin):
    """Devuelve indicadores individuales a partir de historial autorizado."""
    return calcular_estadisticas(historial_empleado(operador, identificador, inicio, fin))


def asistencias_por_dia_semana(filas):
    """Agrupa asistencias en un arreglo bidimensional de siete listas."""
    matriz = [[], [], [], [], [], [], []]
    for fila in filas:
        if len(fila) >= 12:
            indice = dia_de_la_semana(fila[1])
            if indice >= 0:
                matriz[indice].append(fila)
    return matriz


def estadisticas_generales(operador, inicio, fin):
    """Identifica líderes de puntualidad, tiempo trabajado y retardos."""
    if not tiene_permiso(operador, ["Administrador", "Supervisor"]):
        return {}
    mas_puntual = "Sin datos"
    mas_horas = "Sin datos"
    mas_retardos = "Sin datos"
    mejor = -1
    horas_mayores = -1
    retardos_mayores = -1
    distribucion = [[], [], [], [], [], [], []]
    for empleado in leer_registros("empleados"):
        if len(empleado) < 10:
            continue
        filas = historial_empleado(operador, empleado[0], inicio, fin)
        indicadores = calcular_estadisticas(filas)
        nombre = empleado[2] + " " + empleado[3]
        if indicadores["puntuales"] + indicadores["retardos"] > 0 and indicadores["puntualidad"] > mejor:
            mejor = indicadores["puntualidad"]
            mas_puntual = nombre
        if indicadores["minutos"] > horas_mayores:
            horas_mayores = indicadores["minutos"]
            mas_horas = nombre
        if indicadores["retardos"] > retardos_mayores:
            retardos_mayores = indicadores["retardos"]
            mas_retardos = nombre
        matriz_empleado = asistencias_por_dia_semana(filas)
        indice = 0
        while indice < 7:
            for fila in matriz_empleado[indice]:
                distribucion[indice].append(fila)
            indice = indice + 1
    return {"mas_puntual": mas_puntual, "mas_horas": mas_horas,
            "mas_retardos": mas_retardos, "por_dia": distribucion}


def resumen_dashboard(operador, fecha):
    """Cuenta empleados activos, presentes, ausentes, retardos y extras."""
    if not validar_fecha(fecha):
        return {}
    if not tiene_permiso(operador, ["Administrador", "Supervisor", "Empleado"]):
        return {}
    admin = tiene_permiso(operador, ["Administrador", "Supervisor"])
    resultado = {"activos": 0, "presentes": 0, "ausentes": 0, "retardos": 0,
                 "extra": 0, "puntuales": 0}
    for empleado in leer_registros("empleados"):
        if len(empleado) < 10 or empleado[9] != "Activo":
            continue
        if not admin and empleado[0] != operador:
            continue
        resultado["activos"] = resultado["activos"] + 1
        if empleado[8] > fecha or not es_laborable(fecha):
            continue
        fila = buscar_asistencia(empleado[0], fecha)
        if fila is None or fila[2] == "":
            resultado["ausentes"] = resultado["ausentes"] + 1
        else:
            resultado["presentes"] = resultado["presentes"] + 1
            if fila[4] == "Puntual":
                resultado["puntuales"] = resultado["puntuales"] + 1
            if fila[4] == "Retardo":
                resultado["retardos"] = resultado["retardos"] + 1
            try:
                resultado["extra"] = resultado["extra"] + int(fila[7])
            except ValueError:
                pass
    return resultado


def minutos_a_texto(minutos):
    """Representa minutos como horas y minutos, sin decimales."""
    return str(minutos // 60) + "h " + str(minutos % 60) + "min"


def crear_reporte(operador, periodo, fecha, identificador="", hora_actual="08:00"):
    """Prepara y guarda un reporte de texto con detalle e indicadores."""
    if not tiene_permiso(operador, ["Administrador", "Supervisor"]):
        return False, "Permiso denegado", ""
    if periodo not in ["Diario", "Semanal", "Mensual", "Individual"]:
        return False, "Periodo inválido", ""
    if periodo == "Individual":
        if buscar_empleado(identificador) is None:
            return False, "Empleado inexistente", ""
        inicio, fin = rango_periodo("Mensual", fecha)
    else:
        inicio, fin = rango_periodo(periodo, fecha)
    if inicio == "":
        return False, "Fecha inválida", ""
    lineas = []
    lineas.append("KRONVIA | GESTIÓN DE ASISTENCIA")
    lineas.append("REPORTE " + periodo + " | " + inicio + " a " + fin)
    lineas.append("Generado por: " + operador)
    lineas.append("=" * 92)
    lineas.append("ID | FECHA | ENTRADA | SALIDA | ESTADO ENTRADA | ESTADO SALIDA | TRABAJO | EXTRA")
    todos = []
    for empleado in leer_registros("empleados"):
        if len(empleado) < 10:
            continue
        if periodo == "Individual" and empleado[0] != identificador:
            continue
        filas = historial_empleado(operador, empleado[0], inicio, fin)
        for fila in filas:
            todos.append(fila)
            lineas.append(fila[0] + " | " + fila[1] + " | " + fila[2] + " | " + fila[3] + " | " + fila[4] + " | " + fila[5] + " | " + minutos_a_texto(int(fila[6])) + " | " + minutos_a_texto(int(fila[7])))
    indicadores = calcular_estadisticas(todos)
    lineas.append("=" * 92)
    lineas.append("Registros: " + str(len(todos)))
    lineas.append("Puntuales: " + str(indicadores["puntuales"]) + " | Retardos: " + str(indicadores["retardos"]) + " | Ausencias: " + str(indicadores["ausencias"]))
    lineas.append("Justificadas: " + str(indicadores["justificadas"]) + " | Sin salida: " + str(indicadores["sin_salida"]))
    lineas.append("Tiempo trabajado: " + minutos_a_texto(indicadores["minutos"]) + " | Extra: " + minutos_a_texto(indicadores["extras"]))
    lineas.append("Puntualidad: " + str(indicadores["puntualidad"]) + "%")
    if periodo != "Individual":
        generales = estadisticas_generales(operador, inicio, fin)
        lineas.append("Más puntual: " + generales["mas_puntual"])
        lineas.append("Más horas: " + generales["mas_horas"])
        lineas.append("Más retardos: " + generales["mas_retardos"])
    contenido = "\n".join(lineas) + "\n"
    etiquetas = {"Diario": "diario", "Semanal": "semanal", "Mensual": "mensual", "Individual": "individual"}
    nombre = "reporte_" + etiquetas[periodo] + "_" + fecha
    if periodo == "Individual":
        nombre = nombre + "_" + identificador
    nombre = nombre + ".txt"
    try:
        archivo = open(nombre, "w", encoding="utf-8")
        archivo.write(contenido)
        archivo.close()
    except OSError:
        return False, "No se pudo guardar el reporte", contenido
    registrar_bitacora(operador, fecha, hora_actual, "Generó reporte " + periodo)
    return True, nombre, contenido


def consultar_bitacora(operador):
    """Permite ver el registro de actividad solo al administrador."""
    if not tiene_permiso(operador, ["Administrador"]):
        return []
    return leer_registros("bitacora")


def nombre_respaldo(nombre, fecha):
    """Construye el nombre de una copia fechada del archivo."""
    return nombre + "_respaldo_" + fecha + ".txt"


def nombre_respaldo_evidencias(fecha):
    """Construye el nombre de la carpeta de fotografías respaldadas."""
    return "evidencias_respaldo_" + fecha


def crear_respaldo(operador, fecha, hora):
    """Copia los archivos de datos y las fotografías de evidencia."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    if not validar_fecha(fecha) or not validar_hora(hora):
        return False, "Fecha u hora inválida"
    destino_fotos = nombre_respaldo_evidencias(fecha)
    for nombre in ARCHIVOS:
        destino = nombre_respaldo(nombre, fecha)
        if os.path.exists(destino):
            return False, "Ya existe respaldo para esa fecha: " + destino
    if os.path.exists(destino_fotos):
        return False, "Ya existe respaldo de fotografías para esa fecha"

    creados = []
    try:
        for nombre in ARCHIVOS:
            origen = open(ARCHIVOS[nombre], "r", encoding="utf-8")
            contenido = origen.read()
            origen.close()
            destino = nombre_respaldo(nombre, fecha)
            archivo = open(destino, "w", encoding="utf-8")
            archivo.write(contenido)
            archivo.close()
            creados.append(destino)
        if os.path.isdir(CARPETA_EVIDENCIAS):
            shutil.copytree(CARPETA_EVIDENCIAS, destino_fotos)
        else:
            os.makedirs(destino_fotos)
        creados.append(destino_fotos)
    except OSError:
        for elemento in creados:
            try:
                if os.path.isdir(elemento):
                    shutil.rmtree(elemento)
                elif os.path.isfile(elemento):
                    os.remove(elemento)
            except OSError:
                pass
        return False, "No fue posible completar el respaldo de datos y fotografías"

    registrar_bitacora(operador, fecha, hora, "Creó respaldo " + fecha)
    return True, "Respaldo de datos y fotografías creado para " + fecha


def restaurar_respaldo(operador, fecha_respaldo, fecha_actual, hora_actual):
    """Restaura datos y, si existe, la carpeta de fotografías del respaldo."""
    if not tiene_permiso(operador, ["Administrador"]):
        return False, "Permiso denegado"
    if not validar_fecha(fecha_respaldo) or not validar_fecha(fecha_actual) or not validar_hora(hora_actual):
        return False, "Fecha u hora inválida"
    contenidos = {}
    for nombre in ARCHIVOS:
        try:
            archivo = open(nombre_respaldo(nombre, fecha_respaldo), "r", encoding="utf-8")
            contenidos[nombre] = archivo.read()
            archivo.close()
        except OSError:
            return False, "Falta copia de " + nombre

    respaldo_fotos = nombre_respaldo_evidencias(fecha_respaldo)
    carpeta_temporal = CARPETA_EVIDENCIAS + "_restauracion_temporal"
    tiene_respaldo_fotos = os.path.isdir(respaldo_fotos)
    if tiene_respaldo_fotos:
        try:
            if os.path.isdir(carpeta_temporal):
                shutil.rmtree(carpeta_temporal)
            shutil.copytree(respaldo_fotos, carpeta_temporal)
        except OSError:
            return False, "No fue posible preparar la restauración de fotografías"

    for nombre in ARCHIVOS:
        try:
            archivo = open(ARCHIVOS[nombre], "w", encoding="utf-8")
            archivo.write(contenidos[nombre])
            archivo.close()
        except OSError:
            if os.path.isdir(carpeta_temporal):
                shutil.rmtree(carpeta_temporal)
            return False, "Error al restaurar " + nombre

    if tiene_respaldo_fotos:
        try:
            if os.path.isdir(CARPETA_EVIDENCIAS):
                shutil.rmtree(CARPETA_EVIDENCIAS)
            os.replace(carpeta_temporal, CARPETA_EVIDENCIAS)
        except OSError:
            return False, "Los datos se restauraron, pero no fue posible reemplazar las fotografías"

    registrar_bitacora(operador, fecha_actual, hora_actual, "Restauró respaldo " + fecha_respaldo)
    if tiene_respaldo_fotos:
        return True, "Respaldo de datos y fotografías restaurado. Vuelva a iniciar sesión"
    return True, "Datos restaurados. Este respaldo antiguo no contenía fotografías; se conservaron las evidencias actuales."


def menu_consola():
    """Menú sencillo para comprobar reglas sin iniciar Tkinter."""
    correcto, mensaje = inicializar_archivos()
    print(mensaje)
    if not correcto:
        return
    usuario = ""
    rol = ""
    fecha = FECHA_SUGERIDA
    hora = "08:00"
    while True:
        print("\n--- MENÚ DE CONSOLA ---")
        print("1) Iniciar sesión | 2) Ver empleados | 3) Registrar entrada")
        print("4) Registrar salida | 5) Ver historial | 6) Ver resumen | 0) Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            print("Hasta pronto")
            break
        if opcion == "1":
            usuario_nuevo = input("Usuario: ").strip()
            clave = input("Contraseña: ")
            fecha = input("Fecha AAAA-MM-DD: ").strip()
            hora = input("Hora HH:MM: ").strip()
            correcto, mensaje, rol_nuevo = iniciar_sesion(usuario_nuevo, clave, fecha, hora)
            print(mensaje)
            if correcto:
                usuario = usuario_nuevo
                rol = rol_nuevo
        elif usuario == "":
            print("Primero debe iniciar sesión")
        elif opcion == "2":
            for empleado in consultar_empleados(usuario):
                print(empleado[0], empleado[2], empleado[3], empleado[9])
        elif opcion == "3" or opcion == "4":
            tipo = "Entrada"
            if opcion == "4":
                tipo = "Salida"
            foto = input("Ruta de la fotografía de evidencia (JPG/PNG): ").strip()
            correcto, mensaje = registrar_asistencia(usuario, tipo, foto)
            print(mensaje)
        elif opcion == "5":
            id_empleado = input("ID del empleado: ").strip()
            inicio = input("Fecha inicial: ").strip()
            fin = input("Fecha final: ").strip()
            for fila in historial_empleado(usuario, id_empleado, inicio, fin):
                print(" | ".join(fila))
        elif opcion == "6":
            fecha = input("Fecha a consultar: ").strip()
            print("Rol:", rol, "Indicadores:", resumen_dashboard(usuario, fecha))
        else:
            print("Opción inválida")


if __name__ == "__main__":
    menu_consola()
