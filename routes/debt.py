# routes/debt.py
from flask import Blueprint, jsonify, request
from models import DebtJuniorLienBond
from models import db

debt_bp = Blueprint('debt', __name__, url_prefix='/api/debt')

@debt_bp.route('/', methods=['GET'])
def get_debt_data():
    # Optional query parameters
    issuer = request.args.get('issuer')
    lien_position = request.args.get('lien_position')

    query = DebtJuniorLienBond.query
    if issuer:
        query = query.filter(DebtJuniorLienBond.issuer.ilike(f"%{issuer}%"))  # Case-insensitive search
    if lien_position:
        query = query.filter(DebtJuniorLienBond.lien_position == lien_position)

    try:
        results = query.all()
        data = [{
            'bond_id': record.bond_id,
            'issuer': record.issuer,
            'principal_amount': float(record.principal_amount),
            'interest_rate': float(record.interest_rate),
            'maturity_date': record.maturity_date.strftime('%Y-%m-%d'),
            'lien_position': record.lien_position
        } for record in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
