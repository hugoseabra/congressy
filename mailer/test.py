import django

django.setup()

from django.core.mail import send_mail

send_mail(
    subject='Hello from SparkPost',
    message='Woo hoo! Sent from Django!',
    from_email='mail@congressy.net',
    recipient_list=['hugoseabra19@gmail.com'],
    html_message='<p>Hello Rock stars!</p>'
)
