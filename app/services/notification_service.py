from app import db
from app.models.alert import Alert, UserNotification
from app.models.user import User
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_user_notification(user_id, title, message, alert_id=None):
        """
        Create a notification for a specific user
        """
        notification = UserNotification(
            user_id=user_id,
            alert_id=alert_id,
            title=title,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def send_alert_to_users(alert):
        """
        Send alert to targeted users.
        Now uses alert.route_id (instead of target_route_id) and alert.body (instead of message).
        send_to_all is removed; targeting is based on presence of route_id or bus_id.
        """
        users = []

        # Targeting logic (send_to_all removed)
        if alert.route_id:
            # Send to users who favorited this route
            from app.models.user import UserFavorite
            favorite_users = UserFavorite.query.filter_by(route_id=alert.route_id).all()
            users = [fav.user for fav in favorite_users if fav.user.is_verified]
        elif alert.bus_id:
            # Optional: send to users who favorited this bus (if you have a similar table)
            # For now, fallback to all verified users
            users = User.query.filter_by(is_verified=True).all()
        else:
            # No specific target → send to all verified users
            users = User.query.filter_by(is_verified=True).all()

        notifications_created = 0
        for user in users:
            NotificationService.create_user_notification(
                user_id=user.id,
                title=alert.title,
                message=alert.body,           # changed from alert.message
                alert_id=alert.id
            )
            notifications_created += 1

        # Mark alert as sent
        alert.is_sent = True
        alert.sent_at = datetime.utcnow()
        db.session.commit()

        return notifications_created

    @staticmethod
    def get_unread_notifications_count(user_id):
        """
        Get count of unread notifications for a user
        """
        return UserNotification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_notification_as_read(notification_id, user_id):
        """
        Mark a notification as read
        """
        notification = UserNotification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_notifications_as_read(user_id):
        """
        Mark all notifications as read for a user
        """
        UserNotification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
        return True