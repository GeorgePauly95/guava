window = document.defaultView
Navigator = window.navigator
Geolocation = Navigator.geolocation

addEventListener("click", recordActivity)

function sendCurrentPosition(GeolocationPosition) {
  const coords = GeolocationPosition.coords;
  const timestamp = GeolocationPosition.timestamp;
  const coordsJSON = (coords.toJSON())
  const data = JSON.stringify(coordsJSON)
  const distance = document.getElementById("distance")
  distance.innerText = "DISTANCE!"
  console.log("Location Data:", data, timestamp)
  fetch("/workout", {
    "method": "POST",
    "body": data
  })
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

function createMetricScreen() {
  main = document.createElement("div")
  distance = document.createElement("div")
  console.log("distance element:", distance)
  distance.style.backgroundColor = "green"
  id = document.createAttribute("id")
  id.value = "distance"
  distance.setAttributeNode(id)
  main.appendChild(distance)

}

function recordActivity() {
  button = document.getElementById("record")
  if (button.innerText == "START") {
    createStopButton()
    createMetricScreen()
    Geolocation.watchPosition(sendCurrentPosition)
  }
  else {
    createStartButton()
    Geolocation.clearWatch()
  }
}
