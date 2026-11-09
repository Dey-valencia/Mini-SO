"""Pruebas funcionales automaticas del Mini-SO (python pruebas.py)."""
import io, contextlib
import simulador as s

def run(cmd):
    b = io.StringIO()
    with contextlib.redirect_stdout(b):
        s.ejecutar(cmd)
    return b.getvalue()

def reset():
    s.ram[:] = [None] * s.TAM_RAM
    s.pcb.clear(); s.cola_listos.clear(); s.vfs.clear()
    s.en_ejecucion = None; s.siguiente_pid = 1; s.reloj = 0; s.quantum = 2; s.usado = 0

def t01():  # RF-01
    reset(); assert "desconocido" in run("bailar"); assert "invalidos" in run("crear")
def t02():  # RF-02
    reset(); run("crear a 3 2"); assert s.pcb[1]["estado"] == "Listo"
    run("step"); assert s.pcb[1]["estado"] == "Ejecucion"
    run("step"); assert s.pcb[1]["estado"] == "Terminado"
def t03():  # RF-03
    reset(); assert "ociosa" in run("step")
    run("crear a 2 3"); run("step"); assert s.pcb[1]["restante"] == 2
def t04():  # RF-04
    reset(); run("crear a 10 1"); assert "Error" in run("crear b 8 1")
    run("step"); assert all(c is None for c in s.ram)       # liberada al terminar
    run("crear b 8 1"); assert s.pcb[2]["inicio"] == 0
def t05():  # RF-05
    reset(); run("guardar nota hola mundo"); assert run("ver nota").strip() == "hola mundo"
    assert "no existe" in run("ver x")
def t06():  # integracion
    reset(); run("crear a 4 1"); run("crear b 4 2"); run("step"); run("crear c 6 1")
    assert s.pcb[3]["inicio"] == 8   # a y b ocupan 0-7; c cabe en 8-13
    while s.en_ejecucion or s.cola_listos: run("step")
    assert all(p["estado"] == "Terminado" for p in s.pcb.values()) and all(c is None for c in s.ram)

def t07():  # RF-03 Round Robin
    reset(); run("crear a 2 3"); run("crear b 2 3")
    run("step"); run("step")                                  # a agota su quantum (2)
    assert s.pcb[1]["estado"] == "Listo" and s.cola_listos == [2, 1]
    run("step"); assert s.en_ejecucion == 2 and s.pcb[1]["restante"] == 1
    while s.en_ejecucion or s.cola_listos: run("step")
    assert s.reloj == 6 and all(p["estado"] == "Terminado" for p in s.pcb.values())
def t08():  # comando quantum
    reset(); assert "= 2" in run("quantum"); assert "= 5" in run("quantum 5")
    assert "invalidos" in run("quantum 0") and "invalidos" in run("quantum x") and s.quantum == 5
    run("crear a 2 6"); run("crear b 2 1")
    for _ in range(5): run("step")                            # con quantum 5 a no es expulsado antes
    assert s.pcb[1]["estado"] == "Listo" and s.pcb[1]["restante"] == 1
def t09():  # kill
    reset(); run("crear a 4 5"); run("crear b 4 5"); run("step")
    assert "eliminado" in run("kill 1") and s.en_ejecucion is None and s.pcb[1]["estado"] == "Eliminado"
    assert all(c != 1 for c in s.ram)                         # RAM liberada
    run("kill 2"); assert s.cola_listos == [] and all(c is None for c in s.ram)
    assert "Error" in run("kill 2") and "Error" in run("kill 99") and "invalidos" in run("kill")
def t10():  # compactacion
    reset(); run("crear a 4 1"); run("crear b 4 9"); run("crear c 4 9"); run("step")   # a termina
    assert "Error" in run("crear d 6 1")                       # 4 + 4 libres pero separados
    run("kill 2"); run("compactar")                            # c se desplaza a 0-3
    assert s.pcb[3]["inicio"] == 0 and s.ram[:4] == [3] * 4 and all(c is None for c in s.ram[4:])
    run("crear d 12 1"); assert s.pcb[4]["inicio"] == 4        # ahora cabe un bloque de 12
def t11():  # VFS: borrar y listar con tamano
    reset(); assert "vacio" in run("ls")
    run("guardar nota hola mundo"); run("guardar x abc")
    salida = run("ls"); assert "nota" in salida and "10 caracteres" in salida and "Total: 2 archivo" in salida
    assert "borrado" in run("borrar nota") and "no existe" in run("ver nota")
    assert "no existe" in run("borrar nota") and "invalidos" in run("borrar")
def t12():  # integracion final: RR + fragmentacion + kill + compactar + VFS
    reset(); run("crear a 4 3"); run("crear b 6 2"); run("crear c 4 4"); run("guardar log fin")
    for _ in range(3): run("step")                             # a(2) b(1)... orden RR
    run("kill 3"); run("compactar")
    while s.en_ejecucion or s.cola_listos: run("step")
    assert all(p["estado"] in ("Terminado", "Eliminado") for p in s.pcb.values())
    assert all(c is None for c in s.ram) and s.vfs == {"log": "fin"}

if __name__ == "__main__":
    for t in (t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12):
        t(); print(f"OK  {t.__name__}")
    print("Todas las pruebas pasaron.")
