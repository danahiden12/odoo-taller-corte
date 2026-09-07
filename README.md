# 🧵 Taller de Corte — Módulo Odoo 17

Módulo personalizado desarrollado en **Odoo 17 Community** para digitalizar y gestionar el flujo de producción de un taller de corte de indumentaria.

Centraliza la información operativa del corte y permite hacer seguimiento desde el ingreso de la orden hasta la entrega.

## 📹 Demo en video

[Ver demo completa en Drive](https://drive.google.com/file/d/1UGDdYbDyVdBCwyGB05hy_4Wyx5i6A3K3/view?usp=sharing)

## Capturas

[Tablero Kanban](https://docs.google.com/presentation/d/1a1E5nCD8DrxradPdkdzeK1H5WJX6595P2i-d6xggnuk/edit?slide=id.p#slide=id.p)

[Hoja de Corte PDF](https://drive.google.com/file/d/10v-2Fq0zHm7b88y41oW9UQ9eAjrbdRXx/view?usp=sharing)

> Los enlaces muestran versiones anteriores y parte de la evolución del desarrollo del módulo.

## ¿Qué hace este módulo?

Digitaliza el flujo productivo de un taller de corte mediante un tablero Kanban, órdenes de corte, gestión de tizadas, cálculos automáticos de producción y generación de documentación PDF.

## Funcionalidades

- Tablero Kanban con las etapas reales del proceso productivo
- Formulario de orden de corte
- Gestión de curva por talle
- Curvas con valores fraccionarios
- Cantidades solicitadas por color
- Distribución automática por talle y color
- Gestión de múltiples tizadas por material
- Cálculo de capas y producción planificada
- Cálculo automático de tela total y consumo por prenda
- Diferenciación entre color base y color de combinación
- Historial de cambios de estado
- Ficha técnica multipágina
- Generación automática de Hoja de Corte en PDF
- Inclusión automática de una o dos páginas A4 de Ficha Técnica dentro del PDF

## Etapas del Kanban

Ingreso Corte → Moldería Digital → Tizada → En Corte → Cortado / Control → Entregado

## Hoja de Corte PDF

El reporte incluye:

- Datos de la orden
- Curva del pedido
- Cantidades por color y talle
- Detalle de tizadas
- Capas y producción planificada
- Consumo de tela
- Notas operativas
- Ficha Técnica en páginas A4 independientes

## Stack tecnológico

- Odoo 17 Community Edition
- Python
- XML / QWeb
- PostgreSQL
- wkhtmltopdf 0.12.6
- Git / GitHub

## Estructura del módulo

```text
taller_corte/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── orden_corte.py
├── views/
│   └── orden_corte_views.xml
├── reports/
│   └── reporte_corte.xml
├── data/
└── security/
    └── ir.model.access.csv
