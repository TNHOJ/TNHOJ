jQuery(function ($) {
    $(document).on('martor:preview', function (e, $content) {
        function update_math() {
            MathJax.typesetPromise([$content[0]]).then(function () {
                $content.find('.tex-image').hide();
                $content.find('.tex-text').show();
            });
        }

        var $jax = $content.find('.require-mathjax-support');
        if ($jax.length) {
            if (!('MathJax' in window)) {
                $.ajax({
                    type: 'GET',
                    url: $jax.attr('data-config'),
                    dataType: 'script',
                    cache: true,
                    success: function () {
                        window.MathJax.startup = {typeset: false};
                        $.ajax({
                            type: 'GET',
                            url: 'https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.min.js',
                            dataType: 'script',
                            cache: true,
                            success: update_math
                        });
                    }
                });
            } else {
                update_math();
            }
        }
    })
});
