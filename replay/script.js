import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth/innerHeight, 0.1, 1000);
camera.position.z = 3;

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

// Screen (plane)
const screenGeom = new THREE.PlaneGeometry(2, 1.2);
const screenMat = new THREE.MeshBasicMaterial({ color: 0x2222ff, wireframe: true });
const screen = new THREE.Mesh(screenGeom, screenMat);
scene.add(screen);

// Cursor (sphere)
const cursorGeom = new THREE.SphereGeometry(0.03, 16, 16);
const cursorMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const cursor = new THREE.Mesh(cursorGeom, cursorMat);
cursor.position.z = 0.01;
scene.add(cursor);

// Overlay text
const overlay = document.getElementById('overlay');

// Load logs
let events;
fetch("logs.json").then(r => r.json()).then(data => {
  events = data.sort((a,b)=>a.timestamp-b.timestamp);
  playEvents();
});

function mapToScreen(x, y) {
  const nx = (x / 1920) * 2 - 1;   // assuming 1920x1080 screen
  const ny = -((y / 1080) * 2 - 1);
  return {x: nx, y: ny};
}

async function playEvents() {
  for (let i=0;i<events.length;i++) {
    const e = events[i];
    const n = events[i+1];
    
    if (e.type === "window_change") {
      overlay.textContent = "Fenêtre : " + e.title;
    }

    if (e.type === "mouse_click") {
      const {x, y} = mapToScreen(e.x, e.y);
      cursor.position.set(x, y, 0.01);
      // flash effect
      cursor.material.color.set(0xffff00);
      setTimeout(()=>cursor.material.color.set(0xff0000), 150);
    }

    if (e.type === "keystroke") {
      overlay.textContent = "Key: " + e.key;
    }

    // attendre le vrai timing
    const dt = (n ? n.timestamp - e.timestamp : 0.1) * 100;
    await new Promise(res=>setTimeout(res, dt));
  }
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();
