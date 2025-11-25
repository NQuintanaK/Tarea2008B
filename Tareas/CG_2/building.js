#!/usr/bin/env node

const fs = require('fs');
const readline = require('readline');

// Crear interfaz de lectura
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Función para hacer preguntas
function question(prompt) {
    return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
        resolve(answer);
    });
    });
}

async function main() {
    console.log('\n=== Building OBJ Generator ===\n');

  // Obtener parámetros del usuario
    let sides = 8;
    let height = 6.0;
    let radiusBottom = 1.0;
    let radiusTop = 0.8;

    const sidesInput = await question('Número de lados del círculo (3-36) [8]: ');
    if (sidesInput) sides = Math.max(3, Math.min(36, parseInt(sidesInput))) || sides;

    const heightInput = await question('Altura del edificio [6.0]: ');
    if (heightInput) height = Math.max(0.1, parseFloat(heightInput)) || height;

    const radiusBottomInput = await question('Radio de la base [1.0]: ');
    if (radiusBottomInput) radiusBottom = Math.max(0.1, parseFloat(radiusBottomInput)) || radiusBottom;

    const radiusTopInput = await question('Radio de la cima [0.8]: ');
    if (radiusTopInput) radiusTop = Math.max(0.1, parseFloat(radiusTopInput)) || radiusTop;

    rl.close();

    const outputFile = 'buildingdraw.obj';

  // Generar geometría del edificio
    const vertices = [];
    const normals = [];
    const faces = [];

  // Generar vértices para la base
    for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2;
    const x = Math.cos(angle) * radiusBottom;
    const z = Math.sin(angle) * radiusBottom;
    vertices.push([x, 0, z]);
    }

  // Generar vértices para la cima
    const topStartIndex = sides;
    for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2;
    const x = Math.cos(angle) * radiusTop;
    const z = Math.sin(angle) * radiusTop;
    vertices.push([x, height, z]);
    }

  // Calcular normales para las caras laterales
    for (let i = 0; i < sides; i++) {
    const angle = (i + 0.5) / sides * Math.PI * 2;
    const nx = Math.cos(angle);
    const nz = Math.sin(angle);
    const normal = [nx, 0, nz];
    normals.push(normal);
    }

  // Generar caras laterales
    for (let i = 0; i < sides; i++) {
    const base1 = i + 1;
    const base2 = ((i + 1) % sides) + 1;
    const top1 = topStartIndex + i + 1;
    const top2 = topStartIndex + ((i + 1) % sides) + 1;

    faces.push({
        vertices: [base1, base2, top1],
        normals: [i, i, i]
    });

    faces.push({
        vertices: [base2, top2, top1],
        normals: [i, i, i]
    });
    }

  // Generar base
    const baseNormalIdx = normals.length;
    normals.push([0, -1, 0]);
    for (let i = 0; i < sides; i++) {
    const v1 = i + 1;
    const v2 = ((i + 1) % sides) + 1;
    faces.push({
        vertices: [v2, v1, 1],
        normals: [baseNormalIdx, baseNormalIdx, baseNormalIdx]
    });
    }

  // Generar cima
    const topNormalIdx = normals.length;
    normals.push([0, 1, 0]);
    for (let i = 1; i < sides - 1; i++) {
    const v1 = topStartIndex + 1;
    const v2 = topStartIndex + i + 1;
    const v3 = topStartIndex + i + 2;
    faces.push({
        vertices: [v1, v2, v3],
        normals: [topNormalIdx, topNormalIdx, topNormalIdx]
    });
    }

  // Generar archivo OBJ
    let objContent = `# Building OBJ File\n`;
    objContent += `# Generated with building_generator.js\n`;
    objContent += `# Parameters: sides=${sides}, height=${height}, radiusBottom=${radiusBottom}, radiusTop=${radiusTop}\n\n`;

  // Escribir vértices
    for (const v of vertices) {
    objContent += `v ${v[0].toFixed(6)} ${v[1].toFixed(6)} ${v[2].toFixed(6)}\n`;
    }
    objContent += "\n";

  // Escribir normales
    for (const n of normals) {
    const len = Math.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2]);
    objContent += `vn ${(n[0]/len).toFixed(6)} ${(n[1]/len).toFixed(6)} ${(n[2]/len).toFixed(6)}\n`;
    }
    objContent += "\n";

  // Escribir caras
    for (const face of faces) {
    const v = face.vertices;
    const n = face.normals;
    objContent += `f ${v[0]}//${n[0]+1} ${v[1]}//${n[1]+1} ${v[2]}//${n[2]+1}\n`;
    }

  // Guardar archivo OBJ
    fs.writeFileSync(outputFile, objContent);
    console.log(`\n✓ Parámetros utilizados:\n  - Lados: ${sides}\n  - Altura: ${height}\n  - Radio base: ${radiusBottom}\n  - Radio cima: ${radiusTop}`);
    console.log(`✓ Archivo guardado: ${outputFile}\n`);
}

main();