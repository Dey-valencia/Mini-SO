"""Mini-SO en consola - Sistemas Operativos y Compiladores (UCC, 2026).
Integra: interprete de comandos, procesos (PCB), CPU Round Robin, RAM con compactacion y VFS."""

TAM_RAM = 16
ram = [None] * TAM_RAM      # cada casilla guarda el PID que la ocupa (o None)
pcb = {}                    # tabla de procesos: pid -> dict con el estado
cola_listos = []            # PIDs en estado Listo (orden de llegada)
en_ejecucion = None         # PID que tiene la CPU
vfs = {}                    # "disco" virtual: nombre -> texto
siguiente_pid = 1
reloj = 0                   # tick global del sistema
quantum = 2                 # ticks maximos seguidos por proceso (Round Robin)
usado = 0                   # ticks que lleva el proceso actual en la CPU


# ---------- RF-04: Gestion de memoria RAM (primer ajuste, bloques continuos) ----------
def reservar(pid, tamano):
    """Primer ajuste: reserva 'tamano' casillas continuas; devuelve la casilla inicial o -1."""
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


def compactar():
    """Desplaza los procesos activos al inicio de la RAM para eliminar la fragmentacion."""
    pos = 0
    activos = [p for p in pcb if pcb[p]["estado"] in ("Listo", "Ejecucion")]
    for pid in sorted(activos, key=lambda p: pcb[p]["inicio"]):
        liberar(pid)
        for j in range(pos, pos + pcb[pid]["tam"]):
            ram[j] = pid
        pcb[pid]["inicio"] = pos
        pos += pcb[pid]["tam"]
    print(f"Memoria compactada: {TAM_RAM - pos} casillas libres continuas (RAM[{pos}..{TAM_RAM - 1}]).")


# ---------- RF-02: Gestion de procesos ----------
def crear(nombre, tamano, duracion):
    global siguiente_pid
    if tamano < 1 or duracion < 1:
        raise ValueError
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


def kill(pid):
    """Elimina un proceso activo (Listo o Ejecucion) y libera su memoria."""
    global en_ejecucion, usado
    if pid not in pcb or pcb[pid]["estado"] not in ("Listo", "Ejecucion"):
        print(f"Error: no hay un proceso activo con PID {pid}.")
        return
    if pid == en_ejecucion:
        en_ejecucion, usado = None, 0
    else:
        cola_listos.remove(pid)
    pcb[pid]["estado"] = "Eliminado"
    liberar(pid)
    print(f"Proceso PID {pid} ({pcb[pid]['nombre']}) eliminado; memoria liberada.")


# ---------- RF-03: Control de CPU (Round Robin, avance manual por ticks) ----------
def step():
    global en_ejecucion, reloj, usado
    if en_ejecucion is None and cola_listos:
        en_ejecucion, usado = cola_listos.pop(0), 0
        pcb[en_ejecucion]["estado"] = "Ejecucion"
    if en_ejecucion is None:
        print("CPU ociosa: no hay procesos listos.")
        return
    reloj += 1
    usado += 1
    p = pcb[en_ejecucion]
    p["restante"] -= 1
    print(f"[tick {reloj}] PID {en_ejecucion} ({p['nombre']}) ejecuta, "
          f"le quedan {p['restante']} ticks.")
    if p["restante"] == 0:
        p["estado"] = "Terminado"
        liberar(en_ejecucion)
        print(f"  -> PID {en_ejecucion} termino y libero su memoria.")
        en_ejecucion = None
    elif usado >= quantum and cola_listos:      # quantum agotado y hay otros esperando
        p["estado"] = "Listo"
        cola_listos.append(en_ejecucion)
        print(f"  -> quantum agotado: PID {en_ejecucion} vuelve a la cola de listos.")
        en_ejecucion = None


def cambiar_quantum(valor):
    global quantum
    if valor is not None:
        if valor < 1:
            raise ValueError
        quantum = valor
    print(f"Quantum = {quantum} ticks.")


# ---------- RF-05: Sistema de archivos virtual ----------
def guardar(nombre, texto):
    vfs[nombre] = texto
    print(f"Archivo '{nombre}' guardado ({len(texto)} caracteres).")


def ver(nombre):
    print(vfs[nombre] if nombre in vfs else f"Error: el archivo '{nombre}' no existe.")


def borrar(nombre):
    if nombre in vfs:
        del vfs[nombre]
        print(f"Archivo '{nombre}' borrado.")
    else:
        print(f"Error: el archivo '{nombre}' no existe.")


def listar():
    for nombre, texto in vfs.items():
        print(f"{nombre:<14} {len(texto)} caracteres")
    print(f"Total: {len(vfs)} archivo(s), {sum(map(len, vfs.values()))} caracteres" if vfs else "(VFS vacio)")


# ---------- RNF-03: Visualizacion directa ----------
def mostrar_memoria():
    barra = "".join("." if c is None else str(c % 10) for c in ram)
    print(f"RAM [{barra}]  ocupadas={sum(c is not None for c in ram)}/{TAM_RAM}")


def mostrar_procesos():
    print("PID  NOMBRE       ESTADO      RAM        RESTANTE")
    for pid, p in pcb.items():
        rango = f"{p['inicio']}-{p['inicio'] + p['tam'] - 1}" if p["estado"] in ("Listo", "Ejecucion") else "-"
        print(f"{pid:<4} {p['nombre']:<12} {p['estado']:<11} {rango:<10} {p['restante']}")
    print(f"CPU: PID {en_ejecucion or '-'} | quantum={quantum} | cola de listos={cola_listos}"
          if pcb else "(sin procesos)")


AYUDA = """Comandos:
  crear <nombre> <tamano> [ticks]  crea un proceso y reserva RAM (3 ticks por defecto)
  step                             avanza 1 tick de CPU (Round Robin)
  quantum [n]                      muestra o cambia el quantum
  kill <pid>                       elimina un proceso y libera su RAM
  ps                               tabla de procesos (PCB)
  mem                              estado de la RAM
  compactar                        junta los procesos al inicio de la RAM
  guardar <nombre> <texto...>      guarda un archivo en el VFS
  ver <nombre>                     muestra un archivo
  borrar <nombre>                  elimina un archivo del VFS
  ls                               lista archivos del VFS con su tamano
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
        elif accion == "quantum":
            cambiar_quantum(int(args[0]) if args else None)
        elif accion == "kill":
            kill(int(args[0]))
        elif accion == "ps":
            mostrar_procesos()
        elif accion == "mem":
            mostrar_memoria()
        elif accion == "compactar":
            compactar()
        elif accion == "guardar":
            guardar(args[0], " ".join(args[1:]))
        elif accion == "ver":
            ver(args[0])
        elif accion == "borrar":
            borrar(args[0])
        elif accion == "ls":
            listar()
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
    print("Mini-SO v1.0  (escribe 'help')")
    while True:
        try:
            if not ejecutar(input("mini-so> ")):
                break
        except EOFError:
            break


if __name__ == "__main__":
    main()
