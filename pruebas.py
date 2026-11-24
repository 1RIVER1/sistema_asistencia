"""Pruebas sencillas: ejecutar con python pruebas.py, sin instalar librerías."""
import funciones


def comprobar(nombre, condicion):
    """Imprime OK o ERROR para cada situación comprobada."""
    if condicion:
        print("OK - " + nombre)
    else:
        print("ERROR - " + nombre)


def ejecutar_pruebas():
    """Comprueba reglas y restaura los seis archivos al finalizar."""
    correcto, mensaje = funciones.inicializar_archivos()
    if not correcto:
        print("ERROR - Inicialización: " + mensaje)
        return
    copias = {}
    for nombre in funciones.ARCHIVOS:
        archivo = open(funciones.ARCHIVOS[nombre], "r", encoding="utf-8")
        copias[nombre] = archivo.read()
        archivo.close()
    try:
        comprobar("Entrada 08:03 puntual", funciones.clasificar_entrada("08:03") == "Puntual")
        comprobar("Entrada 08:10 retardo", funciones.clasificar_entrada("08:10") == "Retardo")
        comprobar("Salida 16:30 anticipada", funciones.clasificar_salida("16:30") == "Anticipada")
        comprobar("Salida 17:30 normal", funciones.clasificar_salida("17:30") == "Normal")
        comprobar("Salida 17:30 cero extra", funciones.calcular_hora_extra("17:30") == 0)
        comprobar("Salida 18:45 45 minutos extra", funciones.calcular_hora_extra("18:45") == 45)
        comprobar("Ausencia al día 2 pendiente", funciones.estado_ausencia("2026-11-16", "2026-11-18") == "Pendiente de justificar")
        comprobar("Ausencia al día 4 injustificada", funciones.estado_ausencia("2026-11-16", "2026-11-20") == "Injustificada")
        comprobar("Día lunes 2026-11-23", funciones.dia_de_la_semana("2026-11-23") == 0)
        comprobar("Día jueves bisiesto 2024-02-29", funciones.dia_de_la_semana("2024-02-29") == 3)
        comprobar("Rechaza 2026-02-29", not funciones.validar_fecha("2026-02-29"))
        comprobar("Sumar día bisiesto", funciones.sumar_dias("2024-02-28", 1) == "2024-02-29")
        comprobar("Restar año nuevo", funciones.sumar_dias("2026-01-01", -1) == "2025-12-31")
        comprobar("Dos días entre fechas", funciones.dias_entre("2026-11-16", "2026-11-18") == 2)
        correcto, mensaje, rol = funciones.iniciar_sesion("admin", "admin123", "2026-11-23", "08:00")
        comprobar("Login administrador", correcto and rol == "Administrador")
        correcto, mensaje = funciones.crear_usuario("admin", "prueba_bloqueo", "bien", "Supervisor", "2026-11-23", "08:00")
        comprobar("Crear cuenta para bloqueo", correcto)
        intento = 0
        while intento < 3:
            correcto, mensaje, rol = funciones.iniciar_sesion("prueba_bloqueo", "mal", "2026-11-23", "08:00")
            intento = intento + 1
        cuenta = funciones.buscar_usuario("prueba_bloqueo")
        comprobar("Tres claves incorrectas bloquean", cuenta is not None and cuenta[3] == "Bloqueado" and cuenta[4] == "3")
        correcto, mensaje, rol = funciones.iniciar_sesion("prueba_bloqueo", "bien", "2026-11-23", "08:00")
        comprobar("Login bloqueado denegado", not correcto and "bloqueado" in mensaje)
        correcto, mensaje = funciones.modificar_usuario("admin", "prueba_bloqueo", "desbloquear", "", "2026-11-23", "08:00")
        comprobar("Desbloqueo por administrador", correcto)
        correcto, mensaje, rol = funciones.iniciar_sesion("prueba_bloqueo", "bien", "2026-11-23", "08:00")
        comprobar("Login después de desbloqueo", correcto)
        correcto, mensaje, rol = funciones.iniciar_sesion("E001", "empleado123", "2026-11-23", "08:00")
        comprobar("Login empleado", correcto)
        correcto, mensaje = funciones.registrar_asistencia("E001", "2026-11-23", "08:03", "Entrada")
        comprobar("Primera entrada guardada", correcto)
        correcto, mensaje = funciones.registrar_asistencia("E001", "2026-11-23", "08:10", "Entrada")
        comprobar("Doble entrada rechazada", not correcto and "doble" in mensaje)
        correcto, mensaje = funciones.registrar_asistencia("E001", "2026-11-23", "18:45", "Salida")
        comprobar("Salida con extra almacenada", correcto and funciones.buscar_asistencia("E001", "2026-11-23")[7] == "45")
        correcto, mensaje = funciones.registrar_asistencia("E001", "2026-11-23", "18:50", "Salida")
        comprobar("Doble salida rechazada", not correcto)
        correcto, mensaje = funciones.registrar_justificacion("E002", "2026-11-16", "Permiso personal", "Cita familiar", "soporte.txt", "2026-11-18", "10:00")
        comprobar("Excusa a los 2 días aceptada", correcto)
        correcto, mensaje = funciones.registrar_justificacion("E002", "2026-11-17", "Permiso personal", "Cita familiar", "soporte.txt", "2026-11-21", "10:00")
        comprobar("Excusa a los 4 días rechazada", not correcto and "Plazo" in mensaje)
        correcto, mensaje = funciones.resolver_justificacion("supervisor", "J1", "Aprobado", "Procede", "2026-11-18", "11:00")
        comprobar("Supervisor aprueba excusa", correcto)
        ausencia = funciones.buscar_asistencia("E002", "2026-11-16")
        comprobar("Ausencia pasa a justificada", ausencia is not None and ausencia[4] == "Justificada")
        matriz = funciones.asistencias_por_dia_semana(funciones.leer_registros("asistencias"))
        comprobar("Matriz bidimensional de 7 días", len(matriz) == 7 and len(matriz[0]) > 0)
    finally:
        for nombre in funciones.ARCHIVOS:
            archivo = open(funciones.ARCHIVOS[nombre], "w", encoding="utf-8")
            archivo.write(copias[nombre])
            archivo.close()
        print("Archivos originales restaurados después de las pruebas")


if __name__ == "__main__":
    ejecutar_pruebas()
