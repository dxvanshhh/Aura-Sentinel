// --- 3D Background Animation ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({canvas: document.querySelector('#bg'), alpha: true});
renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.z = 5;

// Create 3D glowing torus (cyber vibe)
const geometry = new THREE.TorusGeometry(1.2, 0.4, 16, 100);
const material = new THREE.MeshStandardMaterial({color: 0x00ffaa, wireframe: true});
const torus = new THREE.Mesh(geometry, material);
scene.add(torus);

// Lighting
const pointLight = new THREE.PointLight(0x00e5ff, 2);
pointLight.position.set(5,5,5);
scene.add(pointLight);

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  torus.rotation.x += 0.01;
  torus.rotation.y += 0.005;
  renderer.render(scene, camera);
}
animate();

// Resize handling
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// --- Login Toggle Logic ---
const loginBtn = document.getElementById('loginBtn');
const mainContent = document.getElementById('main-content');
const loginBox = document.getElementById('loginBox');

loginBtn.addEventListener('click', () => {
  mainContent.style.display = 'none';
  loginBox.classList.add('active');
});
