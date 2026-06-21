from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.app_settings import AppSettings
from app.models.faq import FAQ
from app.models.support_ticket import SupportTicket, ChatMessage, TicketMessage
from datetime import datetime

support_bp = Blueprint('support', __name__)


@support_bp.route('/tickets', methods=['GET'])
@jwt_required()
def get_tickets():
    try:
        user_id = get_jwt_identity()

        tickets = SupportTicket.query.filter_by(user_id=user_id) \
            .order_by(SupportTicket.created_at.desc()).all()

        return jsonify({
            'tickets': [ticket.to_dict() for ticket in tickets]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch tickets', 'error': str(e)}), 500

@support_bp.route('/tickets', methods=['POST'])
@jwt_required()
def create_ticket():
    user_id = get_jwt_identity()
    data = request.get_json()

    required_fields = ['subject', 'message', 'category']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'message': f'{field} is required'}), 400

    # Create support ticket (without message field - that goes to ticket_messages)
    ticket = SupportTicket(
        user_id=user_id,
        subject=data['subject'][:200],
        description=data['message'][:2000],  # Add this line
        category=data['category'],
        priority='medium',
        status='open'
    )
    db.session.add(ticket)
    db.session.flush()  # To get ticket.id

    # Create the first message
    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        body=data['message'][:2000]
    )
    db.session.add(message)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201

@support_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    try:
        user_id = get_jwt_identity()
        ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()

        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404

        return jsonify({
            'ticket': ticket.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch ticket', 'error': str(e)}), 500


@support_bp.route('/faq', methods=['GET'])
def get_faq():
    try:
        # Sample FAQ data - in real application, this would come from database
        faq_data = [
            {
                'question': 'How do I traSupportTicketck my bus?',
                'answer': 'Select your route from the home screen and choose a bus to see its real-time location on the map.'
            },
            {
                'question': 'What do the different bus statuses mean?',
                'answer': 'Green: On time, Yellow: Delayed, Red: Cancelled/Not operating'
            },
            {
                'question': 'How accurate is the ETA?',
                'answer': 'ETA is calculated based on current traffic conditions and may vary by a few minutes.'
            },
            {
                'question': 'Can I use the app without internet?',
                'answer': 'Basic route information is available offline, but real-time tracking requires internet connection.'
            }
        ]

        return jsonify({
            'faq': faq_data
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch FAQ', 'error': str(e)}), 500


@support_bp.route('/chat/messages', methods=['GET'])
@jwt_required()
def get_chat_messages():
    user_id = get_jwt_identity()

    messages = ChatMessage.query.filter_by(user_id=user_id) \
        .order_by(ChatMessage.created_at.asc()).all()

    return jsonify({
        'messages': [msg.to_dict() for msg in messages]
    }), 200


@support_bp.route('/chat/messages', methods=['POST'])
@jwt_required()
def send_chat_message():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data.get('body'):
        return jsonify({'message': 'Message body is required'}), 400

    message = ChatMessage(
        user_id=user_id,
        sender_role='commuter',  # Changed from 'user' to 'commuter'
        body=data['body'][:1000]
    )

    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict()), 201
@support_bp.route('/faqs', methods=['GET'])
def get_faqs():
    try:
        from app.models.faq import FAQ
        faqs = FAQ.query.order_by(FAQ.display_order).all()
        return jsonify({
            'faqs': [{
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'display_order': faq.display_order
            } for faq in faqs]
        }), 200
    except Exception as e:
        print(f"Error in get_faqs: {str(e)}")
        return jsonify({'faqs': []}), 200

@support_bp.route('/app-settings', methods=['GET'])
def get_app_settings():
    try:
        from app.models.app_settings import AppSettings
        settings = AppSettings.query.first()
        if not settings:
            return jsonify({
                'contact_phone': '+254 700 123456',
                'contact_email': 'support@sheshabus.com'
            }), 200
        return jsonify({
            'contact_phone': settings.contact_phone,
            'contact_email': settings.contact_email
        }), 200
    except Exception as e:
        print(f"Error in get_app_settings: {str(e)}")
        return jsonify({
            'contact_phone': '+254 700 123456',
            'contact_email': 'support@sheshabus.com'
        }), 200


@support_bp.route('/tickets/<int:ticket_id>/reply', methods=['POST'])
@jwt_required()
def reply_to_ticket(ticket_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    ticket = SupportTicket.query.filter_by(id=ticket_id, user_id=user_id).first()
    if not ticket:
        return jsonify({'message': 'Ticket not found'}), 404

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=user_id,
        body=data.get('message', '')[:2000]
    )

    db.session.add(message)

    # Update ticket status if it was resolved/closed
    if ticket.status in ['resolved', 'closed']:
        ticket.status = 'in_progress'
        ticket.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify(message.to_dict()), 201