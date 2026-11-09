# Mini-SO: Simulador de Sistema Operativo en consola

Sistemas Operativos y Compiladores - Universidad Cooperativa de Colombia (2026)
Programa de Ingeniería de Software · Docente: Ing. Adriana Paredes Salinas

Simulador didáctico de un sistema operativo básico que se maneja desde la consola. Integra
cinco componentes: **intérprete de comandos, procesos (PCB), CPU con planificación Round Robin,
memoria RAM con compactación y sistema de archivos virtual (VFS)**.

Requiere únicamente **Python 3** (sin librerías externas).

## Ejecutar

    python simulador.py              # consola interactiva
    python pruebas.py                # 12 pruebas funcionales automáticas
    python simulador.py < demo.txt   # sesión de ejemplo (salida en demo_salida.txt)

## Comandos

| Comando | Descripción |
|---|---|
| `crear <nombre> <tamano> [ticks]` | Crea un proceso y reserva RAM (primer ajuste, bloques continuos). 3 ticks por defecto |
| `step` | Avanza 1 tick de CPU (Round Robin) |
| `quantum [n]` | Muestra o cambia el quantum (por defecto 2) |
| `kill <pid>` | Elimina un proceso activo y libera su RAM |
| `ps` | Tabla de procesos (PCB), proceso en CPU y cola de listos |
| `mem` | Estado de la RAM (16 casillas) |
| `compactar` | Junta los procesos activos al inicio de la RAM |
| `guardar <nombre> <texto...>` | Guarda un archivo en el VFS |
| `ver <nombre>` | Muestra el contenido de un archivo |
| `borrar <nombre>` | Elimina un archivo del VFS |
| `ls` | Lista los archivos con su tamaño |
| `help` / `salir` | Ayuda / terminar |

## Requerimientos cubiertos

| Código | Módulo | Función(es) en `simulador.py` |
|---|---|---|
| RF-01 | Intérprete por consola | `ejecutar()`, `main()` |
| RF-02 | Gestión de procesos | `crear()`, `kill()` |
| RF-03 | Control de CPU (Round Robin) | `step()`, `cambiar_quantum()` |
| RF-04 | Gestión de RAM | `reservar()`, `liberar()`, `compactar()` |
| RF-05 | Sistema de archivos virtual | `guardar()`, `ver()`, `borrar()`, `listar()` |
| RNF-03 | Visualización directa | `mostrar_memoria()`, `mostrar_procesos()` |

## Estructura del repositorio

    simulador.py          código fuente del Mini-SO (un solo archivo)
    pruebas.py            pruebas funcionales automáticas (t01..t12)
    demo.txt              sesión de ejemplo (entrada)
    demo_salida.txt       salida real de la sesión de ejemplo
    docs/
      Informe_tecnico_final.pdf   documento técnico final (y .docx editable)
      Manual_de_usuario.pdf       manual de usuario (y .docx editable)
      Presentacion_sustentacion.pptx
      arquitectura.png · componentes.png · estados_proceso.png   diagramas actualizados
      captura1..6.png · pruebas_salida.txt                      evidencias de ejecución y pruebas
      Informe tecnico1.docx                                     informe de la Entrega 2
