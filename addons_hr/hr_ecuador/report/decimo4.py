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

import time
import pooler
from report import report_sxw


class decimo4(report_sxw.rml_parse):

    def _get_employees(self, form, ids=None, done=None, level=1):
        if ids is None:
            ids = []
        res = pooler.get_pool(self.cr.dbname).get('hr.employee').search(self.cr, self.uid, [])
        res1 = pooler.get_pool(self.cr.dbname).get('hr.employee').browse(self.cr, self.uid, res)
        return res1

    def __init__(self, cr, uid, name, context):
        super(decimo4, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'time' : time,
                'get_employees' : self._get_employees,
                })
        self.context = context

report_sxw.report_sxw('report.decimo4', 'hr.employee', 'addons/hr_payroll/report/decimo4_report.rml', parser=decimo4, header=False)
