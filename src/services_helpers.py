"""
PCO Services Module Helper Functions
Functions for managing service types, plans, teams, and schedules
"""

import pypco
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from cache import cached, invalidate_cache


# ============================================================================
# SERVICE TYPES
# ============================================================================

@cached(ttl=3600)  # Cache for 1 hour (service types rarely change)
def get_service_types(pco: pypco.PCO) -> List[Dict[str, Any]]:
    """
    Get all service types.
    
    Args:
        pco: Initialized PCO client
        
    Returns:
        List of service type dictionaries
        
    Example:
        >>> pco = get_pco_client()
        >>> service_types = get_service_types(pco)
        >>> for st in service_types:
        ...     print(f"{st['name']} - {st['id']}")
    """
    service_types = []
    
    try:
        for service_type in pco.iterate('/services/v2/service_types'):
            service_types.append({
                'id': service_type['data']['id'],
                'name': service_type['data']['attributes']['name'],
                'sequence': service_type['data']['attributes'].get('sequence', 0),
                'created_at': service_type['data']['attributes']['created_at'],
                'updated_at': service_type['data']['attributes']['updated_at'],
                'archived_at': service_type['data']['attributes'].get('archived_at'),
                'data': service_type['data']
            })
        
        print(f"Found {len(service_types)} service types")
        return service_types
        
    except Exception as e:
        print(f"ERROR: Error fetching service types: {e}")
        return []


