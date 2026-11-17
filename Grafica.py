import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

# ==================================================
# CONFIGURACIÓN
# ==================================================

NARANJA = "#ff8500"
GUINDO = "#800020"
VERDE = "#16852b"
AZUL = "#0055e8"
COLOR_STANDBY = "#a52b9f"

# Duración ilustrativa, en las mismas unidades del eje Tiempo.
tiempo_standby = 20

# Los picos llegan a 7.9, pero no se muestra ese valor en el eje.
tp = np.array([0, 20, 30, 39, 53, 66, 74, 82, 100])
pp = np.array([6.3, 7.9, 7.2, 7.9, 6.8, 7.9, 7.2, 7.9, 6.4])

# ==================================================
# CURVA SUAVE DE PRESIÓN
# ==================================================

tiempo = []
presion = []

for i in range(len(tp) - 1):
    u = np.linspace(0, 1, 200)

    tiempo.extend(
        tp[i] + (tp[i + 1] - tp[i]) * u
    )

    presion.extend(
        pp[i] + (pp[i + 1] - pp[i])
        * (1 - np.cos(np.pi * u)) / 2
    )

# ==================================================
# CAMBIOS DE ESTADO SEGÚN LA PRESIÓN
# ==================================================

def calcular_estados(carga, descarga, inicial):
    estado = inicial
    eventos = []

    for i in range(len(tp) - 1):
        p0 = pp[i]
        p1 = pp[i + 1]

        if estado == 0 and p1 < p0 and p1 <= carga <= p0:
            nivel = carga
            nuevo_estado = 1

        elif estado == 1 and p1 > p0 and p0 <= descarga <= p1:
            nivel = descarga
            nuevo_estado = 0

        else:
            continue

        fraccion = (nivel - p0) / (p1 - p0)

        u = np.arccos(
            np.clip(1 - 2 * fraccion, -1, 1)
        ) / np.pi

        t = tp[i] + u * (tp[i + 1] - tp[i])

        eventos.append((t, nivel, nuevo_estado))
        estado = nuevo_estado

    tiempos = [tp[0]] + [e[0] for e in eventos] + [tp[-1]]
    estados = [inicial] + [e[2] for e in eventos] + [estado]

    return tiempos, estados, eventos


# Condiciones iniciales conservadas del esquema:
# PARISE en carga y SCHULZ inicialmente inactivo.
t_parise, s_parise, eventos_parise = calcular_estados(
    carga=7.2,
    descarga=7.8,
    inicial=1
)

t_schulz, s_schulz, eventos_schulz = calcular_estados(
    carga=6.8,
    descarga=7.6,
    inicial=0
)

# ==================================================
# CREAR LA FIGURA ANTES DE AÑADIR ELEMENTOS
# ==================================================

fig, (ax_p, ax_parise, ax_schulz) = plt.subplots(
    3, 1,
    figsize=(16, 8),
    sharex=True,
    gridspec_kw={
        "height_ratios": [3.5, 1, 1.2],
        "hspace": 0.15
    }
)

fig.subplots_adjust(
    left=0.25,
    right=0.96,
    top=0.85,
    bottom=0.18
)

fig.suptitle(
    "Diagrama temporal de control",
    fontsize=24,
    fontweight="bold"
)

# ==================================================
# LÍMITES Y CURVA DE PRESIÓN
# ==================================================

for nivel, color, estilo in [
    (7.8, NARANJA, "-"),
    (7.6, GUINDO, "--"),
    (7.2, NARANJA, "-"),
    (6.8, GUINDO, "--")
]:
    ax_p.axhline(
        nivel,
        color=color,
        linestyle=estilo,
        linewidth=1.7,
        zorder=1
    )

ax_p.plot(
    tiempo,
    presion,
    color=VERDE,
    linewidth=2.5,
    zorder=3
)

ax_p.set_ylim(6.2, 8.1)
ax_p.set_yticks([6.8, 7.2, 7.6, 7.8])
ax_p.set_yticklabels(
    ["6,8", "7,2", "7,6", "7,8"],
    fontsize=13
)

ax_p.set_ylabel(
    "P (bar)",
    fontsize=15,
    fontweight="bold"
)

# ==================================================
# SEÑALES DE PARISE Y SCHULZ
# ==================================================

for ax, nombre, t, s in [
    (ax_parise, "PARISE", t_parise, s_parise),
    (ax_schulz, "SCHULZ", t_schulz, s_schulz)
]:
    ax.axhline(
        0,
        color=AZUL,
        linewidth=1.5,
        zorder=1
    )

    ax.step(
        t, s,
        where="post",
        color="black",
        linewidth=2.3,
        zorder=3
    )

    ax.set_ylim(-0.3, 1.6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["0", "1"], fontsize=13)

    ax.text(
        -0.065, 0.5, nombre,
        transform=ax.transAxes,
        ha="right",
        va="center",
        fontsize=15,
        fontweight="bold"
    )

for ax in (ax_p, ax_parise, ax_schulz):
    ax.set_xlim(0, 100)
    ax.set_xticks([])
    ax.tick_params(axis="both", length=0, pad=8)

    # Fondo transparente para que se vean las guías
    # que atraviesan las distintas gráficas.
    ax.patch.set_alpha(0)

    for borde in ax.spines.values():
        borde.set_visible(False)

# ==================================================
# LÍNEAS SEGMENTADAS EN CADA CAMBIO
# ==================================================

