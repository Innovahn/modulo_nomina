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
import datetime
import time

class hr_hora_extra_tipo(osv.osv):
    _name="hr.hora.extra.tipo"
    
    _columns={
          'name' : fields.char('Descripcion', size=30, required=True),
          'percent' : fields.integer('Porcentaje', required=True),
          'numero' : fields.integer('Cantidad'),
          }
hr_hora_extra_tipo()

class hr_registro_hora(osv.osv):
    _name = "hr.registro.hora"
    _description = "Registro de Horas Extra"
    
    def validar_registro(self, cr, uid, ids, args):
        self.write(cr, uid, ids, {'state' : 'validate'})
        return True
    
    def _compute_date(self, cr, uid, ids, field_name, arg, context):
        obj=self.read(cr, uid, ids,['fecha_inicio'])[0]
        res=datetime.datetime.strptime(obj['fecha_inicio'], '%Y-%m-%d') + datetime.timedelta(days=6)
        return{ids[0] : res.strftime('%Y-%m-%d')}

    def _validar_fechas(self, cr, uid, ids):
        result = False
        reg = self.read(cr, uid, ids)[0]
        sql = "SELECT max(fecha_fin) FROM hr_registro_hora WHERE id <> %i and departament_id = %i" % (ids[0],reg['departament_id'][0])
        print sql
        cr.execute(sql)
        res = cr.fetchall()
        if res[0][0]==None:
            result = True
        else:
            days = datetime.datetime.strptime(reg['fecha_inicio'], '%Y-%m-%d') - datetime.datetime.strptime(res[0][0], '%Y-%m-%d')
            dias = abs(days.days) + 1
            if abs(days.days) == 1:
                result = True
            elif  dias % 7 == 0:
                result = True
        return result

    def cargar_empleados(self, cr, uid, ids, context=None):
        reg = self.read(cr, uid, ids)[0]
        val={}
        ids2 =self.pool.get('hr.registro.hora.line').search(cr, uid, [('registro_id','=',ids[0]), ('date_start','=',reg['fecha_inicio'])])
        if ids2:
            raise osv.except_osv(_('Aviso'), _('Ya se han creado registro con esta fecha inicial !'))
        em_ids =self.pool.get('hr.employee').search(cr, uid,[('category_id','=',reg['departament_id'][0])])
#        line = self.pool.get('hr.registro.hora.line').search(cr, uid, [('date_start','=',reg['fecha_inicio']),('date_end','=',reg['fecha_fin'])])
#        if not line:
        line = self.pool.get('hr.registro.hora.line')
        for item in em_ids:
            val['registro_id']=int(",".join(map(str,ids)))            
            val['employee_id']=item
            val['hora_100']= 40
            val['date_start'] = reg['fecha_inicio']
            val['date_end'] = reg['fecha_fin']
            line.create(cr, uid, val)

    _columns={
        'name' : fields.char('Descripcion', size=35),
        'state': fields.selection([('draft','Borrador'),('validate','Done'),],'Estado', select=True, readonly=True),
        'departament_id' : fields.many2one('hr.employee.category', 'Departamento', ondelete = 'cascade'),
        'fecha_inicio' : fields.date('Fecha Inicio', required=True),
        'fecha_fin' : fields.function(_compute_date, method=True, string="Fecha Final", store=True, type='date'),
        'registro_line' : fields.one2many('hr.registro.hora.line', 'registro_id', 'Detalle'),
        }
    
    _defaults={
       'state' : lambda *a: 'draft',
       'name' : lambda self, cr, uid, context : self.pool.get('res.users').read(cr, uid, uid)['name'] + " - " +time.strftime('%m/%Y'),
       }

    _constraints = [
        (_validar_fechas, 'No puede registrar nuevamente en esta semana', ['fecha_fin'])
        ]

hr_registro_hora()

