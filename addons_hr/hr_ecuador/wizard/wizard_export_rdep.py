# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 (http://gnuthink.com) All Rights Reserved.
#       Cristian Salamea <cristian.salamea@gnuthink.com>
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
#
##############################################################################

from openerp.osv import osv,fields
import base64
import StringIO
import pooler
from lxml import etree
from time import strftime

rdep_form="""<?xml version="1.0"?>
        <form string="Asistente de generación de Anexo">
          <separator string="Retención por Relación de Dependencia RDEP" colspan="4"/>
          <field name="trans_anio"/>
        </form>"""

view_form_finish="""<?xml version="1.0"?>
<form string="Exportar XML">
	<image name="gtk-dialog-info" colspan="2"/>
	<group colspan="2" col="4">
		<separator string="Archivo Generado" colspan="4"/>
		<field name="data" readonly="1" colspan="3"/>
		<label align="0.0" string="Guardar este documento como .XML \n(NNNN en el nombre tienen q reemplazarse con el año)y cargarlo en el DIMM del SRI." colspan="4"/>
	</group>
</form>"""

rdep_fields ={
    'trans_anio' : {'string' : 'Año de Trabajo', 'type': 'many2one','relation':'hr.fiscalyear', 'required' : True},
}

fields_form_finish={
    'data': {'string':'Archivo', 'type':'binary', 'readonly': True, 'default':strftime('%Y')},
    'name': {'string':'Nombre', 'type':'string', 'readonly': True},
}

def crear_header(self, cr, uid, data, context):
    form = data['form']
    anio = form['trans_anio']
    res = pooler.get_pool(cr.dbname).get('hr.employee').search(cr, uid, [])
    #iter in employees
    for emp in res:
        obj = pooler.get_pool(cr.dbname).get('hr.employee').browse(cr, uid, emp)
        tipoid = obj.tipoid
        cedula = obj.cedula
        address = obj.address
        fono = obj.work_phone
        sis_sal = 2
        res1 = pooler.get_pool(cr.dbname).get('hr.contract').search(cr, uid, [('employee_id','=',emp)])[0]
        ct = pooler.get_pool(cr.dbname).get('hr.contract').browse(cr, uid, res1)
        salario = ct.wage
        sobresueldo = 0
        res2 = pooler.get_pool(cr.dbname).get('hr.provision').search(cr, uid, ['employee_id',])
    res = cr.fetchall()
    if res:
        ruc = res[0][0]   
        rdep = etree.Element('rdep')
        etree.SubElement(rdep, 'numRuc').text = ruc
        etree.SubElement(rdep, 'anio').text = str(anio)
        file = etree.tostring(rdep, pretty_print=True, encoding='iso-8859-1')
        buf=StringIO.StringIO()
        buf.write(file)
        out=base64.encodestring(buf.getvalue())
        buf.close()
        name = "%s%s.XML" % ("RDEP", strftime("%Y"))
    return {'data': out, 'name': name}

def crear_empleados(self):
    retRelDep = etree.Element('retRelDep')
    retRelDep.append(crear_empleado())

def crear_empleado(self, tipidret, idret, dircal, dirnum, dirciu, dirprov, tel, sissalnet, suelsal, sobsuelcomremu, decimter, decimcuar, partutil, apoperiess, rebespdiscap, rebesptered, subtotal, imprentempl, imprentcaus, basimp, valret, anioret, numret):
    datRetRelDep = etree.Element('datRetRelDep')
    etree.SubElement( datRetRelDep, 'tipIdRet' ).text = tipidret
    etree.SubElement( datRetRelDep, 'idRet' ).text = idret
    etree.SubElement( datRetRelDep, 'dirCal' ).text = dircal
    etree.SubElement( datRetRelDep, 'dirNum' ).text = dirnum
    etree.SubElement( datRetRelDep, 'dirCiu' ).text = dirciu
    etree.SubElement( datRetRelDep, 'dirProv' ).text = dirprov
    etree.SubElement( datRetRelDep, 'tel' ).text = tel
    etree.SubElement( datRetRelDep, 'sisSalNet' ).text = sissalnet
    etree.SubElement( datRetRelDep, 'suelSal' ).text = suelsal
    etree.SubElement( datRetRelDep, 'sobSuelComRemu' ).text = sobsuelcomremu
    etree.SubElement( datRetRelDep, 'decimTer' ).text = decimter
    etree.SubElement( datRetRelDep, 'decimCuar' ).text = decimcuar
    etree.SubElement( datRetRelDep, 'partUtil' ).text = partutil
    etree.SubElement( datRetRelDep, 'apoPerIess' ).text = apoperiess
    etree.SubElement( datRetRelDep, 'rebEspDiscap' ).text = rebespdiscap
    etree.SubElement( datRetRelDep, 'rebEspTerEd' ).text = rebesptered
    etree.SubElement( datRetRelDep, 'subTotal' ).text = subtotal
    etree.SubElement( datRetRelDep, 'impRentEmpl' ).text = imprentempl
    etree.SubElement( datRetRelDep, 'impRentCaus' ).text = imprentcaus
    etree.SubElement( datRetRelDep, 'basImp' ).text = basimp
    etree.SubElement( datRetRelDep, 'valRet' ).text = valret
    etree.SubElement( datRetRelDep, 'anioRet' ).text = anioret
    etree.SubElement( datRetRelDep, 'numRet' ).text = numret
    return datRetRelDep

class wizard_export_rdep(osv.osv_memory):
     _name="wizard.export.rdep" 
     states = {
           'init': {
                'actions': [],
                'result': {'type': 'form',
                           'arch': rdep_form,
                           'fields': rdep_fields,
                           'state' : [('end', 'Cancelar'),('generate', 'Generar XML') ]}
          },
           'generate': {
                'actions': [crear_header],
                'result': { 'type': 'form',
                            'arch': view_form_finish,
                            'fields' : fields_form_finish,
                            'state': [
                            ('end', 'Close', 'gtk-cancel', True)
                        ]
                }
          },
     }
wizard_export_rdep()
