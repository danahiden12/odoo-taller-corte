from collections import defaultdict
from functools import reduce
from math import floor, gcd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


TALLES = [
    ('xs', 'XS'),
    ('s', 'S'),
    ('m', 'M'),
    ('l', 'L'),
    ('xl', 'XL'),
    ('2xl', '2XL'),
    ('3xl', '3XL'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
    ('12', '12'),
    ('14', '14'),
    ('16', '16'),
    ('18', '18'),
]


TIPOS_TELA = [
    ('tela_plana', 'Tela plana'),
    ('tela_punto', 'Tela de punto'),
    ('lycra', 'Lycra'),
    ('jean', 'Jean'),
    ('poplin', 'Poplin'),
    ('lino', 'Lino'),
    ('gabardina', 'Gabardina'),
    ('forreria', 'Forreria'),
    ('otro', 'Otro'),
]


ESTADOS_CORTE = [
    ('ingreso', 'Ingreso Corte'),
    ('molderia', 'Molderia Digital'),
    ('tizada', 'Tizada'),
    ('en_corte', 'En Corte'),
    ('control', 'Cortado / Control'),
    ('entregado', 'Entregado'),
]


ESTADOS_REQUIEREN_CANTIDADES = {
    'control',
    'entregado',
}


# ============================================================
# COLOR DE TELA
# ============================================================


class ColorTela(models.Model):
    _name = 'taller.color.tela'
    _description = 'Color de tela'
    _order = 'name'

    name = fields.Char(
        string='Color',
        required=True,
        index=True,
    )

    _sql_constraints = [
        (
            'color_name_unique',
            'unique(name)',
            'Ya existe un color con ese nombre.',
        ),
    ]

    @staticmethod
    def _normalizar_nombre(nombre):
        return ' '.join(
            (nombre or '').strip().split()
        ).title()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = self._normalizar_nombre(
                    vals['name']
                )

        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)

        if vals.get('name'):
            vals['name'] = self._normalizar_nombre(
                vals['name']
            )

        return super().write(vals)


# ============================================================
# CURVA BASE DEL PEDIDO
# ============================================================


class CurvaPedido(models.Model):
    _name = 'taller.orden.curva.pedido'
    _description = 'Curva por capa del pedido'
    _order = 'id'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        required=True,
        index=True,
        ondelete='cascade',
    )

    talle = fields.Selection(
        TALLES,
        string='Talle',
        required=True,
    )

    cantidad_base = fields.Float(
        string='Curva',
        required=True,
        default=1.0,
        digits=(10, 2),
    )

    _sql_constraints = [
        (
            'orden_talle_curva_unique',
            'unique(orden_id, talle)',
            'El talle ya fue agregado a la curva del pedido.',
        ),
    ]

    @api.constrains('cantidad_base')
    def _check_cantidad_base(self):
        for linea in self:
            if linea.cantidad_base <= 0:
                raise ValidationError(
                    _(
                        'La cantidad de la curva '
                        'debe ser mayor que cero.'
                    )
                )


# ============================================================
# CANTIDAD PEDIDA POR COLOR
# ============================================================


class ColorPedido(models.Model):
    _name = 'taller.orden.color.pedido'
    _description = 'Cantidad pedida por color'
    _order = 'id'

    @api.depends('color_tela_id')
    def _compute_display_name(self):
        for linea in self:
            linea.display_name = (
                linea.color_tela_id.display_name
                if linea.color_tela_id
                else _('Color del pedido')
            )

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        required=True,
        index=True,
        ondelete='cascade',
    )

    color_tela_id = fields.Many2one(
        'taller.color.tela',
        string='Color',
        required=True,
        index=True,
    )

    cantidad_prendas = fields.Integer(
        string='Cantidad de prendas',
        required=True,
        default=1,
    )

    _sql_constraints = [
        (
            'orden_color_pedido_unique',
            'unique(orden_id, color_tela_id)',
            'El color ya fue agregado al pedido.',
        ),
    ]

    @api.constrains('cantidad_prendas')
    def _check_cantidad_prendas(self):
        for linea in self:
            if linea.cantidad_prendas <= 0:
                raise ValidationError(
                    _(
                        'La cantidad de prendas por color '
                        'debe ser mayor que cero.'
                    )
                )


# ============================================================
# DISTRIBUCION BASE POR TALLE Y COLOR
# ============================================================


