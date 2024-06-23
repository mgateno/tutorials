# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
        ('pending', 'Pending')
    ], default='pending', copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    date_availability = fields.Date(related='property_id.date_availability')

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)

    @api.depends('date_deadline', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.date_availability and record.validity:
                record.date_deadline = record.date_availability + \
                    datetime.timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline -
                                   record.date_availability).days

    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = 'offer_accepted'
        return True

    def action_reject(self):
        for record in self:
            record.status = 'refused'
        return True

    @api.constrains('property_id')
    def _check_property_sold(self):
        for record in self:
            if (record.property_id.state == 'sold' or record.property_id.state == 'canceled' or record.property_id.state == 'offer_accepted'):
                raise ValidationError(
                    'This property is already sold, canceled or an offer has been accepted.')

    @api.constrains('status')
    def _check_offer_present(self):
        for record in self:
            if record.status == 'pending':
                record.property_id.state = 'offer_received'

    _sql_constraints = [
        ('check_price_positive', 'CHECK(price >= 0)', 'The price must be positive.'),
    ]
