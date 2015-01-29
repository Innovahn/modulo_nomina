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
import pooler
from time import strftime

init_form = '''<?xml version="1.0"?>
<form string="Asistente de Cambio de Sueldo">
      <label string="Este Asistente le ayudará a Realizar un cambio en el sueldo de un empleado\nSeleccionará en contrato." colspan="4"/>
      <field name="contract_id"/>
      <field name="new_wage"/>
</form>
'''

init_fields = {
    'contract_id' : {'string' : 'Contrato', 'type' : 'many2one', 'relation' : 'hr.contract', 'required' : True},
    'new_wage' : {'string' : 'Nuevo Sueldo', 'type' : 'float', 'required' : True},
    }


finish_form = '''<?xml version="1.0"?>
<form string="Asistente de Cambio de Sueldo">
      <label string="El cambio se ha realizado correctamente"/>
</form>'''

class wizard_update_wage(osv.osv_memory):
    _name="wizard.update.wage"   
    def _update_wage(self, cr, uid, data, context):
        form = data['form']
        contract_id = form['contract_id'] 
        contract = pooler.get_pool(cr.dbname).get('hr.contract').browse(cr, uid, contract_id)
        new_wage = form['new_wage']
        pooler.get_pool(cr.dbname).get('hr.contract').write(cr, uid, contract_id, {'wage' : new_wage, 'iess' : new_wage * 0.0935, 
        'help_food' : new_wage * 0.20, 'costo_hora' :(new_wage +(new_wage * 0.20))/240})
        line = pooler.get_pool(cr.dbname).get('hr.contract.wage')
        line.create(cr, uid, {'name' : strftime('%Y-%m-%d : %H:%M'), 'wage': contract.wage, 'contract_id' : contract.id})
        return {}

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form', 'arch' : init_form, 'fields' : init_fields, 'state' : [('end', 'Cancelar'), ('update_wage', 'Actualizar Sueldo')] },
            },
        'update_wage' : {
            'actions' : [_update_wage],
            'result' : {'type' : 'form', 'arch' : finish_form, 'fields' : {}, 'state' : [('end', 'Ok', 'gtk-ok', True)]}
            }
        }
wizard_update_wage()
