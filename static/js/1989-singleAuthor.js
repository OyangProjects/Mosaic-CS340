var socket;
socket = io();
socket.on(`mosaic ${author}`, function (mosaicInfo) {
  var blob = new Blob( [ mosaicInfo.image ], { type: "image/png" } );
  var imageUrl = (window.URL || window.webkitURL).createObjectURL( blob );

  html = "";
  html += `<div class="col-2 mb-2">`;
  html += `<img src="${imageUrl}" class="img-fluid">`
  html += `<div style="font-size: 12px">`;
  html += `<b>Mosaic #${mosaicInfo.id}</b> (${mosaicInfo.tiles} tiles)<br>`;
  html += `<i>${mosaicInfo.description}<i>`;
  html += `</div>`;
  html += `</div>`;

  let e;
  if (mosaicInfo.tiles >= 0) {
    e = document.getElementById("mosaics");
  } else {
    e = document.getElementById("reduction");
  }
  e.innerHTML += html;
  /*
  if (mosaicInfo.id == 1) {
    e.innerHTML = html;
  } else {
    e.innerHTML += html;
  }
  */
});



addEventListener("DOMContentLoaded", (event) => {
  setTimeout(() => {
    fetch(`/testMosaic?author=${encodeURIComponent(author)}`)
    .then((response) => response.json())
    .then((json) => {
      if (json.error) {
        let e = document.getElementById("output");
        e.innerHTML =
          `<div class="alert alert-danger mb-3" role="alert"><h3>Mosaic Generation Error</h3>${json.error}</div>`
          + e.innerHTML;
      }
    })}, 1000
  );
});


let doSubmit = function () {
  document.getElementById("output").innerHTML = `<div id="mosaics" class="row"></div>`;

  let e = document.getElementById("image");
  let f = e.files[0];
  let tilesAcross = document.getElementById("tilesAcross").value;
  let renderedTileSize = document.getElementById("renderedTileSize").value;
  let fileFormat = document.getElementById("fileFormat").value;

  var data = new FormData();
  data.append("image", f);
  data.append("tilesAcross", tilesAcross);
  data.append("renderedTileSize", renderedTileSize);
  data.append("fileFormat", fileFormat);

  fetch("/makeMosaic", {
    method: "POST",
    body: data,
  })
  .then((response) => response.json())
  .then((json) => {
    if (json.error) {
      let e = document.getElementById("output");
      e.innerHTML =
        `<div class="alert alert-danger mb-3" role="alert"><h3>Mosaic Generation Error</h3>${json.error}</div>`
        + e.innerHTML;
    }
  });
};