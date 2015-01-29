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

from openerp.osv import osv,fields
import base64
import StringIO
import pooler
from time import strftime
from string import upper
from string import join


pay_form = """<?xml version="1.0"?>
<form string="Crear Cash">
    <separator string="Generacion de Cash para Pago" colspan="4"/>
    <field name="month"/>
</form>
"""

pay_fields={
    'month' : {'string':'Mes', 'type':'many2one', 'relation':'hr.contract.period', 'required' : True},
}

view_form_finish="""<?xml version="1.0"?>
<form string="Exportar TXT">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Archivo Generado" colspan="4"/>
        <field name="data" readonly="1" colspan="3"/>
        <separator  string="Guardar este Documento como TXT\nConfirmar la info !" colspan="4"/>
    </group>
</form>"""

fields_form_finish={
    'data': {'string':'Archivo', 'type':'binary', 'readonly': True,},
    'name': {'string':'Nombre', 'type':'string', 'readonly': True,},
}

class wizard_payment_cash(osv.osv_memory):
    _name="wizard.payment.cash" 	   
    def crear_cash(self, cr, uid, data, context):
        form = data['form']
        period_id = form['month']
        forma_pago = "CTA"
        cur = "USD"
        ref = "PAGO NOMINA " + str(period_id)
        buf = StringIO.StringIO()
        res = pooler.get_pool(cr.dbname).get('hr.payroll').search(cr, uid, [('period_id','=', period_id),('state','=','validate')])
        if res:
            for payroll_id in res:
              rol =  pooler.get_pool(cr.dbname).get('hr.payroll').browse(cr, uid, payroll_id)
              cadena = ""
              ced = str(rol.employee_id.cedula)
              val = str(rol.total)
              l = ""
              for item in val:
                  if item <> '.':
                      l += item
              print l
              t_cta = str(rol.employee_id.bank_account_id.type)
              num_cta = str(rol.employee_id.bank_account_id.name)
              t_em = str(rol.employee_id.tipoid)
              nombre = str(rol.employee_id.name.encode('UTF-8'))
              cadena = "PA\t" + ced + '\t' + cur + '\t' + l + '\t' + forma_pago + '\t' + t_cta + '\t' + num_cta + '\t' + ref + '\t' + t_em + '\t' + ced + '\t' + nombre +'\n'
              buf.write(upper(cadena))
        out = base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s.TXT" % ("PAGOS", strftime('%Y-%m'))
        print "nombre del archivo %s" % name
        return {'data': out, 'name': name}

    states = {
           'init': {
                'actions': [],
                'result': {'type': 'form',
                           'arch': pay_form,
                           'fields': pay_fields,
                           'state' : [('end', 'Cancelar', 'gtk-cancel', True),('generate', 'Generar Cash')]}
                },
           'generate': {
                'actions': [crear_cash],
                'result': { 'type': 'form',
                            'arch': view_form_finish,
                            'fields' : fields_form_finish,
                            'state': [
                            ('end', 'Cerrar', 'gtk-cancel', True)
                        ]
                }
          },
    }
wizard_payment_cash()
