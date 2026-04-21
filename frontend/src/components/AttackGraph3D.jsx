import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Billboard } from '@react-three/drei';
import * as THREE from 'three';

// ============ Graph Node ============
function GraphNode({ node, isActive, isShieldBurst, defenseMode }) {
  const meshRef = useRef();
  const glowRef = useRef();
  const burstRef = useRef();
  const timeRef = useRef(0);

  const typeColors = {
    source: '#00f0ff',
    defense: '#7b61ff',
    target: '#ff9f0a',
    resource: '#3b82f6',
    sink: '#30d158',
  };

  const color = isActive ? '#ff2d55' : typeColors[node.type] || '#00f0ff';
  const position = [node.x * 1.5 - 6, node.y * 1.5, node.z * 1.5];

  useFrame((state, delta) => {
    timeRef.current += delta;
    if (meshRef.current) {
      const pulseSpeed = defenseMode === 'lockdown' ? 4 : defenseMode === 'elevated' ? 3 : 2;
      const pulseAmt = defenseMode === 'lockdown' ? 0.1 : 0.05;
      meshRef.current.scale.setScalar(1 + Math.sin(timeRef.current * pulseSpeed) * pulseAmt);
    }
    if (glowRef.current) {
      glowRef.current.material.opacity = 0.15 + Math.sin(timeRef.current * 3) * 0.08;
    }
    if (burstRef.current && isShieldBurst) {
      burstRef.current.scale.setScalar(burstRef.current.scale.x + delta * 4);
      burstRef.current.material.opacity = Math.max(0, burstRef.current.material.opacity - delta * 1.5);
      if (burstRef.current.material.opacity <= 0) {
        burstRef.current.scale.setScalar(0.1);
        burstRef.current.material.opacity = 0.8;
      }
    }
  });

  return (
    <group position={position}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.25, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isActive ? 1.5 : defenseMode === 'lockdown' ? 0.6 : 0.4}
          roughness={0.3}
          metalness={0.7}
        />
      </mesh>

      <mesh ref={glowRef}>
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshBasicMaterial color={color} transparent opacity={0.15} side={THREE.BackSide} />
      </mesh>

      {isShieldBurst && (
        <mesh ref={burstRef} scale={0.1}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshBasicMaterial
            color={defenseMode === 'lockdown' ? '#ff2d55' : '#00f0ff'}
            transparent opacity={0.8} side={THREE.BackSide} wireframe
          />
        </mesh>
      )}

      <Billboard position={[0, 0.5, 0]}>
        <Text
          fontSize={0.16}
          color={isActive ? '#ff2d55' : '#8e8e9a'}
          anchorX="center"
          anchorY="bottom"
          font={undefined}
        >
          {node.label}
        </Text>
      </Billboard>
    </group>
  );
}

