"""
Flask API endpoints for PCO Services module
Provides REST endpoints for managing service types, plans, teams, and schedules
"""

from flask import Blueprint, request, jsonify
from typing import Optional
import os
from dotenv import load_dotenv
import pypco

from services_helpers import (
    get_service_types,
    get_service_type_by_id,
    get_plans,
    get_plan_by_id,
    create_plan,
    update_plan,
    delete_plan,
    get_teams,
    get_team_by_id,
    get_team_positions,
    get_plan_people,
    add_person_to_plan,
    update_plan_person_status,
    remove_person_from_plan,
    get_upcoming_plans,
    get_past_plans,
    find_plan_by_date
)

# Load environment variables
load_dotenv()

# Create Blueprint
services_bp = Blueprint('services', __name__, url_prefix='/api/services')

# Initialize PCO client
PCO_APP_ID = os.getenv("PCO_APP_ID")
PCO_SECRET = os.getenv("PCO_SECRET")

if not PCO_APP_ID or not PCO_SECRET:
    raise ValueError("PCO_APP_ID and PCO_SECRET must be set in the .env file")

pco = pypco.PCO(PCO_APP_ID, PCO_SECRET)


# ============================================================================
# SERVICE TYPES ENDPOINTS
# ============================================================================

@services_bp.route('/service-types', methods=['GET'])
def api_get_service_types():
    """
    Get all service types.
    
    Returns:
        JSON response with service types
        
    Example:
        GET /api/services/service-types
    """
    try:
        service_types = get_service_types(pco)
        
        return jsonify({
            'count': len(service_types),
            'data': service_types
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>', methods=['GET'])
def api_get_service_type(service_type_id: str):
    """
    Get a specific service type.
    
    Args:
        service_type_id: The service type ID
        
    Returns:
        JSON response with service type data
        
    Example:
        GET /api/services/service-types/123
    """
    try:
        service_type = get_service_type_by_id(pco, service_type_id)
        
        if not service_type:
            return jsonify({'error': 'Service type not found'}), 404
        
        return jsonify(service_type)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PLANS ENDPOINTS
# ============================================================================

@services_bp.route('/service-types/<service_type_id>/plans', methods=['GET'])
def api_get_plans(service_type_id: str):
    """
    Get plans for a service type.
    
    Query Parameters:
        filter: Filter plans (future, past, after, before, no_dates)
        order: Sort order (default: -sort_date)
        
    Returns:
        JSON response with plans
        
    Example:
        GET /api/services/service-types/123/plans?filter=future
    """
    try:
        filter_by = request.args.get('filter')
        order = request.args.get('order', '-sort_date')
        
        plans = get_plans(pco, service_type_id, filter_by=filter_by, order=order)
        
        return jsonify({
            'count': len(plans),
            'service_type_id': service_type_id,
            'filter': filter_by,
            'data': plans
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>', methods=['GET'])
def api_get_plan(service_type_id: str, plan_id: str):
    """
    Get a specific plan.
    
    Args:
        service_type_id: The service type ID
        plan_id: The plan ID
        
    Returns:
        JSON response with plan data
        
    Example:
        GET /api/services/service-types/123/plans/456
    """
    try:
        plan = get_plan_by_id(pco, service_type_id, plan_id)
        
        if not plan:
            return jsonify({'error': 'Plan not found'}), 404
        
        return jsonify(plan)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans', methods=['POST'])
def api_create_plan(service_type_id: str):
    """
    Create a new plan.
    
    Request Body:
        {
            "title": "Sunday Service",
            "dates": "January 15, 2024",
            "series_title": "New Year Series"
        }
        
    Returns:
        JSON response with created plan
        
    Example:
        POST /api/services/service-types/123/plans
    """
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'title is required'}), 400
        
        plan = create_plan(
            pco,
            service_type_id,
            title=data['title'],
            dates=data.get('dates'),
            series_title=data.get('series_title')
        )
        
        if not plan:
            return jsonify({'error': 'Failed to create plan'}), 500
        
        return jsonify({
            'message': 'Plan created successfully',
            'data': plan
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>', methods=['PATCH'])
def api_update_plan(service_type_id: str, plan_id: str):
    """
    Update a plan.
    
    Request Body:
        {
            "title": "Updated Title",
            "dates": "January 16, 2024"
        }
        
    Returns:
        JSON response with updated plan
        
    Example:
        PATCH /api/services/service-types/123/plans/456
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        plan = update_plan(pco, service_type_id, plan_id, data)
        
        if not plan:
            return jsonify({'error': 'Failed to update plan'}), 500
        
        return jsonify({
            'message': 'Plan updated successfully',
            'data': plan
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>', methods=['DELETE'])
def api_delete_plan(service_type_id: str, plan_id: str):
    """
    Delete a plan.
    
    Args:
        service_type_id: The service type ID
        plan_id: The plan ID
        
    Returns:
        JSON response confirming deletion
        
    Example:
        DELETE /api/services/service-types/123/plans/456
    """
    try:
        success = delete_plan(pco, service_type_id, plan_id)
        
        if not success:
            return jsonify({'error': 'Failed to delete plan'}), 500
        
        return jsonify({
            'message': 'Plan deleted successfully',
            'plan_id': plan_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# TEAMS ENDPOINTS
# ============================================================================

@services_bp.route('/service-types/<service_type_id>/teams', methods=['GET'])
def api_get_teams(service_type_id: str):
    """
    Get all teams for a service type.
    
    Returns:
        JSON response with teams
        
    Example:
        GET /api/services/service-types/123/teams
    """
    try:
        teams = get_teams(pco, service_type_id)
        
        return jsonify({
            'count': len(teams),
            'service_type_id': service_type_id,
            'data': teams
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/teams/<team_id>', methods=['GET'])
def api_get_team(service_type_id: str, team_id: str):
    """
    Get a specific team.
    
    Args:
        service_type_id: The service type ID
        team_id: The team ID
        
    Returns:
        JSON response with team data
        
    Example:
        GET /api/services/service-types/123/teams/456
    """
    try:
        team = get_team_by_id(pco, service_type_id, team_id)
        
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        
        return jsonify(team)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/teams/<team_id>/positions', methods=['GET'])
def api_get_team_positions(service_type_id: str, team_id: str):
    """
    Get all positions for a team.
    
    Returns:
        JSON response with team positions
        
    Example:
        GET /api/services/service-types/123/teams/456/positions
    """
    try:
        positions = get_team_positions(pco, service_type_id, team_id)
        
        return jsonify({
            'count': len(positions),
            'team_id': team_id,
            'data': positions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# PLAN PEOPLE (SCHEDULE) ENDPOINTS
# ============================================================================

@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>/team-members', methods=['GET'])
def api_get_plan_people(service_type_id: str, plan_id: str):
    """
    Get all scheduled people for a plan.
    
    Returns:
        JSON response with scheduled people
        
    Example:
        GET /api/services/service-types/123/plans/456/team-members
    """
    try:
        people = get_plan_people(pco, service_type_id, plan_id)
        
        return jsonify({
            'count': len(people),
            'plan_id': plan_id,
            'data': people
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>/team-members', methods=['POST'])
def api_add_person_to_plan(service_type_id: str, plan_id: str):
    """
    Add a person to a plan schedule.
    
    Request Body:
        {
            "person_id": "123",
            "team_id": "456",
            "team_position_id": "789",
            "status": "C"
        }
        
    Returns:
        JSON response with created team member
        
    Example:
        POST /api/services/service-types/123/plans/456/team-members
    """
    try:
        data = request.get_json()
        
        required_fields = ['person_id', 'team_id', 'team_position_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        member = add_person_to_plan(
            pco,
            service_type_id,
            plan_id,
            person_id=data['person_id'],
            team_id=data['team_id'],
            team_position_id=data['team_position_id'],
            status=data.get('status', 'C')
        )
        
        if not member:
            return jsonify({'error': 'Failed to add person to plan'}), 500
        
        return jsonify({
            'message': 'Person added to plan successfully',
            'data': member
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>/team-members/<team_member_id>', methods=['PATCH'])
def api_update_plan_person_status(service_type_id: str, plan_id: str, team_member_id: str):
    """
    Update a person's status on a plan.
    
    Request Body:
        {
            "status": "C"
        }
        
    Returns:
        JSON response with updated team member
        
    Example:
        PATCH /api/services/service-types/123/plans/456/team-members/789
    """
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'error': 'status is required'}), 400
        
        member = update_plan_person_status(
            pco,
            service_type_id,
            plan_id,
            team_member_id,
            status=data['status']
        )
        
        if not member:
            return jsonify({'error': 'Failed to update person status'}), 500
        
        return jsonify({
            'message': 'Person status updated successfully',
            'data': member
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/<plan_id>/team-members/<team_member_id>', methods=['DELETE'])
def api_remove_person_from_plan(service_type_id: str, plan_id: str, team_member_id: str):
    """
    Remove a person from a plan schedule.
    
    Returns:
        JSON response confirming removal
        
    Example:
        DELETE /api/services/service-types/123/plans/456/team-members/789
    """
    try:
        success = remove_person_from_plan(pco, service_type_id, plan_id, team_member_id)
        
        if not success:
            return jsonify({'error': 'Failed to remove person from plan'}), 500
        
        return jsonify({
            'message': 'Person removed from plan successfully',
            'team_member_id': team_member_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@services_bp.route('/service-types/<service_type_id>/plans/upcoming', methods=['GET'])
def api_get_upcoming_plans(service_type_id: str):
    """
    Get upcoming plans.
    
    Query Parameters:
        days: Number of days to look ahead (default: 30)
        
    Returns:
        JSON response with upcoming plans
        
    Example:
        GET /api/services/service-types/123/plans/upcoming?days=30
    """
    try:
        days = int(request.args.get('days', 30))
        plans = get_upcoming_plans(pco, service_type_id, days_ahead=days)
        
        return jsonify({
            'count': len(plans),
            'service_type_id': service_type_id,
            'days_ahead': days,
            'data': plans
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/past', methods=['GET'])
def api_get_past_plans(service_type_id: str):
    """
    Get past plans.
    
    Query Parameters:
        days: Number of days to look back (default: 30)
        
    Returns:
        JSON response with past plans
        
    Example:
        GET /api/services/service-types/123/plans/past?days=30
    """
    try:
        days = int(request.args.get('days', 30))
        plans = get_past_plans(pco, service_type_id, days_back=days)
        
        return jsonify({
            'count': len(plans),
            'service_type_id': service_type_id,
            'days_back': days,
            'data': plans
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@services_bp.route('/service-types/<service_type_id>/plans/find-by-date', methods=['GET'])
def api_find_plan_by_date(service_type_id: str):
    """
    Find a plan by date.
    
    Query Parameters:
        date: Target date (YYYY-MM-DD format)
        
    Returns:
        JSON response with plan data
        
    Example:
        GET /api/services/service-types/123/plans/find-by-date?date=2024-01-15
    """
    try:
        target_date = request.args.get('date')
        
        if not target_date:
            return jsonify({'error': 'date parameter is required'}), 400
        
        plan = find_plan_by_date(pco, service_type_id, target_date)
        
        if not plan:
            return jsonify({'error': 'Plan not found for the specified date'}), 404
        
        return jsonify(plan)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500