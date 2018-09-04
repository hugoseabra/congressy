window.cgsy = window.cgsy || {};
window.cgsy.attendance = window.cgsy.attendance || {};

(function ($, cgsy, Instascan) {
    "use strict";

    cgsy.QRCodeScanner = function (video_el, log_el, turn_button_el) {
        video_el = $(video_el);
        log_el = $(log_el);
        turn_button_el = $(turn_button_el);
        turn_button_el.hide();

        const STATUS_NOTREADY = 'notready';
        const STATUS_IDLE = 'idle';
        const STATUS_READING = 'reading';
        const STATUS_ERROR = 'error';
        const STATUS_FOUND = 'found';

        const LOG_CLASSES = [
            STATUS_NOTREADY,
            STATUS_READING,
            STATUS_IDLE,
            STATUS_ERROR,
            STATUS_FOUND
        ];

        var started = false;
        var scanner;
        var mirror = false;
        var cameras;
        var selected_camera;

        var scan_callback = default_scan_callback;
        var active_callback = default_active_callback;
        var inactive_callback = default_inactive_callback;

        var clearLogClasses = function () {
            $.each(LOG_CLASSES, function (i, class_name) {
                log_el.removeClass(class_name);
            });
            log_el.text('');
        };

        var setErrorMessage = function (msg) {
            clearLogClasses();
            log_el.addClass(STATUS_ERROR);
            if (msg) {
                log_el.text(msg);
            }
        };

        var setNotReadyMessage = function (msg) {
            clearLogClasses();
            log_el.addClass(STATUS_NOTREADY);
            if (msg) {
                log_el.text(msg);
            }
        };

        var setIdleMessage = function (msg) {
            clearLogClasses();
            log_el.addClass(STATUS_IDLE);
            if (msg) {
                log_el.text(msg);
            }
        };

        var setReadingMessage = function (msg) {
            clearLogClasses();
            log_el.addClass(STATUS_READING);
            if (msg) {
                log_el.text(msg);
            }
        };

        var setFoundMessage = function (msg) {
            clearLogClasses();
            log_el.addClass(STATUS_FOUND);
            if (msg) {
                log_el.text(msg);
            }
        };

        var default_scan_callback = function (content) {
            setReadingMessage();
            console.log('Scan content: ' + content);
            if (content) {
                setFoundMessage();
                window.setTimeout(function () {
                    setIdleMessage();
                }, 3000);
            }
        };
        var default_active_callback = function () {
            setIdleMessage();
        };
        var default_inactive_callback = function () {
            setNotReadyMessage();
        };

        this.getCameras = function () {
            return cameras;
        };

        /**
         * Suporte a 2 câmeras comente.
         */
        this.turnCamera = function () {
            if (selected_camera === 1) {
                this.selectCamera(0);
            }

            if (selected_camera === 0) {
                this.selectCamera(1);
            }
        };

        /**
         * Suporte a 2 câmeras comente.
         */
        this.selectCamera = function (num) {
            if (scanner) {
                scanner.stop();
            }

            scanner = createScanner(mirror);
            scanner.addListener('scan', scan_callback);
            scanner.addListener('active', active_callback);
            scanner.addListener('inactive', inactive_callback);

            Instascan.Camera.getCameras().then(function (found_cams) {
                var num_cameras = found_cams.length;
                if (!num_cameras) {
                    setErrorMessage('No cameras found.');
                    console.error('No cameras found.');
                    cameras = null;
                    turn_button_el.hide();
                    return;
                }

                if (num_cameras > 1) {
                    if (typeof num === 'undefined') {
                        num = 1; // default back camera
                    }
                    turn_button_el.show();
                }

                if (num_cameras === 1) {
                    num = 0;
                    turn_button_el.hide();
                }

                cameras = found_cams;
                selected_camera = num;
                mirror = num === 1;

                console.log('Selected cam: ' + num);
                console.log('Mirror: ' + mirror);

                scanner.start(found_cams[num]);

            }).catch(function (e) {
                setErrorMessage(e);
                console.error(e);
            });
        };

        this.start = function () {
            this.selectCamera();
            started = true;
        };

        this.setScanCallback = function (callback) {

            scan_callback = function (content) {
                callback(content);
                default_scan_callback(content);
            };

            if (started) {
                scanner.addListener('scan', scan_callback);
            }
        };

        this.setActiveCallback = function (callback) {
            active_callback = function () {
                callback();
                default_active_callback();
            };

            if (started) {
                scanner.addListener('active', active_callback);
            }
        };

        this.setInactiveCallback = function (callback) {
            inactive_callback = function () {
                callback();
                default_inactive_callback();
            };

            if (started) {
                scanner.addListener('inactive', inactive_callback);
            }
        };

        var createScanner = function(mirror) {
            return new Instascan.Scanner({
                video: video_el[0],
                backgroundScan: false,
                mirror: mirror
            });
        };

        setNotReadyMessage();
    };

})(jQuery, window.cgsy, Instascan);