class LineaTalle(models.Model):
    _name = 'taller.linea.talle'
    _description = 'Linea de talle'
    _order = 'id'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        required=True,
        index=True,
        ondelete='cascade',
    )

    talle = fields.Selection(
        TALLES,
        string='Talle',
        required=True,
    )

    color_tela_id = fields.Many2one(
        'taller.color.tela',
        string='Color',
        required=True,
        index=True,
    )

    cantidad = fields.Integer(
        string='Cantidad',
        required=True,
        default=0,
    )

    @api.constrains(
        'cantidad',
        'orden_id',
    )
    def _check_cantidad(self):
        for linea in self:
            if linea.cantidad < 0:
                raise ValidationError(
                    _('La cantidad no puede ser negativa.')
                )

            if (
                linea.orden_id
                and linea.orden_id.estado
                in ESTADOS_REQUIEREN_CANTIDADES
                and linea.cantidad <= 0
            ):
                raise ValidationError(
                    _(
                        'En Control o Entregado todas las cantidades '
                        'deben ser mayores que cero.'
                    )
                )

    def unlink(self):
        ordenes = self.mapped('orden_id')

        resultado = super().unlink()

        for orden in ordenes:
            if (
                orden.exists()
                and orden.estado
                in ESTADOS_REQUIEREN_CANTIDADES
            ):
                orden._validar_cantidades_finales()

        return resultado


# ============================================================
# CURVA INTERNA DE TIZADA
# ============================================================


class LineaCurvaTizada(models.Model):
    _name = 'taller.linea.curva.tizada'
    _description = 'Linea de curva de tizada'
    _order = 'id'

    tizada_id = fields.Many2one(
        'taller.linea.tizada',
        string='Tizada',
        required=True,
        index=True,
        ondelete='cascade',
    )

    talle = fields.Selection(
        TALLES,
        string='Talle',
        required=True,
    )

    cantidad_por_capa = fields.Float(
        string='Curva',
        required=True,
        default=1.0,
        digits=(10, 2),
    )

    _sql_constraints = [
        (
            'tizada_talle_unique',
            'unique(tizada_id, talle)',
            'El talle ya fue agregado a la curva de esta tizada.',
        ),
    ]

    @api.constrains('cantidad_por_capa')
    def _check_cantidad_por_capa(self):
        for linea in self:
            if linea.cantidad_por_capa <= 0:
                raise ValidationError(
                    _(
                        'La cantidad de la curva '
                        'debe ser mayor que cero.'
                    )
                )


# ============================================================
# CAPAS POR COLOR
# ============================================================


class CapaColorTizada(models.Model):
    _name = 'taller.tizada.capa.color'
    _description = 'Capas por color de tizada'
    _order = 'id'

    tizada_id = fields.Many2one(
        'taller.linea.tizada',
        string='Tizada',
        required=True,
        index=True,
        ondelete='cascade',
    )

    pedido_color_id = fields.Many2one(
        'taller.orden.color.pedido',
        string='Color del pedido',
        index=True,
        ondelete='cascade',
    )

    color_base_carga_id = fields.Many2one(
        'taller.color.tela',
        string='Color base de carga',
        index=True,
    )

    cantidad_pedida_carga = fields.Integer(
        string='Cantidad pedida de carga',
        default=0,
    )

    color_base_id = fields.Many2one(
        'taller.color.tela',
        string='Color base',
        compute='_compute_datos_pedido',
        readonly=True,
    )

    cantidad_pedida = fields.Integer(
        string='Cantidad pedida',
        compute='_compute_datos_pedido',
        readonly=True,
    )

    color_tela_id = fields.Many2one(
        'taller.color.tela',
        string='Color de combinacion',
        index=True,
    )

    cantidad_capas = fields.Integer(
        string='Cantidad de capas',
        required=True,
        default=1,
    )

    cantidad_producida = fields.Integer(
        string='Cantidad planificada',
        compute='_compute_resultado_color',
        store=True,
    )

    diferencia = fields.Integer(
        string='Diferencia',
        compute='_compute_resultado_color',
        store=True,
    )

    _sql_constraints = [
        (
            'tizada_pedido_color_unique',
            'unique(tizada_id, pedido_color_id)',
            'Este color del pedido ya fue agregado a la tizada.',
        ),
    ]

    @api.depends(
        'pedido_color_id',
        'pedido_color_id.color_tela_id',
        'pedido_color_id.cantidad_prendas',
        'color_base_carga_id',
        'cantidad_pedida_carga',
    )
    def _compute_datos_pedido(self):
        for linea in self:
            if linea.pedido_color_id:
                linea.color_base_id = (
                    linea.pedido_color_id.color_tela_id
                )
                linea.cantidad_pedida = (
                    linea.pedido_color_id.cantidad_prendas
                )
            else:
                linea.color_base_id = (
                    linea.color_base_carga_id
                )
                linea.cantidad_pedida = (
                    linea.cantidad_pedida_carga
                )

    @api.depends(
        'cantidad_capas',
        'pedido_color_id.cantidad_prendas',
        'cantidad_pedida_carga',
        'tizada_id.curva_ids.cantidad_por_capa',
    )
    def _compute_resultado_color(self):
        for linea in self:
            producido = 0

            for curva in linea.tizada_id.curva_ids:
                producido += floor(
                    curva.cantidad_por_capa
                    * linea.cantidad_capas
                )

            linea.cantidad_producida = producido

            if linea.pedido_color_id:
                cantidad_pedida = (
                    linea.pedido_color_id.cantidad_prendas
                )
            else:
                cantidad_pedida = (
                    linea.cantidad_pedida_carga
                )

            linea.diferencia = (
                producido - cantidad_pedida
                if cantidad_pedida
                else 0
            )

    @api.constrains('cantidad_capas')
    def _check_cantidad_capas(self):
        for linea in self:
            if linea.cantidad_capas <= 0:
                raise ValidationError(
                    _(
                        'La cantidad de capas '
                        'debe ser mayor que cero.'
                    )
                )