// ============ Graph Edge ============
function GraphEdge({ sourcePos, targetPos, isActive, defenseMode }) {
  const particlesRef = useRef();
  const timeRef = useRef(Math.random() * 100);

  const particleCount = 8;
  const particlePositions = useMemo(() => new Float32Array(particleCount * 3), []);
  const particleColors = useMemo(() => {
    const colors = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      if (isActive) {
        colors[i * 3] = 1; colors[i * 3 + 1] = 0.18; colors[i * 3 + 2] = 0.33;
      } else {
        colors[i * 3] = 0; colors[i * 3 + 1] = 0.94; colors[i * 3 + 2] = 1;
      }
    }
    return colors;
  }, [isActive]);

  useFrame((state, delta) => {
    const speed = isActive ? 3 : defenseMode === 'lockdown' ? 0.2 : defenseMode === 'elevated' ? 0.35 : 0.5;
    timeRef.current += delta * speed;
    if (particlesRef.current) {
      const start = new THREE.Vector3(...sourcePos);
      const end = new THREE.Vector3(...targetPos);
      for (let i = 0; i < particleCount; i++) {
        const t = ((timeRef.current * 0.3 + i / particleCount) % 1);
        const pos = start.clone().lerp(end, t);
        particlePositions[i * 3] = pos.x;
        particlePositions[i * 3 + 1] = pos.y + Math.sin(t * Math.PI) * 0.1;
        particlePositions[i * 3 + 2] = pos.z;
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <group>
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position" count={2}
            array={new Float32Array([...sourcePos, ...targetPos])} itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={isActive ? '#ff2d55' : defenseMode === 'lockdown' ? '#1a0a10' : '#1a1a2e'}
          transparent opacity={isActive ? 0.8 : 0.3}
        />
      </line>

      <points ref={particlesRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" count={particleCount} array={particlePositions} itemSize={3} />
          <bufferAttribute attach="attributes-color" count={particleCount} array={particleColors} itemSize={3} />
        </bufferGeometry>
        <pointsMaterial
          size={isActive ? 0.08 : 0.04}
          vertexColors transparent
          opacity={isActive ? 0.9 : defenseMode === 'lockdown' ? 0.2 : 0.4}
          sizeAttenuation
        />
      </points>
    </group>
  );
}

// ============ Background Particles ============
function BackgroundParticles({ defenseMode }) {
  const particlesRef = useRef();
  const count = 150;

  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 30;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      const speed = defenseMode === 'lockdown' ? 0.005 : 0.02;
      particlesRef.current.rotation.y = state.clock.elapsedTime * speed;
    }
  });

  const particleColor = defenseMode === 'lockdown' ? '#ff2d55' : defenseMode === 'elevated' ? '#ff9f0a' : '#00f0ff';

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.03} color={particleColor} transparent opacity={0.15} sizeAttenuation />
    </points>
  );
}

// ============ Main Scene ============
function Scene({ graphData, activeNodes, activeEdges, shieldBurst, defenseMode }) {
  const nodePositions = useMemo(() => {
    const map = {};
    graphData.nodes.forEach(n => {
      map[n.id] = [n.x * 1.5 - 6, n.y * 1.5, n.z * 1.5];
    });
    return map;
  }, [graphData.nodes]);

  const autoRotateSpeed = defenseMode === 'lockdown' ? 0.05 : defenseMode === 'elevated' ? 0.2 : 0.3;

  return (
    <>
      <ambientLight intensity={defenseMode === 'lockdown' ? 0.2 : 0.3} />
      <pointLight position={[10, 10, 10]} intensity={0.8}
        color={defenseMode === 'lockdown' ? '#ff2d55' : defenseMode === 'elevated' ? '#ff9f0a' : '#00f0ff'} />
      <pointLight position={[-10, -5, -10]} intensity={0.4} color="#7b61ff" />

      <BackgroundParticles defenseMode={defenseMode} />
      <gridHelper args={[30, 30, '#0d1117', '#0d1117']} position={[0, -3, 0]} />

      {graphData.edges.map((edge, i) => {
        const edgeId = `${edge.source}-${edge.target}`;
        return (
          <GraphEdge key={i}
            sourcePos={nodePositions[edge.source]}
            targetPos={nodePositions[edge.target]}
            isActive={activeEdges.includes(edgeId)}
            defenseMode={defenseMode}
          />
        );
      })}

      {graphData.nodes.map(node => (
        <GraphNode key={node.id}
          node={node}
          isActive={activeNodes.includes(node.id)}
          isShieldBurst={shieldBurst === node.id}
          defenseMode={defenseMode}
        />
      ))}

      <OrbitControls
        autoRotate autoRotateSpeed={autoRotateSpeed}
        enableDamping dampingFactor={0.05}
        maxDistance={20} minDistance={5}
      />
    </>
  );
}

// ============ Export ============
export default function AttackGraph3D({ graphData, activeNodes, activeEdges, shieldBurst, defenseMode }) {
  return (
    <Canvas
      camera={{ position: [0, 4, 12], fov: 55 }}
      style={{ width: '100%', height: '100%' }}
      gl={{ antialias: true, alpha: true }}
    >
      <Scene
        graphData={graphData}
        activeNodes={activeNodes}
        activeEdges={activeEdges}
        shieldBurst={shieldBurst}
        defenseMode={defenseMode || 'normal'}
      />
    </Canvas>
  );
}
