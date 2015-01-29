# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 (http://gnuthink.com) All Rights Reserved.
#       Cristian Salamea <cristian.salamea@gnuthink.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import osv,fields
import pooler
import StringIO
import base64
import csv
from time import strftime

init_form = """<?xml version="1.0"?>
        <form string="Asistente de generación de Anexo">
          <separator string="Asistente de Ajuste Retención por Relación de Dependencia RDEP" colspan="4"/>
          <label string="Este asistente, te ayudará a realizar el ajuste para en Impuesto a la Renta." colspan="4"/>
          <label string="Luego de esto, tendrás que guardar el archivo para subir a rol de este Mes."/>
        </form>"""

view_form_finish="""<?xml version="1.0"?>
<form string="Exportar XML">
	<image name="gtk-dialog-info" colspan="2"/>
	<group colspan="2" col="4">
		<separator string="Archivo Generado" colspan="4"/>
		<field name="data" readonly="1" colspan="3"/>
		<label align="0.0" string="Guardar este documento como .CSV" colspan="4"/>
	</group>
</form>"""

fields_form_finish={
    'data': {'string':'Archivo', 'type':'binary', 'readonly': True, 'default':strftime('%Y')},
    'name': {'string':'Nombre', 'type':'string', 'readonly': True},
}


class wizard_adjust_rdep(osv.osv_memory):
    _name="wizard.adjust.rdep"   
    def crear_file(self, cr, uid, data, context):
        emp_ids = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [])
        buf = StringIO.StringIO()
        writer = csv.writer(buf)
        for emp_id in emp_ids:
            rol_ids = pooler.get_pool(cr.dbname).get('hr.payroll').search(cr, uid, [('employee_id','=',emp_id)])
            roles = pooler.get_pool(cr.dbname).get('hr.payroll').browse(cr, uid, rol_ids)
            acum_ingresos = 0
            acum_whelp = 0
            for obj in roles:
                res = pooler.get_pool(cr.dbname).get('hr.contract.period').search(cr, uid, [('date_stop','<=','31-12-'+strftime('%Y'))])
                ing_grav = (obj.contract_id.wage + obj.contract_id.help_food + obj.horas_125 + obj.horas_150 + obj.horas_200)
                t_whelp = ing_grav - obj.contract_id.help_food
                acum_ingresos += ing_grav
                acum_whelp += t_whelp

            ap_personal = acum_whelp * 0.0935
            t_wiess = acum_ingresos - ap_personal
            gastos_personales = obj.contract_id.proyeccion + obj.contract_id.proy_vivienda + obj.contract_id.proy_salud + obj.contract_id.proy_alimentacion + obj.contract_id.proy_vestimenta
            base = t_wiess - gastos_personales
            sql = "SELECT l.percent, l.fraccion_basica, l.frac_basica_tax FROM hr_base_retention t, hr_base_retencion_line l WHERE \
                                     t.year='%s' AND l.fraccion_basica <=%f and %f <= l.exceso_hasta" % (strftime('%Y'),base,base)
            cr.execute(sql)
            res1 = cr.fetchall()
            exed = base - res1[0][1]
            pago_exed = exed * res1[0][0]
            total = pago_exed + res1[0][2]

            contract_id = pooler.get_pool(cr.dbname).get('hr.contract').search(cr, uid, [('employee_id','=',emp_id)])
            contract = pooler.get_pool(cr.dbname).get('hr.contract').browse(cr, uid, contract_id)[0]
            value = total - contract.impuesto_renta
            if value > 0:
                item = contract.employee_id.cedula, value
                writer.writerow(item)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        return {'data' : out, 'name': "AjusteImpuestoRenta-%s.csv" % strftime('%Y')}
            

    states = {
           'init': {
                'actions': [],
                'result': {'type': 'form',
                           'arch': init_form,
                           'fields': {},
                           'state' : [('end', 'Cancelar'),('generate', 'Generar CSV') ]}
          },
           'generate': {
                'actions': [crear_file],
                'result': { 'type': 'form',
                            'arch': view_form_finish,
                            'fields' : fields_form_finish,
                            'state': [
                            ('end', 'Close', 'gtk-cancel', True)
                        ]
                }
          },
     }
wizard_adjust_rdep()
