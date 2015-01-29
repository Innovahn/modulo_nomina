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
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class hr_fiscalyear(osv.osv):
    _name = "hr.fiscalyear"
    _description = "Fiscal Year"
    _columns = {
        'name': fields.char('Año Fiscal', size=64, required=True),
        'code': fields.char('Codigo', size=6, required=True),
        'company_id': fields.many2one('res.company', 'Empresa'),
        'date_start': fields.date('Fecha Inicial', required=True),
        'date_stop': fields.date('Fecha Final', required=True),
        'period_ids': fields.one2many('hr.contract.period', 'fiscalyear_id', 'Periodos'),
        'state': fields.selection([('draft','Borrador'), ('done','Terminado')], 'Estado', readonly=True),
    }

    _defaults = {
        'state': lambda *a: 'draft',
    }
    _order = "date_start"

    def _check_duration(self,cr,uid,ids):
        obj_fy=self.browse(cr,uid,ids[0])
        if obj_fy.date_stop < obj_fy.date_start:
            return False
        return True

    _constraints = [
        (_check_duration, 'Error ! The duration of the Fiscal Year is invalid. ', ['date_stop'])
    ]

    def create_period3(self,cr, uid, ids, context={}):
        return self.create_period(cr, uid, ids, context, 3)

    def create_period(self,cr, uid, ids, context={}, interval=1):
        for fy in self.browse(cr, uid, ids, context):
            ds = mx.DateTime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d')<fy.date_stop:
                de = ds + RelativeDateTime(months=interval, days=-1)

                if de.strftime('%Y-%m-%d')>fy.date_stop:
                    de=mx.DateTime.strptime(fy.date_stop, '%Y-%m-%d')

                self.pool.get('hr.contract.period').create(cr, uid, {
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + RelativeDateTime(months=interval)
        return True

    def find(self, cr, uid, dt=None, exception=True, context={}):
        if not dt:
            dt = time.strftime('%Y-%m-%d')
        ids = self.search(cr, uid, [('date_start', '<=', dt), ('date_stop', '>=', dt)])
        if not ids:
            if exception:
                raise osv.except_osv(_('Error !'), _('No hay un año fiscal para este periodo!\nPor favor crear uno.'))
            else:
                return False
        return ids[0]
hr_fiscalyear()