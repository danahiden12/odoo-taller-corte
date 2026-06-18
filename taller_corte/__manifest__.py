{
    'name': 'Taller de Corte',
    'version': '17.0.1.0.0',
    'summary': 'Gestión de órdenes de corte para taller de indumentaria',
    'category': 'Manufacturing',
    'author': 'Dana Hiden',
    'license': 'LGPL-3',
    'application': True,
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/orden_corte_views.xml',
        'reports/reporte_corte.xml',
    ],
    'installable': True,
    'auto_install': False,
}