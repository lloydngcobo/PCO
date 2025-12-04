#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to show all upcoming services from Planning Center Online
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from src.pco_helpers import get_pco_client
from src.services_helpers import get_service_types, get_upcoming_plans

# Load environment variables
load_dotenv()

def format_date(date_str):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')
    except:
        return date_str

def show_upcoming_services(days_ahead=30):
    """Show all upcoming services across all service types"""
    try:
        # Get PCO client
        print("Connecting to Planning Center Online...")
        pco = get_pco_client()
        print("[SUCCESS] Connected successfully!\n")
        
        # Get all service types
        print("Fetching service types...")
        service_types = get_service_types(pco)
        
        if not service_types:
            print("[INFO] No service types found")
            return
        
        print(f"[SUCCESS] Found {len(service_types)} service type(s)\n")
        print("=" * 80)
        
        total_plans = 0
        
        # For each service type, get upcoming plans
        for service_type in service_types:
            service_type_id = service_type.get('id')
            service_type_name = service_type.get('attributes', {}).get('name', 'Unknown')
            
            print(f"\n📋 SERVICE TYPE: {service_type_name}")
            print(f"   ID: {service_type_id}")
            print("-" * 80)
            
            # Get upcoming plans
            upcoming_plans = get_upcoming_plans(pco, service_type_id, days_ahead=days_ahead)
            
            if not upcoming_plans:
                print("   [INFO] No upcoming plans found")
                continue
            
            print(f"   Found {len(upcoming_plans)} upcoming plan(s):\n")
            total_plans += len(upcoming_plans)
            
            # Display each plan
            for i, plan in enumerate(upcoming_plans, 1):
                plan_id = plan.get('id')
                attributes = plan.get('attributes', {})
                
                title = attributes.get('title', 'Untitled')
                dates = attributes.get('dates', 'No date')
                series_title = attributes.get('series_title', '')
                sort_date = attributes.get('sort_date', '')
                
                print(f"   {i}. {title}")
                print(f"      Plan ID: {plan_id}")
                print(f"      Date: {dates}")
                if sort_date:
                    print(f"      Sort Date: {format_date(sort_date)}")
                if series_title:
                    print(f"      Series: {series_title}")
                print()
        
        print("=" * 80)
        print(f"\n[SUMMARY] Total upcoming plans across all service types: {total_plans}")
        print(f"[SUMMARY] Looking ahead: {days_ahead} days")
        print()
        
    except ValueError as e:
        print(f"[ERROR] {e}")
        print("\nPlease ensure PCO_APP_ID and PCO_SECRET are set in your .env file")
        return
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    print("=" * 80)
    print("PCO Upcoming Services Viewer")
    print("=" * 80)
    print()
    
    # Check for command line argument for days ahead
    days_ahead = 30
    if len(sys.argv) > 1:
        try:
            days_ahead = int(sys.argv[1])
            print(f"Looking ahead: {days_ahead} days\n")
        except ValueError:
            print(f"Invalid days argument. Using default: {days_ahead} days\n")
    
    show_upcoming_services(days_ahead)
    
    print("=" * 80)
    print("[INFO] To change the number of days to look ahead:")
    print("       python show_upcoming_services.py 60")
    print("=" * 80)