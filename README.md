# daphnia_tracker

## Разметка

Для разметки реальных данных использовались:

- **FFmpeg** - утилита для обработки видеофайлов. С помощью данной утилиты видеофайл разделялся на фреймы. Использование:
	
	`ffmpeg -i /path/to/video.avi %04d.png`

- **VVG Image Annotator** - программа для разметки полученных изображений. Ссылка на сайт: https://www.robots.ox.ac.uk/~vgg/software/via/. Для разметки дафний использовались эллипсы. 

- **markup.py** - данная программа приводит выходной json из разметчика к форме для использования в framework. Использование:
	
	`python3 markup.py /path/to/orig/json path/to/mod/json`
 
 Пример получаемого json-файла:

```json
{
    "_via_attributes": {
        "region": {}, 
        "file": {}
    }, 
    "_via_img_metadata": {
        "0037.png": {
            "regions": [
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 3, 
                        "ry": 5, 
                        "cy": 937, 
                        "cx": 518, 
                        "theta": 0
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 3.168, 
                        "ry": 5.842, 
                        "cy": 950, 
                        "cx": 515, 
                        "theta": -0.862
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 4, 
                        "ry": 9, 
                        "cy": 933, 
                        "cx": 598, 
                        "theta": 0
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 6, 
                        "ry": 4, 
                        "cy": 983, 
                        "cx": 535, 
                        "theta": 0
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 7.63, 
                        "ry": 3.802, 
                        "cy": 944, 
                        "cx": 609, 
                        "theta": 0.844
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 6, 
                        "ry": 4, 
                        "cy": 945, 
                        "cx": 627, 
                        "theta": 0
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 7.63, 
                        "ry": 3.168, 
                        "cy": 951, 
                        "cx": 631, 
                        "theta": 2.415
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 3.802, 
                        "ry": 6.854, 
                        "cy": 938, 
                        "cx": 675, 
                        "theta": -0.588
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 4, 
                        "ry": 6, 
                        "cy": 943, 
                        "cx": 691, 
                        "theta": 0
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 3.168, 
                        "ry": 7.94, 
                        "cy": 939, 
                        "cx": 742, 
                        "theta": 1.071
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 6.524, 
                        "ry": 3.802, 
                        "cy": 971, 
                        "cx": 768, 
                        "theta": -0.507
                    }, 
                    "region_attributes": {}
                }, 
                {
                    "shape_attributes": {
                        "name": "ellipse", 
                        "rx": 3.802, 
                        "ry": 6.736, 
                        "cy": 941, 
                        "cx": 1145, 
                        "theta": 0.852
                    }, 
                    "region_attributes": {}
                }
            ], 
            "filename": "0037.png", 
            "file_attributes": {}, 
            "size": 1194107
        }
    }, 
    "_via_image_id_list": [ 
        "0037.png"
    ], 
    "_via_settings": {
        "project": {
            "name": "via_project_6May2022_21h10m"
        }, 
        "core": {
            "buffer_size": 18, 
            "default_filepath": "", 
            "filepath": {}
        }, 
        "ui": {
            "image_grid": {
                "rshape_stroke_width": 2, 
                "img_height": 80, 
                "rshape_fill": "none", 
                "rshape_stroke": "yellow", 
                "rshape_fill_opacity": 0.3, 
                "show_image_policy": "all", 
                "show_region_shape": true
            }, 
            "annotation_editor_height": 25, 
            "image": {
                "region_color": "__via_default_region_color__", 
                "region_label_font": "10px Sans", 
                "region_label": "__via_region_id__", 
                "on_image_annotation_editor_placement": "NEAR_REGION"
            }, 
            "annotation_editor_fontsize": 0.8, 
            "leftsidebar_width": 18
        }
    }, 
    "_via_data_format_version": "2.0.10"
}
```

Данные и markup.py лежат в папке markup.

## Оценка качества

Качество оценивается с помощью скрипта quality_estimator.py. Ссылка: https://gitlab.com/combat_helicopter/daphnia-tracker/-/blob/main/CODE/scripts/quality_estimator/quality_estimator.py. 

Метод оценки следующий: на вход алгоритма подаются изображения, разметка и бинаризованные сегментированные изображения- выход нейронной сети. Для каждого изображения формируется список эллипсов из разметки и список центров компонент связности, полученных из бинаризованного изображения с помощью функции opencv - connectedComponentsWithStats. Пиксели в данных компонентах связности были определены нейросетью, как дафнии. Для изображения подсчитывается количество TP - количество правильно задетектированных дафний (если центр компоненты связности попал в эллипс, если таких центров в одном эллипсе больше одного, то TP увеличивается на один, и FP увеличивается на количество оставшихся), FP - количество ложно задетектированных дафний, FN - количество эллипсов из разметки, куда не попали центры.

Подсчитываемые статистики 

$$ Precision = \frac{TP}{TP+TN},$$

$$ Recall = \frac{TP}{TP+FN}.$$ 

Для данных объединенных разметкой, средние статистики формируется усреднением статистик по рассматриваемым изображениям. Значения величин записываются в csv-файл. Пример есть в общей документации framework.  