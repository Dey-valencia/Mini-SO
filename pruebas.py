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
    s.en_ejecucion = None; s.siguiente_pid = 1; s.reloj = 0

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

if __name__ == "__main__":
    for t in (t01, t02, t03, t04, t05, t06):
        t(); print(f"OK  {t.__name__}")
    print("Todas las pruebas pasaron.")
