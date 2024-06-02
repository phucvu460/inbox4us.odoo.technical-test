{
    'name': 'Inbox4us Hotel Booking Management',
    'version': '1.0',
    'category': 'Hotel Management',
    'summary': 'Manage hotel room bookings and customers',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'views/hotel_booking_views.xml',
        'views/hotel_customer_views.xml',
        'views/hotel_room_views.xml',
        'views/menuitems.xml'
    ],
    'installable': True,
    'application': True,
}