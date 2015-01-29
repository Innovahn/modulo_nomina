from osv import osv
from osv import fields
from datetime import datetime

class hr_holidays(osv.osv):
    _inherit="hr.holidays"
    
    def _not_negative(self, cr, uid, ids):
        pet = self.browse(cr, uid, ids)[0]
        if pet.number_of_days<0:
            return False
        else:
            return True

    def holidays_confirm(self, cr, uid, ids, *args):
        peticion = self.read(cr, uid, ids)[0]
        peticiones = self.browse(cr, uid, ids)
        date_from = peticion['date_from']
        em_id = peticion['employee_id'][0]
        ids2 = self.pool.get('hr.holidays.per.user').search(cr, uid, [('employee_id','=',em_id)])
        if ids2:
            if self.pool.get('hr.holidays.per.user').browse(cr, uid, ids2)[0].max_leaves>0:
                user = False
                for id in peticiones:
                    if id.employee_id.user_id:
                        user = id.employee_id.user_id.id
                self.write(cr, uid, ids, {
		    'state':'confirm',
		    'user_id': user,
		})
                self._create_log(cr, uid, ids)
                return True
        else:
            raise osv.except_osv('Error', "No dispone de vacaciones!\n Por no cumplir con el tiempo de trabajo necesario.")

    def holidays_refuse(self, cr, uid, ids, *args):
        ids2 = self.pool.get('hr.employee').search(cr, uid, [('user_id','=', uid)])
        if ids2:
            self.write(cr, uid, ids, {
                'state':'refuse',
                'manager_id':ids2[0]
            })
        else:
            self.write(cr, uid, ids, {
                'state':'refuse',
            })            
        self._create_log(cr, uid, ids)
        return True

    _constraints=[
        (_not_negative, "Su peticion de dias es Erronea", ['number_of_days'])
        ]

hr_holidays()
