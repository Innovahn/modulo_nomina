# -*- encoding: utf-8 -*-
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import time
import pooler
from openerp.report import report_sxw

UNIDADES = ('','UN ','DOS ','TRES ','CUATRO ','CINCO ','SEIS ','SIETE ','OCHO ','NUEVE ','DIEZ ','ONCE ','DOCE ','TRECE ','CATORCE ','QUINCE ',   'DIECISEIS ', 'DIECISIETE ',
	    'DIECIOCHO ', 'DIECINUEVE ', 'VEINTE ')
DECENAS = ( 'VENTI', 'TREINTA ', 'CUARENTA ', 'CINCUENTA ', 'SESENTA ', 'SETENTA ', 'OCHENTA ', 'NOVENTA ', 'CIEN ')
CENTENAS = ('CIENTO ', 'DOSCIENTOS ', 'TRESCIENTOS ', 'CUATROCIENTOS ', 'QUINIENTOS ', 'SEISCIENTOS ', 'SETECIENTOS ', 'OCHOCIENTOS ', 'NOVECIENTOS ')

def toWord(number):

    """
    Converts a number into string representation
    """
    converted = ''

    if not (0 < number < 999999999):

        return 'No es posible convertir el numero a letras'

    number_str = str(number).zfill(9)
    millones = number_str[:3]
    miles = number_str[3:6]
    cientos = number_str[6:]

    if(millones):
        if(millones == '001'):
            converted += 'UN MILLON '
        elif(int(millones) > 0):
            converted += '%sMILLONES ' % __convertNumber(millones)

    if(miles):
        if(miles == '001'):
            converted += 'MIL '
        elif(int(miles) > 0):
            converted += '%sMIL ' % __convertNumber(miles)

    if(cientos):
        if(cientos == '001'):
            converted += 'UN '
        elif(int(cientos) > 0):
            converted += '%s ' % __convertNumber(cientos)

    converted += ''

    return converted.title()

def __convertNumber(n):
    """
    Max length must be 3 digits
    """
    output = ''

    if(n == '100'):
        output = "CIEN "
    elif(n[0] != '0'):
        output = CENTENAS[int(n[0])-1]

    k = int(n[1:])
    if(k <= 20):
        output += UNIDADES[k]
    else:
        if((k > 30) & (n[2] != '0')):
            output += '%sY %s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])
        else:
            output += '%s%s' % (DECENAS[int(n[1])-2], UNIDADES[int(n[2])])

    return output

class hr_payrolls(report_sxw.rml_parse):
    
    inherit='hr.payroll'
    def _num_let(self, rol, form):
        pe = int(rol.total)
	dec = rol.total - pe
        letras = toWord(pe)
	print form, letras
	return letras + ',' + str(dec)[2:4]+'/'+'100******'

    def __init__(self, cr, uid, name, context):
        super(hr_payrolls,self).__init__(cr, uid, name, context)
        self.localcontext.update({'time' : time, 'num_let' : self._num_let })
        self.context = context
	
	report_sxw.report_sxw(
		'report.hrpayroll',
		'hr.payroll',
		'addons/hr_ecuador/report/hr_payroll.rml', 
		parser=hr_payrolls,
		header=False)
