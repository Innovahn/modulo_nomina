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
from time import strftime
from datetime import datetime

view_form = """<?xml version="1.0"?>
<form string="Pago Utilidades">
   <group colspan="4" string="Pago Utilidades">
        <field name="year"/>
        <field name="valor_utilidad"/>
   </group>
</form>
"""

fields_form = {
    'year' : {'string' : 'Año', 'type' : 'integer', 'default' : strftime('%Y'), 'required' : True},
    'valor_utilidad' : {'string' : 'Valor Utilidad', 'type' : 'float' , 'required' : True},
    }

end_form="""<?xml version="1.0"?>
<form string="Pago de Utilidad">
<image name="gtk-dialog-info" colspan="2"/>
<label string="El Valor de Utilidades se ha calculado correctamente." colspan="4"/>
<field name="val10" readonly="1"/>
<field name="val5" readonly="1"/>
</form>"""

end_fields = {
    'val10' : {'string' : 'Utilidades al 10%', 'type' : 'float'},
    'val5' : {'string' : 'Utilidades al 5%', 'type' : 'float'}
}

class wizard_utilities(osv.osv_memory):

    _name="wizard.utilities"
    def _process_message(self, cr, uid, data, context):
        return {}

    def _crear_utilidad(self, cr, uid, data, context):
        form = data['form']
        year = form['year']
        valor_utilidad = form['valor_utilidad']
        val10 = valor_utilidad * 0.10
        val5 = valor_utilidad * 0.05
        res = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [])
        cr.execute("SELECT sum(children) FROM hr_employee")
        res1 = cr.fetchall()[0]
        resval = 0
        if res1[0]:
             resval = res1[0]
             util_cargas = val5 / resval
        else:
            util_cargas = 0
        util_employee = val10 / len(res)
        for item in res:
            ruli = pooler.get_pool(cr.dbname).get('hr.employee').browse(cr, uid, item)
            hijos = ruli.children
            if not hijos:
                hijos = 0
            total_cargas = util_cargas * hijos
            sql = "SELECT max(date_start) FROM hr_contract WHERE employee_id = %s" % ruli.id
            cr.execute(sql)
            res2 = cr.fetchall()[0]
            date_start = datetime.strptime(res2[0], "%Y-%m-%d")
            dt = datetime.today() - date_start
            years = dt.days / 365.0
            util = pooler.get_pool(cr.dbname).get('hr.employee.util')
            print util_employee, total_cargas
            val1 = 0
            val5 = 0
            if years >= 1:
                val1 = util_employee
                util.create(cr, uid, {'name' : 'Pago utilidades' + strftime('%Y'), 'val10': util_employee, 'val5' : total_cargas, 
                                      'total' : util_employee + total_cargas, 'employee_id' : ruli.id})
            else:
                months =  dt.days / 30.0
                val1 = months * util_employee / 12
                util.create(cr, uid, {'name' : 'Pago Utilidades' + strftime('%Y'), 'val10' : val1, 'val5' : total_cargas, 
                                      'total' : util_employee + total_cargas, 'employee_id' : ruli.id})            
        return {'val10' : val1, 'val5' : total_cargas}
    
    states={
        'init':{
            'actions': [],
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state':[
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('processed', 'Ok', 'gtk-ok', True)
                ]
            }
        },
        'processed':{
            'actions':[_crear_utilidad],
            'result':{'type':'form', 'arch':end_form, 'fields':end_fields, 'state':[('end','Cerrar')]}
        }
        }
wizard_utilities()