class hr_registro_hora_line(osv.osv):
    _name="hr.registro.hora.line"
    _description="Detalle de horas por empleado"

    _columns={
        'registro_id' : fields.many2one('hr.registro.hora','Detalle por Empleado', ondelete = 'cascade'),
        'employee_id' : fields.many2one('hr.employee', 'Empleado', ondelete = 'cascade'),
        'hora_100' : fields.integer('01', required=True),
        'hora_125' : fields.integer('02'),
        'hora_150' : fields.integer('04'),
        'hora_200' : fields.integer('05'),
        'falta_inj' : fields.integer('FI'),
        'perm_medico' : fields.integer('PM'),
        'justificativo' : fields.selection([('a','A'),('b','B')], 'Justificativo'),
        'cal_dom' : fields.integer('CD'),
        'justifcd' : fields.selection([('a','A'),('b','B')], 'Justificativo'),
        'vacaciones' : fields.integer('V'),
        'feriado' : fields.integer('FERIADO'),
        'justif_feriado' : fields.selection([('b','B')], 'Justificativo'),
        'otros' : fields.integer('OTROS'),
        'date_start' : fields.date('Fecha Inicio'),
        'date_end' : fields.date('Fecha Fin'),
        }

    _defaults = {
        'hora_100' : lambda *a : 40,
        }

hr_registro_hora_line()

class hr_resumen_hora_mensual(osv.osv):
    _name="hr.resumen.hora.mensual"
    _description="Resumen de Horas al Mes para Pago"
    
    def validar_resumen(self, cr, uid, ids, args):
        obj = self.browse(cr, uid, ids)[0]
        res = self.read(cr, uid, ids)[0]
        for item in obj.resumen_line:
            fi = item.falta_inj
            h125 = item.hora_125
            h150 = item.hora_150
            h200 = item.hora_200
            sql = "SELECT max(date_start), costo_hora, wage FROM hr_contract WHERE employee_id = %i GROUP BY costo_hora, wage" % item.employee_id.id
            cr.execute(sql)
            res = cr.fetchall()[0]
            c_hora = res[1]
            wage = res[2]
            val = {'name': "Desc. Faltas. Injustif.", 'employee_id' : item.employee_id.id, 'period_id':obj.periodo_id.id,
                   'date': time.strftime('%Y-%m-%d'), 'value' : ( fi * wage)/ 160, 'state' : 'draft'}
            self.pool.get('hr.expense').create(cr, uid, val)
            if c_hora == None:
                c_hora = 0
            val1 = {'name' : "Horas Extra 02", 'employee_id' : item.employee_id.id, 'period_id':obj.periodo_id.id,
                    'date': time.strftime('%Y-%m-%d'), 'value' : c_hora * h125 * 1.25, 'state' : 'draft'}
            val2 = {'name' : "Horas Extra 04", 'employee_id' : item.employee_id.id, 'period_id':obj.periodo_id.id,
                    'date': time.strftime('%Y-%m-%d'), 'value' : c_hora * h150 * 1.50, 'state' : 'draft'}
            val3 = {'name' : "Horas Extra 05", 'employee_id' : item.employee_id.id, 'period_id':obj.periodo_id.id,
                    'date': time.strftime('%Y-%m-%d'), 'value' : c_hora * h125 * 2, 'state' : 'draft'}
            self.pool.get('hr.income').create(cr, uid, val1)
            self.pool.get('hr.income').create(cr, uid, val2)
            self.pool.get('hr.income').create(cr, uid, val3)
        self.write(cr, uid, ids, {'state' : 'validate'})
        return True

    def cargar_empleados_resumen(self, cr, uid, ids, args):
        reg=self.read(cr, uid, ids)[0]
        val={}
        em_ids =self.pool.get('hr.employee').search(cr, uid,[('category_id','=',reg['departament_id'][0])])
        line=self.pool.get('hr.resumen.line')
        res = line.search(cr, uid, [('registro_id','=',reg['id'])])
        if not res:
            for item in em_ids:
                val['registro_id'] = int(",".join(map(str,ids)))            
                val['employee_id'] = item
                val['period_id'] = reg['periodo_id'][0]
                line.create(cr, uid, val)

    _columns={
        'state': fields.selection([('draft','Borrador'),('validate','Validado'),],'Estado', select=True, readonly=True),
        'name' : fields.char('Descripcion', size=35, states={'open':[('readonly',False)],'close':[('readonly',True)]}),
        'departament_id' : fields.many2one('hr.employee.category', 'Departamento', required=True, states={'draft':[('readonly',False)],'close':[('readonly',True)]}, ondelete = 'cascade'),
        'periodo_id' : fields.many2one('hr.contract.period', 'Mes', states={'draft':[('readonly',False)],'close':[('readonly',True)]}, ondelete = 'cascade'),
        'resumen_line' : fields.one2many('hr.resumen.line', 'registro_id', 'Detalle', states={'draft':[('readonly',False)],'close':[('readonly',True)]}, ondelete='cascade'),
        }
    
    _defaults={
       'state' : lambda *a: 'draft',
       'name' : lambda self, cr, uid, context : self.pool.get('res.users').read(cr, uid, uid)['name'] + " - " +time.strftime('%m/%Y'),
       }

    _sql_constraints=[
        ('dep_month', 'unique(departament_id,periodo_id)','Solo puede sacar un Resumen de Horas de Departamento por Mes')
        ]

