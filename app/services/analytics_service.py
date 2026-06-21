from app import db
from app.models.bus import Bus, BusLocation
from app.models.route import Route
from app.models.driver import Driver          # new import
from app.models.support_ticket import SupportTicket
from app.models.survey import SurveyResponse
from datetime import datetime, timedelta
from sqlalchemy import func, extract


class AnalyticsService:
    @staticmethod
    def get_system_overview():
        """
        Get system overview statistics
        """
        total_routes = Route.query.filter_by(is_active=True).count()
        active_buses = Bus.query.filter_by(status='active').count()
        # fixed: count drivers from the drivers table
        total_drivers = Driver.query.count()
        open_tickets = SupportTicket.query.filter_by(status='open').count()

        # Get buses with recent locations (online in last 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        online_buses = BusLocation.query.filter(
            BusLocation.timestamp >= five_minutes_ago
        ).distinct(BusLocation.bus_id).count()

        return {
            'total_routes': total_routes,
            'active_buses': active_buses,
            'online_buses': online_buses,
            'total_drivers': total_drivers,
            'open_tickets': open_tickets
        }

    @staticmethod
    def get_route_performance(route_id=None):
        """
        Get route performance analytics
        """
        # This would integrate with real tracking data
        # For now, return mock data
        return {
            'on_time_performance': 85.5,
            'average_delay_minutes': 3.2,
            'passenger_satisfaction': 4.2,
            'utilization_rate': 78.1
        }

    @staticmethod
    def get_survey_analytics(survey_id):
        """
        Get analytics for a specific survey
        """
        responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()

        if not responses:
            return {}

        total_responses = len(responses)
        ratings = [resp.rating for resp in responses if resp.rating]
        average_rating = sum(ratings) / len(ratings) if ratings else 0

        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for rating in ratings:
            if 1 <= rating <= 5:
                rating_distribution[rating] += 1

        return {
            'total_responses': total_responses,
            'average_rating': round(average_rating, 1),
            'rating_distribution': rating_distribution,
            'comments_count': len([r for r in responses if r.comment])
        }