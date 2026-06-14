from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def send_ticket_notification(ticket_message, request=None):
    """
    Send email notification when a new message is added to a ticket.
    Notifies the ticket creator if the message is from staff (not internal).
    Notifies staff if the message is from the client.
    """
    ticket = ticket_message.ticket
    sender = ticket_message.sender
    is_internal = ticket_message.is_internal_note

    # Don't send notifications for internal notes
    if is_internal:
        return

    # If message is from staff, notify the client
    if sender.is_staff or sender.role in ['admin', 'manager']:
        recipient = ticket.created_by
        if recipient.email and not recipient.is_staff:
            subject = _('[#%(ticket_id)d] New reply to your ticket: %(subject)s') % {
                'ticket_id': ticket.id,
                'subject': ticket.subject
            }
            context = {
                'ticket': ticket,
                'message': ticket_message,
                'recipient': recipient,
                'site_url': settings.SITE_URL,
            }
            text_content = render_to_string('emails/ticket_reply_client.txt', context)
            html_content = render_to_string('emails/ticket_reply_client.html', context)

            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_content,
                fail_silently=True,
            )

    # If message is from client, notify assigned staff or all staff
    else:
        if ticket.assigned_to:
            staff_members = [ticket.assigned_to]
        else:
            from .models import CustomUser
            staff_members = CustomUser.objects.filter(
                models.Q(is_staff=True) | models.Q(role__in=['admin', 'manager'])
            ).distinct()

        subject = _('[#%(ticket_id)d] New message from client: %(subject)s') % {
            'ticket_id': ticket.id,
            'subject': ticket.subject
        }

        for staff in staff_members:
            if staff.email:
                context = {
                    'ticket': ticket,
                    'message': ticket_message,
                    'recipient': staff,
                    'site_url': settings.SITE_URL,
                }
                text_content = render_to_string('emails/ticket_reply_staff.txt', context)
                html_content = render_to_string('emails/ticket_reply_staff.html', context)

                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[staff.email],
                    html_message=html_content,
                    fail_silently=True,
                )


def send_ticket_created_notification(ticket, request=None):
    """
    Send email notification when a new ticket is created.
    Notifies staff about new client tickets.
    """
    from .models import CustomUser
    import models

    # Notify staff
    staff_members = CustomUser.objects.filter(
        models.Q(is_staff=True) | models.Q(role__in=['admin', 'manager'])
    ).distinct()

    subject = _('[#%(ticket_id)d] New ticket created: %(subject)s') % {
        'ticket_id': ticket.id,
        'subject': ticket.subject
    }

    for staff in staff_members:
        if staff.email:
            context = {
                'ticket': ticket,
                'recipient': staff,
                'site_url': settings.SITE_URL,
            }
            text_content = render_to_string('emails/ticket_created.txt', context)
            html_content = render_to_string('emails/ticket_created.html', context)

            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[staff.email],
                html_message=html_content,
                fail_silently=True,
            )


def send_direct_message_email(user, subject, message, sender=None):
    """
    Send a direct email message to a user.
    """
    if not user.email:
        return False

    context = {
        'user': user,
        'subject': subject,
        'message': message,
        'sender': sender,
        'site_url': settings.SITE_URL,
    }

    text_content = render_to_string('emails/direct_message.txt', context)
    html_content = render_to_string('emails/direct_message.html', context)

    email_subject = _('[Baikal-Service] %(subject)s') % {'subject': subject}

    send_mail(
        subject=email_subject,
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_content,
        fail_silently=False,
    )
    return True