hr_resumen_hora_mensual()

class hr_resumen_line(osv.osv):
    _name="hr.resumen.line"
    _description="Detalle del resumen mensual"

    def _sumar_horas(self, cr, uid, ids, field_name, arg, context):
        val = 0
        res=self.browse(cr, uid, ids)[0]
        date_start=res.registro_id.periodo_id.date_start
        date_stop=res.registro_id.periodo_id.date_stop
        sql="SELECT sum(%s) FROM hr_registro_hora_line INNER JOIN hr_registro_hora on (hr_registro_hora.id = hr_registro_hora_line.registro_id) where \
                 fecha_inicio >= '%s' AND fecha_inicio<='%s'AND employee_id = %s %s" % (field_name, date_start, date_stop,res.employee_id.id, "GROUP BY employee_id")
        cr.execute(sql)
        ress = cr.fetchall()
        if ress:
            res = ress[0]
            print "el valor", res
            if res[0]:
                val = int(",".join(map(str,res)))
            else:
                val = 0
            return {ids[0] : val}
        else:
            raise osv.except_osv(_('Error !'),_('No existe registro de horas semanales dentro de este periodo !'))

    def _calcular_total(self, cr, uid, ids, field_name, arg, context):
        obj=self.browse(cr, uid, ids)[0]
        val= obj.hora_100 + obj.falta_inj + obj.perm_medico + obj.cal_dom + obj.vacaciones + obj.feriado + obj.otros
        if obj.hora_100 <= 120:
            val = 120
        elif obj.hora_100 <= 160:
            val = 160
        return {ids[0] : val}

    _columns={
        'name' : fields.char('Descripcion', size=35),
        'registro_id' : fields.many2one('hr.resumen.hora.mensual','Detalle por Empleado', ondelete = 'cascade'),
        'period_id' : fields.many2one('hr.contract.period', 'Periodo'),
        'employee_id' : fields.many2one('hr.employee', 'Empleado', ondelete = 'cascade'),
        'payroll_id' : fields.many2one('hr.payroll', 'Rol de Pagos'),
        'hora_100' : fields.function(_sumar_horas, method=True, string="01", store=True, type='integer'),
        'hora_125' : fields.function(_sumar_horas, method=True, string="02", store=True, type='integer'),
        'hora_150' : fields.function(_sumar_horas, method=True, string="04", store=True, type='integer'),
        'hora_200' : fields.function(_sumar_horas, method=True, string="05", store=True, type='integer'),
        'falta_inj' : fields.function(_sumar_horas, method=True, string="FI", store=True, type='integer'),
        'perm_medico' : fields.function(_sumar_horas, method=True, string="PM", store=True, type='integer'),
        'cal_dom' : fields.function(_sumar_horas, method=True, string="CM", store=True, type='integer'),
        'vacaciones' : fields.function(_sumar_horas, method=True, string="VACACIONES", store=True, type='integer'),
        'feriado' : fields.function(_sumar_horas, method=True, string="FERIADO", store=True, type='integer'),
        'otros' : fields.function(_sumar_horas, method=True, string="OTROS", store=True, type='integer'),
        'total' : fields.function(_calcular_total, method=True, string="TOTAL", store=True, type='integer'),
        }
hr_resumen_line()
