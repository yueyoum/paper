$(function(){
    var post_width = $('.post-content').width();
    $('img').each(function(index){
        if($(this).width() > post_width){
            $(this).css('width', post_width);
            $(this).wrap(
                $('<a href="' + $(this).attr('src') + '" target="_blank">')
            );
        }
    });
});