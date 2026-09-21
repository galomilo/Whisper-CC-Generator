# Whisper-CC-Generator

Generá subtítulos `.srt` automáticamente a partir de cualquier video.

**Gratis, local y sin suscripciones.**

Arrastrá un video, elegí el modelo de Whisper y procesalo. La aplicación genera un archivo `.srt` listo para importar en tu editor de video.

**Video → Whisper-CC-Generator → SRT → Editor**

Una alternativa simple para generar subtítulos sin depender de funciones de subtitulado de pago dentro de editores de video.

## ¿Qué hace?

Whisper-CC-Generator utiliza [OpenAI Whisper](https://github.com/openai/whisper) para transcribir automáticamente el audio de un video.

Podés generar:

* `.srt` — subtítulos con timestamps, listos para importar.
* `.txt` — transcripción en texto.
* `.json` — información estructurada de la transcripción.

El archivo generado se guarda junto al video original.

## Gratis y local

No necesitás pagar una suscripción para generar tus subtítulos.

La aplicación ejecuta Whisper localmente en tu equipo, por lo que el video no necesita ser enviado a un servicio de transcripción propio de Whisper-CC-Generator.

(El rendimiento depende del modelo seleccionado y del hardware de tu PC).

## Características

### Drag & Drop

Arrastrá un video directamente sobre la aplicación.

### Modelos de Whisper

Podés seleccionar entre:

| Modelo     | Velocidad  | Calidad  |
| ---------- | ---------- | -------- |
| `tiny`     | Muy rápida | Menor    |
| `base`     | Rápida     | Buena    |
| `small`    | Media      | Mejor    |
| `medium`   | Lenta      | Alta     |
| `large`    | Muy lenta  | Muy alta |
| `large-v2` | Muy lenta  | Muy alta |
| `large-v3` | Muy lenta  | Muy alta |

El rendimiento real depende del hardware utilizado.

### Selección de idioma

Podés seleccionar manualmente el idioma o utilizar detección automática.

### Formatos de salida

#### SRT

El formato principal de la aplicación.

```srt
1
00:00:01,200 --> 00:00:04,500
Bienvenidos a este nuevo video.

2
00:00:04,500 --> 00:00:07,200
Hoy vamos a aprender algo nuevo.
```

El archivo `.srt` puede importarse posteriormente en cualquier editor compatible.

#### TXT

Genera únicamente la transcripción en texto, sin timestamps.

#### JSON

Guarda la información estructurada generada por Whisper.

## División de subtítulos

Cuando se trabaja con la salida JSON, la aplicación permite dividir la transcripción en bloques según una cantidad determinada de palabras.

Por ejemplo:

```text
Palabras por bloque: 5
```

La aplicación calcula los timestamps correspondientes y genera un nuevo archivo:

```text
video_dividido.srt
```

## Instalación

### Ejecutable

Si descargaste una versión compilada, ejecutá:

```text
Whisper-CC-Generator.exe
```

y seguí las instrucciones de la aplicación.

### Desde el código fuente

Cloná el repositorio:

```bash
git clone https://github.com/TU-USUARIO/Whisper-CC-Generator.git
cd Whisper-CC-Generator
```

Instalá las dependencias necesarias y asegurate de tener Whisper correctamente configurado.

Ejecutá:

```bash
python main.py
```

## Tecnologías

* Python
* OpenAI Whisper
* Tkinter
* TkinterDnD
* SRT
* JSON
* TXT

## Privacidad

Whisper-CC-Generator está diseñado para procesar los videos localmente mediante Whisper.

No necesitás crear una cuenta ni pagar una suscripción de Whisper-CC-Generator.

Los archivos generados se guardan localmente en el equipo.

## Requisitos

El rendimiento depende principalmente de:

* Modelo de Whisper.
* CPU.
* GPU.
* Memoria RAM.
* Duración del video.
* Calidad del audio.

Los modelos más grandes requieren considerablemente más recursos.

## Licencia

Whisper-CC-Generator se distribuye bajo la licencia indicada en el archivo `LICENSE`.

Este proyecto utiliza software de terceros que mantiene sus propias licencias.

Consultá sus respectivos repositorios para conocer sus condiciones de uso.

## Créditos

Whisper-CC-Generator utiliza [OpenAI Whisper](https://github.com/openai/whisper) como motor de reconocimiento de voz.

---

**Video → SRT → Editor.**

**Subtítulos automáticos, gratis y ejecutados localmente.**
