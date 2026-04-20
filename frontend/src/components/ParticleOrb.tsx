import { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface ParticleOrbProps {
  stateRef: React.MutableRefObject<{
    audioLevel: number;
    status: 'idle' | 'listening' | 'processing' | 'speaking';
  }>;
}

const ParticleOrb = ({ stateRef }: ParticleOrbProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sphereRef = useRef<THREE.Mesh | null>(null);
  const frameRef = useRef<number>(0);
  const smoothedLevel = useRef(0);

  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 3;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true
    });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create gradient sphere
    const geometry = new THREE.SphereGeometry(1, 64, 64);

    // Shader material for vertical gradient
    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
        audioLevel: { value: 0 },
      },
      vertexShader: `
        varying vec3 vPosition;
        varying vec3 vNormal;
        uniform float audioLevel;
        
        void main() {
          vPosition = position;
          vNormal = normalize(normalMatrix * normal);
          
          // Subtle pulsing based on audio
          vec3 pos = position * (1.0 + audioLevel * 0.1);
          
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 vPosition;
        varying vec3 vNormal;
        uniform float audioLevel;
        
        void main() {
          // Vertical gradient: white at top, blue at bottom
          float gradientFactor = (vPosition.y + 1.0) * 0.5;
          
          // White to cyan-blue gradient
          vec3 topColor = vec3(1.0, 1.0, 1.0);
          vec3 bottomColor = vec3(0.2, 0.6, 1.0);
          vec3 color = mix(bottomColor, topColor, gradientFactor);
          
          // Fresnel effect for glow
          float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 2.0);
          color += fresnel * vec3(0.3, 0.5, 0.8) * 0.5;
          
          // Slight brightness boost from audio
          color += audioLevel * 0.2;
          
          gl_FragColor = vec4(color, 0.95);
        }
      `,
      transparent: true,
      side: THREE.DoubleSide,
    });

    const sphere = new THREE.Mesh(geometry, material);
    scene.add(sphere);
    sphereRef.current = sphere;

    // Animation loop
    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      const time = performance.now() * 0.001;

      const targetLevel = stateRef.current.audioLevel;
      smoothedLevel.current += (targetLevel - smoothedLevel.current) * 0.2;

      const currentStatus = stateRef.current.status;

      if (sphereRef.current) {
        const mat = sphereRef.current.material as THREE.ShaderMaterial;
        mat.uniforms.time.value = time;
        mat.uniforms.audioLevel.value = smoothedLevel.current;

        // Breathing effect - fast when listening, slow otherwise
        const isListening = currentStatus === 'listening';
        const breathingSpeed = isListening ? 3.0 : 1.0;
        const breathingIntensity = isListening ? 0.12 : 0.05;
        const breathingScale = 1.0 + Math.sin(time * breathingSpeed) * breathingIntensity;
        sphereRef.current.scale.set(breathingScale, breathingScale, breathingScale);

        // Gentle rotation
        sphereRef.current.rotation.y = time * 0.1;
        sphereRef.current.rotation.x = Math.sin(time * 0.2) * 0.1;
      }

      renderer.render(scene, camera);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(frameRef.current);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden">
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-96 h-96 rounded-full blur-[80px] bg-gradient-to-b from-white via-cyan-300 to-blue-500 opacity-30 will-change-transform" />
      </div>
    </div>
  );
};

export default ParticleOrb;