for ax_destino, eventos in [
    (ax_parise, eventos_parise),
    (ax_schulz, eventos_schulz)
]:
    for t, nivel, estado in eventos:
        guia = ConnectionPatch(
            xyA=(t, nivel),
            coordsA="data",
            axesA=ax_p,
            xyB=(t, 0),
            coordsB="data",
            axesB=ax_destino,
            arrowstyle="-",
            linestyle=(0, (5, 5)),
            linewidth=1,
            color="#777777",
            clip_on=False
        )

        guia.set_zorder(0.5)
        fig.add_artist(guia)

        ax_p.plot(
            t, nivel,
            "o",
            color=VERDE,
            markersize=3,
            zorder=4
        )

# ==================================================
# FLECHAS DE LOS EJES
# ==================================================

ax_p.annotate(
    "",
    xy=(0, 1.02),
    xytext=(0, 0),
    xycoords="axes fraction",
    arrowprops=dict(
        arrowstyle="-|>",
        color="black",
        linewidth=1.5
    ),
    annotation_clip=False
)

ax_schulz.annotate(
    "",
    xy=(1.02, -0.1),
    xytext=(0, -0.1),
    xycoords="axes fraction",
    arrowprops=dict(
        arrowstyle="-|>",
        color="black",
        linewidth=1.5
    ),
    annotation_clip=False
)

# ==================================================
# REFERENCIAS SUPERIORES IZQUIERDAS
# ==================================================

ax_ref = fig.add_axes([0.015, 0.73, 0.20, 0.19])
ax_ref.set_xlim(0, 1)
ax_ref.set_ylim(0, 1)
ax_ref.axis("off")


def dibujar_referencia(nombre, y, descarga, carga, color):
    ax_ref.text(
        0.02, y, nombre,
        color=color,
        fontsize=11,
        fontweight="bold",
        ha="left",
        va="center"
    )

    for destino_y, texto in [
        (y + 0.12, f"{descarga} descarga"),
        (y - 0.12, f"{carga} carga")
    ]:
        ax_ref.annotate(
            "",
            xy=(0.53, destino_y),
            xytext=(0.34, y),
            arrowprops=dict(
                arrowstyle="->",
                color=color,
                linewidth=1.3
            )
        )

        ax_ref.text(
            0.56, destino_y, texto,
            color=color,
            fontsize=10,
            ha="left",
            va="center"
        )


dibujar_referencia(
    "PARISE", 0.75, "7,8", "7,2", NARANJA
)

dibujar_referencia(
    "SCHULZ", 0.25, "7,6", "6,8", GUINDO
)

# ==================================================
# STANDBY Y APAGADO DEL MOTOR SCHULZ
# ==================================================

inicio_standby = None
hubo_carga = False

for t, nivel, estado in eventos_schulz:
    if estado == 1:
        hubo_carga = True

    elif estado == 0 and hubo_carga:
        inicio_standby = t
        break

if inicio_standby is not None:
        # Alinear el final del standby con una guía existente.
    fin_deseado = inicio_standby + tiempo_standby

    guias_disponibles = [
        t for t, nivel, estado in eventos_parise
        if t > inicio_standby
    ]

    fin_standby = min(
        guias_disponibles,
        key=lambda t: abs(t - fin_deseado),
        default=fin_deseado
    )

    siguientes_cargas = [
        t for t, nivel, estado in eventos_schulz
        if estado == 1 and t > inicio_standby
    ]

    proxima_carga = (
        min(siguientes_cargas)
        if siguientes_cargas else float("inf")
    )

    fin_visible = min(
        fin_standby,
        proxima_carga,
        tp[-1]
    )

    ax_schulz.annotate(
        "",
        xy=(fin_visible, 0.55),
        xytext=(inicio_standby, 0.55),
        arrowprops=dict(
            arrowstyle="<->",
            color=COLOR_STANDBY,
            linewidth=1.8
        )
    )

    ax_schulz.text(
        (inicio_standby + fin_visible) / 2,
        0.83,
        "Tiempo de standby",
        color=COLOR_STANDBY,
        fontsize=11,
        ha="center",
        va="bottom"
    )

    ax_schulz.vlines(
        [inicio_standby, fin_visible],
        ymin=0.12,
        ymax=1.12,
        colors=COLOR_STANDBY,
        linewidth=1.4
    )

    if fin_standby < proxima_carga and fin_standby <= tp[-1]:
        texto_final = "Se apaga motor"

    elif proxima_carga <= fin_standby and proxima_carga <= tp[-1]:
        texto_final = "Vuelve a cargar"

    else:
        texto_final = "Continúa en standby"

    # Mostrar texto final después de la flecha
    ax_schulz.text(
        fin_visible + 1.5,
        0.14,
        texto_final,
        color=COLOR_STANDBY,
        fontsize=10,
        ha="left",
        va="bottom"
    )

# ==================================================
# LEYENDA Y GUARDADO
# ==================================================

fig.text(
    0.60, 0.075,
    "1 = en carga     ·     0 = sin carga",
    ha="center",
    fontsize=14
)

fig.text(
    0.60, 0.035,
    "Curva ilustrativa · Standby con motor encendido en descarga",
    ha="center",
    fontsize=10,
    color="#555555"
)

plt.savefig(
    "diagrama_control_corregido.png",
    dpi=300,
    bbox_inches="tight",
    facecolor="white"
)

plt.show()