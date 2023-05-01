/**Данный класс описывает положение прямоугольника в поле путеводителя, куда могут быть добавлены элементы путеводителя.
 * Положение описывается строкой и столбцом (start_row & start_column), в которых находится верхняя левая ячейка, входящая в прямоугольник,
 * а также строкой и столбцом правой нижней ячейки (end_row & end_column), которая не включана в прямоугольник, но касается его своим левым верхним углом.
 * Таким образом, эти атрибуты класса могут быть использованы для установки параметров css блока для его корректного отображения в родителе с {display:grid}
 * следующим образом: {grid-area: start_row / start_column / end_row / end_column}
 * Кроме того, на основе этих атрибутов вычисляется высота и ширина блока для последующего сохранения в БД.
 * 
 * @constructor
 * @param id - если этот аргумент задан, экземпляр класса установит свои атрибуты в соотвествии с положением и размерами уже существуещего блока, идентификатор которого был получен
 * @param start_row - верхняя строка прямоугольника
 * @param start_column - левый столбец прямоугольника
 * @param end_row - нижняя строка прямоугольника (если не была задана, экземпляр будет построен как одна ячейка, заданая start_row и start_column)
 * @param end_column - правый столбец прямоугольник
 * 
 *  */ 
class Position{
    constructor(id, start_row, start_column, end_row, end_column){
        if (id){ // создать по айди блока
            this.start_row = parseInt($("*[name='" + id + ":row']").val());
            this.start_column = parseInt($("*[name='" + id + ":column']").val());
            this.width = parseInt($("*[name='" + id + ":width']").val());
            this.height = parseInt($("*[name='" + id + ":height']").val());
            this.end_column = this.start_column + this.width;
            this.end_row = this.start_row + this.height;
        }
        else if (!end_row){ // создать по одной ячейке
            this.start_row = parseInt(start_row);
            this.start_column = parseInt(start_column);
            this.end_row = this.start_row + 1;
            this.end_column = this.start_column + 1;
            this.calc_size();
        }
        else{ // создать по двум ячейкам
            this.start_row = parseInt(start_row);
            this.start_column = parseInt(start_column);
            this.end_row = parseInt(end_row);
            this.end_column = parseInt(end_column);
            this.calc_size();
        }        
    }

    /**
     * Посчитать ширину и высоту
     */
    calc_size(){
        this.width = this.end_column - this.start_column;
        this.height = this.end_row - this.start_row;
    }

    /**
     * Изменить размер (ширину и высоту) на заданный, при этом верхний левый угол сохраняет свое положение в таблице, а нижний правый перемещается.
     */
    set_size(width, height){
        this.width = parseInt(width);
        this.height = parseInt(height);
        this.end_column = this.start_column + this.width;
        this.end_row = this.start_row + this.height;
    }


    /**
     * Задать эту позицую html элементу
     */
    set_to(element){  
        $(element).css("grid-area", this.start_row+"/"+this.start_column+"/"+this.end_row+"/"+this.end_column);
    }

    /**
     * Задать эту позицую html элементу с указанным идентификатором, а также обновить скрытые поля в нем, чтобы при отправке формы на сервер позиция была сохранена
     * в атрибутах models.TourBlock 
     */
    update_form(id){
        $("*[name='" + id + ":row']").val(this.start_row);
        $("*[name='" + id + ":column']").val(this.start_column);
        $("*[name='" + id + ":width']").val(this.width);
        $("*[name='" + id + ":height']").val(this.height);
        this.set_to($("#"+id));
        
    }

    /**
     * Изменить размер, если правая граница прямоугольника вылезла за пределы таблицы.
     */
    fix_out_of_bounds(){
        if (this.end_column > 5){
            this.end_column = 5;
            this.calc_size();
        }
    }
    
}
/**
 * Определяет, в какой ячейке таблицы находится курсор.
 * 
 * @param event событие, содержащее данные о положении курсора
 * @returns экземпляр Position, описывающий данную ячейку
 */
