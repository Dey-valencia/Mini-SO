"""Mini-SO en consola - Sistemas Operativos y Compiladores (UCC, 2026).
Integra: interprete de comandos, procesos (PCB), CPU por ticks, RAM y VFS."""

TAM_RAM = 16
ram = [None] * TAM_RAM      # cada casilla guarda el PID que la ocupa (o None)
pcb = {}                    # tabla de procesos: pid -> dict con el estado
cola_listos = []            # PIDs en estado Listo (orden de llegada)
en_ejecucion = None         # PID que tiene la CPU
vfs = {}                    # "disco" virtual: nombre -> texto
siguiente_pid = 1
reloj = 0                   # tick global del sistema


# ---------- RF-04: Gestion de memoria RAM (primer ajuste, bloques continuos) ----------
def reservar(pid, tamano):
    libres = 0
    for i in range(TAM_RAM):
        libres = libres + 1 if ram[i] is None else 0
        if libres == tamano:
            inicio = i - tamano + 1
            for j in range(inicio, i + 1):
                ram[j] = pid
            return inicio
    return -1


def liberar(pid):
    for i in range(TAM_RAM):
        if ram[i] == pid:
            ram[i] = None


# ---------- RF-02: Gestion de procesos ----------
def crear(nombre, tamano, duracion):
    global siguiente_pid
    inicio = reservar(siguiente_pid, tamano)
    if inicio < 0:
        print(f"Error: no hay {tamano} casillas continuas libres en la RAM.")
        return
    pid = siguiente_pid
    siguiente_pid += 1
    pcb[pid] = {"nombre": nombre, "tam": tamano, "inicio": inicio,
                "restante": duracion, "estado": "Listo"}
    cola_listos.append(pid)
    print(f"Proceso '{nombre}' creado: PID={pid}, RAM[{inicio}..{inicio + tamano - 1}], "
          f"{duracion} ticks.")


# ---------- RF-03: Control de CPU (avance manual por ticks) ----------
def step():
    global en_ejecucion, reloj
    if en_ejecucion is None and cola_listos:
        en_ejecucion = cola_listos.pop(0)
        pcb[en_ejecucion]["estado"] = "Ejecucion"
    if en_ejecucion is None:
        print("CPU ociosa: no hay procesos listos.")
        return
    reloj += 1
    p = pcb[en_ejecucion]
    p["restante"] -= 1
    print(f"[tick {reloj}] PID {en_ejecucion} ({p['nombre']}) ejecuta, "
          f"le quedan {p['restante']} ticks.")
    if p["restante"] == 0:
        p["estado"] = "Terminado"
        liberar(en_ejecucion)
        print(f"  -> PID {en_ejecucion} termino y libero su memoria.")
        en_ejecucion = None


# ---------- RF-05: Sistema de archivos virtual ----------
def guardar(nombre, texto):
    vfs[nombre] = texto
    print(f"Archivo '{nombre}' guardado ({len(texto)} caracteres).")


def ver(nombre):
    print(vfs[nombre] if nombre in vfs else f"Error: el archivo '{nombre}' no existe.")


# ---------- RNF-03: Visualizacion directa ----------
def mostrar_memoria():
    barra = "".join("." if c is None else str(c % 10) for c in ram)
    print(f"RAM [{barra}]  ocupadas={sum(c is not None for c in ram)}/{TAM_RAM}")


def mostrar_procesos():
    print("PID  NOMBRE       ESTADO      RAM        RESTANTE")
    for pid, p in pcb.items():
        rango = f"{p['inicio']}-{p['inicio'] + p['tam'] - 1}"
        print(f"{pid:<4} {p['nombre']:<12} {p['estado']:<11} {rango:<10} {p['restante']}")
    if not pcb:
        print("(sin procesos)")


AYUDA = """Comandos:
  crear <nombre> <tamano> [ticks]  crea un proceso y reserva RAM
  step                             avanza 1 tick de CPU
  ps                               tabla de procesos (PCB)
  mem                              estado de la RAM
  guardar <nombre> <texto...>      guarda un archivo en el VFS
  ver <nombre>                     muestra un archivo
  ls                               lista archivos del VFS
  help | salir"""


# ---------- RF-01: Interprete por consola ----------
def ejecutar(linea):
    partes = linea.split()
    if not partes:
        return True
    accion, args = partes[0].lower(), partes[1:]
    try:
        if accion == "crear":
            crear(args[0], int(args[1]), int(args[2]) if len(args) > 2 else 3)
        elif accion == "step":
            step()
        elif accion == "ps":
            mostrar_procesos()
        elif accion == "mem":
            mostrar_memoria()
        elif accion == "guardar":
            guardar(args[0], " ".join(args[1:]))
        elif accion == "ver":
            ver(args[0])
        elif accion == "ls":
            print(", ".join(vfs) if vfs else "(VFS vacio)")
        elif accion == "help":
            print(AYUDA)
        elif accion == "salir":
            return False
        else:
            print(f"Comando desconocido: '{accion}'. Escribe help.")
    except (IndexError, ValueError):
        print("Error: argumentos invalidos. Escribe help.")
    return True


def main():
    print("Mini-SO v0.2  (escribe 'help')")
    while True:
        try:
            if not ejecutar(input("mini-so> ")):
                break
        except EOFError:
            break


if __name__ == "__main__":
    main()
