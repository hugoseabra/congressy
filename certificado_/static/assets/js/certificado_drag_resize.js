window.cert = window.cert || {};
(function (window, $) {
    window.cert.moveElement = function(element, x, y) {
        element = $(element);

        // translate the element
        var translate = 'translate(' + x + 'px, ' + y + 'px)';
        element.css('webkitTransform', translate);
        element.css('transform', translate);

        // update the posiion attributes
        element.attr('data-x', x);
        element.attr('data-y', y);
    };

    function dragMoveListener (event) {
        var target = event.target,
            // keep the dragged position in the data-x/data-y attributes
            x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
            y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

        cert.moveElement($(target), x, y)
        if(target.id === 'text'){
            cert.saveTextPosition(x,y);

        }
        else if (target.id === 'titleText'){
            cert.saveTitlePosition(x,y);
        }
        else if (target.id === 'dateText'){
            cert.saveDatePosition(x,y);
        }
    }

    // this is used later in the resizing and gesture demos
    window.dragMoveListener = dragMoveListener;

    interact('.drag')
        .draggable({
            onmove: window.dragMoveListener,
            restrict: {
                restriction: 'parent',
                elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
            }
        });
    interact('.resize-drag')
        .draggable({
            onmove: window.dragMoveListener,
            restrict: {
                restriction: 'parent',
                elementRect: { top: 0, left: 0, bottom: 1, right: 1 },
            }
        })
        .resizable({
            // resize from all edges and corners
            edges: { left: true, right: true, bottom: true, top: true },

            // keep the edges inside the parent
            restrictEdges: {
                outer: 'parent',
                endOnly: true
            },
            // minimum size
            restrictSize: {
                min: { width: 50, height: 50 }
            },

            inertia: true
        })
        .on('resizemove', function (event) {
            var target = event.target,
                x = (parseFloat(target.getAttribute('data-x')) || 0),
                y = (parseFloat(target.getAttribute('data-y')) || 0);

            // update the element's style
            target.style.width  = event.rect.width + 'px';
            target.style.height = event.rect.height + 'px';

            // translate when resizing from top or left edges
            x += event.deltaRect.left;
            y += event.deltaRect.top;

            target.style.webkitTransform = target.style.transform =
                'translate(' + x + 'px,' + y + 'px)';

            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
            cert.saveTextSize(target.style.height, target.style.width);


        });
})(window, jQuery);