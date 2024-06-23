# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from . import estate_property


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "name"

    name = fields.Char('Property Type', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id',
                                   string='Properties')
    sequence = fields.Integer('Sequence', default=1,
                              help='Used to order property types')

    _sql_constraints = [('name_uniq', 'unique(name)', 'Property type name must be unique'
                         )]
