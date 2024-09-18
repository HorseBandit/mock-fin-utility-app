# routes/ferc.py
from flask import Blueprint, jsonify, request
from models import FERCTrialBalance
from sqlalchemy import or_
from models import db

ferc_bp = Blueprint('ferc', __name__, url_prefix='/api/ferc')

@ferc_bp.route('/', methods=['GET'])
def get_ferc_data():
    # Optional query parameters
    account_number = request.args.get('account_number')
    period = request.args.get('period')
    entity = request.args.get('entity')

    query = FERCTrialBalance.query
    if account_number:
        query = query.filter(FERCTrialBalance.account_number == account_number)
    if period:
        query = query.filter(FERCTrialBalance.period == period)
    if entity:
        query = query.filter(FERCTrialBalance.entity == entity)

    try:
        results = query.all()
        data = [{
            'id': record.id,
            'account_number': record.account_number,
            'account_description': record.account_description,
            'debit': float(record.debit),
            'credit': float(record.credit),
            'period': record.period,
            'entity': record.entity
        } for record in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
