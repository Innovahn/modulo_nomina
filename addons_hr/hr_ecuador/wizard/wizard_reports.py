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

view_form="""<?xml version="1.0"?>
<form string="Generar Reportes">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Generar Reportes" colspan="4"/>
        <field name="tipo"/>
    </group>
</form>"""

view_fields = {
    'tipo' : {'string' : 'Tipo', 'type' : 'selection', 'selection'  :[('decimo3','Decimo Tercero'),('decimo4','Decimo Cuarto'),('utilidades', 'Utilidades')], 'required':True},
    }

class wizard_reports(osv.osv_memory):
    _name="wizard.reports"
    def _get_selection(self, cr, uid, data, context):
        return data['form']

    def _check_report(self, cr, uid, data, context):
        form = data['form']
        sel = form['tipo']
        print "seleccion", sel
        if sel == 'decimo3':
            return 'report_13'
        elif sel == 'decimo4':
            return 'report_14'
        else:
            return 'utilidades'

    states = {
           'init': {
                'actions': [_get_selection],
                'result': {'type': 'form',
                           'arch': view_form,
                           'fields': view_fields,
                           'state' : [('end', 'Cancelar'),('check', 'Imprimir Reporte') ]}
          },
           'check': {
                'actions': [],
                'result': { 'type': 'choice', 'next_state' : _check_report}
          },

           'report_13' : {'actions' : [], 
                          'result' : {'type' : 'print', 'report' : 'decimo3', 'state' : 'end'}},
           'report_14' : {'actions' : [], 
                          'result' : {'type' : 'print', 'report' : 'decimo4', 'state' : 'end'}},
           'utilidades' : {'actions' : [], 
                           'result' : {'type' : 'print', 'report' : 'utilidades', 'state' : 'end'}},
        }
wizard_reports()
