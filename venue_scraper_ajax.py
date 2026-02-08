"""
Venue Calendar Aggregator for Stadt Linz booking system
Uses AJAX endpoints to efficiently fetch ALL venues for multiple days

This is much more efficient than the per-venue approach!
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from collections import defaultdict
from typing import List, Dict
import time
import re

class VenueCalendarAggregator:
    def __init__(self, base_url="https://book.venuzle.at/stadt-linz/venues"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_day_availability(self, date: str, cluster_id: int = 6) -> Dict:
        """
        Fetch availability for ALL venues on a specific date using AJAX endpoint
        date format: YYYYMMDD (e.g., 20260209)
        cluster_id: venue cluster (default 6 seems to be all venues)
        """
        url = f"{self.base_url}/c/{cluster_id}/{date}/ajax/"
        
        try:
            print(f"  Fetching {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # The response is HTML table rows for all venues
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all venue rows
            venues_data = self._extract_venues_from_ajax(soup, date)
            
            # Debug info
            all_rows = soup.find_all('tr')
            print(f"    Found {len(all_rows)} venue rows, {len(venues_data)} with availability")
            
            return {
                'date': date,
                'url': url,
                'venues': venues_data,
                'total_venues': len(all_rows),
                'venues_with_slots': len(venues_data),
                'fetched_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"  Error fetching date {date}: {e}")
            return {
                'date': date,
                'error': str(e),
                'venues': []
            }
    
    def _extract_venues_from_ajax(self, soup: BeautifulSoup, date: str) -> List[Dict]:
        """
        Extract all venues and their availability from AJAX response
        Each <tr> represents one venue
        NOW INCLUDES ALL SLOTS - available, blocked, and unavailable
        """
        venues = []
        
        # Find all table rows (each is a venue)
        rows = soup.find_all('tr')
        
        for row in rows:
            # First cell contains venue name and link
            first_cell = row.find('td')
            if not first_cell:
                continue
            
            # Extract venue name and ID from link
            link = first_cell.find('a', class_='timetable-row-link')
            if not link:
                continue
            
            # Venue name might have facility name in span + line break + venue name
            facility_span = link.find('span', class_='facility_name')
            if facility_span:
                facility_name = facility_span.get_text(strip=True)
                # Get text after the span
                venue_text = ''.join(link.find_all(text=True, recursive=False)).strip()
                venue_name = f"{facility_name} - {venue_text}" if venue_text else facility_name
            else:
                venue_name = link.get_text(strip=True)
            
            # Clean up venue name
            venue_name = ' '.join(venue_name.split())
            
            # Extract venue ID from href like "/stadt-linz/venues/v/86/20260209/"
            href = link.get('href', '')
            venue_id_match = re.search(r'/v/(\d+)/', href)
            venue_id = int(venue_id_match.group(1)) if venue_id_match else None
            
            if not venue_id:
                continue
            
            # Extract time slots from this row
            time_slots = self._extract_time_slots_from_row(row, venue_id, date)
            
            # Include ALL venues, even without available slots
            venues.append({
                'venue_id': venue_id,
                'venue_name': venue_name,
                'available_slots': time_slots
            })
        
        return venues
    
    def _extract_time_slots_from_row(self, row, venue_id: int, date: str) -> List[Dict]:
        """
        Extract ALL time slots from a venue row (including blocked/unavailable)
        """
        slots = []
        
        # Find all slot cells (not just free-slots)
        all_slot_cells = row.find_all('td', class_='slot')
        
        # We need to figure out which hour each cell represents
        # The table has 15 hours (07:00-21:00), each hour split into 12 cells (5-min intervals)
        hour_start = 7  # Starts at 07:00
        cell_index = 0
        
        for cell in all_slot_cells:
            # Skip cells that are just padding
            if 'width: 0px' in cell.get('style', ''):
                continue
            
            # Determine the time based on position
            # Each hour has 12 cells (colspan="12")
            colspan = int(cell.get('colspan', '1'))
            
            # Calculate time
            total_5min_slots = cell_index
            hour = hour_start + (total_5min_slots // 12)
            minute_slot = (total_5min_slots % 12) * 5
            
            hour_from = f"{hour:02d}:{minute_slot:02d}"
            
            # Calculate end time based on colspan
            duration_5min = colspan  # Each colspan unit is 5 minutes
            end_total = total_5min_slots + duration_5min
            hour_to = hour_start + (end_total // 12)
            minute_to = (end_total % 12) * 5
            hour_to_str = f"{hour_to:02d}:{minute_to:02d}"
            
            # Determine status
            classes = cell.get('class', [])
            onclick = cell.get('onclick', '')
            price = cell.get_text(strip=True)
            
            # Extract reason from title, aria-label, or other attributes
            reason = cell.get('title', '') or cell.get('aria-label', '') or None
            if reason:
                reason = reason.strip() or None
            
            # Check if it's available
            is_available = False
            if onclick and 'book' in onclick:
                is_available = True
                # Parse actual times from onclick
                match = re.search(r"book\((\d+),'([^']+)','([^']+)'\)", onclick)
                if match:
                    time_from = match.group(2)
                    time_to = match.group(3)
                    hour_from = time_from[-4:-2] + ':' + time_from[-2:]
                    hour_to_str = time_to[-4:-2] + ':' + time_to[-2:]
            
            # Determine slot type
            if 'noDisplay' in classes:
                slot_type = 'not_offered'  # Venue not offered at this time
            elif 'free-slots' in classes:
                if is_available:
                    slot_type = 'available'
                else:
                    slot_type = 'unavailable'  # Shown but not bookable
            elif 'blocked-slot' in classes:
                slot_type = 'blocked'  # Already booked or blocked
            else:
                slot_type = 'unknown'
            
            # Only add if it's not a tiny spacing cell
            if colspan >= 12:  # At least 1 hour
                slots.append({
                    'time': f"{hour_from}-{hour_to_str}",
                    'time_from': hour_from,
                    'time_to': hour_to_str,
                    'price': price if price and price != '&nbsp;' else None,
                    'status': slot_type,
                    'is_available': is_available,
                    'reason': reason
                })
            
            cell_index += colspan
        
        return slots
    
    def get_week_availability(self, start_date: str, days: int = 7, cluster_id: int = 6) -> Dict:
        """
        Fetch availability for multiple days
        start_date: YYYYMMDD format
        days: number of days to fetch
        """
        all_days_data = []
        
        # Parse start date
        date_obj = datetime.strptime(start_date, "%Y%m%d")
        
        print(f"Fetching {days} days starting from {start_date}...")
        
        for day_offset in range(days):
            current_date = date_obj + timedelta(days=day_offset)
            date_str = current_date.strftime("%Y%m%d")
            
            day_data = self.get_day_availability(date_str, cluster_id)
            all_days_data.append(day_data)
            
            time.sleep(0.5)  # Be polite to the server
        
        return self._process_week_data(all_days_data)
    
    def _process_week_data(self, all_days_data: List[Dict]) -> Dict:
        """
        Process and organize week data for calendar view
        Structure optimized for day x time grid display
        """
        # Create a grid: day -> time -> [venues]
        calendar_grid = {}
        all_times = set()
        
        for day_data in all_days_data:
            if 'error' in day_data:
                continue
            
            date = day_data['date']
            
            # Parse date to get day name
            date_obj = datetime.strptime(date, "%Y%m%d")
            day_name = date_obj.strftime("%a %d.%m")  # e.g., "Mon 09.02"
            
            calendar_grid[date] = {
                'day_name': day_name,
                'day_of_week': date_obj.strftime("%A"),
                'date_formatted': date_obj.strftime("%d.%m.%Y"),
                'slots_by_time': defaultdict(list)
            }
            
            # Process each venue's slots
            for venue in day_data.get('venues', []):
                for slot in venue['available_slots']:
                    time_key = slot['time_from']
                    all_times.add(time_key)
                    
                    calendar_grid[date]['slots_by_time'][time_key].append({
                        'venue_id': venue['venue_id'],
                        'venue_name': venue['venue_name'],
                        'time_range': slot['time'],
                        'time_to': slot['time_to'],
                        'price': slot['price'],
                        'status': slot.get('status', 'unknown'),
                        'is_available': slot.get('is_available', False),
                        'reason': slot.get('reason', None)
                    })
        
        # Sort times
        sorted_times = sorted(all_times)
        sorted_dates = sorted(calendar_grid.keys())
        
        # Calculate statistics
        total_slots = sum(
            len(day_data.get('venues', []))
            for day_data in all_days_data
        )
        
        return {
            'calendar_grid': calendar_grid,
            'sorted_times': sorted_times,
            'sorted_dates': sorted_dates,
            'start_date': all_days_data[0]['date'] if all_days_data else None,
            'end_date': all_days_data[-1]['date'] if all_days_data else None,
            'total_days': len(all_days_data),
            'all_days_data': all_days_data
        }
    
    def save_results(self, data: Dict, filename: str = 'venue_calendar.json'):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Results saved to {filename}")


def main():
    """
    Example usage
    """
    aggregator = VenueCalendarAggregator()
    
    # Fetch a week of availability starting from a specific date
    start_date = "20260209"  # Format: YYYYMMDD (Feb 9, 2026)
    
    # Get 7 days (one week)
    results = aggregator.get_week_availability(start_date, days=7)
    
    # Save to file
    aggregator.save_results(results)
    
    # Print summary
    print("\n=== WEEKLY CALENDAR SUMMARY ===")
    print(f"Date Range: {results['start_date']} - {results['end_date']}")
    print(f"Total Days: {results['total_days']}")
    print(f"Time Slots: {len(results['sorted_times'])} unique times")
    
    print("\nAvailability by Day:")
    for date in results['sorted_dates']:
        day_info = results['calendar_grid'][date]
        total_slots = sum(len(venues) for venues in day_info['slots_by_time'].values())
        print(f"  {day_info['day_name']}: {total_slots} available slots")
    
    print("\nSample availability (first day, first 3 time slots):")
    first_date = results['sorted_dates'][0] if results['sorted_dates'] else None
    if first_date:
        day_info = results['calendar_grid'][first_date]
        for time_slot in results['sorted_times'][:3]:
            venues = day_info['slots_by_time'].get(time_slot, [])
            if venues:
                print(f"\n  {time_slot}:")
                for venue in venues[:2]:
                    price = f" - {venue['price']}" if venue['price'] else ""
                    print(f"    • {venue['venue_name']} ({venue['time_range']}){price}")
    
    print(f"\n✓ Open viewer.html to see the calendar visualization!")


if __name__ == "__main__":
    main()
