$(document).ready(function(){
    let containers = $(".for-canvas");
    containers = [].slice.call(containers);
    containers.forEach(container => {
        $(container).append(get_tour_canvas(container.id));
    });
});