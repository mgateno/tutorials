# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char('Property Tag', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Property tag name must be unique')]
