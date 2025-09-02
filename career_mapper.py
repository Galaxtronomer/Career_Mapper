import webbrowser
import os

html_code = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Career Map Editor with End Arrows</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet-rotatedmarker/leaflet.rotatedMarker.js"></script>

<style>
  body { margin:0; }
  #map { width:100%; height:100vh; }
  #menu {
    position: fixed; top:10px; right:10px; z-index:1000;
    background-color:white; padding:10px; border-radius:5px;
    box-shadow:0 0 5px gray; font-family:sans-serif;
    max-width:220px;
  }
  #menu b { display:block; margin-top:5px; }
  #menu button, #menu select, #menu input { display:block; margin:3px 0; width: 200px; }
  .custom-text { white-space: nowrap; font-weight:bold; background:none; }
</style>
</head>
<body>

<div id="menu">
  <button id="toggleMenuBtn">Hide/Show Menu</button>

  <b>Location Drop</b>
  <button id="addDropBtn">Add</button>
  <select id="dropList"><option value="">Select Drop</option></select>
  <button id="removeDropBtn">Remove</button>

  <b>Text</b>
  <input type="text" id="textInput" placeholder="Text content"/>
  <label>Font Size: <input type="number" id="fontSizeInput" value="14" min="8" max="72"/></label>
  <label>Font Color: <input type="color" id="fontColorInput" value="#000000"/></label>
  <button id="addTextBtn">Add</button>
  <select id="textList"><option value="">Select Text</option></select>
  <button id="removeTextBtn">Remove</button>
  <button id="rotateTextBtn">Rotate</button>

  <b>Curve</b>
  <label>Curve Color: <input type="color" id="curveColorInput" value="#ff0000"/></label>
  <button id="addCurveBtn">Add</button>
  <select id="curveList"><option value="">Select Curve</option></select>
  <button id="removeCurveBtn">Remove</button>
  <button id="modifyCurveBtn">Modify</button>
  <button id="exitModifyCurveBtn">Exit Modify</button>
</div>

<div id="map"></div>

<script>
var map = L.map('map').setView([20,0],2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{ attribution:'© OpenStreetMap contributors | Credit: Ankit Kumar @ UNAB' }).addTo(map);

var drops = [];
var texts = [];
var curves = [];

// --- Toggle Menu ---
document.getElementById('toggleMenuBtn').onclick = function() {
    var menu = document.getElementById('menu');
    for(let i=1;i<menu.children.length;i++){
        menu.children[i].style.display = menu.children[i].style.display === 'none' ? 'block' : 'none';
    }
};

// --- Location Drop ---
function updateDropList(){
    var sel = document.getElementById('dropList');
    sel.innerHTML = '<option value="">Select Drop</option>';
    drops.forEach((d,i)=>{ sel.innerHTML += '<option value="'+i+'">Drop '+i+'</option>'; });
}
document.getElementById('addDropBtn').onclick = function(){
    alert("Click on map to place drop");
    var clickHandler = function(e){
        var marker = L.marker(e.latlng,{draggable:true}).addTo(map);
        drops.push(marker);
        updateDropList();
        map.off('click',clickHandler);
    };
    map.on('click',clickHandler);
};
document.getElementById('removeDropBtn').onclick = function(){
    var idx = document.getElementById('dropList').value;
    if(idx!=""){ map.removeLayer(drops[idx]); drops.splice(idx,1); updateDropList(); }
};

// --- Text ---
function updateTextList(){
    var sel = document.getElementById('textList');
    sel.innerHTML = '<option value="">Select Text</option>';
    texts.forEach((t,i)=>{ sel.innerHTML += '<option value="'+i+'">Text '+i+'</option>'; });
}
document.getElementById('addTextBtn').onclick = function(){
    var txt = document.getElementById('textInput').value;
    if(!txt) return alert("Enter text");
    var latlng = map.getCenter();
    var size = document.getElementById('fontSizeInput').value;
    var color = document.getElementById('fontColorInput').value;
    var t = L.marker(latlng,{ 
        icon:L.divIcon({className:'custom-text',html:txt,iconAnchor:[0,0], 
        style: 'font-size:'+size+'px; color:'+color}),
        draggable:true, rotationAngle:0, rotationOrigin: 'center'
    }).addTo(map);
    t.setRotation = function(angle){ t.options.rotationAngle = angle; t._icon.style.transform = 'rotate('+angle+'deg)'; };
    texts.push(t);
    updateTextList();
};
document.getElementById('removeTextBtn').onclick = function(){
    var idx = document.getElementById('textList').value;
    if(idx!=""){ map.removeLayer(texts[idx]); texts.splice(idx,1); updateTextList(); }
};
document.getElementById('rotateTextBtn').onclick = function(){
    var idx = document.getElementById('textList').value;
    if(idx==="") return;
    var angle = prompt("Enter rotation in degrees:",0);
    if(angle!==null){ texts[idx].setRotation(parseFloat(angle)); }
};

