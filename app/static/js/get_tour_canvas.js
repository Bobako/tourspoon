/**Получить с сервера отрисовынные блоки тура с заданным id */
function get_tour_canvas(tour_id){
    let req = new XMLHttpRequest();
    req.open("GET",
        "/api/get_tour_canvas/"+tour_id,
        false);
    req.send(null);
    return req.responseText;
}