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

class hr_provision_account(osv.osv):
    _name = "hr.provision.account"
    _description = "Payroll Info"
    _rec_name = "description"
    
    _columns = {'description': fields.char('Descripcion', size=30),
                'account': fields.char('Cod. Cuenta Contable', size=20),
                'account_credit' : fields.char('Cod. Cta Haber', size = 20),
                'is_income' : fields.boolean('Es Ingreso?'),
                'is_expense' : fields.boolean('Es Egreso?'),
                'is_provision' : fields.boolean('Es Provision'),
                'type' : fields.selection((('admin','Gasto Administrativo'), ('oper','Gasto Operativo'), ('prod','Emp. Produccion')), "Tipo de Gasto Contable"),
                }
    _sql_constraints = [
        ('unique_desc_provision_account', 'unique(description, type)', 'Solo puede ingresar una sola descripcion')
        ]
    
hr_provision_account()
