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

import wizard

view_form="""<?xml version="1.0"?>
<form string="">
<image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Generar Liquidacion de Vacaciones" colspan="4"/>
        <field name="employee_id"/>
        <field name="hr_fiscal_id"/>
    </group>
</form>"""

class wizard_holidays_pay(wizard.interface):
        states={
        }
wizard_holidays_pay('wizard.holidays.pay')