function define_grid_position(event){
    let grid = document.getElementsByClassName("canvas")[0];
    let grid_rect = grid.getBoundingClientRect();
    let left = event.pageX - grid_rect.left;
    let top = event.pageY - grid_rect.top;
    const gridComputedStyle = window.getComputedStyle(grid);
    const gridRowCount = gridComputedStyle.getPropertyValue("grid-template-rows").split(" ").length;
    const gridColumnCount = 4;
    let px_per_col = grid_rect.width / gridColumnCount;
    let px_per_row = grid_rect.height / gridRowCount;
    let position = new Position(null, Math.ceil(top / px_per_row), Math.ceil(left / px_per_col));
    return position;

}
/**
 * Отрисовывает в таблице призрак блока с заданной позицией.
 * 
 * @param position 
 */
function project_ghost(position){ 
    let ghost = `<div class='ghost'></div>`;
    $(".canvas").append(ghost);
    position.set_to($(".ghost"));

}

/**
 * Определяет, есть ли поле путеводителя под курсором
 * 
 * @param event  событие, содержащее данные о положении курсора
 * @returns boolean есть ли поле путеводителя под курсором 
 */
function is_canvas_below(event){  
    let canvas_below = false;
    let below = document.elementsFromPoint(event.pageX, event.pageY);
        below.forEach(el => {
            if (el.classList.contains('canvas')){
                canvas_below = true;
            }
        });
    return canvas_below;
}

/**
 * Идентификатор выбранного блока
 */
let selected_block_id = null;

/**
 * Перетянуть блок из левого сайдбара
 * 
 * @param e событие нажатия кнопки мыши по блоку 
 * @param block блок, который перетягивается
 */
function drag_stable_block(e, block){  
    let dragable = $(block).clone()[0];
    dragable.style.width = block.offsetWidth + "px";
    drag_n_drop(e, dragable, block);
}


/**
 * Визуально обозначить блок с переданным идентификатором как отмеченный, сохранить идентификатор в selected_block_id
 * 
 * @param id идентификатор блока для выбора
 */
function mark_selected(id){ 
    let selector = "#" + selected_block_id;
    if (selector != "#"){
        $('#'+selected_block_id).css("border", "none");
    }
    selector = "#"+id;
    if (selector != "#"){
        selected_block_id = id;
        $(selector).css("border", "blue 2px solid");
        update_fields();
    }
}


/**
 * Перетянуть блок
 * 
 * @param e событие нажатия кнопки мыши по блоку 
 * @param dragable перетягиваемы блок
 * @param origin необязательный; задается, если блок перетягивается из левого сайдбара
 */
function drag_n_drop(e, dragable, origin=null){ 
    mark_selected(dragable.id);    
    if (e.button!=0){
        return;
    }
    if (!origin){
        dragable = dragable.parentElement;
        var coords = getCoords(dragable);
        dragable.style.width = dragable.offsetWidth + "px";
        dragable.style.height = dragable.offsetHeight+ "px";
    }
    else{
        var coords = getCoords(origin);
    }
    
    var shiftX = e.pageX - coords.left;
    var shiftY = e.pageY - coords.top;

    dragable.style.position = 'absolute';
    document.body.appendChild(dragable);
    moveAt(e);

    dragable.style.zIndex = 1000;
    
    function moveAt(e){
        dragable.style.left = e.pageX - shiftX + 'px';
        dragable.style.top = e.pageY - shiftY + 'px';
    }
    
    document.onmousemove = function(e) {
        moveAt(e);
        $(".ghost").remove();

        let position = define_grid_position(e);
        if (!origin){
            let dragable_position = new Position(dragable.id);
            position.set_size(dragable_position.width, dragable_position.height);
        }
        position.fix_out_of_bounds();
        if (is_canvas_below(e)) project_ghost(position);
    };

    document.onmouseup = function(e){
        if (is_canvas_below(e)){
            let position = define_grid_position(e);
            if (origin){
                $(dragable).remove();
                let id=insert_block(position);
                mark_selected(id);
            }
            else{
                let dragable_position = new Position(dragable.id);
                position.set_size(dragable_position.width, dragable_position.height);

                $(dragable).css("position", "static");
                $(".canvas").append(dragable);
                position.fix_out_of_bounds();
                position.update_form(dragable.id);
                mark_selected(dragable.id);
            }
        } 
        else{
            if (origin) $(dragable).remove();
            else {
                $(dragable).css("position", "static");
                $(".canvas").append(dragable);
            }
        }
        document.onmousemove = null;
        document.onmouseup = null;
        $(".ghost").remove();
        
    };

    function getCoords(elem) {
        var box = elem.getBoundingClientRect();
        return {
          top: box.top + pageYOffset,
          left: box.left + pageXOffset
        };

    }
}
/**
 * Изменить размер блока
 * 
 * @param event событие нажатия кнопки мыши по области изменения размера блока 
 */
