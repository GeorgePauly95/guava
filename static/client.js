// use let, var, const for data that is not changing
// any variable that changes value should not be in the global scope 
// DONE: Break it into two parts. sendCurrentPosition function is doing too many things, and the name is wrong:
// DONE: 1. get coordinate data
// DONE: 2. calculate distance (including updating previous location)
// DONE: 3. DOM update 
// DONE: use getElementById since there's only one instance of speed, distance, and time.
// DO LATER: (not clear how this reduces work) read values from the DOM once, assign variables these values and use the variables. instead of reading DOM multiple times.

var Geolocation = window.navigator.geolocation
const button = document.getElementById("record")


button.addEventListener("click", trackWorkout())


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
  const stop = document.getElementById("record")
  stop.style.backgroundColor = "red"
  stop.innerText = "STOP"
}


function createStartButton() {
  const start = document.getElementById("record")
  start.style.backgroundColor = "green"
  start.innerText = "START"
}

function updateMetricsScreen(distance_moved) {
  const distance = document.getElementById("distance")
  const speed = document.getElementById("speed")
  const time = document.getElementById("time")
  distance.innerText = Number(distance.innerText) + distance_moved
  if (time.innerText != 0) {
    speed.innerText = distance.innerText / time.innerText
  }
}


function trackWorkout() {

  let time_id
  let id
  let previous_latitude = null
  let previous_longitude = null

  function getCurrentPosition(GeolocationPosition) {
    let coords = GeolocationPosition.coords;
    let coordsJSON = (coords.toJSON())
    console.log(JSON.stringify(coordsJSON))
    let current_latitude = coordsJSON["latitude"]
    let current_longitude = coordsJSON["longitude"]
    return { "current_latitude": current_latitude, "current_longitude": current_longitude }
  }


  function calculateDistanceMoved(current_position) {
    let current_latitude = current_position["current_latitude"]
    let current_longitude = current_position["current_longitude"]

    if (previous_latitude == null && previous_longitude == null) {
      previous_latitude = current_latitude
      previous_longitude = current_longitude
    }

    distance_moved = haversineDistance(previous_latitude, previous_longitude, current_latitude, current_longitude) * 1000

    previous_latitude = current_latitude
    previous_longitude = current_longitude

    return distance_moved
  }


  function trackPosition(GeolocationPosition) {
    let current_position = getCurrentPosition(GeolocationPosition)
    let distance_moved = calculateDistanceMoved(current_position)
    updateMetricsScreen(distance_moved)
  }


  function timeWorkout() {
    const time = document.getElementById("time")
    time.innerText = Number(time.innerText) + 1
  }


  function startWorkout() {
    createStopButton()
    time_id = setInterval(timeWorkout, 1000)
    console.log("time_id in startActivity", time_id)
    id = Geolocation.watchPosition(trackPosition)
  }


  function stopWorkout() {
    createStartButton()
    console.log("time_id in stopActivity", time_id)
    clearInterval(time_id)
    Geolocation.clearWatch(id)
  }


  function recordWorkout() {
    const button = document.getElementById("record")

    if (button.innerText == "START") {
      startWorkout()
    }

    else {
      stopWorkout()
    }
  }

  return recordWorkout
}
