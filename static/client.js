// use let, var, const for data that is not changing
// any variable that changes value should not be in the global scope 

var Geolocation = window.navigator.geolocation

let previous_latitude = null
let previous_longitude = null

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

// sendCurrentPosition function is doing too many things, and the name is wrong
// Break it into two parts:
// 1. get coordinate data
// 2. calculate distance (including updating previous location)
// 3. DOM update 

function sendCurrentPosition(GeolocationPosition) {
  const coords = GeolocationPosition.coords;
  const coordsJSON = (coords.toJSON())
  console.log(JSON.stringify(coordsJSON))
  current_latitude = coordsJSON["latitude"]
  current_longitude = coordsJSON["longitude"]
  if (previous_latitude == null && previous_longitude == null) {
    previous_latitude = current_latitude
    previous_longitude = current_longitude
  }

  // DONE: use getElementById since there's only one instance of speed, distance, and time.
  // read values from the DOM once, assign variables these values and use the variables. instead of reading DOM multiple times.
  distance = document.getElementById("distance")
  distance_travelled = haversineDistance(previous_latitude, previous_longitude, current_latitude, current_longitude) * 1000
  previous_latitude = current_latitude
  previous_longitude = current_longitude
  distance.innerText = Number(distance.innerText) + distance_travelled
  speed = document.getElementById("speed")
  time = document.getElementById("time")
  if (time.innerText != 0) {
    speed.innerText = distance.innerText / time.innerText
  }
}

function timeWorkout() {
  time = document.getElementById("time")
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
