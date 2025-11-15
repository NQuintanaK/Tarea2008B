/*
Nicolas Quintana Kluchnik
A01785655
2D Transformation Library
Date: November 14th, 2024
*/

'use strict';

// Clase para vectores 2D
class V2 {
    static create(px, py) {
        let v = new Float32Array(2);
        v[0] = px;
        v[1] = py;
        return v;
    }
}

// Clase para matrices 3x3 (transformaciones 2D en coordenadas homogéneas)
class M3 {
    // Crea una matriz identidad 3x3
    static identity() {
        return new Float32Array([
            1, 0, 0,
            0, 1, 0,
            0, 0, 1
        ]);
    }

    // Matriz de escala
    static scale(vs) {
        return new Float32Array([
            vs[0], 0, 0,
            0, vs[1], 0,
            0, 0, 1
        ]);
    }

    // Matriz de traslación
    static translation(vt) {
        return new Float32Array([
            1, 0, 0,
            0, 1, 0,
            vt[0], vt[1], 1
        ]);
    }

    // Matriz de rotación
    static rotation(angleRadians) {
        const c = Math.cos(angleRadians);
        const s = Math.sin(angleRadians);
        return new Float32Array([
            c, s, 0,
            -s, c, 0,
            0, 0, 1
        ]);
    }

    // Multiplicación de matrices 3x3
    // Formato de matriz:
    // a00 a01 a02
    // a10 a11 a12
    // a20 a21 a22
    static multiply(ma, mb) {
        const ma00 = ma[0 * 3 + 0];
        const ma01 = ma[0 * 3 + 1];
        const ma02 = ma[0 * 3 + 2];
        const ma10 = ma[1 * 3 + 0];
        const ma11 = ma[1 * 3 + 1];
        const ma12 = ma[1 * 3 + 2];
        const ma20 = ma[2 * 3 + 0];
        const ma21 = ma[2 * 3 + 1];
        const ma22 = ma[2 * 3 + 2];

        const mb00 = mb[0 * 3 + 0];
        const mb01 = mb[0 * 3 + 1];
        const mb02 = mb[0 * 3 + 2];
        const mb10 = mb[1 * 3 + 0];
        const mb11 = mb[1 * 3 + 1];
        const mb12 = mb[1 * 3 + 2];
        const mb20 = mb[2 * 3 + 0];
        const mb21 = mb[2 * 3 + 1];
        const mb22 = mb[2 * 3 + 2];

        return new Float32Array([
            ma00 * mb00 + ma10 * mb01 + ma20 * mb02,
            ma01 * mb00 + ma11 * mb01 + ma21 * mb02,
            ma02 * mb00 + ma12 * mb01 + ma22 * mb02,

            ma00 * mb10 + ma10 * mb11 + ma20 * mb12,
            ma01 * mb10 + ma11 * mb11 + ma21 * mb12,
            ma02 * mb10 + ma12 * mb11 + ma22 * mb12,

            ma00 * mb20 + ma10 * mb21 + ma20 * mb22,
            ma01 * mb20 + ma11 * mb21 + ma21 * mb22,
            ma02 * mb20 + ma12 * mb21 + ma22 * mb22,
        ]);
    }

    // Rotación alrededor de un punto específico (pivote)
    // Para rotar alrededor de un punto (px, py):
    // 1. Trasladar el punto al origen
    // 2. Aplicar la rotación
    // 3. Trasladar de vuelta
    static rotateAroundPoint(angleRadians, px, py) {
        let m = M3.translation([-px, -py]);
        m = M3.multiply(m, M3.rotation(angleRadians));
        m = M3.multiply(m, M3.translation([px, py]));
        return m;
    }
}