
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
from string import index

class hr_payroll(osv.osv):
    _name = 'hr.payroll'
    _description = "Payroll Info"

    def load_info(self, cr, uid, ids, args):
        """Laod info about Payroll, incomes, expenses, extra_hours """
        id_rol = int(",".join(map(str, ids)))
        payroll = self.browse(cr, uid, ids)[0]
        iess = payroll.contract_id.iess
        divi = 12
        #CHECK ME  fixme, necesary now
        if strftime('%Y') == '2009':
            divi = 9
        imp_r = payroll.contract_id.impuesto_renta / divi
        ayudat = payroll.employee_id.help_trans
        res=self.read(cr, uid, ids)[0]
        #egresos
        egresos = self.pool.get('hr.expense')
        ingresos = self.pool.get('hr.income')
        res_ex = egresos.search(cr, uid, [('payroll_id','=',id_rol)])
        res_in = ingresos.search(cr, uid, [('payroll_id','=',id_rol)])
        if not res_in and not res_ex:
            ids2 = self.pool.get('hr.expense').search(cr, uid, [('employee_id','=',res['employee_id'][0]), ('period_id','=',res['period_id'][0])])
            if ids2:
                egresos.write(cr, uid, ids2, {'payroll_id':id_rol})
            egresos.create(cr, uid, {'payroll_id':res['id'], 'employee_id':res['employee_id'][0], 'value':imp_r, 'name': 'Retencion Impuesto',
                                     'period_id' : res['period_id'][0]})
            egresos.create(cr, uid, {'payroll_id':res['id'], 'employee_id':res['employee_id'][0], 'value':ayudat, 'name':'Ayuda Transporte', 
                                     'period_id' : res['period_id'][0]})
            #ingresos
            valor100 = payroll.contract_id.wage
            ingresos.create(cr, uid, {'name':'Tiempo Ordinario','employee_id': res['employee_id'][0], 
                                      'value':valor100, 'payroll_id' : res['id'], 'period_id' : res['period_id'][0]})
            ingresos.create(cr, uid, {'name':'Ayuda Alimenticia','employee_id' : res['employee_id'][0], 'value' : payroll.contract_id.help_food, 
                                     'payroll_id' : res['id'], 'period_id' : res['period_id'][0]})
            ingresos.create(cr, uid, {'name' : 'Ayuda Transporte', 'employee_id' : res['employee_id'][0], 'value' : payroll.employee_id.help_trans,
                                      'payroll_id' : res['id'], 'period_id' : res['period_id'][0]})
            ingresos = self.pool.get('hr.income')
            ids4 = self.pool.get('hr.income').search(cr, uid, [('employee_id','=',res['employee_id'][0]),('name','like','Hora Extra')])
            if ids4:
                horas = self.pool.get('hr.income').browse(cr, uid, ids4)
                for item in horas:
                    self.pool.get('hr.income').write(cr, uid, {'payroll_id' : res['id']})
        else:
            raise osv.except_osv("Informacion",'Ya se ha cargado la informacion de este rol !')
    
    def liquidar_vacaciones(self, cr, uid, ids, args):
        sql="SELECT max(base_vacaciones) FROM hr_payroll"
        payroll = self.read(cr, uid, ids)[0]
        cr.execute(sql)
        res = cr.fetchall()
        if res:
            var = res[0][0]
            ids2 = self.pool.get('hr.holidays.per.user').search(cr, uid, [('employee_id','=',payroll['employee_id'][0])])
            if ids2:
                hpu = self.pool.get('hr.holidays.per.user').read(cr, uid, ids2)[0]
                dias = hpu['max_leaves'] - hpu['leaves_taken']
                liq = var / 30 * dias
                self.write(cr, uid, ids, {'liq_vacaciones' : liq})
            

    def _compute_total_horas(self, cr, uid, ids, field_name, arg, context):
        val = 0
        payroll = self.browse(cr, uid, ids)[0]
        c_hora = payroll.contract_id.costo_hora
        res = self.read(cr, uid, ids)[0]
        sql = "SELECT hora_125, hora_150, hora_200, id FROM hr_resumen_line WHERE period_id=%i AND employee_id=%i" % (res['period_id'][0], res['employee_id'][0])
        cr.execute(sql)
        res1 = cr.fetchall()
        if res1:
            res1 = res1[0]
            rs = []
            for i in res1:
                if i:
                    rs.append(i)
                else:
                    rs.append(0)
            rs = tuple(rs)
            if field_name == 'total_horas125':
                val = c_hora * 1.25 * rs[0]
            if field_name == 'total_horas150':
                val = c_hora * 1.50 * rs[1]
            if field_name == 'total_horas200':
                val = c_hora * 2 * rs[2]
            self.pool.get('hr.resumen.line').write(cr, uid, rs[3], {'payroll_id' : payroll.id})
        return {ids[0] : val }

    def _compute_total(self, cr, uid, ids, field_name, arg, context):
        id_rol = int(",".join(map(str, ids)))
        payroll = self.browse(cr, uid, ids)[0]
        res = self.read(cr, uid, ids)[0]
        t_in = payroll.total_ingresos
        t_ex = payroll.total_egresos
        vacaciones = payroll['liq_vacaciones']
        return {ids[0] : t_in - t_ex + vacaciones}

    def compute_values(self, cr, uid, ids, args):
        id_rol=int(",".join(map(str,ids)))
        payroll = self.read(cr, uid, ids)[0]
        in_ids = payroll['incomes_ids']
        ex_ids = payroll['expenses_ids']
        total_horas = payroll['total_horas125'] + payroll['total_horas150'] + payroll['total_horas200']
        incomes = self.pool.get('hr.income').read(cr, uid, in_ids)
        expenses = self.pool.get('hr.expense').read(cr, uid, ex_ids)
        temp = 0
        proll = self.browse(cr, uid, ids)[0]
        h25 = payroll['total_horas125'] / (proll.contract_id.costo_hora * 1.25)
        h50 = payroll['total_horas150'] / (proll.contract_id.costo_hora * 1.50)
        h100 = payroll['total_horas200'] / (proll.contract_id.costo_hora * 2)
        ingresos = self.pool.get('hr.income')
        ids2 = ingresos.search(cr, uid, [('name','like','H Ext%'), ('payroll_id', '=', payroll['id'])])
        if ids2 == []:
            ingresos.create(cr, uid, {'name' : 'H Ext 25%'+'\t'+'('+str('%.2f'%h25)+')', 'employee_id' : payroll['employee_id'][0], 'value' : payroll['total_horas125'], 
                                      'payroll_id':payroll['id'], 'period_id' : payroll['period_id'][0]})

            ingresos.create(cr, uid, {'name' : 'H Ext 50%'+'\t'+'('+str('%.2f'%h50)+')', 'employee_id' : payroll['employee_id'][0], 'value' : payroll['total_horas150'], 
                                      'payroll_id':payroll['id'], 'period_id' : payroll['period_id'][0]})

            ingresos.create(cr, uid, {'name' : 'H Ext 100%'+'\t'+'('+str('%.2f'%h100)+')', 'employee_id' : payroll['employee_id'][0], 'value' : payroll['total_horas200'], 
                                      'payroll_id':payroll['id'], 'period_id' : payroll['period_id'][0]})

        for income in incomes:
            if income['name'] == 'Tiempo Ordinario' or income['name'] == 'Ayuda Alimenticia':
                temp += income['value']
        temp += total_horas
        t_in = 0
        t_ex = 0
        for item_in in incomes:
            t_in += item_in['value']
        t_in += total_horas
        for item_ex in expenses:
            t_ex += item_ex['value']
        prov = self.pool.get('hr.provision')
        prov_ids = prov.search(cr, uid, [('payroll_id','=',id_rol)])
        if prov_ids:
            return
        proll = self.browse(cr, uid, ids)[0]
        provisiones = prov.compute(cr, uid, ids, payroll['contract_id'][0], t_in, proll.contract_id.help_food, payroll['num_dias'])
        provisiones['payroll_id'] = id_rol
        provisiones['employee_id'] = payroll['employee_id'][0]
        prov.create(cr, uid, provisiones)
        if t_in > 0:
            egresos = self.pool.get('hr.expense')
            iess = (t_in - proll.contract_id.help_food) * 0.0935
            egresos.create(cr, uid, {'payroll_id':payroll['id'], 'employee_id': payroll['employee_id'][0], 'value':iess, 'name' : 'Aporte al IESS', 
                                     'period_id' : payroll['period_id'][0]})
            t_ex += iess
        self.write(cr, uid, ids, {'total_egresos' : t_ex, 'total_ingresos' : t_in, 'base_vacaciones' : temp})

    def _convertir_mes(self, cr, uid, context={}):
        """ Change id for mounth """
        mes = int(strftime('%m'))
        meses = ['Enero','Febrero','Marzo','Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return meses[int(mes) - 1]
    
    def validar_registro(self, cr, uid, ids, args):
        """Change states in income, expense, and payroll, then asociate account properties """
        this = self.read(cr, uid, ids)[0]
        this2 = self.browse(cr, uid, ids)[0]
        self.pool.get('hr.expense').write(cr, uid, this['expenses_ids'], {'state' : 'procesado'})
        self.pool.get('hr.income').write(cr, uid, this['incomes_ids'], {'state' : 'procesado'})
        expenses = self.pool.get('hr.income').browse(cr, uid, this['incomes_ids'])
        for item in expenses:
            name_account = self.get_account(cr, uid, item.name, 'is_income', this2.employee_id.tipo)
            self.pool.get('hr.income').write(cr, uid, [item.id], {'account' : name_account})
        incomes = self.pool.get('hr.expense').browse(cr, uid, this['expenses_ids'])
        for item_ex in incomes:
            name_account = self.get_account(cr, uid, item_ex.name, 'is_expense', this2.employee_id.tipo)
            self.pool.get('hr.expense').write(cr, uid, [item_ex.id], {'account' : name_account})
        self.write(cr, uid, ids, {'state' : 'validate'})

    def get_account(self, cr, uid, name, what_is, type):
        """ Return account profil about incomes/ expenses """
        ids2 = self.pool.get('hr.provision.account').search(cr, uid, [(what_is,'=',True), ('type','=', type)])
        in_desc = self.pool.get('hr.provision.account').read(cr, uid, ids2, ['description', 'account'])
        for it in in_desc:
            try:
                if index(name, it['description']) >= 0:
                    return it['account']
            except:
                print "no coincidio solo por depreciacion"
    
    _columns = {
          'num_dias' : fields.integer('Dias. Trabaj.'),
          'liq_vacaciones' : fields.float('Liq. Vacaciones', digits = (8,2)),
          'base_vacaciones' : fields.float('Base Vacaciones', digits = (8,2)),
          'name' : fields.char('Descripcion', size=50),
          'employee_id' : fields.many2one('hr.employee', 'Empleado'),
          'contract_id' : fields.many2one('hr.contract', 'Contrato'),
          'period_id' : fields.many2one('hr.contract.period', 'Periodo de Trabajo'),
          'month' : fields.char('Mes', size=30),
          'user_id' : fields.many2one('res.users', 'Creado por'),
          'date' : fields.date('Fecha de Creacion'),
          'provisiones_id' : fields.one2many('hr.provision','payroll_id','Provisiones'),
          'expenses_ids' : fields.one2many('hr.expense', 'payroll_id', 'Rubros Egresos'),
          'incomes_ids' : fields.one2many('hr.income', 'payroll_id', 'Rubros Ingresos'),
          'horas_resumen' : fields.one2many('hr.resumen.line', 'payroll_id', 'Total Horas'),
          'total_ingresos' : fields.float('Total Ingresos', digits = (8,2)),
          'total_egresos' : fields.float('Total Egresos', digits = (8,2)),
          'total' : fields.function(_compute_total, method=True, string="Total a Percibir", store=True, type='float'),
          'total_horas125' : fields.function(_compute_total_horas, method=True, string="Horas 02", store=True, type='float'),
          'total_horas150' : fields.function(_compute_total_horas, method=True, string="Horas 04", store=True, type='float'),
          'total_horas200' : fields.function(_compute_total_horas, method=True, string="Horas 05", store=True, type='float'),
          'state' : fields.selection([('draft','Borrador'),('validate','Validado'),],'Estado', select=True, readonly=True),
          }

    _defaults = {
        'num_dias' : lambda *a: 30,
        'state' : lambda *a: 'draft',
        'month' : _convertir_mes,
        'date' : lambda *a: strftime('%Y-%m-%d'),
        'user_id' : lambda self, cr, uid, context : self.pool.get('res.users').browse(cr, uid, uid).id,
           }
    _sql_constraints = [
        ('unique_emp_per', 'unique(employee_id,period_id)', 'Solo Puede realizar un Pago por mes a cada Empleado')
        ]
hr_payroll()

class hr_expense(osv.osv):
    _name = "hr.expense"
    _description = "Expenses for Employee"
    
    meses=[('enero','Enero'),('febrero','Febrero'),('marzo','Marzo'),('abril','Abril'),
           ('mayo','Mayo'),('junio','Junio'),('julio','Julio'),('agosto','Agosto'),
           ('septiembre','Septiembre'),('octubre','Octubre'),('noviembre','Noviembre'),('diciembre','Diciembre')]

    _columns={
        'payroll_id' : fields.many2one('hr.payroll', 'Rol de Pagos'),
        'name' : fields.char('Descripcion', size = 40),
        'value' : fields.float('Valor', digits = (10,2)),
        'employee_id' : fields.many2one('hr.employee', "Empleado"),
        'state' : fields.selection([('draft', 'No Procesado'), ('procesado', 'Procesado')], 'Status', readonly = True),
        'period_id' : fields.many2one('hr.contract.period', 'Periodo', help = "Mes al que pertenece el Egreso"),
        'date' : fields.datetime('Fecha de Registro'),
        'account' : fields.char('Cta. Contable', size = 40),
        }

    _sql_constraints=[
        ('name','unique(name)','El pago por mes es único.'),
        ]
    
    _defaults={
        'state' : lambda *a: 'draft',
           }
hr_expense()
    
class hr_income(osv.osv):
    _name = "hr.income"
    _description = "Incomes for Employee"
    
    _columns={
        'payroll_id' : fields.many2one('hr.payroll', 'Rol de Pagos'),
        'name' : fields.char('Description', size = 50),
        'value' : fields.float('Valor', digits = (10,2)),
        'employee_id' : fields.many2one('hr.employee', 'Empleado'),
        'state' : fields.selection([('draft', 'No Procesado'), ('procesado', 'Procesado')], 'Status', readonly = True),
        'period_id' : fields.many2one('hr.contract.period', 'Periodo', help = "Mes al que pertenece el Ingreso"),
        'date' : fields.datetime('Fecha de Registro'),
        'account' : fields.char('Cta. Contable', size = 40),
    }
    _defaults={
        'state' : lambda *a: 'draft',
           }
hr_income()    
    
class hr_provision(osv.osv):
    _name = 'hr.provision'
    _description = "Provisiones por Ley"
    
    def compute(self, cr, uid, ids, contrato_id, t_in, h_food, num_dt):
        s = t_in-h_food
        cr.execute("SELECT COALESCE(" + str(t_in) + " / 12)::decimal(16,2) AS decimo3ro, \
        COALESCE((sueldo_basico/360)*"+str(num_dt)+")::decimal(16,2) AS decimo4to,\
        COALESCE (" +str(t_in)+  "/24)::decimal(16,2) as vacaciones,\
        COALESCE (" +str(t_in)+  "/12)::decimal(16,2) as fondo_reserva,\
        COALESCE (" +str(t_in-h_food)+  "*0.1115)::decimal(16,2) as aporte_patronal, \
        COALESCE (" +str(t_in-h_food)+  "*0.005)::decimal(16,2) as secap,\
        COALESCE (" +str(t_in-h_food)+  "*0.005)::decimal(16,2) as iece \
        from hr_contract c where id =" + str(contrato_id))
        res = cr.fetchall()[0]
        resp = {}
        resp['contrato_id'] = contrato_id
        resp['decimo3ro'] = res[0]
        resp['decimo4to'] = res[1]
        resp['vacaciones'] = res[2]
        resp['fondo_reserva'] = res[3]
        resp['aporte_patronal'] = res[4]
        resp['secap'] = res[5]
        resp['iece'] = res[6]
        total = 0.0
        for item in res:
            total += item
        resp['total'] = total
        return resp

    
    _columns={
        'payroll_id' : fields.many2one('hr.payroll','Rol de Pagos', ondelete = 'cascade'),
        'contrato_id' : fields.many2one('hr.contract', 'Contrato'),
        'employee_id' : fields.many2one('hr.employee', 'Empleado'),
        'decimo3ro' : fields.float('Decimo Tercero', digits=(8,2)),
        'decimo4to' : fields.float('Decimo Cuarto', digits=(8,2)),
        'vacaciones' : fields.float('Vacaciones', digits=(8,2)),
        'fondo_reserva' : fields.float('Fondo de Reserva', digits=(8,2)),
        'aporte_patronal' : fields.float('Aporte Patronal', digits=(8,2)),
        'secap' : fields.float('Secap', digits=(8,2)),
        'iece' : fields.float('IECE', digits=(8,2)),
        'total' : fields.float('Total', digits=(8,2)),          
          }
    
    _defaults={
               'decimo3ro' : lambda *a : 0.0,
               'decimo4to' : lambda *a: 0.0,
               'vacaciones' : lambda *a: 0.0,
               'fondo_reserva' : lambda *a: 0.0,
               'secap' : lambda *a : 0.0,
               'iece' : lambda *a: 0.0,
               'total' : lambda *a : 0.0,
    }
hr_provision()


class hr_payroll_hours(osv.osv):
    _name = "hr.payroll.hours"
    _description = "Control de Horas Trabajadas"
    
    def _get_categories(self, cr, uid, context={}):
        obj = self.pool.get('hr.employee.category')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name', 'id'], context)
        res = [(r['id'], r['name']) for r in res]
        return res
    
    _columns={
          'category_id' : fields.many2one('hr.employee.category', 'Area de Trabajo', selection = _get_categories, ondelete = 'cascade'),
          'date_start' : fields.date('Fecha Inicio', required = True),
          'date_end' : fields.date('Fecha Fin', required = True),
          'employee_ids' : fields.one2many('hr.employee','payroll_hours_id','Empleados'),
          }
hr_payroll_hours()

