var Geolocation = window.navigator.geolocation

const button = document.getElementById("record")

button.addEventListener("click", recordWorkout)

function recordWorkout() {
  const trackPosition = positionTrackerFactory()
  const { startWorkout, stopWorkout } = workoutTrackerFactory(trackPosition)
  const button = document.getElementById("record")

  if (button.innerText == "START") {
    startWorkout()
  }

  else {
    stopWorkout()
  }
}

function positionTrackerFactory() {

  let previous_latitude = null
  let previous_longitude = null


  function calculateDistanceMoved(current_position) {
    let current_latitude = current_position["current_latitude"]
    let current_longitude = current_position["current_longitude"]

    if (previous_latitude == null && previous_longitude == null) {
      previous_latitude = current_latitude
      previous_longitude = current_longitude
      return 0
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

  return trackPosition
}


function getCurrentPosition(GeolocationPosition) {
  let coords = GeolocationPosition.coords;
  let coordsJSON = (coords.toJSON())
  let current_latitude = coordsJSON["latitude"]
  let current_longitude = coordsJSON["longitude"]
  console.log(JSON.stringify(coordsJSON))
  return { "current_latitude": current_latitude, "current_longitude": current_longitude }
}



function updateMetricsScreen(distance_moved) {
  const distance = document.getElementById("distance")
  const speed = document.getElementById("speed")
  const time = document.getElementById("time")
  distance.innerText = Number(distance.innerText) + distance_moved
  var workout_time = time.innerText
  if (workout_time != 0) {
    speed.innerText = distance.innerText / workout_time
  }
}


function workoutTrackerFactory(trackPosition) {
  let time_id
  let id

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

  return { startWorkout, stopWorkout }
}


function timeWorkout() {
  const time = document.getElementById("time")
  time.innerText = Number(time.innerText) + 1
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
