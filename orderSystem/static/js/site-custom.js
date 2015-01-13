
$(document).ready(function() {

    $('#login_form').submit(function(e) {
        e.preventDefault();
        $.ajax({ // create an AJAX call...
            data: $(this).serialize(), // get the form data
            type: $(this).attr('method'), // GET or POST
            url: $(this).attr('action'), // the file to call
            success: function(response) { // on success..

                if(response.is_valid == true){
                    window.location.href = response.redirect_url;

                }else{
                    $('#error_div').html(response.data);
                    $('#error_div').fadeIn(700);
                    $('#error_div').fadeOut(15000);

                }


            },
            error: function(e, x, r) { // on error..
                alert("error");
                $('#error_div').html(e);
            }
        });
    });


});