// --- Dynamic text update ---
document.getElementById('textList').onchange = function() {
    var idx = this.value;
    if(idx === "") return;
    var t = texts[idx];
    document.getElementById('textInput').value = t._icon.innerHTML;
    var style = t._icon.style;
    document.getElementById('fontSizeInput').value = parseInt(style.fontSize);
    document.getElementById('fontColorInput').value = rgbToHex(style.color);
};
function rgbToHex(rgb) {
    if(!rgb) return "#000000";
    var result = /^rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)$/.exec(rgb);
    if(!result) return rgb;
    return "#" + [1,2,3].map(i => parseInt(result[i]).toString(16).padStart(2,'0')).join('');
}
document.getElementById('textInput').oninput = updateSelectedText;
document.getElementById('fontSizeInput').oninput = updateSelectedText;
document.getElementById('fontColorInput').oninput = updateSelectedText;
function updateSelectedText() {
    var idx = document.getElementById('textList').value;
    if(idx === "") return;
    var t = texts[idx];
    var txt = document.getElementById('textInput').value;
    var size = document.getElementById('fontSizeInput').value;
    var color = document.getElementById('fontColorInput').value;
    t._icon.innerHTML = txt;
    t._icon.style.fontSize = size + "px";
    t._icon.style.color = color;
}

// --- Curve functions ---
function drawCurve(curve){
    var start = curve.start, end = curve.end, control = curve.control;
    var points = [];
    for(var t=0; t<=1; t+=0.02){
        var lat = (1-t)*(1-t)*start[0] + 2*(1-t)*t*control[0] + t*t*end[0];
        var lng = (1-t)*(1-t)*start[1] + 2*(1-t)*t*control[1] + t*t*end[1];
        points.push([lat, lng]);
    }

    if(curve.poly) map.removeLayer(curve.poly);
    if(curve.arrow) map.removeLayer(curve.arrow);

    curve.poly = L.polyline(points, {color: curve.color, weight: 3}).addTo(map);

    // Arrow at the end of the curve
    var p0 = points[points.length - 2];
    var p1 = points[points.length - 1];
    var angle = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) * 180 / Math.PI;

    var arrowIcon = L.divIcon({
    className: '',
    html: `<div style="width:0; height:0;border-left:6px solid transparent;border-right:6px solid transparent;
    border-bottom:12px solid ${curve.color};transform:rotate(${angle}deg);transform-origin:center;"></div>`
    });

    curve.arrow = L.marker([p1[0], p1[1]], {icon: arrowIcon}).addTo(map);
}

function updateCurveList(){
    var sel=document.getElementById('curveList');
    sel.innerHTML='<option value="">Select Curve</option>';
    curves.forEach((c,i)=>{ sel.innerHTML+='<option value="'+i+'">Curve '+i+'</option>'; });
}

document.getElementById('addCurveBtn').onclick=function(){
    alert("Click start point, then end point.");
    var points=[];
    var color = document.getElementById('curveColorInput').value;
    function clickHandler(e){
        points.push([e.latlng.lat,e.latlng.lng]);
        if(points.length===2){
            map.off('click',clickHandler);
            var control=[(points[0][0]+points[1][0])/2+5,(points[0][1]+points[1][1])/2+5];
            var curve={start:points[0],end:points[1],control:control,poly:null,arrow:null,startMarker:null,endMarker:null,controlMarker:null,color:color};
            drawCurve(curve);
            curves.push(curve);
            updateCurveList();
        }
    }
    map.on('click',clickHandler);
};

document.getElementById('removeCurveBtn').onclick=function(){
    var idx=document.getElementById('curveList').value;
    if(idx==="") return;
    var curve=curves[idx];
    if(curve.poly) map.removeLayer(curve.poly);
    if(curve.arrow) map.removeLayer(curve.arrow);
    if(curve.startMarker) map.removeLayer(curve.startMarker);
    if(curve.endMarker) map.removeLayer(curve.endMarker);
    if(curve.controlMarker) map.removeLayer(curve.controlMarker);
    curves.splice(idx,1);
    updateCurveList();
};

document.getElementById('modifyCurveBtn').onclick=function(){
    var idx=document.getElementById('curveList').value;
    if(idx==="") return;
    var curve=curves[idx];
    if(curve.startMarker) return;

    var startMarker=L.marker(curve.start,{draggable:true}).addTo(map);
    var endMarker=L.marker(curve.end,{draggable:true}).addTo(map);
    var controlMarker=L.marker(curve.control,{draggable:true}).addTo(map);

    curve.startMarker=startMarker;
    curve.endMarker=endMarker;
    curve.controlMarker=controlMarker;

    function update(){
        curve.start=[startMarker.getLatLng().lat,startMarker.getLatLng().lng];
        curve.end=[endMarker.getLatLng().lat,endMarker.getLatLng().lng];
        curve.control=[controlMarker.getLatLng().lat,controlMarker.getLatLng().lng];
        curve.color = document.getElementById('curveColorInput').value; 
        drawCurve(curve);
    }
    startMarker.on('drag',update);
    endMarker.on('drag',update);
    controlMarker.on('drag',update);
};

document.getElementById('exitModifyCurveBtn').onclick=function(){
    var idx=document.getElementById('curveList').value;
    if(idx==="") return;
    var curve=curves[idx];
    if(curve.startMarker){ map.removeLayer(curve.startMarker); curve.startMarker=null; }
    if(curve.endMarker){ map.removeLayer(curve.endMarker); curve.endMarker=null; }
    if(curve.controlMarker){ map.removeLayer(curve.controlMarker); curve.controlMarker=null; }
};
</script>
</body>
</html>
"""

filename = "career_map.html"
with open(filename,"w",encoding="utf-8") as f:
    f.write(html_code)

webbrowser.open('file://' + os.path.realpath(filename))
