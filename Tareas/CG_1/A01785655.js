/*
Nicolas Quintana Kluchnik
A01785655
Date: November 14th, 2024
Transformaciones 2D - WebGL
*/

'use strict';

// Esperar a que todo esté cargado
window.addEventListener('load', function() {
    console.log('=== INICIANDO APLICACIÓN ===');
    
    // Verificar dependencias
    if (typeof M3 === 'undefined') {
        alert('ERROR: 2d-lib.js no se cargó. Asegúrate de que el archivo existe y está antes de A01785655.js');
        return;
    }
    
    if (typeof lil === 'undefined') {
        alert('ERROR: lil-gui no se cargó. Verifica la conexión a internet o cambia el CDN.');
        return;
    }
    
    console.log('Dependencias verificadas ✓');
    
    //   SHADERS  
    
    const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform mat3 u_transforms;

out vec4 v_color;

void main() {
    vec3 transformedPos = u_transforms * vec3(a_position, 1.0);
    gl_Position = vec4(transformedPos.xy, 0.0, 1.0);
    v_color = a_color;
}
`;

    const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;
out vec4 outColor;

void main() {
    outColor = v_color;
}
`;

    //   INICIALIZACIÓN WEBGL  
    
    const canvas = document.querySelector('canvas');
    if (!canvas) {
        alert('ERROR: No se encontró el canvas');
        return;
    }
    
    const gl = canvas.getContext('webgl2');
    if (!gl) {
        alert('WebGL 2 no está disponible en tu navegador');
        return;
    }
    
    console.log('WebGL 2 inicializado ✓');
    
    // Ajustar tamaño del canvas
    canvas.width = 800;
    canvas.height = 600;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0.95, 0.95, 0.95, 1.0);
    
    // Compilar shader
    function compileShader(type, source) {
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Error compilando shader:', gl.getShaderInfoLog(shader));
            alert('Error compilando shader: ' + gl.getShaderInfoLog(shader));
            return null;
        }
        return shader;
    }
    
    // Crear programa
    const vertexShader = compileShader(gl.VERTEX_SHADER, vsGLSL);
    const fragmentShader = compileShader(gl.FRAGMENT_SHADER, fsGLSL);
    
    const prg = gl.createProgram();
    gl.attachShader(prg, vertexShader);
    gl.attachShader(prg, fragmentShader);
    gl.linkProgram(prg);
    
    if (!gl.getProgramParameter(prg, gl.LINK_STATUS)) {
        console.error('Error enlazando programa:', gl.getProgramInfoLog(prg));
        alert('Error enlazando programa');
        return;
    }
    
    gl.detachShader(prg, vertexShader);
    gl.deleteShader(vertexShader);
    gl.detachShader(prg, fragmentShader);
    gl.deleteShader(fragmentShader);
    
    console.log('Programa de shaders creado ✓');
    
    // Obtener ubicaciones
    const positionLoc = gl.getAttribLocation(prg, 'a_position');
    const colorLoc = gl.getAttribLocation(prg, 'a_color');
    const transformsLoc = gl.getUniformLocation(prg, 'u_transforms');
    
    //   GEOMETRÍA  
    
    function createCircleVertices(cx, cy, radius, segments, r, g, b, a) {
        const positions = [];
        const colors = [];
        
        for (let i = 0; i < segments; i++) {
            const angle1 = (i / segments) * Math.PI * 2;
            const angle2 = ((i + 1) / segments) * Math.PI * 2;
            
            const x1 = cx + Math.cos(angle1) * radius;
            const y1 = cy + Math.sin(angle1) * radius;
            const x2 = cx + Math.cos(angle2) * radius;
            const y2 = cy + Math.sin(angle2) * radius;
            
            positions.push(cx, cy, x1, y1, x2, y2);
            
            for (let j = 0; j < 3; j++) {
                colors.push(r, g, b, a);
            }
        }
        
        return { positions, colors };
    }
    
    // OBJETO 1: Pivote
    const pivotData = {
        a_position: {
            numComponents: 2,
            data: new Float32Array([
                0, 0.03, -0.03, 0, 0, -0.03,
                0, 0.03, 0, -0.03, 0.03, 0,
                0, 0.03, 0.03, 0, 0, 0.03,
                0, 0.03, 0, 0.03, -0.03, 0,
            ])
        },
        a_color: {
            numComponents: 4,
            data: new Uint8Array([
                100, 100, 100, 255, 100, 100, 100, 255, 100, 100, 100, 255,
                100, 100, 100, 255, 100, 100, 100, 255, 100, 100, 100, 255,
                100, 100, 100, 255, 100, 100, 100, 255, 100, 100, 100, 255,
                100, 100, 100, 255, 100, 100, 100, 255, 100, 100, 100, 255,
            ])
        }
    };
    
    // OBJETO 2: Cara
    function createFaceData() {
        const positions = [];
        const colors = [];
        
        // Cara amarilla
        const face = createCircleVertices(0, 0, 0.4, 30, 255, 255, 0, 255);
        positions.push(...face.positions);
        colors.push(...face.colors);
        
        // Ojo izquierdo
        positions.push(-0.15, 0.15, -0.2, 0.05, -0.1, 0.05);
        colors.push(0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255);
        
        // Ojo derecho
        positions.push(0.15, 0.15, 0.1, 0.05, 0.2, 0.05);
        colors.push(0, 0, 0, 255, 0, 0, 0, 255, 0, 0, 0, 255);
        
        // Sonrisa
        const mouthSegments = 10;
        const mouthRadius = 0.25;
        const mouthWidth = 0.05;
        
        for (let i = 0; i < mouthSegments; i++) {
            const angle1 = Math.PI + (i / mouthSegments) * Math.PI;
            const angle2 = Math.PI + ((i + 1) / mouthSegments) * Math.PI;
            
            const x1 = Math.cos(angle1) * mouthRadius;
            const y1 = Math.sin(angle1) * mouthRadius * 0.6 - 0.05;
            const x2 = Math.cos(angle2) * mouthRadius;
            const y2 = Math.sin(angle2) * mouthRadius * 0.6 - 0.05;
            
            const x1b = Math.cos(angle1) * (mouthRadius - mouthWidth);
            const y1b = Math.sin(angle1) * (mouthRadius - mouthWidth) * 0.6 - 0.05;
            const x2b = Math.cos(angle2) * (mouthRadius - mouthWidth);
            const y2b = Math.sin(angle2) * (mouthRadius - mouthWidth) * 0.6 - 0.05;
            
            positions.push(x1, y1, x2, y2, x1b, y1b);
            positions.push(x2, y2, x2b, y2b, x1b, y1b);
            
            for (let j = 0; j < 6; j++) {
                colors.push(0, 0, 0, 255);
            }
        }
        
        return {
            a_position: {
                numComponents: 2,
                data: new Float32Array(positions)
            },
            a_color: {
                numComponents: 4,
                data: new Uint8Array(colors)
            }
        };
    }
    
    const faceData = createFaceData();
    console.log('Geometría creada ✓');
    
    //   VAO  
    
    function createVAO(data) {
        const vao = gl.createVertexArray();
        gl.bindVertexArray(vao);
        
        const posBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, data.a_position.data, gl.STATIC_DRAW);
        gl.enableVertexAttribArray(positionLoc);
        gl.vertexAttribPointer(positionLoc, data.a_position.numComponents, gl.FLOAT, false, 0, 0);
        
        const colorBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, data.a_color.data, gl.STATIC_DRAW);
        gl.enableVertexAttribArray(colorLoc);
        gl.vertexAttribPointer(colorLoc, data.a_color.numComponents, gl.UNSIGNED_BYTE, true, 0, 0);
        
        gl.bindVertexArray(null);
        
        return { 
            vao, 
            vertexCount: data.a_position.data.length / data.a_position.numComponents 
        };
    }
    
    const pivotVAO = createVAO(pivotData);
    const faceVAO = createVAO(faceData);
    
    console.log('VAOs creados - Pivot:', pivotVAO.vertexCount, 'Face:', faceVAO.vertexCount);
    
    //   ESTADO  
    
    const state = {
        pivot: { 
            x: -0.3, 
            y: 0, 
            scale: { x: 1, y: 1 } 
        },
        face: { 
            translation: { x: 0.3, y: 0 }, 
            rotation: 0, 
            scale: { x: 1, y: 1 } 
        }
    };
    
    //   UI  
    
    const gui = new lil.GUI();
    
    const pivotFolder = gui.addFolder('Pivote');
    pivotFolder.add(state.pivot, 'x', -1, 1, 0.01).name('Traslación X');
    pivotFolder.add(state.pivot, 'y', -1, 1, 0.01).name('Traslación Y');
    pivotFolder.add(state.pivot.scale, 'x', 0.1, 3, 0.01).name('Escala X');
    pivotFolder.add(state.pivot.scale, 'y', 0.1, 3, 0.01).name('Escala Y');
    pivotFolder.open();
    
    const faceFolder = gui.addFolder('Cara (Smiley)');
    faceFolder.add(state.face.translation, 'x', -1, 1, 0.01).name('Traslación X');
    faceFolder.add(state.face.translation, 'y', -1, 1, 0.01).name('Traslación Y');
    faceFolder.add(state.face.scale, 'x', 0.1, 3, 0.01).name('Escala X');
    faceFolder.add(state.face.scale, 'y', 0.1, 3, 0.01).name('Escala Y');
    faceFolder.add(state.face, 'rotation', 0, Math.PI * 2, 0.01).name('Rotación (rad)');
    faceFolder.open();
    
    console.log('GUI configurado ✓');
    
    //   RENDERIZADO  
    
    function drawObject(vaoObj, transformMatrix, vertexCount) {
        gl.useProgram(prg);
        gl.uniformMatrix3fv(transformsLoc, false, transformMatrix);
        gl.bindVertexArray(vaoObj.vao);
        gl.drawArrays(gl.TRIANGLES, 0, vertexCount);
        gl.bindVertexArray(null);
    }
    
    function render() {
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        // Dibujar pivote
        let pivotMatrix = M3.identity();
        pivotMatrix = M3.multiply(pivotMatrix, M3.translation([state.pivot.x, state.pivot.y]));
        pivotMatrix = M3.multiply(pivotMatrix, M3.scale([state.pivot.scale.x, state.pivot.scale.y]));
        
        drawObject(pivotVAO, pivotMatrix, pivotVAO.vertexCount);
        
        // Dibujar cara
        let faceMatrix = M3.identity();
        faceMatrix = M3.multiply(faceMatrix, M3.scale([state.face.scale.x, state.face.scale.y]));
        faceMatrix = M3.multiply(faceMatrix, M3.translation([state.face.translation.x, state.face.translation.y]));
        
        if (state.face.rotation !== 0) {
            const rotMatrix = M3.rotateAroundPoint(state.face.rotation, state.pivot.x, state.pivot.y);
            faceMatrix = M3.multiply(faceMatrix, rotMatrix);
        }
        
        drawObject(faceVAO, faceMatrix, faceVAO.vertexCount);
        
        requestAnimationFrame(render);
    }
    
    console.log('Iniciando render loop ✓');
    render();
    console.log('=== APLICACIÓN INICIADA CORRECTAMENTE ===');
});