function resize(event){
    let block = event.target;
    if (block.id == '')return;
    $(block).css("width", "");
    $(block).css("height", "");
    mark_selected(block.id);
    let rect = block.getBoundingClientRect();
    if (rect.right - 15 > event.pageX && event.pageX> rect.left + 15 && rect.bottom - 15 > event.pageY && event.pageY > rect.top + 15)return;    
    let new_position = new Position(block.id);
    document.onmousemove = function(e){
        $(".ghost").remove();
        new_position = new Position(block.id);
        let position = define_grid_position(e);
        if (e.pageX < rect.left) new_position.start_column = position.start_column;
        else new_position.end_column = position.end_column;
        if (e.pageY < rect.top) new_position.start_row = position.start_row;
        else new_position.end_row = position.end_row;
        new_position.fix_out_of_bounds();
        project_ghost(new_position);
    }

    document.onmouseup = function(e){
        if (is_canvas_below(e)){
            new_position.calc_size();
            new_position.update_form(block.id);
        }
        document.onmousemove = null;
        document.onmouseup = null;
        mark_selected(block.id);
        $(".ghost").remove();
    }

}
/**
 * вставить в таблицу новый блок в заданную ячейку
 * 
 * @param position Позиция для вставки
 * @param type тип блока
 * @returns 
 */
function insert_block(position, type=0){ 
    let new_block_id = document.getElementsByClassName("block").length;
    let block = `<div class="block" id="`+new_block_id+`"
                    onmousedown=resize(event);>
                    <div onmousedown="drag_n_drop(event, this)"> 
                    <h3 class="preview_name"></h3>
                    <p class="preview_text"></p>                 
                    </div>
                    <input hidden name="`+new_block_id+`:name">
                    <input hidden name="`+new_block_id+`:text">
                    <input type='file' hidden name="`+new_block_id+`:content_path">
                    <input hidden name="`+new_block_id+`:type_" value=`+type+`>
                    <input type='checkbox' hidden name="`+new_block_id+`:show_on_map">
                    <input hidden name="`+new_block_id+`:latitude" value=0>
                    <input hidden name="`+new_block_id+`:longitude" value=0>
                    <input hidden name="`+new_block_id+`:width" value=1>
                    <input hidden name="`+new_block_id+`:column">
                    <input hidden name="`+new_block_id+`:row">
                    <input hidden name="`+new_block_id+`:height" value=1>
                    <input hidden name="`+new_block_id+`:tour_id">
                </div>`;
    $(".canvas").append(block);
    position.update_form(new_block_id);
    return new_block_id;
}

/**
 * обновить доступ к полям properties (правый сайдбар) при выборе блока. Например, если выбран блок тип текст, поле для загрузки файла будет отключено.
 * 
 */
function update_fields_permissions(){ 
    let type = $("*[name='"+selected_block_id+":type_']").val();
    $(".properties>*").attr('disabled', true);
    $("#show_on_map").attr("disabled", false);
    $("#type_").attr("disabled", false);
    if (type == 0){
        $("#name").attr("disabled", false);
        $("#text").attr("disabled", false);        
    }
    else if (type == 1 || type == 3 || type ==4){
        $("#content_path").attr("disabled", false); 
    }
    else if (type ==2){
        $("#text").attr("disabled", false);
    }
    else if (type == 6){
        $("#name").attr("disabled", false);
        $("#text").attr("disabled", false);  
    }
    else if (type == 5){
        $("#show_on_map").attr("disabled", true);
    }
    else {
        $("#show_on_map").attr("disabled", true);
        return;
    }
}

/**
 * обновить поля properties (правый сайдбар), установив туда значения полей выбранного блока
 * 
 */
