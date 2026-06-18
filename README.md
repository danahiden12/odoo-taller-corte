# 🧵 Taller de Corte — Módulo Odoo 17

Módulo personalizado desarrollado en Odoo 17 Community para la gestión 
de órdenes de corte de un taller de indumentaria.

## 📹 Demo en video
[Ver demo completa en Drive](TU_LINK_DE_DRIVE)

## ¿Qué hace este módulo?

Digitaliza el flujo de producción de un taller de corte mediante un 
tablero Kanban con las etapas reales del proceso, reemplazando el 
seguimiento manual en papel.

## Funcionalidades

- Tablero Kanban con 5 etapas del proceso productivo
- Formulario de orden de corte con campos específicos del taller
- Tabla de talles con lista desplegable y campo de color
- Cálculo automático de cantidad total de piezas
- Tabla de tizadas con cálculo automático de consumo de tela por material
- Foto de referencia del cliente
- Generación de hoja de corte en PDF con un solo clic

## Etapas del Kanban

Ingreso Corte → Molderia Digital → En Corte → Cortado/Control → Entregado

## Stack tecnológico

- Odoo 17 Community Edition
- Python 3.12
- XML (vistas QWeb)
- PostgreSQL 15
- wkhtmltopdf 0.12.6

## Estructura del módulo

taller_corte/

├── init.py

├── manifest.py

├── models/

│   ├── init.py

│   └── orden_corte.py

├── views/

│   └── orden_corte_views.xml

├── reports/

│   └── reporte_corte.xml

└── security/

└── ir.model.access.csv

