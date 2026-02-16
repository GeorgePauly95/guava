window = document.defaultView
Navigator = window.navigator
Geolocation = Navigator.geolocation

let previous_latitude = null
let previous_longitude = null
let distance = 0

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

function sendCurrentPosition(GeolocationPosition) {
  const coords = GeolocationPosition.coords;
  const coordsJSON = (coords.toJSON())
  current_latitude = coordsJSON["latitude"]
  current_longitude = coordsJSON["longitude"]
  distance_screen = document.getElementsByClassName("distance")
  if (previous_latitude == null && previous_longitude == null) {
    previous_latitude = current_latitude
    previous_longitude = current_longitude
  }
  distance_travelled = haversineDistance(previous_latitude, previous_longitude, current_latitude, current_longitude)
  distance += distance_travelled
  distance_screen.innerText = distance
}

function timeWorkout() {
  time = document.getElementsByClassName("time")[0]
  time.innerText = Number(time.innerText) + 1
}

function startActivity() {
  createStopButton()
  time_id = setInterval(timeWorkout, 1000)

  id = Geolocation.watchPosition(sendCurrentPosition)
}

function stopActivity() {
  createStartButton()
  clearInterval(time_id)
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
