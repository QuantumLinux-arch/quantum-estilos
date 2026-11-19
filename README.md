# Galería de estilos de Quantum Linux

Estilos de escritorio creados por la comunidad de [Quantum Linux](https://quantumlinux-arch.github.io). Aparecen en **Personalizar → Estilos → Galería de la comunidad** y se aplican con un clic.

## Subir tu estilo

1. En Quantum, deja tu escritorio como te guste.
2. Abre **Personalizar → Estilos** y toca **Subir a la galería**. Quantum guarda una captura en *Imágenes* y abre el formulario de GitHub con tu estilo ya pegado.
3. Arrastra la captura al formulario y envíalo.
4. Cuando el equipo lo revise y le ponga la etiqueta `aprobado`, aparece solo en la galería.

También puedes abrir un issue con la plantilla **Subir un estilo** y pegar el contenido de un estilo que exportaste.

## Me gusta

Cada estilo tiene su issue. Los 👍 de ese issue son sus «me gusta» y ordenan la galería (se actualizan una vez al día).

## Qué contiene un estilo

`estilos/<nombre>/estilo.json` (nombre, descripción, autor, forma del shell y ajustes de apariencia), `captura.jpg` y `meta.json`. Nunca se publica tu fondo, tu ciudad, tus notas ni tus archivos: solo el aspecto.

`index.json` lo arma la Action `Galería` (`scripts/galeria.py`).
