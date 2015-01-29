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

from datetime import datetime, date
from osv import osv
from osv import fields

class hr_family_item(osv.osv):

    _name="hr.family.item"
    _description="Items employee family"

    def onchange_birth(self, cr, uid, ids, birth):
        v={}
        result={}
        if birth:
            fecha_n = datetime.strptime(birth, "%Y-%m-%d")
            if fecha_n <= datetime.today():
                today = date.today().strftime("%Y-%m-%d")
                now = today.split('-')
                birth = birth.split('-')
                datenow = date( int(now[0]), int(now[1]), int(now[2]) )
                datebirth = date( int(birth[0]), int(birth[1]), int(birth[2]) )
                delta = datenow - datebirth
                age = delta.days/365
                v['age']=int(age)
                return {'value' : v}
            else:
                result['value']={'birth':""}
                result['warning']={'title' : 'Error de Usuario', 'message':'La fecha de nacimiento no puede ser mayor a la actual'}
                return result
    
    _columns={
          'name' : fields.char('Nombre Completo', size=50, required=True),
          'age' : fields.integer('Edad', required=True),
          'birth' : fields.date('Fecha de Nacimiento', required=True),
          'parentezco' : fields.selection((('hb_wife','Conyugue'), ('son', 'Hijo(a)'),('ulibre','Unión Libre')), 'Parentezco'),
          'asegurado' : fields.boolean('Asegurado'),
          'employee_id' : fields.many2one('hr.employee', 'Empleado'),
          }
    
    _defaults={
           'age' : lambda *a: 0,
           }

hr_family_item()
