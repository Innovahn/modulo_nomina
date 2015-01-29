# -*- encoding: utf-8 -*-
##############################################################################
#
#    HHRR Module
#    Copyright (C) 2009 GnuThink Software All Rights Reserved
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

{
    "name" : "Human Resources Management in Ecuador",
    "version" : "1.0",
    "depends" : ["base", "hr", "hr_contract","hr_holidays"],
    "author" : "GnuThink Software",
    "description": """RRHH module that covers:
    contracts with Ecuador laws, payroll, prestamos, incomes, expenses, extra hours
    """,
    'author': 'GnuThink Software',
    'website': 'http://www.gnuthink.com',
    'init_xml': [],
    'update_xml': [
               "views/hr_contract_view.xml",
               "views/hr_employee_view.xml",
               "views/hr_family_item_view.xml",
               "views/hr_payroll_view.xml",
               "views/hr_fiscalyear_view.xml",
               "views/hr_contract_period_view.xml",
               "views/hr_wizard.xml",
               "views/hr_horas_extras_view.xml",
               "views/hr_provision_account_view.xml",
               "views/hr_report.xml",
    ],
    'installable': True,
    'active': False,
}
