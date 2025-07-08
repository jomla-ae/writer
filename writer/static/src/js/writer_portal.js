var export_writer_commission_line_ids = [];
function select_writer_commission_line(ev) {
  const writer_commission_line_id = parseInt(ev.id, 10);
  const index = export_writer_commission_line_ids.indexOf(writer_commission_line_id);

  if (index == -1) {
    if (ev.checked) {
      export_writer_commission_line_ids.push(writer_commission_line_id);
    } else {
      export_writer_commission_line_ids.splice(index, 1);
    }
  }
}

async function onclick_writer_commission_lines_export() {
  var data = new FormData();
  data.append("export_writer_commission_line_ids", export_writer_commission_line_ids);
  const keep_query = document.getElementById("keep_query").value;
  await downloadFile("/my/writer_commission_lines/export?" + keep_query, data);
}

var export_writer_target_ids = [];
function select_writer_target(ev) {
  const writer_target_id = parseInt(ev.id, 10);
  var index = export_writer_target_ids.indexOf(writer_target_id);

  if (ev.checked) {
    if (index == -1) {
      export_writer_target_ids.push(writer_target_id);
    }
  } else {
    if (index != -1) {
      export_writer_target_ids.splice(index, 1);
    }
  }
}

async function onclick_writer_targets_export() {
  var data = new FormData();
  data.append("export_writer_target_ids", export_writer_target_ids);
  const keep_query = document.getElementById("keep_query").value;
  await downloadFile("/my/writer_targets/export?" + keep_query, data);
}

if (document.readyState === "complete") {
  const tr_writer_commission_lines = document.getElementsByClassName("tr_writer_commission_line");
  if (tr_writer_commission_lines) {
    for (let tr_writer_commission_line of tr_writer_commission_lines) {
      tr_writer_commission_line.children[0].children[0].checked = false;
    }
  }

  const tr_writer_targets = document.getElementsByClassName("tr_writer_target");
  if (tr_writer_targets) {
    for (let tr_writer_target of tr_writer_targets) {
      tr_writer_target.children[0].children[0].checked = false;
    }
  }
}

async function downloadFile(url, data) {
  const response = await fetch(url, { method: "POST", body: data });
  const blob = await response.blob();
  const a = document.createElement("a");
  a.href = window.URL.createObjectURL(blob);
  a.download = response.headers.get("Content-Disposition").split("attachment; filename=")[1];
  a.click();
}