# ============================================================
# TIZADA
# ============================================================


class LineaTizada(models.Model):
    _name = 'taller.linea.tizada'
    _description = 'Linea de tizada'
    _order = 'id'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        required=True,
        index=True,
        ondelete='cascade',
    )

    tipo_tela = fields.Selection(
        TIPOS_TELA,
        string='Tipo de tela',
        required=True,
    )

    descripcion = fields.Char(
        string='Descripcion',
    )

    ancho_tizada = fields.Float(
        string='Ancho de tizada (m)',
        digits=(10, 2),
    )

    largo_tizada = fields.Float(
        string='Largo de tizada (m)',
        digits=(10, 2),
    )

    curva_ids = fields.One2many(
        'taller.linea.curva.tizada',
        'tizada_id',
        string='Curva interna',
    )

    capas_color_ids = fields.One2many(
        'taller.tizada.capa.color',
        'tizada_id',
        string='Capas por color',
    )

    prendas_por_capa = fields.Float(
        string='Prendas por capa',
        compute='_compute_datos_tizada',
        store=True,
        digits=(10, 2),
    )

    cantidad_capas = fields.Integer(
        string='Total de capas',
        compute='_compute_datos_tizada',
        store=True,
    )

    cantidad_producida = fields.Integer(
        string='Cantidad planificada',
        compute='_compute_datos_tizada',
        store=True,
    )

    tela_total = fields.Float(
        string='Tela total utilizada (m)',
        compute='_compute_datos_tizada',
        store=True,
        digits=(10, 2),
    )

    consumo = fields.Float(
        string='Consumo por prenda (m)',
        compute='_compute_datos_tizada',
        store=True,
        digits=(10, 3),
    )

    advertencia_produccion = fields.Text(
        string='Diferencia de produccion',
        compute='_compute_advertencia_produccion',
    )

    @api.depends(
        'largo_tizada',
        'curva_ids.cantidad_por_capa',
        'capas_color_ids.cantidad_capas',
        'capas_color_ids.cantidad_producida',
    )
    def _compute_datos_tizada(self):
        for tizada in self:
            tizada.prendas_por_capa = sum(
                tizada.curva_ids.mapped(
                    'cantidad_por_capa'
                )
            )

            tizada.cantidad_capas = sum(
                tizada.capas_color_ids.mapped(
                    'cantidad_capas'
                )
            )

            tizada.cantidad_producida = sum(
                tizada.capas_color_ids.mapped(
                    'cantidad_producida'
                )
            )

            tizada.tela_total = (
                tizada.largo_tizada
                * tizada.cantidad_capas
            )

            tizada.consumo = (
                tizada.tela_total
                / tizada.cantidad_producida
                if tizada.cantidad_producida
                else 0.0
            )

    @api.depends(
        'capas_color_ids.pedido_color_id',
        'capas_color_ids.color_base_carga_id',
        'capas_color_ids.cantidad_pedida_carga',
        'capas_color_ids.color_tela_id',
        'capas_color_ids.cantidad_producida',
        'capas_color_ids.diferencia',
    )
    def _compute_advertencia_produccion(self):
        for tizada in self:
            avisos = []

            for linea in tizada.capas_color_ids:
                if (
                    not linea.color_base_id
                    or linea.diferencia == 0
                ):
                    continue

                color_pedido = (
                    linea.color_base_id.display_name
                )

                color_material = (
                    linea.color_tela_id.display_name
                    if linea.color_tela_id
                    else '-'
                )

                if linea.diferencia > 0:
                    texto_diferencia = (
                        f'+{linea.diferencia}'
                    )
                else:
                    texto_diferencia = str(
                        linea.diferencia
                    )

                avisos.append(
                    _(
                        '%(pedido)s -> %(material)s: '
                        'pedido %(cantidad_pedida)s, '
                        'planificado %(cantidad_producida)s '
                        '(%(diferencia)s).'
                    ) % {
                        'pedido': color_pedido,
                        'material': color_material,
                        'cantidad_pedida': linea.cantidad_pedida,
                        'cantidad_producida': linea.cantidad_producida,
                        'diferencia': texto_diferencia,
                    }
                )

            tizada.advertencia_produccion = (
                '\n'.join(avisos)
                if avisos
                else False
            )

    @api.constrains(
        'ancho_tizada',
        'largo_tizada',
    )
    def _check_medidas_tizada(self):
        for tizada in self:
            if tizada.ancho_tizada < 0:
                raise ValidationError(
                    _(
                        'El ancho de la tizada '
                        'no puede ser negativo.'
                    )
                )

            if tizada.largo_tizada < 0:
                raise ValidationError(
                    _(
                        'El largo de la tizada '
                        'no puede ser negativo.'
                    )
                )

    def _valores_propuesta_pedido(self):
        self.ensure_one()

        orden = self.orden_id

        if (
            not orden
            or not orden.curva_pedido_ids
            or not orden.colores_pedido_ids
        ):
            return False

        curva = [
            (
                0,
                0,
                {
                    'talle': linea.talle,
                    'cantidad_por_capa': linea.cantidad_base,
                },
            )
            for linea in orden.curva_pedido_ids
        ]

        capas = []

        for color in orden.colores_pedido_ids:
            if not color.color_tela_id:
                continue

            cantidad_capas = (
                orden._calcular_capas_propuestas(
                    color.cantidad_prendas
                )
            )

            cantidad_capas = max(
                1,
                cantidad_capas,
            )

            capas.append(
                (
                    0,
                    0,
                    {
                        'color_base_carga_id': (
                            color.color_tela_id.id
                        ),
                        'cantidad_pedida_carga': (
                            color.cantidad_prendas
                        ),
                        'color_tela_id': False,
                        'cantidad_capas': cantidad_capas,
                    },
                )
            )

        return {
            'curva_ids': [
                (5, 0, 0),
                *curva,
            ],
            'capas_color_ids': [
                (5, 0, 0),
                *capas,
            ],
        }

    def _completar_datos_pedido_faltantes(self):
        for tizada in self:
            orden = tizada.orden_id

            if not orden:
                continue

            valores = {}

            if (
                not tizada.curva_ids
                and orden.curva_pedido_ids
            ):
                valores['curva_ids'] = [
                    (
                        0,
                        0,
                        {
                            'talle': linea.talle,
                            'cantidad_por_capa': linea.cantidad_base,
                        },
                    )
                    for linea in orden.curva_pedido_ids
                ]

            if (
                not tizada.capas_color_ids
                and orden.curva_pedido_ids
                and orden.colores_pedido_ids
            ):
                capas = []

                for color in orden.colores_pedido_ids:
                    if not color.color_tela_id:
                        continue

                    cantidad_capas = (
                        orden._calcular_capas_propuestas(
                            color.cantidad_prendas
                        )
                    )

                    cantidad_capas = max(
                        1,
                        cantidad_capas,
                    )

                    capas.append(
                        (
                            0,
                            0,
                            {
                                'color_base_carga_id': (
                                    color.color_tela_id.id
                                ),
                                'cantidad_pedida_carga': (
                                    color.cantidad_prendas
                                ),
                                'color_tela_id': False,
                                'cantidad_capas': cantidad_capas,
                            },
                        )
                    )

                if capas:
                    valores['capas_color_ids'] = capas

            if valores:
                tizada.write(valores)

        return True

    def _cargar_datos_pedido_en_memoria(self):
        for tizada in self:
            if (
                tizada.orden_id
                and not tizada.curva_ids
                and not tizada.capas_color_ids
            ):
                valores = (
                    tizada._valores_propuesta_pedido()
                )

                if valores:
                    tizada.update(valores)

    @api.onchange(
        'orden_id',
        'tipo_tela',
    )
    def _onchange_datos_tizada(self):
        self._cargar_datos_pedido_en_memoria()

    def _vincular_colores_pedido(self):
        for tizada in self:
            if not tizada.orden_id:
                continue

            for capa in tizada.capas_color_ids:
                color_base = (
                    capa.color_base_carga_id
                    or (
                        capa.pedido_color_id.color_tela_id
                        if capa.pedido_color_id
                        else False
                    )
                )

                if not color_base:
                    continue

                pedido_color = (
                    tizada.orden_id.colores_pedido_ids.filtered(
                        lambda pedido: (
                            pedido.color_tela_id.id
                            == color_base.id
                        )
                    )[:1]
                )

                if not pedido_color:
                    continue

                valores = {}

                if (
                    capa.pedido_color_id
                    != pedido_color
                ):
                    valores['pedido_color_id'] = (
                        pedido_color.id
                    )

                if (
                    capa.color_base_carga_id
                    != pedido_color.color_tela_id
                ):
                    valores['color_base_carga_id'] = (
                        pedido_color.color_tela_id.id
                    )

                if (
                    capa.cantidad_pedida_carga
                    != pedido_color.cantidad_prendas
                ):
                    valores['cantidad_pedida_carga'] = (
                        pedido_color.cantidad_prendas
                    )

                if valores:
                    capa.write(valores)

        return True

    @api.model_create_multi
    def create(self, vals_list):
        tizadas = super().create(vals_list)

        for tizada in tizadas:
            tizada._completar_datos_pedido_faltantes()
            tizada._vincular_colores_pedido()

        return tizadas


