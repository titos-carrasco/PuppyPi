# PuppyPi

Acceso desde Python al robot cuadrúpedo PuppyPi de Hiwonder.

En lo posible trabajar en ambiente virtual (venv) e instalar los módulos roslibpy para la librería. En el caso de utilizar
la imagen de la cámara instalar también opencv y numpy:

```
> pip install roslibpy
> pip install opencv-python
> pip install numpy
```

Para generar la documentación utilizar pdoc3:

```
> pip install pdoc3
> pdoc3 --html .\PuppyPi.py html
```
