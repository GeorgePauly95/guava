window = document.defaultView
Navigator = window.navigator
Geolocation = Navigator.geolocation

button = document.getElementById("record")

button.addEventListener("click", recordActivity)

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c; // km
}

function sendCurrentPosition(GeolocationPosition) {
  const coords = GeolocationPosition.coords;
  const coordsJSON = (coords.toJSON())
  current_latitude = coordsJSON["latitude"]
  current_longitude = coordsJSON["longitude"]
  const data = JSON.stringify(coordsJSON)
  metric_screen = document.getElementById("screen")
  metric_screen.innerText = Number(metric_screen.innerText) + 1
  console.log(data)
  fetch("/workout", {
    "method": "POST",
    "body": data
  })
}


function styleMetricScreen(metric_screen) {
  metric_screen.style.backgroundColor = "orange"
  metric_screen.style.height = "200px"
  metric_screen.style.width = "400px"
}

function assignMetricScreenId(metric_screen) {
  id = document.createAttribute("id")
  id.value = "screen"
  metric_screen.setAttributeNode(id)
}


function createMetricScreen(distance) {
  metric_screen = document.createElement("div")
  metric_screen.innerText = distance
  styleMetricScreen(metric_screen)
  assignMetricScreenId(metric_screen)
  document.body.appendChild(metric_screen)
}


function createStopButton() {
  stop = document.getElementById("record")
  stop.style.backgroundColor = "red"
  stop.innerText = "STOP"
}

function createStartButton() {
  start = document.getElementById("record")
  start.style.backgroundColor = "green"
  start.innerText = "START"
}

function startActivity() {
  var distance = 0
  createStopButton()
  createMetricScreen(distance)
  id = Geolocation.watchPosition(sendCurrentPosition)
}

function stopActivity() {
  createStartButton()
  Geolocation.clearWatch(id)
}

function recordActivity() {
  button = document.getElementById("record")
  if (button.innerText == "START") {
    startActivity()
  }
  else {
    stopActivity()
  }
}
