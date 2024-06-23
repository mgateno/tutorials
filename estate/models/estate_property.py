# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=datetime.datetime.now() + datetime.timedelta(days=90), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'),
                   ('east', 'East'), ('west', 'West')]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')],
        default='new', copy=False
    )
    property_type_id = fields.Many2one(
        'estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    seller_id = fields.Many2one('res.users', string='Salesperson',
                                index=True, tracking=True, default=lambda self: self.env.user)
    property_tag_ids = fields.Many2many(
        'estate.property.tag', string='Property Tags')
    offer_ids = fields.One2many(
        'estate.property.offer', 'property_id', string='Offers')

    total_area = fields.Integer(compute='_compute_total_area', store=True)

    _sql_constraints = [
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)',
         'The selling price must be positive.'),
    ]

    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price >= 0)',
         'The expected price must be positive.'),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.state == 'sold':
                if record.selling_price < record.expected_price * 0.9:
                    raise UserError(
                        ('The selling price cannot be lower than 90% of the expected price.'))

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    best_price = fields.Float(
        compute='_compute_best_price', string="Best Offer", store=True)

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped('price') or [0])

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_orientation = 'north'
            self.garden_area = 100
        else:
            self.garden_orientation = False
            self.garden_area = 0

    def action_sold(self):
        for record in self:
            if record.state != 'canceled':
                record.state = 'sold'
                record.active = False
            else:
                raise UserError(
                    ('You cannot sell a property that is canceled.'))
        return record.state

    def action_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
                record.active = False
            else:
                raise UserError(('You cannot cancel a property that is sold.'))
        return record.state
