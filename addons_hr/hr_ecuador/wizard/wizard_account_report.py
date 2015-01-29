# -*- encoding: utf-8 -*-
##############################################################################
#
#    HHRR Module
#    Copyright (C) 2009 GnuThink Software  All Rights Reserved
#    info@gnuthink.com
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import wizard
import base64
import StringIO
import csv
import pooler
from time import strftime

view_form="""<?xml version="1.0"?>
<form string="Exportar Archivos">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Exportar Archivos" colspan="4"/>
        <field name="period_id"/>
    </group>
</form>"""

view_fields = {
    'period_id' : {'string' : 'Periodo/Mes' , 'type' : 'many2one', 'relation' : 'hr.contract.period', 'required' : True},
    }

fields_form_finish = {
    'data': {'string':'Archivo Nomina', 'type':'binary', 'readonly': True},
    'name': {'string':'Nombre', 'type':'string', 'readonly': True},
    'data1': {'string':'Archivo Provisiones', 'type':'binary', 'readonly': True},
    'name1': {'string':'Nombre', 'type':'string', 'readonly': True},    
    }

view_form_finish="""<?xml version="1.0"?>
<form string="Exportar Reportes">
	<image name="gtk-dialog-info" colspan="2"/>
	<group colspan="2" col="4">
		<separator string="Archivo Generado" colspan="4"/>
		<field name="data" readonly="1" colspan="3"/>
                <separator string="Archivo Provisiones" colspan="4"/>
                <field name="data1" readonly="1" colspan="3"/>
	</group>
</form>"""


class wizard_account_report(wizard.interface):
    def crear_archivos(self, cr, uid, data, context):
        form = data['form']
        periodo = form['period_id']
        res = pooler.get_pool(cr.dbname).get('hr.payroll').search(cr, uid, [('period_id','=',periodo)])
        buf = StringIO.StringIO()
        writer = csv.writer(buf)
        for item in res:
            rol = pooler.get_pool(cr.dbname).get('hr.payroll').browse(cr, uid, item)
            item = rol.employee_id.name.encode('UTF-8'), rol.employee_id.cedula, 30, rol.num_dias, rol.total_ingresos, rol.total_egresos, rol.total
            writer.writerow(item)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        return { 'data' : out, 'name' : "reporte-nomina-periodo-%s-%s.csv" % (str(periodo), strftime("%Y-%m-%d  %H:%M"))}

    def crear_prov(self, cr, uid, data, context):
        form = data['form']
        periodo = form['period_id']
        res = pooler.get_pool(cr.dbname).get('hr.payroll').search(cr, uid, [('period_id','=',periodo)])
        buf2 = StringIO.StringIO()
        writer2 = csv.writer(buf2)
        for item in res:
            rol = pooler.get_pool(cr.dbname).get('hr.payroll').browse(cr, uid, item)
            for it in rol.provisiones_id:
                item2 = rol.employee_id.cedula, it.decimo3ro, it.decimo4to, it.vacaciones, it.fondo_reserva, it.aporte_patronal
            writer2.writerow(item2)
        out2 = base64.encodestring(buf2.getvalue())
        buf2.close()
        return {'data1' : out2, 'name1' : "provisiones-Mes-%s.csv" % ( strftime("%Y-%m-%d  %H:%M"))}

    states = {
           'init': {
                'actions': [],
                'result': {'type': 'form',
                           'arch': view_form,
                           'fields': view_fields,
                           'state' : [('end', 'Cancelar'),('generate', 'Generar Archivos') ]}
          },
           'generate': {
                'actions': [crear_archivos, crear_prov],
                'result': { 'type': 'form',
                            'arch': view_form_finish,
                            'fields' : fields_form_finish,
                            'state': [
                            ('end', 'Close', 'gtk-cancel', True)
                        ]
                }
          },
        }
wizard_account_report('wizard.account.report')
