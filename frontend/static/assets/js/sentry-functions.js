function setConfig(dsn, release) {
    Raven.config(dsn, {
        'environment': 'production',
        'release': release
    });
}

function setUserContext(id, username, email) {
    Raven.setUserContext({
        'id': id,
        'username': username,
        'email': email
    });
}

function user_feedback_report(sentry_id, public_dsn) {
    Raven.showReportDialog({
        eventId: sentry_id,
        dsn: public_dsn
    });
}
