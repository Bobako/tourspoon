/**Удалить с сервера объект заданным id и типом*/
function delete_(type, id){
    let req = new XMLHttpRequest();
    req.open("GET",
        "/api/delete?t="+type+"&id=" + id,
        false);
    req.send(null);
    return req.responseText;
}