function update_fields(){
    update_fields_permissions();
    let block = document.getElementById(selected_block_id);
    let inputs = block.getElementsByTagName("input");
    inputs = [].slice.call(inputs); // преобразовать в нормальный массив
    inputs.forEach(input => {
        let name =$(input).attr("name");
        name = name.split(":")[1];
        if (name!='content_path'){
            $("#"+name).val($(input).val());
        }
        else{
            $("#content_path").prop("files", $(input).prop("files"));
        }
        if ($(input).attr("type") == "checkbox"){
            $("#"+name).prop("checked", $(input).prop("checked"));
            if ($(input).prop("checked")){
                $("#latitude").attr('disabled', false);
                $("#longitude").attr('disabled', false);
            }
        }
    });
}

/**
 * Обновить предмостр медиа блока
 * 
 * @param file_field поле для загрузки файла 
 */
function update_media_preview(file_field){
    let block = $("#"+selected_block_id);
    let type = $("*[name='"+selected_block_id+":type_']").val();
    $(block).find(".media-preview").remove();
    const [file] = file_field.files;
    if (!file)return;
    let media = null;
    if (type == 1) media = "<img class=media-preview>";
    else if (type == 3) media = "<video controls class=media-preview>Video preview</video>";
    else if (type == 4) media = "<audio controls='controls' class=media-preview>Audio preview</audio>"
    if (media){
    $(block).find("div").append(media);
        media = $(block).find(".media-preview");
        $(media).attr("src", URL.createObjectURL(file));
    }
}



/**
 * сбросить значение полей блока при изменении типа
 */
function clear_fields(){
    let block = document.getElementById(selected_block_id);
    let inputs = block.getElementsByTagName("input");
    inputs = [].slice.call(inputs); // преобразовать в нормальный массив
    inputs.forEach(input => {
        let name =$(input).attr("name");
        name = name.split(":")[1];
        if (["name", "text"].includes(name)){
            $(input).val('');
            $("#"+name).val('');    
        }
        else if (name == "content_path"){
            $(input).prop('files', null);
            $(input).val('');
            $("#content_path").prop('files', null);
            $("#content_path").val('');
        }
    
    });
    $(block).find(".preview_name").text('');
    $(block).find(".preview_text").text('');
    $(block).find(".media-preview").remove();
    
}

/**
 * обновить информацию в форме блока, когда меняется информация в правом сайдбаре
 * @param  event cобытие изменения поля формы properties (правый сайдбар)
 */
function update_block(event){
    let changed = event.target;
    let block = $("#"+selected_block_id);
    if (changed.id != "content_path") $(`*[name="`+selected_block_id+ ":" + changed.id +`"]`).val(changed.value);
    if (changed.id == "type_"){
        clear_fields();
        update_fields();
    }
    if (changed.id == "show_on_map"){
        $("#latitude").attr('disabled', !changed.checked);
        $("#longitude").attr('disabled', !changed.checked);
        $(`*[name="`+selected_block_id+ ":" + changed.id +`"]`).attr("checked", changed.checked);
    }
    if (changed.id == "name") $(block).find(".preview_name").text(changed.value);
    if (changed.id == "text") $(block).find(".preview_text").text(changed.value);
    if (changed.id == "content_path"){
        update_media_preview(changed);
        $(`*[name="`+selected_block_id+ ":" + changed.id +`"]`).prop("files", $(changed).prop("files"));
        console.log($(`*[name="`+selected_block_id+ ":" + changed.id +`"]`).prop("files"));  
    } 
}

$(document).ready(function(){ // установить ивент хэндлеры для правого сайдбара
    let input = document.getElementById("name");
    input.addEventListener('input', update_block);
    input.addEventListener('propertychange', update_block);

    input = document.getElementById("type_");
    input.addEventListener("change", update_block);

    input = document.getElementById("text");
    input.addEventListener('input', update_block);
    input.addEventListener('propertychange', update_block);

    input = document.getElementById("content_path");
    input.addEventListener("change", update_block);

    input = document.getElementById("show_on_map");
    input.addEventListener("change", update_block);
    
    input = document.getElementById("latitude");
    input.addEventListener('input', update_block);
    input.addEventListener('propertychange', update_block);

    input = document.getElementById("longitude");
    input.addEventListener('input', update_block);
    input.addEventListener('propertychange', update_block);
    $(".properties>*").attr("disabled", true);


});