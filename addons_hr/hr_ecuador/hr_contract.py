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
from time import strftime
import datetime
import copy


class hr_contract_type(osv.osv):
    _name = "hr.contract.type"
    _description = "Type of contracts"

    _columns = {
        'name' : fields.char("Nombre", size = 50),
        'description' : fields.char('Descripcion', size = 60),
        }
hr_contract_type()

class hr_contract_wage(osv.osv):
    _name = "hr.contract.wage"
    _description = "wage history"

    _columns = {
        'name' : fields.char("Fecha", size = 30),
        'wage' : fields.float("Anterior Salario", digits = (8,2)),
        'contract_id' : fields.many2one('hr.contract', 'Contrato'),
        }
hr_contract_wage()

class hr_base_retention(osv.osv):
    _name = "hr.base.retention"
    _description = "Tabla de Retencion"

    _columns={
        'year' : fields.char('Año', size=4),
        'name' : fields.char('Descripción', size=40),
        'retention_line' : fields.one2many('hr.base.retencion.line', 'retention_id','Detalle'),
        }

    _defaults={
        'year' : lambda *a: str(strftime('%Y')),
        'name' : lambda *a: 'Tabla de Retencion',
        }

    _sql_constraints=[
        ('unique_year','unique(year)','Solo puede configurar un año.')
        ]
hr_base_retention()

class hr_base_retencion_line(osv.osv):
    _name="hr.base.retencion.line"
    _description="Tabla Base de para Retenciones"

    _columns={
        'fraccion_basica' : fields.float('Fracción Básica', required=True),
        'exceso_hasta' : fields.float('Exceso Hasta', required=True),
        'frac_basica_tax' : fields.float('Imp. Fracción Básica', required=True),
        'percent' : fields.float('% Fracción Excedente', required=True),
        'retention_id' : fields.many2one('hr.base.retention','Detalle', ondelete='cascade'),
        }
hr_base_retencion_line()

class hr_contract(osv.osv):
    _inherit="hr.contract"

    def onchange_name(self, cr, uid, ids, name, date_start):
        v = {}
        res = ""
        if name == 'fijo':
            res = datetime.datetime.strptime(date_start, '%Y-%m-%d') + datetime.timedelta(days=365)
        elif name=='eventual':
            res = datetime.datetime.strptime(date_start, '%Y-%m-%d') + datetime.timedelta(days=365)
        elif name == 'prueba':
            res = datetime.datetime.strptime(date_start, '%Y-%m-%d') + datetime.timedelta(days=365)
        elif name == 'indefinido':
            res = datetime.datetime.strptime(date_start, '%Y-%m-%d') + datetime.timedelta(days=365)
        if res:
            v['date_end'] = res.strftime("%Y-%m-%d")
        return {'value' : v}
    
    def onchange_wage(self, cr, uid, ids, wage):
        v = {}
        iess = wage * 0.0935
        aal = wage * 0.20
        cost_hour = (wage+aal)/240
        v['iess'] = iess
        v['help_food'] = aal
        v['costo_hora'] = cost_hour
        return {'value' : v}

    def _compute_tax(self, cr, uid, ids, field_name, arg, context):
        obj = self.browse(cr, uid, ids)[0]
        res = self.pool.get('hr.contract.period').search(cr, uid, [('date_stop','<=','31-12-'+strftime('%Y'))])
	print "!"*90
        print res
	print obj.wage
	print obj.help_food

	ing_grav = (obj.wage + obj.help_food) * len(res)
	print "&"*90+"ing_grav"
        print ing_grav
	t_whelp = obj.wage * len(res)
        ap_personal = t_whelp * 0.0935
        t_wiess = ing_grav - ap_personal
	print "'"*60 + "t_wiess"
	print t_wiess
        gastos_personales = obj.proyeccion + obj.proy_vivienda + obj.proy_salud + obj.proy_alimentacion + obj.proy_vestimenta
        base = t_wiess - gastos_personales
        
	print "%"*60 + "base"
	print base
	sql = "SELECT l.percent, l.fraccion_basica, l.frac_basica_tax FROM hr_base_retention t, hr_base_retencion_line l WHERE \
                                     t.year='%s' AND l.fraccion_basica <=%f and %f <= l.exceso_hasta" % (strftime('%Y'),base,base)
        cr.execute(sql)
        res1 = cr.fetchall()
	print "#"*90	
	print type(res1)
	print len(res1)
        exed = base - res1[0][1]
        pago_exed = exed * res1[0][0]
        total = pago_exed + res1[0][2]
        return{ids[0] : total}
        
    def _compute_cost_hour(self,cr, uid, ids, field_name, arg, context):
        obj = self.browse(cr, uid, ids)[0]
        return {ids[0] : (obj.wage + obj.help_food)/240 }
    
    def _compute_fraccion(self, cr, uid, ids, field_name, arg, context):
        obj = self.browse(cr, uid, ids)[0]
        return {ids[0] : obj.impuesto_renta / 12}

    def _check_first(self, cr, uid, ids, field_name, arg, context):
        contract = self.read(cr, uid, ids[0])
        d_start = contract['date_start']
        em_id = contract['employee_id'][0]        
        res=self.search(cr, uid, [('employee_id','=',em_id), ('date_start','<=',d_start)])
        res1=copy.copy(res)
        val = False
        if ids[0] in res1:
            res1.remove(ids[0])
        if not res1:
            val = True
        return {ids[0]:True}

    def load_types(self, cr, uid, context={}):
        obj = self.pool.get('hr.contract.type')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name', 'id'], context)
        res = [(r['id'], r['name']) for r in res]
        print res
        return res

    _columns={
        'nombre' : fields.many2one('hr.contract.type','Tipo Contrato', selection=load_types),
        'costo_hora' : fields.function(_compute_cost_hour, method=True, string='Valor Hora 100%', store=True, type='float'),
        'help_food' : fields.float('Ayuda Alimenticia', digits = (8,2)),
        'impuesto_renta' : fields.function(_compute_tax, method=True, string='Imp. Renta', store=True),
        'first_contract' : fields.function(_check_first, method=True, string='fc', store=True, type='boolean'),
        'sub_antiguedad' : fields.float('Subsidio de Antiguedad', digits=(8,2)),
        'name' : fields.char('Descripcion de Contrato', size=50, required=True),
        'iess' : fields.float('IESS', digits=(8,2)),
        'sueldo_basico' : fields.float('Sueldo Basico', digits=(8,2)),
        'proyeccion' : fields.float('Gastos Pers. - Educacion', digits=(8,2), 
                                      help="Ingresar el valor que proyecta el empleado en medicina, educacion, etc"),
        'proy_vivienda' : fields.float('Gastos Pers. - Vivienda', digits = (8,2)),
        'proy_salud' : fields.float('Gastos Pers. - Salud', digits = (8,2)),
        'proy_alimentacion' : fields.float('Gastos Pers. - Alimentacion', digits = (8,2)),
        'proy_vestimenta' : fields.float('Gastos Pers. - Vestimenta', digits = (8,2)),
        'fraccion_mensual' : fields.function(_compute_fraccion, method=True, string='Fraccion Mensual', store=True, type='float'),
        'wage_line' : fields.one2many('hr.contract.wage', 'contract_id', 'Historial de Salarios'),
          }
    
    _defaults={
           'sueldo_basico' : lambda *a: 218.0,
           'iess' : lambda *a: 0.0,
           'name' : lambda *a: 'Contrato Prodegel S.A.',
           }

hr_contract()