# ============================================================
# HISTORIAL
# ============================================================


class HistorialEstadoOrden(models.Model):
    _name = 'taller.orden.corte.historial'
    _description = 'Historial de estados de orden de corte'
    _order = 'fecha_inicio desc, id desc'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        required=True,
        index=True,
        ondelete='cascade',
    )

    estado_anterior = fields.Selection(
        ESTADOS_CORTE,
        string='Estado anterior',
    )

    estado = fields.Selection(
        ESTADOS_CORTE,
        string='Estado',
        required=True,
    )

    fecha_inicio = fields.Datetime(
        string='Inicio',
        required=True,
        default=fields.Datetime.now,
    )

    fecha_fin = fields.Datetime(
        string='Fin',
        readonly=True,
    )

    duracion_horas = fields.Float(
        string='Duracion (horas)',
        compute='_compute_duracion_horas',
        digits=(10, 2),
    )

    usuario_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )

    @api.depends(
        'fecha_inicio',
        'fecha_fin',
    )
    def _compute_duracion_horas(self):
        ahora = fields.Datetime.now()

        for historial in self:
            if not historial.fecha_inicio:
                historial.duracion_horas = 0.0
                continue

            fecha_fin = (
                historial.fecha_fin
                or ahora
            )

            diferencia = (
                fecha_fin
                - historial.fecha_inicio
            )

            historial.duracion_horas = (
                diferencia.total_seconds()
                / 3600
            )


