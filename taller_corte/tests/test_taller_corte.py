from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestTallerCorte(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.color_negro = cls.env[
            'taller.color.tela'
        ].create({
            'name': 'Negro Test',
        })

        cls.color_azul = cls.env[
            'taller.color.tela'
        ].create({
            'name': 'Azul Test',
        })

    # ========================================================
    # CANTIDADES BÁSICAS
    # ========================================================

    def test_cantidad_total(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({
            'lineas_talle_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 10,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 20,
                    },
                ),
            ],
        })

        self.assertEqual(
            orden.cantidad_total,
            30,
        )

    def test_cantidad_negativa(self):
        with self.assertRaises(ValidationError):

            self.env[
                'taller.orden.corte'
            ].create({
                'lineas_talle_ids': [
                    (
                        0,
                        0,
                        {
                            'talle': 'm',
                            'color_tela_id': self.color_negro.id,
                            'cantidad': -10,
                        },
                    ),
                ],
            })

    # ========================================================
    # PLAN DEL PEDIDO
    # ========================================================

    def test_generar_cantidades_desde_plan(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({
            'curva_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'cantidad_base': 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'cantidad_base': 1,
                    },
                ),
            ],
            'colores_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_negro.id,
                        'cantidad_prendas': 150,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_azul.id,
                        'cantidad_prendas': 150,
                    },
                ),
            ],
        })

        self.assertEqual(
            orden.prendas_por_capa_plan,
            6,
        )

        self.assertEqual(
            orden.cantidad_total_plan,
            300,
        )

        orden.action_generar_cantidades_desde_plan()

        self.assertEqual(
            len(orden.lineas_talle_ids),
            8,
        )

        self.assertEqual(
            orden.cantidad_total,
            300,
        )

        linea_s_negro = (
            orden.lineas_talle_ids.filtered(
                lambda linea: (
                    linea.talle == 's'
                    and linea.color_tela_id
                    == self.color_negro
                )
            )
        )

        self.assertEqual(
            linea_s_negro.cantidad,
            50,
        )

        linea_l_azul = (
            orden.lineas_talle_ids.filtered(
                lambda linea: (
                    linea.talle == 'l'
                    and linea.color_tela_id
                    == self.color_azul
                )
            )
        )

        self.assertEqual(
            linea_l_azul.cantidad,
            25,
        )

    # ========================================================
    # CANTIDAD NO DIVISIBLE POR LA CURVA
    # ========================================================

    def test_cantidad_no_divisible_por_curva(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({
            'curva_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'cantidad_base': 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'cantidad_base': 1,
                    },
                ),
            ],
            'colores_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_negro.id,
                        'cantidad_prendas': 155,
                    },
                ),
            ],
        })

        with self.assertRaises(ValidationError):
            orden.action_generar_cantidades_desde_plan()

    # ========================================================
    # INFERIR PLAN DESDE UNA ORDEN ANTERIOR
    # ========================================================

    def test_inferir_plan_desde_cantidades(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({
            'lineas_talle_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 50,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 50,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 25,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'color_tela_id': self.color_negro.id,
                        'cantidad': 25,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'color_tela_id': self.color_azul.id,
                        'cantidad': 50,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'color_tela_id': self.color_azul.id,
                        'cantidad': 50,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'color_tela_id': self.color_azul.id,
                        'cantidad': 25,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'color_tela_id': self.color_azul.id,
                        'cantidad': 25,
                    },
                ),
            ],
        })

        orden.action_inferir_plan_desde_cantidades()

        self.assertEqual(
            len(orden.curva_pedido_ids),
            4,
        )

        self.assertEqual(
            len(orden.colores_pedido_ids),
            2,
        )

        curva_s = (
            orden.curva_pedido_ids.filtered(
                lambda linea: linea.talle == 's'
            )
        )

        curva_l = (
            orden.curva_pedido_ids.filtered(
                lambda linea: linea.talle == 'l'
            )
        )

        self.assertEqual(
            curva_s.cantidad_base,
            2,
        )

        self.assertEqual(
            curva_l.cantidad_base,
            1,
        )

        negro = (
            orden.colores_pedido_ids.filtered(
                lambda linea: (
                    linea.color_tela_id
                    == self.color_negro
                )
            )
        )

        azul = (
            orden.colores_pedido_ids.filtered(
                lambda linea: (
                    linea.color_tela_id
                    == self.color_azul
                )
            )
        )

        self.assertEqual(
            negro.cantidad_prendas,
            150,
        )

        self.assertEqual(
            azul.cantidad_prendas,
            150,
        )

        self.assertEqual(
            orden.prendas_por_capa_plan,
            6,
        )

        self.assertEqual(
            orden.cantidad_total_plan,
            300,
        )

    # ========================================================
    # CÁLCULO DE TIZADA
    # ========================================================

    def test_calculo_tizada(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({})

        tizada = self.env[
            'taller.linea.tizada'
        ].create({
            'orden_id': orden.id,
            'tipo_tela': 'lycra',
            'ancho_tizada': 1.40,
            'largo_tizada': 3.30,
            'curva_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'cantidad_por_capa': 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'cantidad_por_capa': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'cantidad_por_capa': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'cantidad_por_capa': 1,
                    },
                ),
            ],
            'capas_color_ids': [
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_negro.id,
                        'cantidad_capas': 20,
                    },
                ),
            ],
        })

        self.assertEqual(
            tizada.prendas_por_capa,
            6,
        )

        self.assertEqual(
            tizada.cantidad_capas,
            20,
        )

        self.assertEqual(
            tizada.cantidad_producida,
            120,
        )

        self.assertAlmostEqual(
            tizada.tela_total,
            66.0,
            places=2,
        )

        self.assertAlmostEqual(
            tizada.consumo,
            0.55,
            places=3,
        )

    # ========================================================
    # PROPONER TIZADA DESDE EL PEDIDO
    # ========================================================

    def test_proponer_tizada_desde_pedido(self):
        orden = self.env[
            'taller.orden.corte'
        ].create({
            'curva_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'talle': 's',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'm',
                        'cantidad_base': 2,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'l',
                        'cantidad_base': 1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'talle': 'xl',
                        'cantidad_base': 1,
                    },
                ),
            ],
            'colores_pedido_ids': [
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_negro.id,
                        'cantidad_prendas': 150,
                    },
                ),
                (
                    0,
                    0,
                    {
                        'color_tela_id': self.color_azul.id,
                        'cantidad_prendas': 150,
                    },
                ),
            ],
        })

        orden.action_generar_cantidades_desde_plan()

        tizada = self.env[
            'taller.linea.tizada'
        ].create({
            'orden_id': orden.id,
            'tipo_tela': 'lycra',
            'largo_tizada': 3.30,
        })

        tizada.action_proponer_desde_pedido()

        self.assertEqual(
            len(tizada.curva_ids),
            4,
        )

        self.assertEqual(
            len(tizada.capas_color_ids),
            2,
        )

        self.assertEqual(
            tizada.prendas_por_capa,
            6,
        )

        self.assertEqual(
            tizada.cantidad_capas,
            50,
        )

        self.assertEqual(
            tizada.cantidad_producida,
            300,
        )

        negro = (
            tizada.capas_color_ids.filtered(
                lambda linea: (
                    linea.color_tela_id
                    == self.color_negro
                )
            )
        )

        azul = (
            tizada.capas_color_ids.filtered(
                lambda linea: (
                    linea.color_tela_id
                    == self.color_azul
                )
            )
        )

        self.assertEqual(
            negro.cantidad_capas,
            25,
        )

        self.assertEqual(
            azul.cantidad_capas,
            25,
        )

        self.assertAlmostEqual(
            tizada.tela_total,
            165.0,
            places=2,
        )