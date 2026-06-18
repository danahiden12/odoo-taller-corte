from odoo import models, fields, api


class LineaTalle(models.Model):
    _name = 'taller.linea.talle'
    _description = 'Línea de Talle'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        ondelete='cascade'
    )

    talle = fields.Selection([
        ('xs',  'XS'),
        ('s',   'S'),
        ('m',   'M'),
        ('l',   'L'),
        ('xl',  'XL'),
        ('2xl', '2XL'),
        ('3xl', '3XL'),
        ('1',  '1'),
        ('2',  '2'),
        ('3',  '3'),
        ('4',  '4'),
        ('5',  '5'),
        ('6',  '6'),
        ('7',  '7'),
        ('8',  '8'),
        ('9',  '9'),
        ('10', '10'),
        ('12', '12'),
        ('14', '14'),
        ('16', '16'),
        ('18', '18'),
    ], string='Talle', required=True)

    cantidad = fields.Integer(
        string='Cantidad',
        required=True,
        default=0
    )

    color_tela = fields.Char(
        string='Color',
        help='Ej: negro, blanco, rojo'
    )


class LineaTizada(models.Model):
    _name = 'taller.linea.tizada'
    _description = 'Línea de Tizada'

    orden_id = fields.Many2one(
        'taller.orden.corte',
        string='Orden',
        ondelete='cascade'
    )

    tipo_tela = fields.Selection([
        ('tela_plana',  'Tela plana'),
        ('tela_punto',  'Tela de punto'),
        ('lycra',       'Lycra'),
        ('jean',        'Jean'),
        ('poplin',      'Poplin'),
        ('lino',        'Lino'),
        ('gabardina',   'Gabardina'),
        ('forreria',    'Forreria'),
        ('otro',        'Otro'),
    ], string='Tipo de Tela', required=True)

    descripcion = fields.Char(
        string='Descripción',
        help='Ej: Lycra negra, Poplin blanco rayado'
    )

    ancho_tizada = fields.Float(
        string='Ancho (mts)',
        digits=(6, 2)
    )

    largo_tizada = fields.Float(
        string='Largo (mts)',
        digits=(6, 2)
    )

    consumo = fields.Float(
        string='Consumo (mts)',
        compute='_compute_consumo',
        store=True,
        digits=(6, 3)
    )

    @api.depends('largo_tizada', 'orden_id.cantidad_total')
    def _compute_consumo(self):
        for linea in self:
            if linea.orden_id.cantidad_total > 0:
                linea.consumo = (
                    linea.largo_tizada / linea.orden_id.cantidad_total
                )
            else:
                linea.consumo = 0.0


class OrdenCorte(models.Model):
    _name = 'taller.orden.corte'
    _description = 'Orden de Corte'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _read_group_estado(self, estados, domain, order):
        """
        Fuerza el orden de las columnas del Kanban.
        Sin esto Odoo las ordena alfabéticamente.
        """
        return ['ingreso', 'molderia', 'en_corte', 'control', 'entregado']

    name = fields.Char(
    string='N° de Orden',
    required=True,
    copy=False,
    tracking=True
)

    molderia = fields.Char(
        string='Moldería',
        help='Nombre o código de la moldería digital'
    )

    tela = fields.Char(
        string='Tela / Material'
    )

    lineas_talle_ids = fields.One2many(
        'taller.linea.talle',
        'orden_id',
        string='Talles y Cantidades'
    )

    cantidad_total = fields.Integer(
        string='Cantidad Total',
        compute='_compute_cantidad_total',
        store=True,
        tracking=True
    )

    @api.depends('lineas_talle_ids.cantidad')
    def _compute_cantidad_total(self):
        for orden in self:
            orden.cantidad_total = sum(
                linea.cantidad for linea in orden.lineas_talle_ids
            )

    lineas_tizada_ids = fields.One2many(
        'taller.linea.tizada',
        'orden_id',
        string='Tizadas'
    )

    fecha_ingreso = fields.Date(
        string='Fecha de Ingreso',
        default=fields.Date.today
    )

    fecha_entrega = fields.Date(
        string='Fecha de Entrega',
        tracking=True
    )

    cliente_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        tracking=True
    )

    notas = fields.Text(
        string='Notas / Instrucciones Especiales'
    )

    foto_referencia = fields.Image(
        string='Foto de Referencia',
        max_width=1920,
        max_height=1920
    )

    tiene_foto = fields.Boolean(
        compute='_compute_tiene_foto',
        store=True
    )

    @api.depends('foto_referencia')
    def _compute_tiene_foto(self):
        for orden in self:
            orden.tiene_foto = bool(orden.foto_referencia)

    estado = fields.Selection([
        ('ingreso',   'Ingreso Corte'),
        ('molderia',  'Moldería Digital'),
        ('en_corte',  'En Corte'),
        ('control',   'Cortado / Control'),
        ('entregado', 'Entregado'),
    ],
        string='Estado',
        default='ingreso',
        tracking=True,
        group_expand='_read_group_estado'
    )

# ── MÉTODOS DE CAMBIO DE ESTADO ─────────────────
    def action_molderia(self):
        # mueve la orden a Moldería Digital
        self.estado = 'molderia'

    def action_en_corte(self):
        # mueve la orden a En Corte
        self.estado = 'en_corte'

    def action_control(self):
        # mueve la orden a Cortado/Control
        self.estado = 'control'

    def action_entregado(self):
        # mueve la orden a Entregado
        self.estado = 'entregado'

    def action_ingreso(self):
        # vuelve la orden a Ingreso (por si hay que corregir)
        self.estado = 'ingreso'

    color = fields.Integer(string='Color')