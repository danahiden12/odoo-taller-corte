# 🧵 Taller de Corte — Módulo Odoo 17

Módulo personalizado desarrollado en Odoo 17 Community para la gestión 
de órdenes de corte de un taller de indumentaria.

## 📹 Demo en video
[Ver demo completa en Drive](https://drive.google.com/file/d/1UGDdYbDyVdBCwyGB05hy_4Wyx5i6A3K3/view?usp=sharing)

## Capturas

![Tablero Kanban](https://docs.google.com/presentation/d/1a1E5nCD8DrxradPdkdzeK1H5WJX6595P2i-d6xggnuk/edit?slide=id.p#slide=id.p)

![Hoja de Corte PDF](https://drive.google.com/drive/u/0/folders/1tfJ3bLRHdne5PhHbD4DhkTJ1XLy5_Z_h)

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

## Instalación

1. Clonar este repositorio en la carpeta `custom-addons` de tu instalación de Odoo
2. Reiniciar Odoo con `--addons-path=addons,custom-addons`
3. Activar modo desarrollador
4. Instalar el módulo desde Aplicaciones

## Autora

**Dana Hiden** — Analista de Procesos y Datos | Supply Chain & Operaciones
[LinkedIn](https://www.linkedin.com/in/danahiden)        
