# 🧵 Taller de Corte — Odoo 17 Community

Módulo desarrollado en **Odoo 17 Community** para digitalizar y ordenar el flujo productivo de un taller de corte de indumentaria.

## Objetivo

El proyecto buscó centralizar en Odoo la gestión de órdenes de corte, reemplazando procesos manuales y dispersos.
La idea fue poder cargar en una sola orden:

- curva por talle;
- cantidades pedidas por color;
- distribución automática;
- múltiples tizadas;
- capas de corte;
- consumo de tela;
- color base y color de combinación;
- seguimiento por estados;
- y generación de Hoja de Corte en PDF.

## Resultado

El módulo permite gestionar el proceso completo:
`Ingreso Corte → Moldería Digital → Tizada → En Corte → Cortado / Control → Entregado`

También incluye cálculos automáticos de producción, soporte para curvas fraccionarias, diferencias entre pedido y producción, historial de estados, ficha técnica multipágina y PDF final de corte.
La carga puede completarse antes de guardar la orden, y al finalizar se asigna automáticamente el número de Orden de Corte.

---

## Demo incluida

El repositorio incluye datos de demostración con una orden:
`DEMO/0001`

La demo contiene:

- cliente de ejemplo;
- curva por talles;
- pedido por color;
- distribución automática;
- tizada de Lycra;
- tizada de Forrería;
- color base y color de combinación;
- cálculo de capas, producción y consumo.

---

## Cómo probarlo

Clonar el repositorio:

```bash
git clone https://github.com/danahiden12/odoo-taller-corte.git

Copiar el módulo dentro de los addons personalizados de Odoo:
odoo/
└── custom-addons/
    └── taller_corte/

Agregar la carpeta al addons_path:
addons_path = addons,custom-addons

Crear una base de datos con datos de demostración habilitados e instalar el módulo Taller de Corte.
```bash
python odoo-bin \
-r USUARIO_POSTGRES \
-w PASSWORD_POSTGRES \
--addons-path=addons,custom-addons \
-d NOMBRE_BASE \
-i taller_corte \
--stop-after-init

Al ingresar a Odoo debería aparecer la orden: DEMO/0001
lista para recorrer y probar las principales funcionalidades del módulo.
