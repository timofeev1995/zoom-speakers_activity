## Zoom speaker activity plot tool

### Installiation:
1. Python>=3.7
2. Clone repo
3. `pip install -r requirements.txt`

### Usage:
1. `$ cd scripts`
2. `python get_speaker_activity_plot.py --recordings_folder=<path_to_zoom_dump> --plot_dump_path=<your_path>`


### Pipeline:
1. Загрузить данные.
2. Найти "положение" дорожки для каждого спикера (кроме хоста) в полном аудио. Используется простой O(n)-алгоритм на спектрограммах, который идет окном по спектрограмме полной записи и считает MAE между этим окном и участком общей спектрограммы. Индекс старта - тот, который дает меньшую меру разности.
3. Дополнить дорожки спикеров "тишиной" с учетом результатов из п.2.
4. Используя простейший VAD определить интервалы с голосом в каждой дорожке.
5. Отрисовать.

### Further work & extensions:
1. Denoising
2. Better VAD
3. etc

### Result example
![result example](https://i.ibb.co/WK4yz5Q/activity.png)
