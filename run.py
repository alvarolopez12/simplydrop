#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Alvaro Lopez Alvarez"
__copyright__ = "2019 Tible Technologies"

__link__ = "https://tibletech.com/es"
__version__ = 1.0

# -------------------------run.py---------------------------------
# Fichero con script principal de la aplicación Flask.
# Se crea la app y se definen los métodos de atención a las peticiones.
# Estas peticiones vendrán a través de GET o POST.
# ---------------------------------------------------------------------

from simplydrop import app

# ----------------------- INICIO APP  ------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # use_reloader=False)

# ----------------------- FIN INICIO APP  ------------------------
