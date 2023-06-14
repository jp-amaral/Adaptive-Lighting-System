import React, { useState, useEffect } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './Home.css'
import L from 'leaflet'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Toggle from 'react-toggle'
import "react-toggle/style.css" // for ES6 modules

const CustomToast = ({ content, description }) => (
  <div>
    <div>{content}</div>
    <h5>{description}</h5>
  </div>
);

function Home() {

  const [obuData, setObuData] = useState({})
  // const [speed, setSpeed] = useState(0)
  const [lampData, setLampData] = useState({})
  const [rsuRanges, setRsuRanges] = useState({})
  const [showHighwayInfo, setShowHighwayInfo] = useState(true)

  const circleRadius = 100; // meters
  const circleColor = 'green';
  // const rsuCircleRadius = 150;
  // const rsuCircleColor = 'green';
  const circleOpacity = 0.08;

  useEffect(() => {
    const interval = setInterval(() => {
      async function fetchCarPos() {
        const res = await fetch('http://localhost:5000/api/v1/obu')
        const data = await res.json()
        setObuData(data)
      }
      fetchCarPos()
    }, 100)
    return () => clearInterval(interval)
  }, [])
  
  useEffect(() => {
    const interval = setInterval(() => {
      async function fetchLampData() {
        const res = await fetch('http://localhost:5000/api/v1/rsu_data')
        const data = await res.json()
        setLampData(data)
        // console.log(data)
      }
      fetchLampData()
    }, 100)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let newRsuRanges = {...rsuRanges};
    Object.keys(lampData).forEach((key) => {
      const in_range = lampData[key].in_range
      let prev_in_range = false
      if (!(key in rsuRanges)) {
        prev_in_range = false
      } else {
        prev_in_range = rsuRanges[key]
      }
      if (prev_in_range === false && in_range === true) {
        let rsu_alerted = Object.keys(lampData[key].target_posts)
        let rsu_alerted_str = rsu_alerted.join(', ')
        const highway_keys = ['19', '22', '25', '28']
        console.log(highway_keys.includes(key))
        if (showHighwayInfo || !highway_keys.includes(key)) {
          notify(`RSU ${key} is in range`, `Alerting lamp posts: ${rsu_alerted_str}`);
        }
      } 
      newRsuRanges[key] = in_range;
    })
  
    setRsuRanges(newRsuRanges);
  }, [lampData])

  const notify = (content, description) => {
    toast(<CustomToast content={content} description={description} />, {
      position: "top-right",
      autoClose: 20000,
      hideProgressBar: true,
      closeOnClick: false,
      pauseOnHover: true,
      draggable: false,
    });
  };

  const handleToggle = () => {
    setShowHighwayInfo(!showHighwayInfo)
  }



  const carIcon = new L.Icon({
    iconUrl: require('../assets/car.png'),
    iconSize: new L.Point(50, 50),
    className: 'car-icon'
  })

  const lampIcons = {
    0: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    1: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    2: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    3: new L.Icon({ 
      iconUrl: require('../assets/post_30.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    4: new L.Icon({
      iconUrl: require('../assets/post_40.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    5: new L.Icon({
      iconUrl: require('../assets/post_50.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    6: new L.Icon({
      iconUrl: require('../assets/post_60.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    7: new L.Icon({
      iconUrl: require('../assets/post_70.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    8: new L.Icon({
      iconUrl: require('../assets/post_80.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    9: new L.Icon({
      iconUrl: require('../assets/post_90.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    10: new L.Icon({
      iconUrl: require('../assets/post_100.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon',
    }),
  }

  const rsuIcons = {
    0: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    1: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    2: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    3: new L.Icon({
      iconUrl: require('../assets/rsu_30.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    4: new L.Icon({
      iconUrl: require('../assets/rsu_40.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    5: new L.Icon({
      iconUrl: require('../assets/rsu_50.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    6: new L.Icon({
      iconUrl: require('../assets/rsu_60.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    7: new L.Icon({
      iconUrl: require('../assets/rsu_70.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    8: new L.Icon({
      iconUrl: require('../assets/rsu_80.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    9: new L.Icon({
      iconUrl: require('../assets/rsu_90.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    10: new L.Icon({
      iconUrl: require('../assets/rsu_100.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
  }

  function getIconFromIntensity(intensity, isRsu) {
    if (isRsu) {
      if (intensity === 0) {
        return rsuIcons[0]
      }
      else if (intensity > 0 && intensity <= 10) {
        return rsuIcons[1]
      }
      else if (intensity > 10 && intensity <= 20) {
        return rsuIcons[2]
      }
      else if (intensity > 20 && intensity <= 30) {
        return rsuIcons[3]
      }
      else if (intensity > 30 && intensity <= 40) {
        return rsuIcons[4]
      }
      else if (intensity > 40 && intensity <= 50) {
        return rsuIcons[5]
      }
      else if (intensity > 50 && intensity <= 60) {
        return rsuIcons[6]
      }
      else if (intensity > 60 && intensity <= 70) {
        return rsuIcons[7]
      }
      else if (intensity > 70 && intensity <= 80) {
        return rsuIcons[8]
      }
      else if (intensity > 80 && intensity <= 90) {
        return rsuIcons[9]
      }
      else if (intensity > 90 && intensity <= 100) {
        return rsuIcons[10]
      }
    } else {
      if (intensity === 0) {
        return lampIcons[0]
      }
      else if (intensity > 0 && intensity <= 10) {
        return lampIcons[1]
      }
      else if (intensity > 10 && intensity <= 20) {
        return lampIcons[2]
      }
      else if (intensity > 20 && intensity <= 30) {
        return lampIcons[3]
      }
      else if (intensity > 30 && intensity <= 40) {
        return lampIcons[4]
      }
      else if (intensity > 40 && intensity <= 50) {
        return lampIcons[5]
      }
      else if (intensity > 50 && intensity <= 60) {
        return lampIcons[6]
      }
      else if (intensity > 60 && intensity <= 70) {
        return lampIcons[7]
      }
      else if (intensity > 70 && intensity <= 80) {
        return lampIcons[8]
      }
      else if (intensity > 80 && intensity <= 90) {
        return lampIcons[9]
      }
      else if (intensity > 90 && intensity <= 100) {
        return lampIcons[10]
      }
    }

  }
  return (
    <div className='container'>
      <label className="toggle">
        <Toggle
          defaultChecked={showHighwayInfo}
          onChange={handleToggle} />
        <span style={{marginLeft:'10px'}}>Show Highway Notifications</span>
      </label>
      <div className="map-container" >  
        <MapContainer 
          center={[40.637003, -8.648004]} 
          zoom={17.5} 
          style={{ height: "100%", width: "100%"}}
          scrollWheelZoom={false}
          // zoomControl={false}
        >
          <TileLayer
          maxZoom={23}
            url="https://api.mapbox.com/styles/v1/jp-amaral/cl758vsmy000714o2rx0w0779/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianAtYW1hcmFsIiwiYSI6ImNsNzU4c3g1MzExMHozbm1hdWlvbnRrbmoifQ.SpZQvOQyQCwhNZluPGPXQg"
          />
          {/* <Marker position={carPos} icon={carIcon}>
            <Popup>
              Speed: {speed} km/h
            </Popup>
          </Marker> */}
          {/* <Circle
            center={carPos}
            radius={circleRadius}
            color={circleColor}
            fillOpacity={circleOpacity}
          /> */}
          {Object.keys(obuData).map((key, index) => (
            <div>
              <Marker key={index} position={[obuData[key].latitude, obuData[key].longitude]} icon={carIcon}>
                <Popup>
                  Speed: {obuData[key].speed} km/h
                  ID: {key}
                </Popup>
              </Marker>
              <Circle
              center={[obuData[key].latitude, obuData[key].longitude]}
              radius={circleRadius}
              color={circleColor}
              fillOpacity={circleOpacity}
            />
            </div>
          ))} 
          {Object.keys(lampData).map((key, index) => (
            <div>
              <Marker key={index} position={[lampData[key].lat + 0.00005, lampData[key].lon+0.00002]} icon={getIconFromIntensity(lampData[key].intensity, lampData[key].rsu)}>
                <Popup>
                  <b>Smart Lamp</b><br/>
                  <b>Id:</b> {key}<br/>
                  <b>Intensity:</b> {lampData[key].intensity}<br/>
                  {lampData[key].rsu && (<div><b>In Range:</b> {lampData[key].in_range ? 'Yes' : 'No'}<br/></div>)}
                  {/* <b>Ordering RSU ID:</b> {lampData[key].ordering_rsu_id}<br/> */}
                </Popup>
              </Marker>
              {/* <Circle
              center={[lampData[key].lat + 0.00005, lampData[key].lon+0.00002]}
              radius={rsuCircleRadius}
              color={rsuCircleColor}
              fillOpacity={circleOpacity}
            /> */}
            </div>
          ))}
        </MapContainer>
      </div>  
      <div className="sidebar">
        {/* <button onClick={() => notify('Hello there')}>Hello Notification</button> */}
        {/* <button onClick={() => notify('Welcome back')}>Welcome Notification</button> */}
        <ToastContainer newestOnTop />
      </div>
    </div>
  )
}

export default Home