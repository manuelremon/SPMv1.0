"""
Planner routes
"""
from flask import Blueprint, jsonify

planner_bp = Blueprint('planner', __name__)


@planner_bp.route('', methods=['GET'])
def get_planner():
    """Obtener vista del planner"""
    return jsonify({
        "ok": True,
        "planner": []
    }), 200
