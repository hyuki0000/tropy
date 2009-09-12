function onLoad() {
  var editarea = document.getElementById('editarea');
  if (editarea) {
    editarea.focus();
  }
  document.getElementById("navi").style.visibility = "hidden";
  setTimeout("onTimeout()", 2000);
}

function onTimeout(){
  document.getElementById("navi").style.visibility = "visible";
}
