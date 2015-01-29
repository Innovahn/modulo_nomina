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
import pooler
import time
import base64
from datetime import datetime

noced=[]
wrong_values=[]

view_form="""<?xml version="1.0"?>
<form string="Importar Pago Comida">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Importar Pago Comida" colspan="4"/>
        <field name="date"/>
        <field name="period_id"/>
        <field name="data" colspan="4"/>
        <label string="Importar un archivo CSV" colspan="4" align="0.0"/>
    </group>
</form>"""

end_form="""<?xml version="1.0"?>
<form string="Carga de Archivo">
<image name="gtk-dialog-info" colspan="2"/>
<label string="El archivo se ha cargado en el sistema" colspan="4"/>
<separator string="De existir errores el detalle se encuentra a continuacion " colspan="4"/>
<separator string="Cedulas que no existen"/>
<field name='no_cedulas' nolabel='1' colspan='4'/>
<separator string='Cedulas con valores erroneos'/>
<field name='wrong_values' nolabel='1' colspan='4'/>
</form>"""

fields_end={
    'no_cedulas' : {'type' : 'text', 'string' : 'Cédulas no cargadas', 'readonly' : True,},
    'wrong_values' : {'type' : 'text', 'string' : 'Cédulas con valores Erróneos', 'readonly' : True,},
}

generate_months=[('1','Enero'),('2','Febrero'),('3','Marzo'),('4','Abril'),('5','Mayo'),('6','Junio'),
                 ('7','Julio'),('8','Agosto'),('9','Septiembre'),('10','Octubre'),('11','Noviembre'),('12','Diciembre')]

fields_form={
        'date' : {'string' : 'Fecha', 'type' : 'date', 'required' : 'True', 'default': lambda *a: time.strftime('%Y-%m-%d'), 'readonly' : True,},
        'period_id' : {'string' : 'Periodo/Mes' , 'type' : 'many2one', 'relation' : 'hr.contract.period', 'required' : True},
        'data':{'string':'Archivo', 'type':'binary', 'required':True,},
        }

class wizard_import_food(wizard.interface):
    
    def _process_message(self, cr, uid, data, context):
        return {
            'no_cedulas' : '\n'.join(noced),
            'wrong_values' : '\n'.join(wrong_values),
            }

    def _load_csv(self, cr, uid, data, context):
        result = {}
        form = data['form']
        period = form['period_id']
        file = form['data']
        buf=base64.decodestring(data['form']['data']).split('\n')
        buf = buf[:len(buf)-1]
        noced = []
        wrong_values = []
        for item in buf:
            flt=0
            item1 = item.split(',')
            try:
                flt = float(item1[1])
            except:
                wrong_values.append(item1[0])
            em_id = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [('cedula','=',item1[0])])
            if em_id:
                if flt>0:
                    vals={'employee_id': em_id[0],
                          'name':"Pago Comida",
                          'value': flt,
                          'date': datetime.today().strftime("%Y/%m/%d : %H:%M"),
                          'period_id' : period,
                          'state' : 'draft' }
                    egresos = pooler.get_pool(cr.dbname).get('hr.expense')
                    egresos.create(cr, uid, vals)
            else:
                noced.append(item1[0])
        return result
    
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
            'actions':[_load_csv,_process_message],
            'result':{'type':'form', 'arch':end_form, 'fields':fields_end, 'state':[('finish','Cerrar')]}
        },
        'finish':{
            'actions':[],
            'result':{'type':'action', 'action':_process_message, 'state' : 'end'}
            },
        }
    
wizard_import_food('wizard.import.food')