@cached(ttl=3600)
def get_service_type_by_id(pco: pypco.PCO, service_type_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific service type by ID.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        
    Returns:
        Service type dictionary if found, None otherwise
    """
    try:
        service_type = pco.get(f'/services/v2/service_types/{service_type_id}')
        
        if service_type:
            return {
                'id': service_type['data']['id'],
                'name': service_type['data']['attributes']['name'],
                'sequence': service_type['data']['attributes'].get('sequence', 0),
                'created_at': service_type['data']['attributes']['created_at'],
                'updated_at': service_type['data']['attributes']['updated_at'],
                'archived_at': service_type['data']['attributes'].get('archived_at'),
                'data': service_type['data']
            }
        return None
        
    except Exception as e:
        print(f"ERROR: Error fetching service type: {e}")
        return None


# ============================================================================
# PLANS
# ============================================================================

@cached(ttl=300)  # Cache for 5 minutes
def get_plans(pco: pypco.PCO, service_type_id: str, 
              filter_by: Optional[str] = None,
              order: str = '-sort_date') -> List[Dict[str, Any]]:
    """
    Get plans for a service type.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        filter_by: Filter plans (future, past, after, before, no_dates)
        order: Sort order (default: -sort_date for newest first)
        
    Returns:
        List of plan dictionaries
        
    Example:
        >>> pco = get_pco_client()
        >>> plans = get_plans(pco, service_type_id, filter_by='future')
        >>> for plan in plans:
        ...     print(f"{plan['dates']} - {plan['title']}")
    """
    plans = []
    
    try:
        url = f'/services/v2/service_types/{service_type_id}/plans'
        params = {'order': order}
        
        if filter_by:
            params['filter'] = filter_by
        
        for plan in pco.iterate(url, **params):
            attributes = plan['data']['attributes']
            plans.append({
                'id': plan['data']['id'],
                'title': attributes.get('title', 'Untitled'),
                'series_title': attributes.get('series_title'),
                'dates': attributes.get('dates'),
                'sort_date': attributes.get('sort_date'),
                'short_dates': attributes.get('short_dates'),
                'planning_center_url': attributes.get('planning_center_url'),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': plan['data']
            })
        
        print(f"Found {len(plans)} plans")
        return plans
        
    except Exception as e:
        print(f"ERROR: Error fetching plans: {e}")
        return []


@cached(ttl=300)
def get_plan_by_id(pco: pypco.PCO, service_type_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific plan by ID.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        
    Returns:
        Plan dictionary if found, None otherwise
    """
    try:
        plan = pco.get(f'/services/v2/service_types/{service_type_id}/plans/{plan_id}')
        
        if plan:
            attributes = plan['data']['attributes']
            return {
                'id': plan['data']['id'],
                'title': attributes.get('title', 'Untitled'),
                'series_title': attributes.get('series_title'),
                'dates': attributes.get('dates'),
                'sort_date': attributes.get('sort_date'),
                'short_dates': attributes.get('short_dates'),
                'planning_center_url': attributes.get('planning_center_url'),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': plan['data']
            }
        return None
        
    except Exception as e:
        print(f"ERROR: Error fetching plan: {e}")
        return None


def create_plan(pco: pypco.PCO, service_type_id: str, 
                title: str, dates: Optional[str] = None,
                series_title: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new plan.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        title: Plan title
        dates: Plan dates (e.g., "January 1, 2024")
        series_title: Series title
        
    Returns:
        Created plan dictionary if successful, None otherwise
    """
    try:
        attributes = {'title': title}
        
        if dates:
            attributes['dates'] = dates
        if series_title:
            attributes['series_title'] = series_title
        
        payload = pco.template('Plan', attributes)
        
        new_plan = pco.post(f'/services/v2/service_types/{service_type_id}/plans', payload)
        
        print(f"SUCCESS: Created plan '{title}'")
        
        # Invalidate plans cache
        invalidate_cache('get_plans', pco, service_type_id)
        
        return {
            'id': new_plan['data']['id'],
            'title': new_plan['data']['attributes']['title'],
            'data': new_plan['data']
        }
        
    except Exception as e:
        print(f"ERROR: Error creating plan: {e}")
        return None


def update_plan(pco: pypco.PCO, service_type_id: str, plan_id: str,
                updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a plan.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        updates: Dictionary of attributes to update
        
    Returns:
        Updated plan dictionary if successful, None otherwise
    """
    try:
        payload = pco.template('Plan', updates)
        
        updated_plan = pco.patch(
            f'/services/v2/service_types/{service_type_id}/plans/{plan_id}',
            payload
        )
        
        print(f"SUCCESS: Updated plan {plan_id}")
        
        # Invalidate caches
        invalidate_cache('get_plan_by_id', pco, service_type_id, plan_id)
        invalidate_cache('get_plans', pco, service_type_id)
        
        return {
            'id': updated_plan['data']['id'],
            'data': updated_plan['data']
        }
        
    except Exception as e:
        print(f"ERROR: Error updating plan: {e}")
        return None


def delete_plan(pco: pypco.PCO, service_type_id: str, plan_id: str) -> bool:
    """
    Delete a plan.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pco.delete(f'/services/v2/service_types/{service_type_id}/plans/{plan_id}')
        
        print(f"SUCCESS: Deleted plan {plan_id}")
        
        # Invalidate caches
        invalidate_cache('get_plan_by_id', pco, service_type_id, plan_id)
        invalidate_cache('get_plans', pco, service_type_id)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error deleting plan: {e}")
        return False


# ============================================================================
# TEAMS
# ============================================================================

@cached(ttl=600)  # Cache for 10 minutes
def get_teams(pco: pypco.PCO, service_type_id: str) -> List[Dict[str, Any]]:
    """
    Get all teams for a service type.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        
    Returns:
        List of team dictionaries
    """
    teams = []
    
    try:
        for team in pco.iterate(f'/services/v2/service_types/{service_type_id}/teams'):
            attributes = team['data']['attributes']
            teams.append({
                'id': team['data']['id'],
                'name': attributes['name'],
                'sequence': attributes.get('sequence', 0),
                'schedule_to': attributes.get('schedule_to'),
                'default_status': attributes.get('default_status'),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': team['data']
            })
        
        print(f"Found {len(teams)} teams")
        return teams
        
    except Exception as e:
        print(f"ERROR: Error fetching teams: {e}")
        return []


@cached(ttl=600)
def get_team_by_id(pco: pypco.PCO, service_type_id: str, team_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific team by ID.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        team_id: The team ID
        
    Returns:
        Team dictionary if found, None otherwise
    """
    try:
        team = pco.get(f'/services/v2/service_types/{service_type_id}/teams/{team_id}')
        
        if team:
            attributes = team['data']['attributes']
            return {
                'id': team['data']['id'],
                'name': attributes['name'],
                'sequence': attributes.get('sequence', 0),
                'schedule_to': attributes.get('schedule_to'),
                'default_status': attributes.get('default_status'),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': team['data']
            }
        return None
        
    except Exception as e:
        print(f"ERROR: Error fetching team: {e}")
        return None


# ============================================================================
# TEAM POSITIONS
# ============================================================================

@cached(ttl=600)
def get_team_positions(pco: pypco.PCO, service_type_id: str, team_id: str) -> List[Dict[str, Any]]:
    """
    Get all positions for a team.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        team_id: The team ID
        
    Returns:
        List of position dictionaries
    """
    positions = []
    
    try:
        url = f'/services/v2/service_types/{service_type_id}/teams/{team_id}/team_positions'
        
        for position in pco.iterate(url):
            attributes = position['data']['attributes']
            positions.append({
                'id': position['data']['id'],
                'name': attributes['name'],
                'sequence': attributes.get('sequence', 0),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': position['data']
            })
        
        print(f"Found {len(positions)} positions")
        return positions
        
    except Exception as e:
        print(f"ERROR: Error fetching team positions: {e}")
        return []


# ============================================================================
# PLAN PEOPLE (SCHEDULE)
# ============================================================================

@cached(ttl=180)  # Cache for 3 minutes (schedules change frequently)
def get_plan_people(pco: pypco.PCO, service_type_id: str, plan_id: str) -> List[Dict[str, Any]]:
    """
    Get all scheduled people for a plan.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        
    Returns:
        List of scheduled person dictionaries
    """
    people = []
    
    try:
        url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/team_members'
        
        for person in pco.iterate(url, include='person,team,times'):
            attributes = person['data']['attributes']
            
            # Extract person info from included data
            person_name = "Unknown"
            team_name = "Unknown"
            
            for included in person.get('included', []):
                if included['type'] == 'Person':
                    person_name = included['attributes'].get('full_name', 'Unknown')
                elif included['type'] == 'Team':
                    team_name = included['attributes'].get('name', 'Unknown')
            
            people.append({
                'id': person['data']['id'],
                'person_name': person_name,
                'team_name': team_name,
                'status': attributes.get('status'),
                'team_position_name': attributes.get('team_position_name'),
                'scheduled_by_name': attributes.get('scheduled_by_name'),
                'created_at': attributes['created_at'],
                'updated_at': attributes['updated_at'],
                'data': person['data']
            })
        
        print(f"Found {len(people)} scheduled people")
        return people
        
    except Exception as e:
        print(f"ERROR: Error fetching plan people: {e}")
        return []


def add_person_to_plan(pco: pypco.PCO, service_type_id: str, plan_id: str,
                       person_id: str, team_id: str, team_position_id: str,
                       status: str = "C") -> Optional[Dict[str, Any]]:
    """
    Add a person to a plan schedule.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        person_id: The person ID
        team_id: The team ID
        team_position_id: The team position ID
        status: Status (C=Confirmed, U=Unconfirmed, D=Declined)
        
    Returns:
        Created team member dictionary if successful, None otherwise
    """
    try:
        payload = {
            "data": {
                "type": "TeamMember",
                "attributes": {
                    "status": status
                },
                "relationships": {
                    "person": {
                        "data": {
                            "type": "Person",
                            "id": person_id
                        }
                    },
                    "team": {
                        "data": {
                            "type": "Team",
                            "id": team_id
                        }
                    },
                    "team_position": {
                        "data": {
                            "type": "TeamPosition",
                            "id": team_position_id
                        }
                    }
                }
            }
        }
        
        url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/team_members'
        new_member = pco.post(url, payload)
        
        print(f"SUCCESS: Added person to plan")
        
        # Invalidate cache
        invalidate_cache('get_plan_people', pco, service_type_id, plan_id)
        
        return {
            'id': new_member['data']['id'],
            'data': new_member['data']
        }
        
    except Exception as e:
        print(f"ERROR: Error adding person to plan: {e}")
        return None


def update_plan_person_status(pco: pypco.PCO, service_type_id: str, plan_id: str,
                              team_member_id: str, status: str) -> Optional[Dict[str, Any]]:
    """
    Update a person's status on a plan.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        team_member_id: The team member ID
        status: New status (C=Confirmed, U=Unconfirmed, D=Declined)
        
    Returns:
        Updated team member dictionary if successful, None otherwise
    """
    try:
        payload = pco.template('TeamMember', {'status': status})
        
        url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/team_members/{team_member_id}'
        updated_member = pco.patch(url, payload)
        
        print(f"SUCCESS: Updated person status to {status}")
        
        # Invalidate cache
        invalidate_cache('get_plan_people', pco, service_type_id, plan_id)
        
        return {
            'id': updated_member['data']['id'],
            'data': updated_member['data']
        }
        
    except Exception as e:
        print(f"ERROR: Error updating person status: {e}")
        return None


def remove_person_from_plan(pco: pypco.PCO, service_type_id: str, plan_id: str,
                            team_member_id: str) -> bool:
    """
    Remove a person from a plan schedule.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        plan_id: The plan ID
        team_member_id: The team member ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f'/services/v2/service_types/{service_type_id}/plans/{plan_id}/team_members/{team_member_id}'
        pco.delete(url)
        
        print(f"SUCCESS: Removed person from plan")
        
        # Invalidate cache
        invalidate_cache('get_plan_people', pco, service_type_id, plan_id)
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error removing person from plan: {e}")
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_upcoming_plans(pco: pypco.PCO, service_type_id: str, 
                      days_ahead: int = 30) -> List[Dict[str, Any]]:
    """
    Get upcoming plans within specified days.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        days_ahead: Number of days to look ahead (default: 30)
        
    Returns:
        List of upcoming plan dictionaries
    """
    return get_plans(pco, service_type_id, filter_by='future', order='-sort_date')


def get_past_plans(pco: pypco.PCO, service_type_id: str,
                   days_back: int = 30) -> List[Dict[str, Any]]:
    """
    Get past plans within specified days.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        days_back: Number of days to look back (default: 30)
        
    Returns:
        List of past plan dictionaries
    """
    return get_plans(pco, service_type_id, filter_by='past', order='-sort_date')


def find_plan_by_date(pco: pypco.PCO, service_type_id: str, 
                     target_date: str) -> Optional[Dict[str, Any]]:
    """
    Find a plan by date.
    
    Args:
        pco: Initialized PCO client
        service_type_id: The service type ID
        target_date: Target date string (e.g., "2024-01-15")
        
    Returns:
        Plan dictionary if found, None otherwise
    """
    plans = get_plans(pco, service_type_id)
    
    for plan in plans:
        if plan.get('sort_date') and target_date in plan['sort_date']:
            return plan
    
    return None