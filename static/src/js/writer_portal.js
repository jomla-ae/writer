var export_writer_commission_line_ids = [];
function select_writer_commission_line(ev) {
    const writer_commission_line_id = parseInt(ev.id, 10);
    var index = export_writer_commission_line_ids.indexOf(writer_commission_line_id);



    if(ev.checked) {
        if(index == -1){
            export_writer_commission_line_ids.push(writer_commission_line_id);
        }
    } else {
        if(index != -1){
            export_writer_commission_line_ids.splice(index, 1);
        }
    }
}

function onclick_writer_commission_lines_export(){
     var xhr = new XMLHttpRequest();
     const keep_query = document.getElementById("keep_query").value
     xhr.open("POST", "/my/writer_commission_lines/export?" + keep_query);

     var data = new FormData()
     data.append("export_writer_commission_line_ids",export_writer_commission_line_ids);

     xhr.responseType = "blob";

     xhr.onload = function (e) {
         var blob = e.currentTarget.response;
         var a = document.createElement("a");
         a.href = window.URL.createObjectURL(blob);
         a.download = "commission_lines.xlsx";
         a.dispatchEvent(new MouseEvent("click"));
     }

     xhr.send(data);
}

var export_writer_target_line_ids = [];
function select_writer_target_line(ev) {
    const writer_target_line_id = parseInt(ev.id, 10);
    var index = export_writer_target_line_ids.indexOf(writer_target_line_id);



    if(ev.checked) {
        if(index == -1){
            export_writer_target_line_ids.push(writer_target_line_id);
        }
    } else {
        if(index != -1){
            export_writer_target_line_ids.splice(index, 1);
        }
    }
}

function onclick_writer_target_lines_export(){
     var xhr = new XMLHttpRequest();
     const keep_query = document.getElementById("keep_query").value
     xhr.open("POST", "/my/writer_target_lines/export?" + keep_query);

     var data = new FormData()
     data.append("export_writer_target_line_ids",export_writer_target_line_ids);

     xhr.responseType = "blob";

     xhr.onload = function (e) {
         var blob = e.currentTarget.response;
         var a = document.createElement("a");
         a.href = window.URL.createObjectURL(blob);
         a.download = "targets.xlsx";
         a.dispatchEvent(new MouseEvent("click"));
     }

     xhr.send(data);
}

if (document.readyState === "complete") {
    const tr_writer_commission_lines = document.querySelectorAll("#tr_writer_commission_line");
    if(tr_writer_commission_lines){
        for(let tr_writer_commission_line of tr_writer_commission_lines){
            tr_writer_commission_line.children[0].children[0].checked = false;
        }
    }

    const tr_writer_target_lines = document.querySelectorAll("#tr_writer_target_line");
    if(tr_writer_target_lines){
        for(let tr_writer_target_line of tr_writer_target_lines){
            tr_writer_target_line.children[0].children[0].checked = false;
        }
    }
}