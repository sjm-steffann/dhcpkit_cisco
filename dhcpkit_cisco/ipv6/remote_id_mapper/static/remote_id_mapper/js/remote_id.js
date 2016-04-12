(function ($) {
    'use strict';

    $(document).ready(function () {
        $('.hex-ascii').each(function (i, elem) {
            // Attach onClick handler to the as-ascii checkbox
            $(elem).on('change', function () {
                // Find the text input next to this checkbox
                var input = $(this).siblings('input');
                var str = '';
                var i = 0;
                var code = 0;

                if (this.checked) {
                    // Want as ASCII, so old value was HEX: try to convert to ASCII
                    var hex = $.trim(input.val());
                    if (hex != '' && !hex.match(/^[0-9A-Fa-f]{2}(:?[0-9A-Fa-f]{2})*$/)) {
                        // Not valid ASCII: stop
                        alert("Remote-ID does not contain  a valid hexadecimal string, cannot convert to ASCII");
                        this.checked = false;
                        return;
                    }
                    hex = hex.replace(/:/g, '');
                    for (i = 0; i < hex.length; i += 2) {
                        // Get ord() and check if within limits
                        code = parseInt(hex.substr(i, 2), 16);
                        if (code < 32 || code > 126) {
                            // Not valid ASCII: stop
                            alert("Remote-ID contains non-ASCII codes, cannot convert to ASCII");
                            this.checked = false;
                            return;
                        }
                        str += String.fromCharCode(code);
                    }
                    input.val(str)
                } else {
                    // Want NOT as ASCII, so old value was ASCII: convert to HEX
                    var asc = $.trim(input.val());
                    for (i = 0; i < asc.length; i += 1) {
                        // Get ord() and check if within limits
                        code = asc.charCodeAt(i);
                        if (code < 32 || code > 126) {
                            // Not valid ASCII: stop
                            alert("Remote-ID contains non-ASCII characters, cannot convert to hexadecimal");
                            this.checked = true;
                            return;
                        }
                        str += code.toString(16) + ':';
                    }
                    if (str.substr(str.length - 1) == ':') {
                        str = str.substr(0, str.length - 1);
                    }
                    input.val(str)
                }
            })
        });
    });
})(django.jQuery);
