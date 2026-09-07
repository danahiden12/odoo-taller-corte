{
    'name': 'Taller de Corte',
    'version': '17.0.3.0.0',
    'summary': 'Gestión de órdenes, tizadas y procesos de corte',
    'category': 'Manufacturing',
    'author': 'Dana Hiden',
    'license': 'LGPL-3',
    'application': True,

    'depends': [
        'base',
        'mail',
        'web',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/secuencia.xml',
        'data/colores.xml',
        'views/orden_corte_views.xml',
        'reports/reporte_corte.xml',
    ],

    'installable': True,
    'auto_install': False,
}