# Simulador de la Máquina Enigma

Simulación en Python de la máquina de cifrado Enigma I, construida a partir del  
diagrama de configuración proporcionado en clase.

```
Rotor I   : EKMFLGDQVZNTOWYHXUSPAIBRCJ  (notch Q)
Rotor II  : AJDKSIRUXBLHWTMCQGZNPYFVOE  (notch E)
Rotor III : BDFHJLCPRTXVZNYEIWGAKMUSQO  (notch V)
Reflector : YRUHQSLDPXNGOKMIEBFZCWVJAT
```

---

## Requisitos

Python 3.10 o superior. Sin dependencias externas.

---

## Uso

```bash
python enigma.py
```

El programa es un loop interactivo simple:

```
(c) encrypt    (d) decrypt    (q) quit

  Operation > c
  Message: CRYPTOGRAPHY
  Key (min. 3 letters): XYZ

  Encrypted: LMKIWKHAPJNK
```

Como la Enigma es su propio inverso, cifrar y descifrar son la misma operación.  
Para descifrar, selecciona `d`, ingresa el texto cifrado y usa la misma clave:

```
  Operation > d
  Message: LMKIWKHAPJNK
  Key (min. 3 letters): XYZ

  Decrypted: CRYPTOGRAPHY
```

### Clave

La clave establece la posición inicial de cada rotor antes de procesar el mensaje.  
La primera letra posiciona el rotor izquierdo, la segunda el del medio, la tercera  
el derecho. Cualquier cadena con al menos 3 letras válidas funciona — solo se usan  
las primeras 3.

### Espacios y caracteres especiales

Los espacios en el mensaje se conservan en la salida. Los caracteres fuera de A-Z  
(números, puntuación, letras acentuadas) se ignoran silenciosamente.

---

# Cómo funciona

## Recorrido de la señal

Cada tecla enviada manda una señal eléctrica por la máquina en este orden:

```
Texto plano -> Rotor I -> Rotor II -> Rotor III -> Reflector
                                                       |
Texto cifrado <- Rotor I <- Rotor II <- Rotor III <----+
```

Cada rotor aplica una sustitución fija de letras desplazada por su posición actual.  
El reflector devuelve la señal por los rotores en sentido inverso usando la  
sustitución inversa. Eso es lo que hace que la máquina sea simétrica.

---

## Avance de los rotores (stepping)

Antes de cifrar cada letra, los rotores avanzan:

- El rotor derecho (III) avanza en cada tecla.
- El rotor del medio (II) avanza cuando el derecho llega a su notch (V), o cuando  
  el propio rotor del medio está en su notch (anomalía del doble paso).
- El rotor izquierdo (I) avanza cuando el del medio llega a su notch (E).

La anomalía del doble paso es una peculiaridad mecánica de la Enigma original:  
si el rotor del medio está en su notch, avanza junto con el izquierdo en el mismo  
paso. Esto crea un patrón de avance irregular que aumenta la impredecibilidad.

---

## Por qué cifrar y descifrar son la misma operación

El reflector garantiza que si la letra A se mapea a Q, entonces Q se mapea de  
vuelta a A. Combinado con el recorrido simétrico de ida y vuelta, esto significa  
que la máquina es su propio inverso. Tanto el emisor como el receptor configuran  
su máquina con la misma clave, y la operación es idéntica en ambas direcciones.

---

# Nota sobre un error conceptual común en simulaciones de Enigma

Algunas simulaciones de Enigma utilizan un modelo incorrecto para decidir cuándo  
un rotor hace avanzar al siguiente. En lugar de basarse en la **posición del rotor**,  
usan el **valor de la letra producida por la sustitución del rotor**.

A este enfoque se le puede llamar **"notch por valor"**, y aunque puede producir  
resultados consistentes dentro de una implementación específica, **no corresponde  
al funcionamiento real de la máquina Enigma**.

---

## Cómo funciona realmente el notch

En la máquina Enigma histórica, el notch es una **pestaña mecánica en el anillo del rotor**.  
Cuando el rotor gira y esa pestaña alcanza una posición específica, empuja  
mecánicamente al siguiente rotor para que avance.

Esto significa que el stepping depende **exclusivamente de la posición física del rotor**,  
no de la letra que produzca su sustitución interna.

Por lo tanto:

- El rotor **no decide avanzar por el valor que produce**.
- El rotor **avanza únicamente cuando su posición coincide con la posición del notch**.

---

## Qué ocurre si se usa "notch por valor"

Si el avance del rotor depende de la letra que produce la sustitución:

- El stepping deja de ser estrictamente mecánico.
- El avance puede depender del flujo de señal dentro del cifrado.
- La posición de los rotores puede cambiar durante el recorrido interno de la señal.

Esto introduce comportamientos que **no existen en la Enigma real**.

En algunos casos incluso puede romper una propiedad fundamental del sistema:  
que el cifrado sea perfectamente reversible.

---

## Importancia del stepping correcto

La Enigma real tiene una propiedad clave:

**Cifrar y descifrar utilizan exactamente el mismo proceso.**

Esto solo es posible porque:

- Las posiciones de los rotores evolucionan de forma **determinista**.
- El stepping depende únicamente de la **posición**, no del contenido del mensaje.

Si el mecanismo de avance depende del valor de la sustitución, esta propiedad  
puede romperse y el sistema deja de comportarse como una Enigma auténtica.

---

## Resumen

| Modelo de stepping | Descripción | Históricamente correcto |
|---|---|---|
| Basado en posición | El rotor avanza cuando su posición alcanza el notch | Sí |
| "Notch por valor" | El rotor avanza según la letra que produce su sustitución | No |

Esta implementación utiliza **stepping basado en posición**, que replica el  
comportamiento histórico de la máquina Enigma.
