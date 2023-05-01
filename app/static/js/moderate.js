/**Отметить тур как модерированный*/
function moderate(id, moder_id){
    let req = new XMLHttpRequest();
    req.open("GET",
        "/api/moderate?tid="+id+"&mid=" + moder_id,
        false);
    req.send(null);
    return req.responseText;
}