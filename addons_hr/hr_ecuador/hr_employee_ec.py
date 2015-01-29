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

from osv import osv
from osv import fields
from datetime import datetime


class hr_employee_ec(osv.osv):

    _inherit="hr.employee"

    def _default_company(self, cr, uid, context={}):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
    
    def _compute_seguro(self, cr, uid, ids, field_name, arg, context):
        emp = self.browse(cr, uid, ids)[0]
        res=emp.cargas_ids
        i=1
        for item in res:
            if item.asegurado:
                i+=1
        return {ids[0] : emp.seguro_priv * i} 

    def _compute_days(self, cr, uid, ids, field_name, arg, context):
        if not ids or len(ids)<>1: return {}
        dias_vacacion=0
        contract_ids = self.pool.get('hr.contract').search(cr, uid, [('first_contract','=', True),('employee_id','=', ids[0])])
        if contract_ids:
            cont = self.pool.get('hr.contract').read(cr, uid, contract_ids)[0]
            d_start = cont['date_start']
            dfrom = datetime.today()
            dstart = datetime.strptime(d_start, '%Y-%m-%d')
            years = (dfrom - dstart).days/365
            if years>=1:
                dias_vacacion = 15
                if years>=5:
                    dias_vacacion += years - 5
            if dias_vacacion>0:
                hpu = self.pool.get('hr.holidays.per.user')
                ids2 = hpu.search(cr, uid, [('employee_id','=',ids[0])])
                if not ids2:
                    status = self.pool.get('hr.holidays.status').search(cr, uid, [('name','like',"Vacaciones")])
                    if not status:
                        self.pool.get('hr.holidays.status').create(cr, uid, {'name':'Vacaciones', 'color_name':'red'})
                        status = self.pool.get('hr.holidays.status').search(cr, uid, [('name','like',"Vacaciones")])
                    hpu1={'employee_id':ids[0], 'holiday_status':status[0], 'max_leaves' : float(dias_vacacion)}
                    self.pool.get('hr.holidays.per.user').create(cr, uid, hpu1)
                else:
                    self.pool.get('hr.holidays.per.user').write(cr, uid, ids2[0], {'max_leaves':dias_vacacion})
        return {ids[0] : dias_vacacion}
    
    def onchange_cedula(self, cr, uid, ids, cedula):
        #ced = cedula
	
        result={}
        ced=cedula
	print "#"*90
	print cedula
	print ced	
	print type(cedula)
	print "#"*90	
	
	if(len(str(cedula))==13):
		comprobar=True 
	else:
		comprobar=False
	
	print "/"*90
	print str(cedula).isdigit()
	print comprobar
	print "/"*90	
	
        if(comprobar and str(cedula).isdigit() ):
            print "entro funcion"
	    string = ""
            resultado = 0
	    '''	
            for i in range (0, 10):
                string += ced[i] + " "
		print ced[i] + "ced[i]"
            lista = string.split()
	    print lista 
	    print 90* "---"
            coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
            for j in range(0, len(coeficientes)):
                valor = int(lista[j]) * coeficientes[j]
                if valor >= 10:
                    str1 = str(valor)
                    suma = int(str1[0]) + int(str1[1])
                    resultado += suma
                else:
                    resultado += int(lista[j]) * coeficientes[j]
            residuo = resultado%10
            verificador = 0
            if residuo > 0:
                verificador = 10 - residuo
            if verificador == int(lista[9]):
                return {'value':{'cedula':cedula}}
            else:
               # result['value']={'cedula':""}
                result['warning']={'title':"Error de Usuario","message":"La cedula es incorrecta"}
                return result   
	    '''	             
	    return{'value':{'cedula':cedula}}
	    return result		
        else:
           # result['value']={'cedula':""}
            result['warning']={'title':"Error de Usuario","message":"La cedula es incorrectas"}
            return result
	
    def _compute_14(self, cr, uid, ids, field_name, arg, context):
        sql = "SELECT sueldo_basico FROM hr_contract WHERE employee_id = %s" % ids[0]
        cr.execute(sql)
        res = cr.fetchall()
        val = 0.0
        if res:
            val = res[0][0]
        return {ids[0] : val}
    
    _columns={
        'dir_trabajo' : fields.char('Direccion de Trabajo', size = 13),
        'bank_account_id' : fields.many2one('hr.employee.bank', 'Cta Bancaria'),
        'dias_vacaciones' : fields.function(_compute_days, method=True, string="Dias Vacaciones", store=True),
        'dias_tomados' : fields.integer('Dias Tomados', readonly=True),
        'cargas_ids' : fields.one2many("hr.family.item", 'employee_id', "Familia"),
        'tipo' : fields.selection((('admin','Administrativo'),('oper','Operativo'), ('prod','Emp. Produccion')), "Tipo Empleado"),
        'check_25' : fields.boolean('Administrativo 25%', help="Activar este campo cuando sea un caso especial de Administrativos con 25%"),
        'seguro_priv' : fields.float("Costo Seguro Privado Individual", digits=(8,2)),
        'cedula' : fields.char('Cedula', size=13),
        'address' : fields.char('Direccion Domicilio', size=150),
        'help_trans' : fields.float('Ayuda Transporte', digits=(8,2)),
        'total_seguro' : fields.function(_compute_seguro, method=True, string="Total Seguro", store=True, type="float"),
        'tipoid' : fields.selection((('c','Cedula'),('p','Pasaporte'),('r','RUC')), "Tipo ID"),
        'utilidades_ids' : fields.one2many('hr.employee.util', 'employee_id', 'Detalle Utilidades'),
        'total_13' : fields.float("Total Decimo 3", digits = (8,2)),
        'total_14' : fields.function(_compute_14, method = True, string = "Total Decimo 4", store = True, type = "float"),
	'payroll_hours_id':fields.many2one('hr.payroll.hours'),	
        }

    _defaults={
        'children' : lambda *a: 0,
        'dias_vacaciones' : lambda *a : 0,
        'company_id' : _default_company,
        'dir_trabajo' : lambda *a : "Planta Ambato",
        }

    _sql_constraints=[
          ('cedula_uniq', 'unique(cedula)', 'Un Empleado esta ya registrado con esa cedula.'),
      ]

hr_employee_ec()

class hr_employee_util(osv.osv):
    _name = "hr.employee.util"
    _description = "Utilidad de empleado"

    _columns = {
        'name' : fields.char('Descripcion', size = 30),
        'employee_id' : fields.many2one('hr.employee', 'Empleado'),
        'val10' : fields.float('Util. 10%', digits = (8,2)),
        'val5' : fields.float('Util. 5%', digits = (8,2)),
        'total' : fields.float('Total', digits = (8,2)),
        }
hr_employee_util()


class hr_employee_category(osv.osv):
    _inherit = "hr.employee.category"

    _columns = {
        'code' : fields.char('Cod. Centro de Utilidad', size = 30, required = True),
        }
hr_employee_category()