# ============================================================
# ORDEN DE CORTE
# ============================================================


class OrdenCorte(models.Model):
    _name = 'taller.orden.corte'
    _description = 'Orden de corte'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
    ]
    _order = 'fecha_ingreso desc, id desc'

    name = fields.Char(
        string='N.º de orden',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
        tracking=True,
        index=True,
    )

    molderia = fields.Char(
        string='Molderia',
        tracking=True,
    )

    tela = fields.Char(
        string='Tela / Material',
    )

    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        tracking=True,
        index=True,
    )

    fecha_ingreso = fields.Date(
        string='Fecha de ingreso',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        index=True,
    )

    fecha_entrega_prevista = fields.Date(
        string='Entrega prevista',
        tracking=True,
        index=True,
    )

    fecha_entrega_real = fields.Date(
        string='Entrega real',
        readonly=True,
        tracking=True,
        index=True,
    )

    fecha_documento = fields.Date(
        string='Fecha del documento',
        compute='_compute_fecha_documento',
    )

    curva_pedido_ids = fields.One2many(
        'taller.orden.curva.pedido',
        'orden_id',
        string='Curva',
    )

    colores_pedido_ids = fields.One2many(
        'taller.orden.color.pedido',
        'orden_id',
        string='Cantidad pedida por color',
    )

    prendas_por_capa_plan = fields.Float(
        string='Curva total teorica',
        compute='_compute_totales_plan',
        digits=(10, 2),
    )

    cantidad_total_plan = fields.Integer(
        string='Total pedido',
        compute='_compute_totales_plan',
    )

    lineas_talle_ids = fields.One2many(
        'taller.linea.talle',
        'orden_id',
        string='Detalle por talle y color',
    )

    cantidad_total = fields.Integer(
        string='Cantidad base planificada',
        compute='_compute_cantidad_total',
        store=True,
        tracking=True,
    )

    lineas_tizada_ids = fields.One2many(
        'taller.linea.tizada',
        'orden_id',
        string='Tizadas',
    )

    notas = fields.Text(
        string='Notas / Instrucciones especiales',
    )

    foto_referencia = fields.Image(
        string='Ficha tecnica - Pagina 1',
        max_width=3508,
        max_height=3508,
    )

    ficha_tecnica_pagina_2 = fields.Image(
        string='Ficha tecnica - Pagina 2',
        max_width=3508,
        max_height=3508,
    )

    tiene_foto = fields.Boolean(
        string='Tiene ficha tecnica',
        compute='_compute_tiene_foto',
        store=True,
    )

    estado = fields.Selection(
        ESTADOS_CORTE,
        string='Estado',
        required=True,
        default='ingreso',
        tracking=True,
        index=True,
        group_expand='_read_group_estado',
    )

    historial_ids = fields.One2many(
        'taller.orden.corte.historial',
        'orden_id',
        string='Historial de estados',
        readonly=True,
    )

    advertencia_produccion = fields.Text(
        string='Advertencia de produccion',
        compute='_compute_advertencia_produccion',
    )

    @api.model
    def _read_group_estado(
        self,
        estados,
        domain,
        order,
    ):
        return [
            estado
            for estado, etiqueta
            in ESTADOS_CORTE
        ]

    def _compute_fecha_documento(self):
        hoy = fields.Date.context_today(self)

        for orden in self:
            orden.fecha_documento = hoy

    @api.depends(
        'curva_pedido_ids.cantidad_base',
        'colores_pedido_ids.cantidad_prendas',
    )
    def _compute_totales_plan(self):
        for orden in self:
            orden.prendas_por_capa_plan = sum(
                orden.curva_pedido_ids.mapped(
                    'cantidad_base'
                )
            )

            orden.cantidad_total_plan = sum(
                orden.colores_pedido_ids.mapped(
                    'cantidad_prendas'
                )
            )

    @api.depends(
        'lineas_talle_ids.cantidad',
    )
    def _compute_cantidad_total(self):
        for orden in self:
            orden.cantidad_total = sum(
                orden.lineas_talle_ids.mapped(
                    'cantidad'
                )
            )

    @api.depends(
        'foto_referencia',
        'ficha_tecnica_pagina_2',
    )
    def _compute_tiene_foto(self):
        for orden in self:
            orden.tiene_foto = bool(
                orden.foto_referencia
                or orden.ficha_tecnica_pagina_2
            )

    @api.depends(
        'lineas_tizada_ids.advertencia_produccion',
    )
    def _compute_advertencia_produccion(self):
        etiquetas_telas = dict(TIPOS_TELA)

        for orden in self:
            bloques = []

            for tizada in orden.lineas_tizada_ids:
                if not tizada.advertencia_produccion:
                    continue

                titulo = etiquetas_telas.get(
                    tizada.tipo_tela,
                    tizada.tipo_tela or _('Tizada'),
                )

                bloques.append(
                    f'{titulo}:\n'
                    f'{tizada.advertencia_produccion}'
                )

            orden.advertencia_produccion = (
                '\n\n'.join(bloques)
                if bloques
                else False
            )

    # --------------------------------------------------------
    # PRODUCCION BASE
    # --------------------------------------------------------

    def _produccion_plan_con_capas(
        self,
        cantidad_capas,
    ):
        self.ensure_one()

        return sum(
            floor(
                linea.cantidad_base
                * cantidad_capas
            )
            for linea in self.curva_pedido_ids
        )

    def _calcular_capas_propuestas(
        self,
        cantidad_pedida,
    ):
        self.ensure_one()

        if (
            cantidad_pedida <= 0
            or not self.curva_pedido_ids
        ):
            return 0

        suma_teorica = sum(
            self.curva_pedido_ids.mapped(
                'cantidad_base'
            )
        )

        if suma_teorica <= 0:
            return 0

        cantidad_capas = max(
            0,
            floor(
                cantidad_pedida
                / suma_teorica
            ),
        )

        while (
            self._produccion_plan_con_capas(
                cantidad_capas + 1
            )
            <= cantidad_pedida
        ):
            cantidad_capas += 1

        while (
            cantidad_capas > 0
            and self._produccion_plan_con_capas(
                cantidad_capas
            )
            > cantidad_pedida
        ):
            cantidad_capas -= 1

        return cantidad_capas

    def _comandos_distribucion_plan(self):
        self.ensure_one()

        comandos = [
            (5, 0, 0),
        ]

        if (
            not self.curva_pedido_ids
            or not self.colores_pedido_ids
        ):
            return comandos

        for color in self.colores_pedido_ids:
            if (
                not color.color_tela_id
                or color.cantidad_prendas <= 0
            ):
                continue

            capas = self._calcular_capas_propuestas(
                color.cantidad_prendas
            )

            for curva in self.curva_pedido_ids:
                if (
                    not curva.talle
                    or curva.cantidad_base <= 0
                ):
                    continue

                cantidad = floor(
                    curva.cantidad_base
                    * capas
                )

                if cantidad <= 0:
                    continue

                comandos.append(
                    (
                        0,
                        0,
                        {
                            'talle': curva.talle,
                            'color_tela_id': (
                                color.color_tela_id.id
                            ),
                            'cantidad': cantidad,
                        },
                    )
                )

        return comandos

    def _regenerar_distribucion_plan(self):
        for orden in self:
            super(
                OrdenCorte,
                orden,
            ).write({
                'lineas_talle_ids': (
                    orden._comandos_distribucion_plan()
                ),
            })

        return True

    @api.onchange(
        'curva_pedido_ids',
        'colores_pedido_ids',
    )
    def _onchange_plan_pedido(self):
        for orden in self:
            orden.update({
                'lineas_talle_ids': (
                    orden._comandos_distribucion_plan()
                ),
            })

    def action_generar_cantidades_desde_plan(self):
        for orden in self:
            if not orden.curva_pedido_ids:
                raise ValidationError(
                    _('Cargue primero la curva del pedido.')
                )

            if not orden.colores_pedido_ids:
                raise ValidationError(
                    _(
                        'Cargue primero las cantidades '
                        'pedidas por color.'
                    )
                )

        return self._regenerar_distribucion_plan()

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    def cantidad_planificada_talle_color(
        self,
        color_id,
        talle,
    ):
        self.ensure_one()

        lineas = self.lineas_talle_ids.filtered(
            lambda linea: (
                linea.color_tela_id.id == color_id
                and linea.talle == talle
            )
        )

        return sum(
            lineas.mapped('cantidad')
        )

    def etiqueta_talle(self, talle):
        return dict(TALLES).get(
            talle,
            talle,
        )

    # --------------------------------------------------------
    # INFERIR PLAN LEGACY
    # --------------------------------------------------------

    def action_inferir_plan_desde_cantidades(self):
        for orden in self:
            if not orden.lineas_talle_ids:
                raise ValidationError(
                    _(
                        'La orden no tiene cantidades '
                        'por talle y color para analizar.'
                    )
                )

            por_color = defaultdict(
                lambda: defaultdict(int)
            )

            for linea in orden.lineas_talle_ids:
                if (
                    not linea.color_tela_id
                    or linea.cantidad <= 0
                ):
                    raise ValidationError(
                        _(
                            'No se puede inferir la curva '
                            'si existen lineas sin color '
                            'o con cantidades menores '
                            'o iguales a cero.'
                        )
                    )

                por_color[
                    linea.color_tela_id.id
                ][
                    linea.talle
                ] += linea.cantidad

            curva_referencia = None
            colores_generados = []

            for color_id, cantidades in por_color.items():
                valores = list(
                    cantidades.values()
                )

                divisor = reduce(
                    gcd,
                    valores,
                )

                if divisor <= 0:
                    raise ValidationError(
                        _('No se pudo calcular la curva.')
                    )

                curva_normalizada = {
                    talle: (
                        cantidad
                        // divisor
                    )
                    for talle, cantidad
                    in cantidades.items()
                }

                if curva_referencia is None:
                    curva_referencia = (
                        curva_normalizada
                    )

                elif (
                    curva_normalizada
                    != curva_referencia
                ):
                    color = self.env[
                        'taller.color.tela'
                    ].browse(color_id)

                    raise ValidationError(
                        _(
                            'Las cantidades del color %(color)s '
                            'no siguen la misma curva que '
                            'los demas colores.'
                        ) % {
                            'color': color.display_name,
                        }
                    )

                colores_generados.append(
                    (
                        0,
                        0,
                        {
                            'color_tela_id': color_id,
                            'cantidad_prendas': sum(
                                cantidades.values()
                            ),
                        },
                    )
                )

            orden_talles = {
                talle: indice
                for indice, (
                    talle,
                    etiqueta,
                )
                in enumerate(TALLES)
            }

            curva_generada = []

            for talle, cantidad in sorted(
                curva_referencia.items(),
                key=lambda item: (
                    orden_talles.get(
                        item[0],
                        999,
                    )
                ),
            ):
                curva_generada.append(
                    (
                        0,
                        0,
                        {
                            'talle': talle,
                            'cantidad_base': float(
                                cantidad
                            ),
                        },
                    )
                )

            orden.write({
                'curva_pedido_ids': [
                    (5, 0, 0),
                    *curva_generada,
                ],
                'colores_pedido_ids': [
                    (5, 0, 0),
                    *colores_generados,
                ],
            })

        return True

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

    @api.constrains(
        'fecha_ingreso',
        'fecha_entrega_prevista',
    )
    def _check_fechas(self):
        for orden in self:
            if (
                orden.fecha_ingreso
                and orden.fecha_entrega_prevista
                and orden.fecha_entrega_prevista
                < orden.fecha_ingreso
            ):
                raise ValidationError(
                    _(
                        'La fecha prevista de entrega '
                        'no puede ser anterior '
                        'a la fecha de ingreso.'
                    )
                )

    def _validar_cantidades_finales(self):
        for orden in self:
            if not orden.lineas_talle_ids:
                raise ValidationError(
                    _(
                        'Debe existir al menos una cantidad '
                        'antes de pasar a Control o Entregado.'
                    )
                )

            incompletas = (
                orden.lineas_talle_ids.filtered(
                    lambda linea: (
                        linea.cantidad <= 0
                    )
                )
            )

            if incompletas:
                raise ValidationError(
                    _(
                        'No se puede pasar la orden '
                        'a Control o Entregado mientras '
                        'existan cantidades iguales a cero.'
                    )
                )

    # --------------------------------------------------------
    # HISTORIAL
    # --------------------------------------------------------

    def _cerrar_historial_abierto(
        self,
        fecha_fin,
    ):
        self.ensure_one()

        historial = self.env[
            'taller.orden.corte.historial'
        ].search(
            [
                ('orden_id', '=', self.id),
                ('fecha_fin', '=', False),
            ],
            order='fecha_inicio desc, id desc',
            limit=1,
        )

        if historial:
            historial.write({
                'fecha_fin': fecha_fin,
            })

    def _crear_historial_estado(
        self,
        estado_anterior,
        estado_nuevo,
        fecha_inicio=None,
    ):
        self.ensure_one()

        self.env[
            'taller.orden.corte.historial'
        ].create({
            'orden_id': self.id,
            'estado_anterior': estado_anterior,
            'estado': estado_nuevo,
            'fecha_inicio': (
                fecha_inicio
                or fields.Datetime.now()
            ),
            'usuario_id': self.env.user.id,
        })

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get(
                'name',
                'Nuevo',
            ) == 'Nuevo':

                fecha = (
                    vals.get('fecha_ingreso')
                    or fields.Date.context_today(
                        self
                    )
                )

                secuencia = (
                    self.env[
                        'ir.sequence'
                    ]
                    .with_context(
                        ir_sequence_date=fecha
                    )
                    .next_by_code(
                        'taller.orden.corte'
                    )
                )

                vals['name'] = (
                    secuencia
                    or 'Nuevo'
                )

        ordenes = super().create(
            vals_list
        )

        for orden in ordenes:
            orden._regenerar_distribucion_plan()

            orden.lineas_tizada_ids._completar_datos_pedido_faltantes()
            orden.lineas_tizada_ids._vincular_colores_pedido()

            if (
                orden.estado
                in ESTADOS_REQUIEREN_CANTIDADES
            ):
                orden._validar_cantidades_finales()

            orden._crear_historial_estado(
                estado_anterior=False,
                estado_nuevo=orden.estado,
            )

        return ordenes

    # --------------------------------------------------------
    # WRITE
    # --------------------------------------------------------

    def write(self, vals):
        resultado = True

        for orden in self:
            estado_anterior = orden.estado
            valores = dict(vals)

            nuevo_estado = valores.get(
                'estado',
                estado_anterior,
            )

            if (
                nuevo_estado == 'entregado'
                and estado_anterior != 'entregado'
            ):
                valores.setdefault(
                    'fecha_entrega_real',
                    fields.Date.context_today(
                        orden
                    ),
                )

            if (
                estado_anterior == 'entregado'
                and nuevo_estado != 'entregado'
            ):
                valores[
                    'fecha_entrega_real'
                ] = False

            resultado = super(
                OrdenCorte,
                orden,
            ).write(valores)

            if (
                'curva_pedido_ids' in valores
                or 'colores_pedido_ids' in valores
            ):
                orden._regenerar_distribucion_plan()

            orden.lineas_tizada_ids._completar_datos_pedido_faltantes()

            if (
                'colores_pedido_ids' in valores
                or 'lineas_tizada_ids' in valores
            ):
                orden.lineas_tizada_ids._vincular_colores_pedido()

            if (
                orden.estado
                in ESTADOS_REQUIEREN_CANTIDADES
            ):
                orden._validar_cantidades_finales()

            if estado_anterior != orden.estado:
                fecha_cambio = (
                    fields.Datetime.now()
                )

                orden._cerrar_historial_abierto(
                    fecha_cambio
                )

                orden._crear_historial_estado(
                    estado_anterior=estado_anterior,
                    estado_nuevo=orden.estado,
                    fecha_inicio=fecha_cambio,
                )

        return resultado

    # --------------------------------------------------------
    # ESTADOS
    # --------------------------------------------------------

    def _cambiar_estado(self, estado):
        self.write({
            'estado': estado,
        })
        return True

    def action_molderia(self):
        return self._cambiar_estado(
            'molderia'
        )

    def action_tizada(self):
        return self._cambiar_estado(
            'tizada'
        )

    def action_en_corte(self):
        return self._cambiar_estado(
            'en_corte'
        )

    def action_control(self):
        return self._cambiar_estado(
            'control'
        )

    def action_entregado(self):
        return self._cambiar_estado(
            'entregado'
        )