function setConfig(dsn, release) {
    Raven.config(dsn, {
        'environment': 'production',
        'release': release,
        'whitelistUrls': [
            /https?:\/\/((www|ev|parceiros)\.)?congressy\.com/
        ],
        // https://gist.github.com/impressiver/5092952
        'ignoreErrors': [
            'top.GLOBALS',
            'originalCreateNotification',
            'canvas.contentDocument',
            'MyApp_RemoveAllHighlights',
            'http://tt.epicplay.com',
            'Can\'t find variable: ZiteReader',
            'jigsaw is not defined',
            'ComboSearch is not defined',
            'http://loading.retry.widdit.com/',
            'atomicFindClose',
            'fb_xd_fragment',
            'bmi_SafeAddOnload',
            'EBCallBackMessageReceived',
            'conduitPage',
            'Script error.'
        ],
        'ignoreUrls': [
            /graph\.facebook\.com/i,
            /connect\.facebook\.net\/en_US\/all\.js/i,
            /eatdifferent\.com\.woopra-ns\.com/i,
            /static\.woopra\.com\/js\/woopra\.js/i,
            /extensions\//i,
            /^chrome:\/\//i,
            /127\.0\.0\.1:4001\/isrunning/i,
            /webappstoolbarba\.texthelp\.com\//i,
            /metrics\.itunes\.apple\.com\.edgesuite\.net\//i
        ]
    }).install();
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
