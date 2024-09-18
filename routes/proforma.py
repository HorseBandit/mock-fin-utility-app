# routes/proforma.py
from flask import Blueprint, jsonify, request
from models import ProForma
from models import db

proforma_bp = Blueprint('proforma', __name__, url_prefix='/api/proforma')

@proforma_bp.route('/', methods=['GET'])
def get_proforma_data():
    # Optional query parameters
    metric_name = request.args.get('metric_name')
    period = request.args.get('period')

    query = ProForma.query
    if metric_name:
        query = query.filter(ProForma.metric_name.ilike(f"%{metric_name}%"))
    if period:
        query = query.filter(ProForma.period == period)

    try:
        results = query.all()
        data = [{
            'metric_id': record.metric_id,
            'metric_name': record.metric_name,
            'value': float(record.value),
            'period': record.period,
            'assumptions': record.assumptions
        } for record in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
