"""Internationalization: 10-language UI translation.

Source language is English; every UI string goes through :func:`tr`. A
translation table maps each English key to the nine non-English locales
(English falls back to the key itself). Switching language emits a Qt signal
so the main window can rebuild its pages.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, SignalInstance

LANGUAGES: list[tuple[str, str]] = [
    ("zh", "简体中文"),
    ("en", "English"),
    ("ja", "日本語"),
    ("fr", "Français"),
    ("ru", "Русский"),
    ("de", "Deutsch"),
    ("pt", "Português"),
    ("es", "Español"),
    ("ko", "한국어"),
    ("it", "Italiano"),
]

# English key -> {locale: translation}. English is implicit.
TRANSLATIONS: dict[str, dict[str, str]] = {
    # ---- status ----
    "Pass": {"zh": "通过", "ja": "合格", "fr": "Réussi", "ru": "Пройдено", "de": "Bestanden", "pt": "Aprovado", "es": "Aprobado", "ko": "통과", "it": "Superato"},
    "Fail": {"zh": "失败", "ja": "失敗", "fr": "Échec", "ru": "Сбой", "de": "Fehlgeschlagen", "pt": "Falhou", "es": "Fallido", "ko": "실패", "it": "Non superato"},
    "Unknown": {"zh": "未知", "ja": "不明", "fr": "Inconnu", "ru": "Неизвестно", "de": "Unbekannt", "pt": "Desconhecido", "es": "Desconocido", "ko": "알 수 없음", "it": "Sconosciuto"},
    "Skipped": {"zh": "跳过", "ja": "スキップ", "fr": "Ignoré", "ru": "Пропущено", "de": "Übersprungen", "pt": "Ignorado", "es": "Omitido", "ko": "건너뜀", "it": "Saltato"},

    # ---- page titles ----
    "Overview": {"zh": "硬件总览", "ja": "ハードウェア概要", "fr": "Vue d'ensemble", "ru": "Обзор", "de": "Übersicht", "pt": "Visão geral", "es": "Resumen", "ko": "하드웨어 개요", "it": "Panoramica"},
    "Screen": {"zh": "屏幕检测", "ja": "画面", "fr": "Écran", "ru": "Экран", "de": "Bildschirm", "pt": "Tela", "es": "Pantalla", "ko": "화면", "it": "Schermo"},
    "Camera": {"zh": "摄像头检测", "ja": "カメラ", "fr": "Caméra", "ru": "Камера", "de": "Kamera", "pt": "Câmera", "es": "Cámara", "ko": "카메라", "it": "Fotocamera"},
    "Microphone": {"zh": "麦克风检测", "ja": "マイク", "fr": "Microphone", "ru": "Микрофон", "de": "Mikrofon", "pt": "Microfone", "es": "Micrófono", "ko": "마이크", "it": "Microfono"},
    "Speaker": {"zh": "扬声器检测", "ja": "スピーカー", "fr": "Haut-parleur", "ru": "Динамик", "de": "Lautsprecher", "pt": "Alto-falante", "es": "Altavoz", "ko": "스피커", "it": "Altoparlante"},
    "Keyboard": {"zh": "键盘检测", "ja": "キーボード", "fr": "Clavier", "ru": "Клавиатура", "de": "Tastatur", "pt": "Teclado", "es": "Teclado", "ko": "키보드", "it": "Tastiera"},
    "Mouse / Touchpad": {"zh": "鼠标/触控板检测", "ja": "マウス/トラックパッド", "fr": "Souris / Pavé tactile", "ru": "Мышь / Тачпад", "de": "Maus / Touchpad", "pt": "Mouse / Touchpad", "es": "Ratón / Panel táctil", "ko": "마우스/터치패드", "it": "Mouse / Touchpad"},
    "Thermal": {"zh": "散热/压力检测", "ja": "温度/負荷", "fr": "Thermique", "ru": "Термальный", "de": "Thermisch", "pt": "Térmico", "es": "Térmico", "ko": "발열/부하", "it": "Termico"},
    "Battery": {"zh": "电池检测", "ja": "バッテリー", "fr": "Batterie", "ru": "Батарея", "de": "Akku", "pt": "Bateria", "es": "Batería", "ko": "배터리", "it": "Batteria"},
    "Disk": {"zh": "磁盘检测", "ja": "ディスク", "fr": "Disque", "ru": "Диск", "de": "Datenträger", "pt": "Disco", "es": "Disco", "ko": "디스크", "it": "Disco"},
    "Memory": {"zh": "内存检测", "ja": "メモリ", "fr": "Mémoire", "ru": "Память", "de": "Arbeitsspeicher", "pt": "Memória", "es": "Memoria", "ko": "메모리", "it": "Memoria"},
    "Network": {"zh": "网络检测", "ja": "ネットワーク", "fr": "Réseau", "ru": "Сеть", "de": "Netzwerk", "pt": "Rede", "es": "Red", "ko": "네트워크", "it": "Rete"},
    "Report": {"zh": "验机报告", "ja": "レポート", "fr": "Rapport", "ru": "Отчёт", "de": "Bericht", "pt": "Relatório", "es": "Informe", "ko": "보고서", "it": "Rapporto"},

    # ---- page subtitles ----
    "Auto-detect hardware info (CPU / memory / disk / GPU / board)": {"zh": "自动采集本机硬件信息（CPU / 内存 / 磁盘 / GPU / 主板）", "ja": "ハードウェア情報を自動収集（CPU / メモリ / ディスク / GPU / 基板）", "fr": "Détection automatique (CPU / mémoire / disque / GPU / carte)", "ru": "Автосбор данных (ЦП / память / диск / ГП / плата)", "de": "Hardware automatisch erkennen (CPU / RAM / Disk / GPU / Board)", "pt": "Detectar hardware (CPU / memória / disco / GPU / placa)", "es": "Detectar hardware (CPU / memoria / disco / GPU / placa)", "ko": "하드웨어 정보 자동 수집 (CPU / 메모리 / 디스크 / GPU / 보드)", "it": "Rilevamento hardware (CPU / memoria / disco / GPU / scheda)"},
    "Check resolution / refresh rate and find dead pixels": {"zh": "检查分辨率/刷新率，并用全屏纯色找出坏点", "ja": "解像度/リフレッシュレートを確認し、デッドピクセルを検出", "fr": "Vérifier la résolution/le taux de rafraîchissement et détecter les pixels morts", "ru": "Проверка разрешения/частоты и поиск битых пикселей", "de": "Auflösung/Bildwiederholrate prüfen und Pixelfehler finden", "pt": "Verificar resolução/taxa e encontrar pixels mortos", "es": "Comprobar resolución/tasa y buscar píxeles muertos", "ko": "해상도/주사율 확인 및 불량 화소 검출", "it": "Controlla risoluzione/frequenza e trova pixel morti"},
    "Preview the camera and take a snapshot": {"zh": "预览摄像头画面并拍照，确认成像正常", "ja": "カメラ映像をプレビューして撮影、正常を確認", "fr": "Prévisualiser la caméra et prendre un cliché", "ru": "Предпросмотр камеры и снимок", "de": "Kamerabild anzeigen und Foto aufnehmen", "pt": "Visualizar a câmera e tirar foto", "es": "Previsualizar la cámara y tomar una foto", "ko": "카메라 미리보기 및 촬영", "it": "Anteprima della fotocamera e scatto"},
    "Speak into the mic and watch the level meter": {"zh": "对麦克风说话，观察电平变化；可录音回放确认", "ja": "マイクに向かって話し、レベルメーターを確認", "fr": "Parlez dans le micro et observez le niveau", "ru": "Говорите в микрофон и следите за уровнем", "de": "Ins Mikrofon sprechen und Pegel beobachten", "pt": "Fale no microfone e observe o nível", "es": "Hable al micrófono y observe el nivel", "ko": "마이크에 대고 말하며 레벨 확인", "it": "Parla nel microfono e osserva il livello"},
    "Play left/right channels and a sweep tone": {"zh": "分别播放左右声道与扫频信号，确认扬声器正常", "ja": "左右チャンネルとスイープ音を再生", "fr": "Lire les canaux gauche/droit et un balayage", "ru": "Воспроизвести левый/правый канал и свип", "de": "Linken/rechten Kanal und Sweep abspielen", "pt": "Reproduzir canais esquerdo/direito e varredura", "es": "Reproducir canales izquierdo/derecho y barrido", "ko": "좌우 채널 및 스윕 재생", "it": "Riproduci canali sinistro/destro e sweep"},
    "Press every key; pressed keys turn green": {"zh": "逐个按下键盘上的键，下方按键会变绿；请确保每个键都被按下", "ja": "すべてのキーを押して緑色に変わるか確認", "fr": "Appuyez sur chaque touche ; les touches s'allument en vert", "ru": "Нажмите каждую клавишу; нажатые станут зелёными", "de": "Jede Taste drücken; gedrückte werden grün", "pt": "Pressione cada tecla; as pressionadas ficam verdes", "es": "Pulse cada tecla; las pulsadas se ponen verdes", "ko": "모든 키를 눌러 초록색으로 변하는지 확인", "it": "Premi ogni tasto; quelli premuti diventano verdi"},
    "Click, scroll and move the pointer in the area below": {"zh": "在下方区域点击左右键、滚动滚轮并移动光标", "ja": "下の領域でクリック、スクロール、移動を確認", "fr": "Cliquez, faites défiler et déplacez le pointeur ci-dessous", "ru": "Кликайте, прокручивайте и двигайте указатель ниже", "de": "Klicken, scrollen und Zeiger unten bewegen", "pt": "Clique, role e mova o ponteiro na área abaixo", "es": "Haga clic, desplace y mueva el puntero abajo", "ko": "아래 영역에서 클릭·스크롤·이동", "it": "Clicca, scorri e muovi il puntatore qui sotto"},
    "Stress the CPU and watch usage, frequency and temperature": {"zh": "对 CPU 加压并观察占用率、频率与温度，判断散热是否正常", "ja": "CPUに負荷をかけ、使用率・周波数・温度を確認", "fr": "Sollicitez le CPU et observez usage, fréquence et température", "ru": "Нагрузите ЦП и следите за загрузкой, частотой и температурой", "de": "CPU belasten und Auslastung/Frequenz/Temperatur prüfen", "pt": "Estresse a CPU e observe uso, frequência e temperatura", "es": "Estrese la CPU y observe uso, frecuencia y temperatura", "ko": "CPU에 부하를 주고 사용률·주파수·온도 확인", "it": "Stressa la CPU e osserva uso, frequenza e temperatura"},
    "Check charge level, cycle count and health": {"zh": "检查电池电量、健康度与循环次数", "ja": "充電量、サイクル数、健康状態を確認", "fr": "Vérifiez la charge, les cycles et la santé", "ru": "Проверка заряда, циклов и состояния", "de": "Ladung, Zyklen und Zustand prüfen", "pt": "Verificar carga, ciclos e saúde", "es": "Comprobar carga, ciclos y salud", "ko": "충전량·사이클·건강 상태 확인", "it": "Controlla carica, cicli e salute"},
    "View partitions and measure read/write speed": {"zh": "查看磁盘分区并测量顺序读写速度", "ja": "パーティション確認と読み書き速度測定", "fr": "Voir les partitions et mesurer lecture/écriture", "ru": "Разделы и скорость чтения/записи", "de": "Partitionen anzeigen und Lesen/Schreiben messen", "pt": "Ver partições e medir leitura/escrita", "es": "Ver particiones y medir lectura/escritura", "ko": "파티션 확인 및 읽기/쓰기 속도 측정", "it": "Vedi partizioni e misura lettura/scrittura"},
    "View memory info and run a self-test": {"zh": "查看内存信息并做读写自检", "ja": "メモリ情報の確認と自己テスト", "fr": "Voir la mémoire et lancer un autotest", "ru": "Информация о памяти и самотест", "de": "Speicherinfo anzeigen und Selbsttest ausführen", "pt": "Ver memória e executar autoteste", "es": "Ver memoria y ejecutar autoprueba", "ko": "메모리 정보 확인 및 자체 테스트", "it": "Vedi memoria ed esegui autotest"},
    "View interfaces and test network latency": {"zh": "查看网卡信息并测试网络延迟", "ja": "インターフェース確認と遅延テスト", "fr": "Voir les interfaces et tester la latence", "ru": "Интерфейсы и задержка сети", "de": "Schnittstellen anzeigen und Latenz testen", "pt": "Ver interfaces e testar latência", "es": "Ver interfaces y probar latencia", "ko": "인터페이스 확인 및 지연 테스트", "it": "Vedi interfacce e testa la latenza"},
    "Aggregate all results and export a report": {"zh": "汇总全部检测结果，可导出为 HTML / Markdown / JSON", "ja": "結果を集計し、HTML / Markdown / JSON で出力", "fr": "Agréger les résultats et exporter (HTML / Markdown / JSON)", "ru": "Сводка результатов и экспорт (HTML / Markdown / JSON)", "de": "Ergebnisse zusammenfassen und exportieren", "pt": "Agregar resultados e exportar (HTML/Markdown/JSON)", "es": "Agregar resultados y exportar (HTML/Markdown/JSON)", "ko": "결과 집계 및 HTML/Markdown/JSON 내보내기", "it": "Aggrega i risultati ed esporta"},

    # ---- common ----
    "Rescan": {"zh": "重新采集", "ja": "再スキャン", "fr": "Relancer", "ru": "Повторить", "de": "Neu scannen", "pt": "Reescanear", "es": "Volver a escanear", "ko": "다시 스캔", "it": "Riscansiona"},
    "Start": {"zh": "开始", "ja": "開始", "fr": "Démarrer", "ru": "Запуск", "de": "Start", "pt": "Iniciar", "es": "Iniciar", "ko": "시작", "it": "Avvia"},
    "Stop": {"zh": "停止", "ja": "停止", "fr": "Arrêter", "ru": "Стоп", "de": "Stopp", "pt": "Parar", "es": "Detener", "ko": "중지", "it": "Ferma"},
    "Reset": {"zh": "重置", "ja": "リセット", "fr": "Réinitialiser", "ru": "Сброс", "de": "Zurücksetzen", "pt": "Reiniciar", "es": "Restablecer", "ko": "초기화", "it": "Ripristina"},
    "Refresh": {"zh": "刷新", "ja": "更新", "fr": "Actualiser", "ru": "Обновить", "de": "Aktualisieren", "pt": "Atualizar", "es": "Actualizar", "ko": "새로고침", "it": "Aggiorna"},
    "Export Report…": {"zh": "导出报告…", "ja": "レポートをエクスポート…", "fr": "Exporter le rapport…", "ru": "Экспорт отчёта…", "de": "Bericht exportieren…", "pt": "Exportar relatório…", "es": "Exportar informe…", "ko": "보고서 내보내기…", "it": "Esporta rapporto…"},
    "Confirm OK ✓": {"zh": "确认正常 ✓", "ja": "正常を確認 ✓", "fr": "Confirmer OK ✓", "ru": "Подтвердить ✓", "de": "OK bestätigen ✓", "pt": "Confirmar OK ✓", "es": "Confirmar OK ✓", "ko": "정상 확인 ✓", "it": "Conferma OK ✓"},
    "Confirm faulty ✗": {"zh": "确认异常 ✗", "ja": "異常を確認 ✗", "fr": "Confirmer défaut ✗", "ru": "Подтвердить сбой ✗", "de": "Fehler bestätigen ✗", "pt": "Confirmar falha ✗", "es": "Confirmar fallo ✗", "ko": "이상 확인 ✗", "it": "Conferma guasto ✗"},
    "Language": {"zh": "语言", "ja": "言語", "fr": "Langue", "ru": "Язык", "de": "Sprache", "pt": "Idioma", "es": "Idioma", "ko": "언어", "it": "Lingua"},

    # ---- hardware labels (overview) ----
    "System": {"zh": "系统", "ja": "システム", "fr": "Système", "ru": "Система", "de": "System", "pt": "Sistema", "es": "Sistema", "ko": "시스템", "it": "Sistema"},
    "Architecture": {"zh": "架构", "ja": "アーキテクチャ", "fr": "Architecture", "ru": "Архитектура", "de": "Architektur", "pt": "Arquitetura", "es": "Arquitectura", "ko": "아키텍처", "it": "Architettura"},
    "Hostname": {"zh": "主机名", "ja": "ホスト名", "fr": "Nom d'hôte", "ru": "Имя хоста", "de": "Hostname", "pt": "Nome do host", "es": "Nombre de host", "ko": "호스트 이름", "it": "Nome host"},
    "Python": {"zh": "Python", "ja": "Python", "fr": "Python", "ru": "Python", "de": "Python", "pt": "Python", "es": "Python", "ko": "Python", "it": "Python"},
    "Board": {"zh": "主板", "ja": "基板", "fr": "Carte mère", "ru": "Плата", "de": "Mainboard", "pt": "Placa-mãe", "es": "Placa base", "ko": "메인보드", "it": "Scheda madre"},
    "Model": {"zh": "型号", "ja": "モデル", "fr": "Modèle", "ru": "Модель", "de": "Modell", "pt": "Modelo", "es": "Modelo", "ko": "모델", "it": "Modello"},
    "Chip": {"zh": "芯片", "ja": "チップ", "fr": "Puce", "ru": "Чип", "de": "Chip", "pt": "Chip", "es": "Chip", "ko": "칩", "it": "Chip"},
    "Serial Number": {"zh": "序列号", "ja": "シリアル番号", "fr": "Numéro de série", "ru": "Серийный номер", "de": "Seriennummer", "pt": "Número de série", "es": "Número de serie", "ko": "일련번호", "it": "Numero di serie"},
    "CPU": {"zh": "CPU", "ja": "CPU", "fr": "CPU", "ru": "ЦП", "de": "CPU", "pt": "CPU", "es": "CPU", "ko": "CPU", "it": "CPU"},
    "Physical Cores": {"zh": "物理核心", "ja": "物理コア", "fr": "Cœurs physiques", "ru": "Физ. ядра", "de": "Physische Kerne", "pt": "Núcleos físicos", "es": "Núcleos físicos", "ko": "물리 코어", "it": "Core fisici"},
    "Logical Cores": {"zh": "逻辑核心", "ja": "論理コア", "fr": "Cœurs logiques", "ru": "Лог. ядра", "de": "Logische Kerne", "pt": "Núcleos lógicos", "es": "Núcleos lógicos", "ko": "논리 코어", "it": "Core logici"},
    "Current Frequency": {"zh": "当前频率", "ja": "現在の周波数", "fr": "Fréquence actuelle", "ru": "Текущая частота", "de": "Aktuelle Frequenz", "pt": "Frequência atual", "es": "Frecuencia actual", "ko": "현재 주파수", "it": "Frequenza attuale"},
    "Max Frequency": {"zh": "最大频率", "ja": "最大周波数", "fr": "Fréquence max", "ru": "Макс. частота", "de": "Max. Frequenz", "pt": "Frequência máx.", "es": "Frecuencia máx.", "ko": "최대 주파수", "it": "Frequenza max"},
    "Performance Cores": {"zh": "性能核心", "ja": "性能コア", "fr": "Cœurs performance", "ru": "Ядра произв.", "de": "Performance-Kerne", "pt": "Núcleos de desempenho", "es": "Núcleos de rendimiento", "ko": "성능 코어", "it": "Core performance"},
    "Efficiency Cores": {"zh": "能效核心", "ja": "効率コア", "fr": "Cœurs efficacité", "ru": "Ядра эфф.", "de": "Effizienz-Kerne", "pt": "Núcleos de eficiência", "es": "Núcleos de eficiencia", "ko": "효율 코어", "it": "Core efficienti"},
    "Performance": {"zh": "性能", "ja": "性能", "fr": "Performance", "ru": "Производительность", "de": "Leistung", "pt": "Desempenho", "es": "Rendimiento", "ko": "성능", "it": "Prestazioni"},
    "Efficiency": {"zh": "能效", "ja": "効率", "fr": "Efficacité", "ru": "Эффективность", "de": "Effizienz", "pt": "Eficiência", "es": "Eficiencia", "ko": "효율", "it": "Efficienza"},
    "Per-core Usage": {"zh": "每核心使用率", "ja": "コアごとの使用率", "fr": "Utilisation par cœur", "ru": "Загрузка по ядрам", "de": "Pro-Kern-Auslastung", "pt": "Uso por núcleo", "es": "Uso por núcleo", "ko": "코어별 사용률", "it": "Uso per core"},
    "Cache": {"zh": "缓存", "ja": "キャッシュ", "fr": "Cache", "ru": "Кэш", "de": "Cache", "pt": "Cache", "es": "Caché", "ko": "캐시", "it": "Cache"},
    "Total": {"zh": "总容量", "ja": "合計", "fr": "Total", "ru": "Всего", "de": "Gesamt", "pt": "Total", "es": "Total", "ko": "총 용량", "it": "Totale"},
    "Available": {"zh": "可用", "ja": "利用可能", "fr": "Disponible", "ru": "Доступно", "de": "Verfügbar", "pt": "Disponível", "es": "Disponible", "ko": "사용 가능", "it": "Disponibile"},
    "Usage": {"zh": "使用率", "ja": "使用率", "fr": "Utilisation", "ru": "Использование", "de": "Auslastung", "pt": "Uso", "es": "Uso", "ko": "사용률", "it": "Utilizzo"},
    "Swap": {"zh": "交换分区", "ja": "スワップ", "fr": "Swap", "ru": "Своп", "de": "Swap", "pt": "Swap", "es": "Swap", "ko": "스왑", "it": "Swap"},
    "GPU": {"zh": "GPU", "ja": "GPU", "fr": "GPU", "ru": "ГП", "de": "GPU", "pt": "GPU", "es": "GPU", "ko": "GPU", "it": "GPU"},
    "Vendor": {"zh": "厂商", "ja": "ベンダー", "fr": "Fabricant", "ru": "Производитель", "de": "Hersteller", "pt": "Fabricante", "es": "Fabricante", "ko": "제조사", "it": "Produttore"},
    "VRAM": {"zh": "显存", "ja": "ビデオメモリ", "fr": "VRAM", "ru": "Видеопамять", "de": "VRAM", "pt": "VRAM", "es": "VRAM", "ko": "VRAM", "it": "VRAM"},
    "GPU Cores": {"zh": "GPU 核心数", "ja": "GPU コア数", "fr": "Cœurs GPU", "ru": "Ядра ГП", "de": "GPU-Kerne", "pt": "Núcleos GPU", "es": "Núcleos GPU", "ko": "GPU 코어 수", "it": "Core GPU"},
    "API Support": {"zh": "支持的 API", "ja": "対応 API", "fr": "API supportées", "ru": "Поддержка API", "de": "API-Unterstützung", "pt": "Suporte a API", "es": "Soporte de API", "ko": "지원 API", "it": "Supporto API"},
    "Displays": {"zh": "显示器", "ja": "ディスプレイ", "fr": "Écrans", "ru": "Дисплеи", "de": "Displays", "pt": "Monitores", "es": "Pantallas", "ko": "디스플레이", "it": "Schermi"},
    "Partitions": {"zh": "磁盘分区", "ja": "パーティション", "fr": "Partitions", "ru": "Разделы", "de": "Partitionen", "pt": "Partições", "es": "Particiones", "ko": "파티션", "it": "Partizioni"},
    "Disk Drives": {"zh": "物理磁盘", "ja": "物理ディスク", "fr": "Disques physiques", "ru": "Физические диски", "de": "Laufwerke", "pt": "Discos físicos", "es": "Discos físicos", "ko": "물리 디스크", "it": "Dischi fisici"},
    "Type": {"zh": "类型", "ja": "種類", "fr": "Type", "ru": "Тип", "de": "Typ", "pt": "Tipo", "es": "Tipo", "ko": "유형", "it": "Tipo"},
    "Protocol": {"zh": "协议", "ja": "プロトコル", "fr": "Protocole", "ru": "Протокол", "de": "Protokoll", "pt": "Protocolo", "es": "Protocolo", "ko": "프로토콜", "it": "Protocollo"},
    "SMART Status": {"zh": "SMART 状态", "ja": "SMART 状態", "fr": "État SMART", "ru": "SMART статус", "de": "SMART-Status", "pt": "Status SMART", "es": "Estado SMART", "ko": "SMART 상태", "it": "Stato SMART"},
    "Health": {"zh": "健康度", "ja": "健康状態", "fr": "Santé", "ru": "Состояние", "de": "Zustand", "pt": "Saúde", "es": "Salud", "ko": "건강 상태", "it": "Salute"},
    "Internal": {"zh": "内置", "ja": "内蔵", "fr": "Interne", "ru": "Внутренний", "de": "Intern", "pt": "Interno", "es": "Interno", "ko": "내장", "it": "Interno"},
    "External": {"zh": "外接", "ja": "外付け", "fr": "Externe", "ru": "Внешний", "de": "Extern", "pt": "Externo", "es": "Externo", "ko": "외장", "it": "Esterno"},
    "SSD": {"zh": "固态硬盘", "ja": "SSD", "fr": "SSD", "ru": "SSD", "de": "SSD", "pt": "SSD", "es": "SSD", "ko": "SSD", "it": "SSD"},
    "HDD": {"zh": "机械硬盘", "ja": "HDD", "fr": "HDD", "ru": "HDD", "de": "HDD", "pt": "HDD", "es": "HDD", "ko": "HDD", "it": "HDD"},
    "Used": {"zh": "已用", "ja": "使用済み", "fr": "Utilisé", "ru": "Использовано", "de": "Belegt", "pt": "Usado", "es": "Usado", "ko": "사용됨", "it": "Usato"},
    "Good": {"zh": "良好", "ja": "良好", "fr": "Bon", "ru": "Хорошо", "de": "Gut", "pt": "Bom", "es": "Bueno", "ko": "양호", "it": "Buono"},
    "Bad": {"zh": "异常", "ja": "異常", "fr": "Mauvais", "ru": "Плохо", "de": "Schlecht", "pt": "Ruim", "es": "Malo", "ko": "불량", "it": "Cattivo"},

    # ---- memory page ----
    "Modules": {"zh": "内存条", "ja": "メモリモジュール", "fr": "Modules", "ru": "Модули", "de": "Module", "pt": "Módulos", "es": "Módulos", "ko": "모듈", "it": "Moduli"},
    "Channels": {"zh": "通道数", "ja": "チャンネル数", "fr": "Canaux", "ru": "Каналы", "de": "Kanäle", "pt": "Canais", "es": "Canales", "ko": "채널 수", "it": "Canali"},
    "Bandwidth": {"zh": "理论带宽", "ja": "理論帯域幅", "fr": "Bande passante", "ru": "Пропускная способность", "de": "Bandbreite", "pt": "Largura de banda", "es": "Ancho de banda", "ko": "대역폭", "it": "Larghezza di banda"},
    "Speed": {"zh": "速度", "ja": "速度", "fr": "Vitesse", "ru": "Скорость", "de": "Geschwindigkeit", "pt": "Velocidade", "es": "Velocidad", "ko": "속도", "it": "Velocità"},
    "Timing": {"zh": "时序", "ja": "タイミング", "fr": "Timing", "ru": "Тайминги", "de": "Timing", "pt": "Timing", "es": "Tiempos", "ko": "타이밍", "it": "Timing"},
    "Manufacturer": {"zh": "厂商", "ja": "メーカー", "fr": "Fabricant", "ru": "Производитель", "de": "Hersteller", "pt": "Fabricante", "es": "Fabricante", "ko": "제조사", "it": "Produttore"},
    "Part Number": {"zh": "型号", "ja": "型番", "fr": "Référence", "ru": "Артикул", "de": "Artikelnummer", "pt": "Nº de peça", "es": "Referencia", "ko": "부품 번호", "it": "Codice prodotto"},
    "Capacity": {"zh": "容量", "ja": "容量", "fr": "Capacité", "ru": "Ёмкость", "de": "Kapazität", "pt": "Capacidade", "es": "Capacidad", "ko": "용량", "it": "Capacità"},
    "Self-test size (MB)": {"zh": "自检大小 (MB)", "ja": "自己テストサイズ (MB)", "fr": "Taille du test (Mo)", "ru": "Размер теста (МБ)", "de": "Testgröße (MB)", "pt": "Tamanho do teste (MB)", "es": "Tamaño de prueba (MB)", "ko": "테스트 크기 (MB)", "it": "Dimensione test (MB)"},
    "Run Self-Test": {"zh": "开始读写自检", "ja": "自己テスト開始", "fr": "Lancer l'autotest", "ru": "Запустить самотест", "de": "Selbsttest starten", "pt": "Executar autoteste", "es": "Ejecutar autoprueba", "ko": "자체 테스트 실행", "it": "Esegui autotest"},
    "Passed: write {0} MB/s, read {1} MB/s": {"zh": "校验通过：写 {0} MB/s，读 {1} MB/s", "ja": "合格：書き込み {0} MB/s、読み込み {1} MB/s", "fr": "Réussi : écriture {0} Mo/s, lecture {1} Mo/s", "ru": "Пройдено: запись {0} МБ/с, чтение {1} МБ/с", "de": "Bestanden: Schreiben {0} MB/s, Lesen {1} MB/s", "pt": "Aprovado: escrita {0} MB/s, leitura {1} MB/s", "es": "Aprobado: escritura {0} MB/s, lectura {1} MB/s", "ko": "통과: 쓰기 {0} MB/s, 읽기 {1} MB/s", "it": "Superato: scrittura {0} MB/s, lettura {1} MB/s"},
    "Memory verify failed": {"zh": "内存读写校验失败，可能存在问题！", "ja": "メモリ検証に失敗しました！", "fr": "Échec de la vérification mémoire !", "ru": "Ошибка проверки памяти!", "de": "Speicherprüfung fehlgeschlagen!", "pt": "Falha na verificação de memória!", "es": "¡Fallo en la verificación de memoria!", "ko": "메모리 검증 실패!", "it": "Verifica memoria fallita!"},

    # ---- disk page ----
    "Test size (MB)": {"zh": "测试大小 (MB)", "ja": "テストサイズ (MB)", "fr": "Taille du test (Mo)", "ru": "Размер теста (МБ)", "de": "Testgröße (MB)", "pt": "Tamanho do teste (MB)", "es": "Tamaño de prueba (MB)", "ko": "테스트 크기 (MB)", "it": "Dimensione test (MB)"},
    "Start Benchmark": {"zh": "开始测速", "ja": "ベンチマーク開始", "fr": "Lancer le test", "ru": "Запустить тест", "de": "Benchmark starten", "pt": "Iniciar benchmark", "es": "Iniciar prueba", "ko": "벤치마크 시작", "it": "Avvia benchmark"},
    "Write": {"zh": "写入", "ja": "書き込み", "fr": "Écriture", "ru": "Запись", "de": "Schreiben", "pt": "Escrita", "es": "Escritura", "ko": "쓰기", "it": "Scrittura"},
    "Read": {"zh": "读取", "ja": "読み込み", "fr": "Lecture", "ru": "Чтение", "de": "Lesen", "pt": "Leitura", "es": "Lectura", "ko": "읽기", "it": "Lettura"},

    # ---- network page ----
    "Target address": {"zh": "目标地址", "ja": "対象アドレス", "fr": "Adresse cible", "ru": "Адрес цели", "de": "Zieladresse", "pt": "Endereço alvo", "es": "Dirección objetivo", "ko": "대상 주소", "it": "Indirizzo di destinazione"},
    "Ping Test": {"zh": "Ping 测试", "ja": "Ping テスト", "fr": "Test ping", "ru": "Пинг-тест", "de": "Ping-Test", "pt": "Teste de ping", "es": "Prueba de ping", "ko": "핑 테스트", "it": "Test ping"},
    "Connected": {"zh": "已连接", "ja": "接続済み", "fr": "Connecté", "ru": "Подключено", "de": "Verbunden", "pt": "Conectado", "es": "Conectado", "ko": "연결됨", "it": "Connesso"},
    "Not connected": {"zh": "未连接", "ja": "未接続", "fr": "Déconnecté", "ru": "Не подключено", "de": "Getrennt", "pt": "Desconectado", "es": "Desconectado", "ko": "연결 안 됨", "it": "Disconnesso"},
    "No IP": {"zh": "无 IP", "ja": "IP なし", "fr": "Pas d'IP", "ru": "Нет IP", "de": "Keine IP", "pt": "Sem IP", "es": "Sin IP", "ko": "IP 없음", "it": "Nessun IP"},

    # ---- battery page ----
    "Read Battery Info": {"zh": "读取电池信息", "ja": "バッテリー情報を取得", "fr": "Lire la batterie", "ru": "Считать батарею", "de": "Akku auslesen", "pt": "Ler bateria", "es": "Leer batería", "ko": "배터리 정보 읽기", "it": "Leggi batteria"},
    "Charge": {"zh": "电量", "ja": "充電量", "fr": "Charge", "ru": "Заряд", "de": "Ladung", "pt": "Carga", "es": "Carga", "ko": "충전량", "it": "Carica"},
    "Charging": {"zh": "充电中", "ja": "充電中", "fr": "En charge", "ru": "Заряжается", "de": "Lädt", "pt": "Carregando", "es": "Cargando", "ko": "충전 중", "it": "In carica"},
    "On Battery": {"zh": "使用电池", "ja": "バッテリー使用中", "fr": "Sur batterie", "ru": "От батареи", "de": "Akku", "pt": "Na bateria", "es": "Con batería", "ko": "배터리 사용 중", "it": "A batteria"},
    "Cycle Count": {"zh": "循环次数", "ja": "サイクル数", "fr": "Cycles", "ru": "Циклы", "de": "Zyklen", "pt": "Ciclos", "es": "Ciclos", "ko": "사이클 수", "it": "Cicli"},
    "Health Status": {"zh": "健康状态", "ja": "健康状態", "fr": "État de santé", "ru": "Состояние", "de": "Zustand", "pt": "Estado de saúde", "es": "Estado de salud", "ko": "건강 상태", "it": "Stato di salute"},
    "Max Capacity": {"zh": "最大容量", "ja": "最大容量", "fr": "Capacité max", "ru": "Макс. ёмкость", "de": "Max. Kapazität", "pt": "Capacidade máx.", "es": "Capacidad máx.", "ko": "최대 용량", "it": "Capacità max"},
    "Design Capacity": {"zh": "设计容量", "ja": "設計容量", "fr": "Capacité nominale", "ru": "Проектная ёмкость", "de": "Nennkapazität", "pt": "Capacidade projetada", "es": "Capacidad de diseño", "ko": "설계 용량", "it": "Capacità di progetto"},
    "Full Capacity": {"zh": "满充容量", "ja": "満充電容量", "fr": "Capacité pleine", "ru": "Полная ёмкость", "de": "Volle Kapazität", "pt": "Capacidade total", "es": "Capacidad completa", "ko": "완충 용량", "it": "Capacità piena"},
    "No battery detected (desktop or removed)": {"zh": "未检测到电池（可能是台式机或电池被移除）", "ja": "バッテリーが検出されませんでした", "fr": "Aucune batterie détectée", "ru": "Батарея не обнаружена", "de": "Kein Akku erkannt", "pt": "Nenhuma bateria detectada", "es": "No se detectó batería", "ko": "배터리가 감지되지 않음", "it": "Nessuna batteria rilevata"},

    # ---- colors ----
    "Red": {"zh": "红", "ja": "赤", "fr": "Rouge", "ru": "Красный", "de": "Rot", "pt": "Vermelho", "es": "Rojo", "ko": "빨강", "it": "Rosso"},
    "Green": {"zh": "绿", "ja": "緑", "fr": "Vert", "ru": "Зелёный", "de": "Grün", "pt": "Verde", "es": "Verde", "ko": "초록", "it": "Verde"},
    "Blue": {"zh": "蓝", "ja": "青", "fr": "Bleu", "ru": "Синий", "de": "Blau", "pt": "Azul", "es": "Azul", "ko": "파랑", "it": "Blu"},
    "White": {"zh": "白", "ja": "白", "fr": "Blanc", "ru": "Белый", "de": "Weiß", "pt": "Branco", "es": "Blanco", "ko": "흰색", "it": "Bianco"},
    "Black": {"zh": "黑", "ja": "黒", "fr": "Noir", "ru": "Чёрный", "de": "Schwarz", "pt": "Preto", "es": "Negro", "ko": "검정", "it": "Nero"},
    "Gray": {"zh": "灰", "ja": "グレー", "fr": "Gris", "ru": "Серый", "de": "Grau", "pt": "Cinza", "es": "Gris", "ko": "회색", "it": "Grigio"},
    "click/arrows to switch · ESC to quit": {"zh": "点击/方向键切换 · ESC 退出", "ja": "クリック/矢印で切替 · ESC 終了", "fr": "clic/flèches pour changer · Échap pour quitter", "ru": "клик/стрелки — смена · ESC — выход", "de": "Klick/Pfeile wechseln · ESC beenden", "pt": "clique/setas para trocar · ESC para sair", "es": "clic/flechas para cambiar · ESC para salir", "ko": "클릭/방향키 전환 · ESC 종료", "it": "clic/frecce per cambiare · ESC per uscire"},

    # ---- screen page ----
    "Start Dead Pixel Test (full-screen)": {"zh": "开始坏点检测（全屏纯色）", "ja": "デッドピクセル検査を開始（全画面）", "fr": "Démarrer le test de pixels morts (plein écran)", "ru": "Начать проверку битых пикселей", "de": "Pixelfehler-Test starten (Vollbild)", "pt": "Iniciar teste de pixels mortos (tela cheia)", "es": "Iniciar prueba de píxeles muertos (pantalla completa)", "ko": "불량 화소 검사 시작 (전체 화면)", "it": "Avvia test pixel morti (schermo intero)"},
    "Dead pixel result": {"zh": "坏点检测结果", "ja": "デッドピクセル結果", "fr": "Résultat pixels morts", "ru": "Результат по пикселям", "de": "Pixelfehler-Ergebnis", "pt": "Resultado de pixels mortos", "es": "Resultado de píxeles muertos", "ko": "불량 화소 결과", "it": "Risultato pixel morti"},
    "No dead pixel": {"zh": "无坏点", "ja": "デッドピクセルなし", "fr": "Aucun pixel mort", "ru": "Нет битых пикселей", "de": "Keine Pixelfehler", "pt": "Sem pixels mortos", "es": "Sin píxeles muertos", "ko": "불량 화소 없음", "it": "Nessun pixel morto"},
    "Dead pixel found": {"zh": "发现坏点", "ja": "デッドピクセルあり", "fr": "Pixel mort détecté", "ru": "Найден битый пиксель", "de": "Pixelfehler gefunden", "pt": "Pixel morto encontrado", "es": "Píxel muerto encontrado", "ko": "불량 화소 발견", "it": "Pixel morto trovato"},

    # ---- keyboard / mouse ----
    "Tested {0} / {1} keys": {"zh": "已测 {0} / {1} 键", "ja": "テスト済み {0} / {1} キー", "fr": "{0} / {1} touches testées", "ru": "Проверено {0} / {1} клавиш", "de": "{0} / {1} Tasten getestet", "pt": "{0} / {1} teclas testadas", "es": "{0} / {1} teclas probadas", "ko": "{0} / {1} 키 테스트됨", "it": "{0} / {1} tasti testati"},
    "Untested": {"zh": "未测", "ja": "未テスト", "fr": "Non testées", "ru": "Не проверено", "de": "Ungetestet", "pt": "Não testadas", "es": "Sin probar", "ko": "미테스트", "it": "Non testati"},
    "All keys pressed ✓": {"zh": "所有键均已按下 ✓", "ja": "すべてのキーを押しました ✓", "fr": "Toutes les touches pressées ✓", "ru": "Все клавиши нажаты ✓", "de": "Alle Tasten gedrückt ✓", "pt": "Todas as teclas pressionadas ✓", "es": "Todas las teclas pulsadas ✓", "ko": "모든 키를 눌렀습니다 ✓", "it": "Tutti i tasti premuti ✓"},
    "Left": {"zh": "左键", "ja": "左ボタン", "fr": "Gauche", "ru": "Левая", "de": "Links", "pt": "Esquerdo", "es": "Izquierdo", "ko": "왼쪽", "it": "Sinistro"},
    "Middle": {"zh": "中键", "ja": "中ボタン", "fr": "Milieu", "ru": "Средняя", "de": "Mitte", "pt": "Meio", "es": "Central", "ko": "가운데", "it": "Centrale"},
    "Right": {"zh": "右键", "ja": "右ボタン", "fr": "Droit", "ru": "Правая", "de": "Rechts", "pt": "Direito", "es": "Derecho", "ko": "오른쪽", "it": "Destro"},
    "Wheel": {"zh": "滚轮", "ja": "ホイール", "fr": "Molette", "ru": "Колесо", "de": "Rad", "pt": "Roda", "es": "Rueda", "ko": "휠", "it": "Rotella"},
    "Moved": {"zh": "移动", "ja": "移動", "fr": "Déplacé", "ru": "Перемещение", "de": "Bewegt", "pt": "Movido", "es": "Movido", "ko": "이동", "it": "Spostato"},
    "Not pressed": {"zh": "未按", "ja": "未押下", "fr": "Non pressé", "ru": "Не нажата", "de": "Nicht gedrückt", "pt": "Não pressionado", "es": "Sin pulsar", "ko": "누르지 않음", "it": "Non premuto"},
    "up {0} / down {1}": {"zh": "上 {0} / 下 {1}", "ja": "上 {0} / 下 {1}", "fr": "haut {0} / bas {1}", "ru": "вверх {0} / вниз {1}", "de": "hoch {0} / runter {1}", "pt": "cima {0} / baixo {1}", "es": "arriba {0} / abajo {1}", "ko": "위 {0} / 아래 {1}", "it": "su {0} / giù {1}"},

    # ---- report page ----
    "Check Item": {"zh": "检测项", "ja": "検査項目", "fr": "Élément", "ru": "Пункт", "de": "Prüfpunkt", "pt": "Item", "es": "Elemento", "ko": "검사 항목", "it": "Elemento"},
    "Result": {"zh": "结果", "ja": "結果", "fr": "Résultat", "ru": "Результат", "de": "Ergebnis", "pt": "Resultado", "es": "Resultado", "ko": "결과", "it": "Risultato"},
    "{0} items · Pass {1} · Fail {2} · Unknown {3} · Skipped {4}": {"zh": "共 {0} 项 · 通过 {1} · 失败 {2} · 未知 {3} · 跳过 {4}", "ja": "合計 {0} 項目 · 合格 {1} · 失敗 {2} · 不明 {3} · スキップ {4}", "fr": "{0} éléments · Réussi {1} · Échec {2} · Inconnu {3} · Ignoré {4}", "ru": "{0} пунктов · Пройдено {1} · Сбой {2} · Неизвестно {3} · Пропущено {4}", "de": "{0} Punkte · Bestanden {1} · Fehler {2} · Unbekannt {3} · Übersprungen {4}", "pt": "{0} itens · Aprovado {1} · Falha {2} · Desconhecido {3} · Ignorado {4}", "es": "{0} elementos · Aprobado {1} · Fallido {2} · Desconocido {3} · Omitido {4}", "ko": "총 {0} 항목 · 통과 {1} · 실패 {2} · 알 수 없음 {3} · 건너뜀 {4}", "it": "{0} elementi · Superato {1} · Non superato {2} · Sconosciuto {3} · Saltato {4}"},
    "Export succeeded": {"zh": "导出成功", "ja": "エクスポート成功", "fr": "Export réussi", "ru": "Экспорт выполнен", "de": "Export erfolgreich", "pt": "Exportação bem-sucedida", "es": "Exportación correcta", "ko": "내보내기 성공", "it": "Esportazione riuscita"},
    "Export failed": {"zh": "导出失败", "ja": "エクスポート失敗", "fr": "Échec de l'export", "ru": "Ошибка экспорта", "de": "Export fehlgeschlagen", "pt": "Falha na exportação", "es": "Error de exportación", "ko": "내보내기 실패", "it": "Esportazione fallita"},
    "Report saved to": {"zh": "报告已保存到", "ja": "レポートを保存しました", "fr": "Rapport enregistré dans", "ru": "Отчёт сохранён в", "de": "Bericht gespeichert unter", "pt": "Relatório salvo em", "es": "Informe guardado en", "ko": "보고서가 저장됨", "it": "Rapporto salvato in"},
    "Export Report": {"zh": "导出验机报告", "ja": "レポートをエクスポート", "fr": "Exporter le rapport", "ru": "Экспорт отчёта", "de": "Bericht exportieren", "pt": "Exportar relatório", "es": "Exportar informe", "ko": "보고서 내보내기", "it": "Esporta rapporto"},

    # ---- report document ----
    "Inspection Report": {"zh": "验机报告", "ja": "検査レポート", "fr": "Rapport d'inspection", "ru": "Отчёт о проверке", "de": "Prüfbericht", "pt": "Relatório de inspeção", "es": "Informe de inspección", "ko": "검사 보고서", "it": "Rapporto di ispezione"},
    "Generated at": {"zh": "生成时间", "ja": "生成日時", "fr": "Généré le", "ru": "Создан", "de": "Erstellt am", "pt": "Gerado em", "es": "Generado el", "ko": "생성 시간", "it": "Generato il"},
    "Host": {"zh": "主机", "ja": "ホスト", "fr": "Hôte", "ru": "Хост", "de": "Host", "pt": "Host", "es": "Host", "ko": "호스트", "it": "Host"},
    "Platform": {"zh": "平台", "ja": "プラットフォーム", "fr": "Plateforme", "ru": "Платформа", "de": "Plattform", "pt": "Plataforma", "es": "Plataforma", "ko": "플랫폼", "it": "Piattaforma"},
    "Summary": {"zh": "结果总览", "ja": "結果サマリー", "fr": "Résumé", "ru": "Сводка", "de": "Zusammenfassung", "pt": "Resumo", "es": "Resumen", "ko": "결과 요약", "it": "Riepilogo"},
    "Details": {"zh": "检测明细", "ja": "検査詳細", "fr": "Détails", "ru": "Детали", "de": "Details", "pt": "Detalhes", "es": "Detalles", "ko": "검사 상세", "it": "Dettagli"},
    "Data": {"zh": "数据", "ja": "データ", "fr": "Données", "ru": "Данные", "de": "Daten", "pt": "Dados", "es": "Datos", "ko": "데이터", "it": "Dati"},

    # ---- misc ----
    "Scanning hardware…": {"zh": "正在采集硬件信息…", "ja": "ハードウェア情報を収集中…", "fr": "Détection du matériel…", "ru": "Сбор данных…", "de": "Hardware wird erkannt…", "pt": "Detectando hardware…", "es": "Detectando hardware…", "ko": "하드웨어 정보 수집 중…", "it": "Rilevamento hardware…"},
    "Scan failed": {"zh": "采集失败", "ja": "収集に失敗", "fr": "Échec de la détection", "ru": "Ошибка сбора", "de": "Erkennung fehlgeschlagen", "pt": "Falha na detecção", "es": "Error de detección", "ko": "수집 실패", "it": "Rilevamento fallito"},
    "Slot": {"zh": "插槽", "ja": "スロット", "fr": "Emplacement", "ru": "Слот", "de": "Steckplatz", "pt": "Slot", "es": "Ranura", "ko": "슬롯", "it": "Slot"},
    "Location": {"zh": "位置", "ja": "場所", "fr": "Emplacement", "ru": "Расположение", "de": "Ort", "pt": "Local", "es": "Ubicación", "ko": "위치", "it": "Posizione"},
    "None": {"zh": "无", "ja": "なし", "fr": "Aucun", "ru": "Нет", "de": "Keine", "pt": "Nenhum", "es": "Ninguno", "ko": "없음", "it": "Nessuno"},
    "N/A": {"zh": "N/A", "ja": "N/A", "fr": "N/A", "ru": "Н/Д", "de": "k. A.", "pt": "N/D", "es": "N/D", "ko": "N/A", "it": "N/D"},
    "Ready": {"zh": "就绪", "ja": "準備完了", "fr": "Prêt", "ru": "Готово", "de": "Bereit", "pt": "Pronto", "es": "Listo", "ko": "준비됨", "it": "Pronto"},
    "Confirm": {"zh": "确认", "ja": "確認", "fr": "Confirmer", "ru": "Подтвердить", "de": "Bestätigen", "pt": "Confirmar", "es": "Confirmar", "ko": "확인", "it": "Conferma"},
    "Start Listening": {"zh": "开始监听", "ja": "リスニング開始", "fr": "Écouter", "ru": "Начать прослушивание", "de": "Abhören starten", "pt": "Ouvir", "es": "Escuchar", "ko": "듣기 시작", "it": "Inizia ascolto"},
    "Stop Listening": {"zh": "停止监听", "ja": "リスニング停止", "fr": "Arrêter", "ru": "Остановить", "de": "Abhören stoppen", "pt": "Parar", "es": "Detener", "ko": "듣기 중지", "it": "Ferma ascolto"},
    "Record 3s & Playback": {"zh": "录音 3 秒并回放", "ja": "3秒録音して再生", "fr": "Enregistrer 3 s et lire", "ru": "Запись 3 с и воспроизведение", "de": "3 s aufnehmen & abspielen", "pt": "Gravar 3s e reproduzir", "es": "Grabar 3 s y reproducir", "ko": "3초 녹음 후 재생", "it": "Registra 3s e riproduci"},
    "Start Preview": {"zh": "开始预览", "ja": "プレビュー開始", "fr": "Aperçu", "ru": "Предпросмотр", "de": "Vorschau starten", "pt": "Iniciar visualização", "es": "Iniciar vista previa", "ko": "미리보기 시작", "it": "Avvia anteprima"},
    "Stop Preview": {"zh": "停止预览", "ja": "プレビュー停止", "fr": "Arrêter l'aperçu", "ru": "Стоп предпросмотр", "de": "Vorschau stoppen", "pt": "Parar visualização", "es": "Detener vista previa", "ko": "미리보기 중지", "it": "Ferma anteprima"},
    "Snapshot": {"zh": "拍照", "ja": "撮影", "fr": "Capturer", "ru": "Снимок", "de": "Foto", "pt": "Foto", "es": "Capturar", "ko": "촬영", "it": "Scatta"},
    "Picture OK ✓": {"zh": "画面正常 ✓", "ja": "映像正常 ✓", "fr": "Image OK ✓", "ru": "Картинка OK ✓", "de": "Bild OK ✓", "pt": "Imagem OK ✓", "es": "Imagen OK ✓", "ko": "화면 정상 ✓", "it": "Immagine OK ✓"},
    "Stress duration (s)": {"zh": "压力测试时长（秒）", "ja": "負荷テスト時間（秒）", "fr": "Durée du stress (s)", "ru": "Длительность (с)", "de": "Belastungsdauer (s)", "pt": "Duração (s)", "es": "Duración (s)", "ko": "부하 시간(초)", "it": "Durata stress (s)"},
    "Start Stress Test": {"zh": "开始压力测试", "ja": "負荷テスト開始", "fr": "Démarrer le stress", "ru": "Начать нагрузку", "de": "Stresstest starten", "pt": "Iniciar teste de estresse", "es": "Iniciar prueba de estrés", "ko": "부하 테스트 시작", "it": "Avvia stress test"},
    "No temperature access on this platform": {"zh": "当前平台不支持直接读取 CPU 温度/风扇转速（macOS 需要 SMC 权限），将依据压力测试中的频率与占用率判断散热。", "ja": "このプラットフォームでは CPU 温度/ファン回転数を直接取得できません。負荷テスト中の周波数と使用率で判断します。", "fr": "La température CPU n'est pas accessible sur cette plateforme (macOS nécessite SMC).", "ru": "Температура ЦП недоступна на этой платформе (macOS требует SMC).", "de": "CPU-Temperatur ist auf dieser Plattform nicht zugänglich.", "pt": "Temperatura da CPU não acessível nesta plataforma.", "es": "Temperatura de CPU no accesible en esta plataforma.", "ko": "이 플랫폼에서는 CPU 온도를 직접 읽을 수 없습니다.", "it": "Temperatura CPU non accessibile su questa piattaforma."},
    "Temperature": {"zh": "温度", "ja": "温度", "fr": "Température", "ru": "Температура", "de": "Temperatur", "pt": "Temperatura", "es": "Temperatura", "ko": "온도", "it": "Temperatura"},
    "Fans": {"zh": "风扇", "ja": "ファン", "fr": "Ventilateurs", "ru": "Вентиляторы", "de": "Lüfter", "pt": "Ventoinhas", "es": "Ventiladores", "ko": "팬", "it": "Ventole"},

    # ---- permissions ----
    "Open System Settings": {"zh": "打开系统设置", "ja": "システム設定を開く", "fr": "Ouvrir les réglages système", "ru": "Открыть настройки", "de": "Systemeinstellungen öffnen", "pt": "Abrir Ajustes do Sistema", "es": "Abrir Ajustes del Sistema", "ko": "시스템 설정 열기", "it": "Apri Impostazioni di Sistema"},
    "Camera permission denied. Enable it in System Settings.": {"zh": "摄像头权限被拒绝，请在系统设置中开启。", "ja": "カメラの権限が拒否されました。システム設定で許可してください。", "fr": "Autorisation caméra refusée. Activez-la dans les réglages système.", "ru": "Доступ к камере запрещён. Включите в настройках.", "de": "Kamerazugriff verweigert. In den Systemeinstellungen erlauben.", "pt": "Permissão da câmera negada. Habilite nas Ajustes.", "es": "Permiso de cámara denegado. Actívelo en Ajustes.", "ko": "카메라 권한이 거부되었습니다. 시스템 설정에서 허용하세요.", "it": "Autorizzazione fotocamera negata. Abilitala nelle Impostazioni."},
    "Camera access is restricted.": {"zh": "摄像头访问受限。", "ja": "カメラへのアクセスが制限されています。", "fr": "Accès caméra restreint.", "ru": "Доступ к камере ограничен.", "de": "Kamerazugriff eingeschränkt.", "pt": "Acesso à câmera restrito.", "es": "Acceso a la cámara restringido.", "ko": "카메라 접근이 제한되었습니다.", "it": "Accesso alla fotocamera limitato."},
    "Camera permission not granted yet. Click Start Preview to allow access.": {"zh": "尚未授予摄像头权限，点击「开始预览」以授权。", "ja": "カメラ権限が未付与です。「プレビュー開始」を押して許可してください。", "fr": "Autorisation caméra non accordée. Cliquez sur « Aperçu » pour autoriser.", "ru": "Доступ к камере ещё не предоставлен. Нажмите «Предпросмотр».", "de": "Kamerazugriff noch nicht erteilt. «Vorschau starten» klicken.", "pt": "Permissão da câmera ainda não concedida. Clique em «Iniciar visualização».", "es": "Permiso de cámara aún no concedido. Pulse «Iniciar vista previa».", "ko": "카메라 권한이 아직 부여되지 않았습니다. «미리보기 시작»을 누르세요.", "it": "Autorizzazione fotocamera non concessa. Clicca «Avvia anteprima»."},
    "Requesting camera permission…": {"zh": "正在申请摄像头权限…", "ja": "カメラ権限を申請中…", "fr": "Demande d'autorisation caméra…", "ru": "Запрос доступа к камере…", "de": "Kamerazugriff wird angefordert…", "pt": "Solicitando permissão da câmera…", "es": "Solicitando permiso de cámara…", "ko": "카메라 권한 요청 중…", "it": "Richiesta autorizzazione fotocamera…"},
    "Microphone permission denied. Enable it in System Settings.": {"zh": "麦克风权限被拒绝，请在系统设置中开启。", "ja": "マイクの権限が拒否されました。システム設定で許可してください。", "fr": "Autorisation micro refusée. Activez-la dans les réglages système.", "ru": "Доступ к микрофону запрещён. Включите в настройках.", "de": "Mikrofonzugriff verweigert. In den Systemeinstellungen erlauben.", "pt": "Permissão do microfone negada. Habilite nas Ajustes.", "es": "Permiso de micrófono denegado. Actívelo en Ajustes.", "ko": "마이크 권한이 거부되었습니다. 시스템 설정에서 허용하세요.", "it": "Autorizzazione microfono negata. Abilitala nelle Impostazioni."},
    "Microphone permission not granted yet. Click Start Listening to allow access.": {"zh": "尚未授予麦克风权限，点击「开始监听」以授权。", "ja": "マイク権限が未付与です。「リスニング開始」を押して許可してください。", "fr": "Autorisation micro non accordée. Cliquez sur « Écouter » pour autoriser.", "ru": "Доступ к микрофону ещё не предоставлен. Нажмите «Начать прослушивание».", "de": "Mikrofonzugriff noch nicht erteilt. «Abhören starten» klicken.", "pt": "Permissão do microfone ainda não concedida. Clique em «Ouvir».", "es": "Permiso de micrófono aún no concedido. Pulse «Escuchar».", "ko": "마이크 권한이 아직 부여되지 않았습니다. «듣기 시작»을 누르세요.", "it": "Autorizzazione microfono non concessa. Clicca «Inizia ascolto»."},
    "Requesting microphone permission…": {"zh": "正在申请麦克风权限…", "ja": "マイク権限を申請中…", "fr": "Demande d'autorisation micro…", "ru": "Запрос доступа к микрофону…", "de": "Mikrofonzugriff wird angefordert…", "pt": "Solicitando permissão do microfone…", "es": "Solicitando permiso de micrófono…", "ko": "마이크 권한 요청 중…", "it": "Richiesta autorizzazione microfono…"},
    "Camera permission denied": {"zh": "摄像头权限被拒绝", "ja": "カメラ権限が拒否されました", "fr": "Autorisation caméra refusée", "ru": "Доступ к камере запрещён", "de": "Kamerazugriff verweigert", "pt": "Permissão da câmera negada", "es": "Permiso de cámara denegado", "ko": "카메라 권한 거부됨", "it": "Autorizzazione fotocamera negata"},
    "Microphone permission denied": {"zh": "麦克风权限被拒绝", "ja": "マイク権限が拒否されました", "fr": "Autorisation micro refusée", "ru": "Доступ к микрофону запрещён", "de": "Mikrofonzugriff verweigert", "pt": "Permissão do microfone negada", "es": "Permiso de micrófono denegado", "ko": "마이크 권한 거부됨", "it": "Autorizzazione microfono negata"},

    # ---- mark names (report item names) ----
    "Status": {"zh": "状态", "ja": "状態", "fr": "Statut", "ru": "Статус", "de": "Status", "pt": "Status", "es": "Estado", "ko": "상태", "it": "Stato"},
    "Dead Pixel": {"zh": "坏点检测", "ja": "デッドピクセル", "fr": "Pixel mort", "ru": "Битые пиксели", "de": "Pixelfehler", "pt": "Pixel morto", "es": "Píxel muerto", "ko": "불량 화소", "it": "Pixel morto"},
    "Camera Image": {"zh": "摄像头成像", "ja": "カメラ映像", "fr": "Image caméra", "ru": "Изображение камеры", "de": "Kamerabild", "pt": "Imagem da câmera", "es": "Imagen de cámara", "ko": "카메라 이미지", "it": "Immagine fotocamera"},
    "Microphone Input": {"zh": "麦克风收音", "ja": "マイク入力", "fr": "Entrée micro", "ru": "Вход микрофона", "de": "Mikrofoneingang", "pt": "Entrada de microfone", "es": "Entrada de micrófono", "ko": "마이크 입력", "it": "Ingresso microfono"},
    "Left Channel": {"zh": "左声道", "ja": "左チャンネル", "fr": "Canal gauche", "ru": "Левый канал", "de": "Linker Kanal", "pt": "Canal esquerdo", "es": "Canal izquierdo", "ko": "왼쪽 채널", "it": "Canale sinistro"},
    "Right Channel": {"zh": "右声道", "ja": "右チャンネル", "fr": "Canal droit", "ru": "Правый канал", "de": "Rechter Kanal", "pt": "Canal direito", "es": "Canal derecho", "ko": "오른쪽 채널", "it": "Canale destro"},
    "Both Channels": {"zh": "双声道", "ja": "両チャンネル", "fr": "Les deux canaux", "ru": "Оба канала", "de": "Beide Kanäle", "pt": "Ambos os canais", "es": "Ambos canales", "ko": "양쪽 채널", "it": "Entrambi i canali"},
    "Keyboard Keys": {"zh": "键盘按键", "ja": "キーボードのキー", "fr": "Touches du clavier", "ru": "Клавиши", "de": "Tastaturtasten", "pt": "Teclas", "es": "Teclas", "ko": "키보드 키", "it": "Tasti tastiera"},
    "Mouse Buttons": {"zh": "鼠标按键", "ja": "マウスボタン", "fr": "Boutons souris", "ru": "Кнопки мыши", "de": "Maustasten", "pt": "Botões do mouse", "es": "Botones del ratón", "ko": "마우스 버튼", "it": "Tasti mouse"},
    "Temperature Sensors": {"zh": "温度传感器", "ja": "温度センサー", "fr": "Capteurs de température", "ru": "Датчики температуры", "de": "Temperatursensoren", "pt": "Sensores de temperatura", "es": "Sensores de temperatura", "ko": "온도 센서", "it": "Sensori di temperatura"},
    "Stress Test": {"zh": "压力测试", "ja": "負荷テスト", "fr": "Test de stress", "ru": "Нагрузочный тест", "de": "Stresstest", "pt": "Teste de estresse", "es": "Prueba de estrés", "ko": "부하 테스트", "it": "Stress test"},
    "Disk Benchmark": {"zh": "磁盘测速", "ja": "ディスクベンチマーク", "fr": "Benchmark disque", "ru": "Тест диска", "de": "Disk-Benchmark", "pt": "Benchmark de disco", "es": "Prueba de disco", "ko": "디스크 벤치마크", "it": "Benchmark disco"},
    "Memory Info": {"zh": "内存信息", "ja": "メモリ情報", "fr": "Infos mémoire", "ru": "Инфо памяти", "de": "Speicherinfo", "pt": "Infos de memória", "es": "Info de memoria", "ko": "메모리 정보", "it": "Info memoria"},
    "Memory Self-Test": {"zh": "内存自检", "ja": "メモリ自己テスト", "fr": "Autotest mémoire", "ru": "Самотест памяти", "de": "Speicher-Selbsttest", "pt": "Autoteste de memória", "es": "Autoprueba de memoria", "ko": "메모리 자체 테스트", "it": "Autotest memoria"},
    "Network Interfaces": {"zh": "网络接口", "ja": "ネットワークインターフェース", "fr": "Interfaces réseau", "ru": "Сетевые интерфейсы", "de": "Netzwerkschnittstellen", "pt": "Interfaces de rede", "es": "Interfaces de red", "ko": "네트워크 인터페이스", "it": "Interfacce di rete"},
    "Network Latency": {"zh": "网络延迟", "ja": "ネットワーク遅延", "fr": "Latence réseau", "ru": "Задержка сети", "de": "Netzwerklatenz", "pt": "Latência de rede", "es": "Latencia de red", "ko": "네트워크 지연", "it": "Latenza di rete"},

    # ---- messages ----
    "No camera detected": {"zh": "未检测到摄像头设备", "ja": "カメラが検出されません", "fr": "Aucune caméra détectée", "ru": "Камера не обнаружена", "de": "Keine Kamera erkannt", "pt": "Nenhuma câmera detectada", "es": "No se detectó cámara", "ko": "카메라가 감지되지 않음", "it": "Nessuna fotocamera rilevata"},
    "No microphone input detected": {"zh": "未检测到麦克风输入设备", "ja": "マイク入力が検出されません", "fr": "Aucune entrée micro détectée", "ru": "Микрофон не обнаружен", "de": "Kein Mikrofon erkannt", "pt": "Nenhum microfone detectado", "es": "No se detectó micrófono", "ko": "마이크 입력이 감지되지 않음", "it": "Nessun microfono rilevato"},
    "Previewing…": {"zh": "预览中…", "ja": "プレビュー中…", "fr": "Aperçu…", "ru": "Предпросмотр…", "de": "Vorschau…", "pt": "Visualizando…", "es": "Vista previa…", "ko": "미리보기 중…", "it": "Anteprima…"},
    "Opened": {"zh": "已打开", "ja": "開きました", "fr": "Ouvert", "ru": "Открыто", "de": "Geöffnet", "pt": "Aberto", "es": "Abierto", "ko": "열림", "it": "Aperto"},
    "Failed to open": {"zh": "打开失败", "ja": "開けませんでした", "fr": "Échec d'ouverture", "ru": "Ошибка открытия", "de": "Öffnen fehlgeschlagen", "pt": "Falha ao abrir", "es": "Error al abrir", "ko": "열기 실패", "it": "Apertura fallita"},
    "Stopped": {"zh": "已停止", "ja": "停止しました", "fr": "Arrêté", "ru": "Остановлено", "de": "Gestoppt", "pt": "Parado", "es": "Detenido", "ko": "중지됨", "it": "Fermato"},
    "Snapshot saved": {"zh": "拍照成功", "ja": "撮影成功", "fr": "Cliché enregistré", "ru": "Снимок сохранён", "de": "Foto gespeichert", "pt": "Foto salva", "es": "Captura guardada", "ko": "촬영 저장됨", "it": "Scatto salvato"},
    "Confirmed OK ✓": {"zh": "已确认正常 ✓", "ja": "正常を確認しました ✓", "fr": "Confirmé OK ✓", "ru": "Подтверждено ✓", "de": "OK bestätigt ✓", "pt": "Confirmado OK ✓", "es": "Confirmado OK ✓", "ko": "정상 확인됨 ✓", "it": "Confermato OK ✓"},
    "Image OK": {"zh": "画面正常", "ja": "映像正常", "fr": "Image OK", "ru": "Изображение OK", "de": "Bild OK", "pt": "Imagem OK", "es": "Imagen OK", "ko": "이미지 정상", "it": "Immagine OK"},
    "Listening… speak into the mic": {"zh": "监听中… 请对麦克风说话", "ja": "リスニング中… マイクに向かって話してください", "fr": "Écoute… parlez dans le micro", "ru": "Прослушивание… говорите в микрофон", "de": "Hört zu… ins Mikrofon sprechen", "pt": "Ouvindo… fale no microfone", "es": "Escuchando… hable al micrófono", "ko": "듣는 중… 마이크에 대고 말하세요", "it": "In ascolto… parla nel microfono"},
    "Input device opened": {"zh": "已打开输入设备", "ja": "入力デバイスを開きました", "fr": "Périphérique d'entrée ouvert", "ru": "Входное устройство открыто", "de": "Eingabegerät geöffnet", "pt": "Dispositivo de entrada aberto", "es": "Dispositivo de entrada abierto", "ko": "입력 장치 열림", "it": "Dispositivo di ingresso aperto"},
    "Recording 3s…": {"zh": "正在录音 3 秒…", "ja": "3秒録音中…", "fr": "Enregistrement 3 s…", "ru": "Запись 3 с…", "de": "Nehme 3 s auf…", "pt": "Gravando 3s…", "es": "Grabando 3 s…", "ko": "3초 녹음 중…", "it": "Registrazione 3s…"},
    "Recording failed": {"zh": "录音失败", "ja": "録音に失敗", "fr": "Échec de l'enregistrement", "ru": "Ошибка записи", "de": "Aufnahme fehlgeschlagen", "pt": "Falha na gravação", "es": "Error de grabación", "ko": "녹음 실패", "it": "Registrazione fallita"},
    "Recorded, playing back": {"zh": "录音完成，正在回放", "ja": "録音完了、再生中", "fr": "Enregistré, lecture", "ru": "Записано, воспроизведение", "de": "Aufgenommen, Wiedergabe", "pt": "Gravado, reproduzindo", "es": "Grabado, reproduciendo", "ko": "녹음 완료, 재생 중", "it": "Registrato, riproduzione"},
    "Captured voice signal (peak {0})": {"zh": "采集到语音信号（峰值 {0}）", "ja": "音声信号を取得（ピーク {0}）", "fr": "Signal vocal capturé (pic {0})", "ru": "Сигнал захвачен (пик {0})", "de": "Sprachsignal erfasst (Peak {0})", "pt": "Sinal de voz capturado (pico {0})", "es": "Señal de voz capturada (pico {0})", "ko": "음성 신호 캡처됨 (피크 {0})", "it": "Segnale vocale catturato (picco {0})"},
    "Click to play test tones; note left/right:": {"zh": "点击播放测试音，注意区分左右声道：", "ja": "テスト音を再生し、左右を確認：", "fr": "Cliquez pour jouer les tonalités ; notez gauche/droite :", "ru": "Нажмите для воспроизведения; следите за левым/правым:", "de": "Klicken zum Abspielen; links/rechts beachten:", "pt": "Clique para reproduzir; observe esquerda/direita:", "es": "Haga clic para reproducir; observe izquierda/derecha:", "ko": "클릭하여 재생, 좌우를 확인:", "it": "Clicca per riprodurre; nota sinistra/destra:"},
    "Sweep (low→high)": {"zh": "扫频（低频→高频）", "ja": "スイープ（低→高）", "fr": "Balayage (bas→haut)", "ru": "Свип (низк→высок)", "de": "Sweep (tief→hoch)", "pt": "Varredura (baixo→alto)", "es": "Barrido (bajo→alto)", "ko": "스윕 (저→고)", "it": "Sweep (basso→alto)"},
    "Channel confirmation:": {"zh": "声道确认：", "ja": "チャンネル確認：", "fr": "Confirmation des canaux :", "ru": "Подтверждение каналов:", "de": "Kanalbestätigung:", "pt": "Confirmação de canal:", "es": "Confirmación de canal:", "ko": "채널 확인:", "it": "Conferma canale:"},
    "Left OK ✓": {"zh": "左声道正常 ✓", "ja": "左正常 ✓", "fr": "Gauche OK ✓", "ru": "Левый OK ✓", "de": "Links OK ✓", "pt": "Esquerdo OK ✓", "es": "Izquierdo OK ✓", "ko": "왼쪽 정상 ✓", "it": "Sinistro OK ✓"},
    "Left silent ✗": {"zh": "左声道无声 ✗", "ja": "左無音 ✗", "fr": "Gauche muet ✗", "ru": "Левый нет звука ✗", "de": "Links stumm ✗", "pt": "Esquerdo mudo ✗", "es": "Izquierdo sin sonido ✗", "ko": "왼쪽 무음 ✗", "it": "Sinistro muto ✗"},
    "Right OK ✓": {"zh": "右声道正常 ✓", "ja": "右正常 ✓", "fr": "Droit OK ✓", "ru": "Правый OK ✓", "de": "Rechts OK ✓", "pt": "Direito OK ✓", "es": "Derecho OK ✓", "ko": "오른쪽 정상 ✓", "it": "Destro OK ✓"},
    "Right silent ✗": {"zh": "右声道无声 ✗", "ja": "右無音 ✗", "fr": "Droit muet ✗", "ru": "Правый нет звука ✗", "de": "Rechts stumm ✗", "pt": "Direito mudo ✗", "es": "Derecho sin sonido ✗", "ko": "오른쪽 무음 ✗", "it": "Destro muto ✗"},
    "Playing": {"zh": "正在播放", "ja": "再生中", "fr": "Lecture", "ru": "Воспроизведение", "de": "Wiedergabe", "pt": "Reproduzindo", "es": "Reproduciendo", "ko": "재생 중", "it": "Riproduzione"},
    "OK": {"zh": "正常", "ja": "正常", "fr": "OK", "ru": "OK", "de": "OK", "pt": "OK", "es": "OK", "ko": "정상", "it": "OK"},
    "silent": {"zh": "无声", "ja": "無音", "fr": "muet", "ru": "нет звука", "de": "stumm", "pt": "mudo", "es": "sin sonido", "ko": "무음", "it": "muto"},
    "marked faulty ✗": {"zh": "已标记异常 ✗", "ja": "異常をマーク ✗", "fr": "marqué défectueux ✗", "ru": "помечено ✗", "de": "als fehlerhaft markiert ✗", "pt": "marcado com falha ✗", "es": "marcado como fallido ✗", "ko": "이상 표시됨 ✗", "it": "segnato guasto ✗"},
    "All OK ✓": {"zh": "全部正常 ✓", "ja": "すべて正常 ✓", "fr": "Tout OK ✓", "ru": "Всё OK ✓", "de": "Alles OK ✓", "pt": "Tudo OK ✓", "es": "Todo OK ✓", "ko": "모두 정상 ✓", "it": "Tutto OK ✓"},
    "Faulty key ✗": {"zh": "有按键失灵 ✗", "ja": "キー不具合 ✗", "fr": "Touche défectueuse ✗", "ru": "Клавиша не работает ✗", "de": "Taste defekt ✗", "pt": "Tecla com falha ✗", "es": "Tecla defectuosa ✗", "ko": "키 고장 ✗", "it": "Tasto guasto ✗"},
    "Confirmed {0}/{1} keys OK": {"zh": "已确认 {0}/{1} 键正常", "ja": "{0}/{1} キー正常を確認", "fr": "{0}/{1} touches confirmées OK", "ru": "Подтверждено {0}/{1} клавиш", "de": "{0}/{1} Tasten OK bestätigt", "pt": "{0}/{1} teclas confirmadas", "es": "{0}/{1} teclas confirmadas", "ko": "{0}/{1} 키 정상 확인", "it": "{0}/{1} tasti confermati"},
    "Keys likely faulty: {0}": {"zh": "以下按键疑似失灵：{0}", "ja": "不具合の疑い：{0}", "fr": "Touches probablement défectueuses : {0}", "ru": "Вероятно неисправны: {0}", "de": "Möglicherweise defekt: {0}", "pt": "Teclas possivelmente com falha: {0}", "es": "Teclas posiblemente defectuosas: {0}", "ko": "고장 의심 키: {0}", "it": "Tasti probabilmente guasti: {0}"},
    "Mouse buttons/wheel/movement OK": {"zh": "鼠标按键/滚轮/移动均正常", "ja": "マウス正常", "fr": "Souris OK", "ru": "Мышь в порядке", "de": "Maus OK", "pt": "Mouse OK", "es": "Ratón OK", "ko": "마우스 정상", "it": "Mouse OK"},
    "Mouse marked faulty": {"zh": "已标记鼠标异常", "ja": "マウス異常をマーク", "fr": "Souris marquée défectueuse", "ru": "Мышь помечена", "de": "Maus als defekt markiert", "pt": "Mouse marcado com falha", "es": "Ratón marcado como defectuoso", "ko": "마우스 이상 표시", "it": "Mouse segnato guasto"},
    "Capture the pointer and sweep the pad to find dead spots": {"zh": "捕获鼠标并扫过整个触控板，找出失灵区域（死点）", "ja": "ポインタをキャプチャしてパッド全体を走査し、不感領域を検出", "fr": "Capturez le pointeur et balayez le pavé pour trouver les zones mortes", "ru": "Захватите указатель и проведите по всей панели для поиска мёртвых зон", "de": "Zeiger fangen und Pad abfahren, um tote Zonen zu finden", "pt": "Capture o ponteiro e percorra o touchpad para achar zonas mortas", "es": "Capture el puntero y barra el panel para encontrar zonas muertas", "ko": "포인터를 캡처하고 패드 전체를 훑어 불량 영역을 찾습니다", "it": "Cattura il puntatore e percorri il pad per trovare le zone morte"},
    "Start Capture": {"zh": "开始捕获", "ja": "キャプチャ開始", "fr": "Démarrer la capture", "ru": "Захватить", "de": "Erfassen starten", "pt": "Iniciar captura", "es": "Iniciar captura", "ko": "캡처 시작", "it": "Avvia cattura"},
    "Stop Capture": {"zh": "停止捕获", "ja": "キャプチャ停止", "fr": "Arrêter la capture", "ru": "Остановить захват", "de": "Erfassung stoppen", "pt": "Parar captura", "es": "Detener captura", "ko": "캡처 중지", "it": "Ferma cattura"},
    "Press {0}+G to release": {"zh": "按 {0}+G 释放鼠标", "ja": "{0}+G でマウスを解放", "fr": "Appuyez sur {0}+G pour libérer", "ru": "Нажмите {0}+G для освобождения", "de": "{0}+G drücken zum Freigeben", "pt": "Pressione {0}+G para liberar", "es": "Pulse {0}+G para liberar", "ko": "{0}+G를 눌러 마우스 해제", "it": "Premi {0}+G per rilasciare"},
    "Click Start Capture to begin": {"zh": "点击「开始捕获」开始检测", "ja": "「キャプチャ開始」を押して開始", "fr": "Cliquez sur « Démarrer la capture »", "ru": "Нажмите «Захватить», чтобы начать", "de": "«Erfassen starten» klicken", "pt": "Clique em «Iniciar captura»", "es": "Pulse «Iniciar captura»", "ko": "«캡처 시작»을 눌러 시작", "it": "Clicca «Avvia cattura»"},
    "Coverage {0}/{1} cells · dead {2}": {"zh": "已覆盖 {0}/{1} 格 · 死点 {2}", "ja": "カバー {0}/{1} セル · 不感 {2}", "fr": "Couverture {0}/{1} cellules · mortes {2}", "ru": "Покрыто {0}/{1} ячеек · мёртвых {2}", "de": "Abdeckung {0}/{1} Zellen · tot {2}", "pt": "Cobertura {0}/{1} células · mortas {2}", "es": "Cobertura {0}/{1} celdas · muertas {2}", "ko": "커버리지 {0}/{1} 칸 · 불량 {2}", "it": "Copertura {0}/{1} celle · morte {2}"},
    "Coverage {0}/{1} cells": {"zh": "已覆盖 {0}/{1} 格", "ja": "カバー {0}/{1} セル", "fr": "Couverture {0}/{1} cellules", "ru": "Покрыто {0}/{1} ячеек", "de": "Abdeckung {0}/{1} Zellen", "pt": "Cobertura {0}/{1} células", "es": "Cobertura {0}/{1} celdas", "ko": "커버리지 {0}/{1} 칸", "it": "Copertura {0}/{1} celle"},
    "All cells covered ✓": {"zh": "所有格子已覆盖 ✓", "ja": "全セルをカバーしました ✓", "fr": "Toutes les cellules couvertes ✓", "ru": "Все ячейки покрыты ✓", "de": "Alle Zellen abgedeckt ✓", "pt": "Todas as células cobertas ✓", "es": "Todas las celdas cubiertas ✓", "ko": "모든 칸을 덮었습니다 ✓", "it": "Tutte le celle coperte ✓"},
    "Dead spots: {0} cells": {"zh": "死点：{0} 个格子", "ja": "不感領域：{0} セル", "fr": "Zones mortes : {0} cellules", "ru": "Мёртвые зоны: {0} ячеек", "de": "Tote Zonen: {0} Zellen", "pt": "Zonas mortas: {0} células", "es": "Zonas muertas: {0} celdas", "ko": "불량 영역: {0} 칸", "it": "Zone morte: {0} celle"},
    "Detected {0} temperature sensors": {"zh": "检测到 {0} 个温度传感器", "ja": "{0} 個の温度センサーを検出", "fr": "{0} capteurs de température détectés", "ru": "Обнаружено {0} датчиков", "de": "{0} Temperatursensoren erkannt", "pt": "{0} sensores detectados", "es": "{0} sensores detectados", "ko": "{0}개 온도 센서 감지", "it": "{0} sensori rilevati"},
    "Cannot read temperature sensors": {"zh": "无法读取温度传感器", "ja": "温度センサーを読み取れません", "fr": "Impossible de lire les capteurs", "ru": "Невозможно прочитать датчики", "de": "Sensoren nicht lesbar", "pt": "Não foi possível ler os sensores", "es": "No se pueden leer los sensores", "ko": "온도 센서를 읽을 수 없음", "it": "Impossibile leggere i sensori"},
    "Stress running…": {"zh": "正在加压…", "ja": "負荷テスト中…", "fr": "Stress en cours…", "ru": "Нагрузка…", "de": "Belastung läuft…", "pt": "Estresse em andamento…", "es": "Estrés en curso…", "ko": "부하 테스트 중…", "it": "Stress in corso…"},
    "CPU usage: {0}%": {"zh": "CPU 占用：{0}%", "ja": "CPU 使用率：{0}%", "fr": "Utilisation CPU : {0}%", "ru": "Загрузка ЦП: {0}%", "de": "CPU-Auslastung: {0}%", "pt": "Uso da CPU: {0}%", "es": "Uso de CPU: {0}%", "ko": "CPU 사용률: {0}%", "it": "Uso CPU: {0}%"},
    "Stress failed": {"zh": "压力测试出错", "ja": "負荷テスト失敗", "fr": "Échec du stress", "ru": "Ошибка нагрузки", "de": "Stresstest fehlgeschlagen", "pt": "Falha no estresse", "es": "Error de estrés", "ko": "부하 테스트 실패", "it": "Stress fallito"},
    "Duration {0}, {1} threads": {"zh": "持续 {0}，{1} 线程", "ja": "時間 {0}、{1} スレッド", "fr": "Durée {0}, {1} threads", "ru": "Длительность {0}, {1} потоков", "de": "Dauer {0}, {1} Threads", "pt": "Duração {0}, {1} threads", "es": "Duración {0}, {1} hilos", "ko": "시간 {0}, {1} 스레드", "it": "Durata {0}, {1} thread"},
    "Avg usage {0}%, peak {1}%": {"zh": "平均占用 {0}%，峰值 {1}%", "ja": "平均 {0}%、ピーク {1}%", "fr": "Usage moyen {0}%, pic {1}%", "ru": "Среднее {0}%, пик {1}%", "de": "Ø {0}%, Spitze {1}%", "pt": "Média {0}%, pico {1}%", "es": "Media {0}%, pico {1}%", "ko": "평균 {0}%, 피크 {1}%", "it": "Media {0}%, picco {1}%"},
    "Frequency {0} → {1} MHz": {"zh": "频率：{0} → {1} MHz", "ja": "周波数：{0} → {1} MHz", "fr": "Fréquence : {0} → {1} MHz", "ru": "Частота: {0} → {1} МГц", "de": "Frequenz: {0} → {1} MHz", "pt": "Frequência: {0} → {1} MHz", "es": "Frecuencia: {0} → {1} MHz", "ko": "주파수: {0} → {1} MHz", "it": "Frequenza: {0} → {1} MHz"},
    "Frequency variation {0} MHz": {"zh": "频率波动 {0} MHz", "ja": "周波数変動 {0} MHz", "fr": "Variation de fréquence {0} MHz", "ru": "Изменение частоты {0} МГц", "de": "Frequenzänderung {0} MHz", "pt": "Variação de frequência {0} MHz", "es": "Variación de frecuencia {0} MHz", "ko": "주파수 변동 {0} MHz", "it": "Variazione frequenza {0} MHz"},
    "Stress interrupted": {"zh": "压力测试被中断", "ja": "負荷テストが中断されました", "fr": "Stress interrompu", "ru": "Нагрузка прервана", "de": "Belastung unterbrochen", "pt": "Estresse interrompido", "es": "Estrés interrumpido", "ko": "부하 테스트 중단됨", "it": "Stress interrotto"},
    "Frequency dropped {0} MHz under load, possible throttling": {"zh": "压力测试期间频率下降 {0} MHz，可能出现过热降频", "ja": "負荷中に周波数が {0} MHz 低下、スロットリングの可能性", "fr": "Fréquence en baisse de {0} MHz, possible throttling", "ru": "Частота упала на {0} МГц, возможен троттлинг", "de": "Frequenz um {0} MHz gefallen, mögliches Throttling", "pt": "Frequência caiu {0} MHz, possível throttling", "es": "Frecuencia cayó {0} MHz, posible throttling", "ko": "부하 중 주파수 {0} MHz 하락, 스로틀링 가능성", "it": "Frequenza scesa di {0} MHz, possibile throttling"},
    "Stable under full load, peak {0}%, no throttling": {"zh": "满载稳定，峰值占用 {0}%，无异常降频", "ja": "全負荷で安定、ピーク {0}%、スロットリングなし", "fr": "Stable à pleine charge, pic {0}%, pas de throttling", "ru": "Стабильно, пик {0}%, без троттлинга", "de": "Stabil unter Volllast, Spitze {0}%, kein Throttling", "pt": "Estável, pico {0}%, sem throttling", "es": "Estable, pico {0}%, sin throttling", "ko": "풀부하 안정, 피크 {0}%, 스로틀링 없음", "it": "Stabile a pieno carico, picco {0}%, nessun throttling"},
    "Not read yet": {"zh": "尚未读取", "ja": "まだ読み取っていません", "fr": "Pas encore lu", "ru": "Ещё не считано", "de": "Noch nicht gelesen", "pt": "Ainda não lido", "es": "Aún no leído", "ko": "아직 읽지 않음", "it": "Non ancora letto"},
    "Reading battery info…": {"zh": "正在读取电池信息…", "ja": "バッテリー情報を読み取り中…", "fr": "Lecture de la batterie…", "ru": "Чтение батареи…", "de": "Akku wird gelesen…", "pt": "Lendo bateria…", "es": "Leyendo batería…", "ko": "배터리 정보 읽는 중…", "it": "Lettura batteria…"},
    "Power": {"zh": "电源状态", "ja": "電源状態", "fr": "Alimentation", "ru": "Питание", "de": "Strom", "pt": "Energia", "es": "Alimentación", "ko": "전원 상태", "it": "Alimentazione"},
    "Charge {0}%, cycles {1}": {"zh": "电量 {0}%，循环 {1} 次", "ja": "充電 {0}%、サイクル {1}", "fr": "Charge {0}%, cycles {1}", "ru": "Заряд {0}%, циклов {1}", "de": "Ladung {0}%, Zyklen {1}", "pt": "Carga {0}%, ciclos {1}", "es": "Carga {0}%, ciclos {1}", "ko": "충전 {0}%, 사이클 {1}", "it": "Carica {0}%, cicli {1}"},
    "{0} partitions": {"zh": "{0} 个分区", "ja": "{0} パーティション", "fr": "{0} partitions", "ru": "{0} разделов", "de": "{0} Partitionen", "pt": "{0} partições", "es": "{0} particiones", "ko": "{0}개 파티션", "it": "{0} partizioni"},
    "Benchmarking…": {"zh": "正在测速…", "ja": "ベンチマーク中…", "fr": "Test en cours…", "ru": "Тест…", "de": "Benchmark…", "pt": "Testando…", "es": "Probando…", "ko": "벤치마크 중…", "it": "Benchmark…"},
    "Benchmark failed": {"zh": "测速失败", "ja": "ベンチマーク失敗", "fr": "Échec du test", "ru": "Ошибка теста", "de": "Benchmark fehlgeschlagen", "pt": "Falha no benchmark", "es": "Error de prueba", "ko": "벤치마크 실패", "it": "Benchmark fallito"},
    "Write {0} MB/s, read {1} MB/s": {"zh": "写 {0} MB/s，读 {1} MB/s", "ja": "書き込み {0} MB/s、読み込み {1} MB/s", "fr": "Écriture {0} Mo/s, lecture {1} Mo/s", "ru": "Запись {0} МБ/с, чтение {1} МБ/с", "de": "Schreiben {0} MB/s, Lesen {1} MB/s", "pt": "Escrita {0} MB/s, leitura {1} MB/s", "es": "Escritura {0} MB/s, lectura {1} MB/s", "ko": "쓰기 {0} MB/s, 읽기 {1} MB/s", "it": "Scrittura {0} MB/s, lettura {1} MB/s"},
    "Total {0}": {"zh": "总量 {0}", "ja": "合計 {0}", "fr": "Total {0}", "ru": "Всего {0}", "de": "Gesamt {0}", "pt": "Total {0}", "es": "Total {0}", "ko": "총 {0}", "it": "Totale {0}"},
    "Running memory self-test…": {"zh": "正在做内存读写自检…", "ja": "メモリ自己テスト実行中…", "fr": "Autotest mémoire…", "ru": "Самотест памяти…", "de": "Speicher-Selbsttest läuft…", "pt": "Autoteste de memória…", "es": "Autoprueba de memoria…", "ko": "메모리 자체 테스트 중…", "it": "Autotest memoria…"},
    "{0} interfaces": {"zh": "{0} 个接口", "ja": "{0} インターフェース", "fr": "{0} interfaces", "ru": "{0} интерфейсов", "de": "{0} Schnittstellen", "pt": "{0} interfaces", "es": "{0} interfaces", "ko": "{0}개 인터페이스", "it": "{0} interfacce"},
    "Pinging {0}…": {"zh": "正在 ping {0} …", "ja": "{0} に ping 実行中…", "fr": "Ping de {0}…", "ru": "Пинг {0}…", "de": "Pinge {0}…", "pt": "Pingando {0}…", "es": "Haciendo ping a {0}…", "ko": "{0} 핑 중…", "it": "Ping a {0}…"},
    "Ping failed": {"zh": "Ping 失败", "ja": "Ping 失敗", "fr": "Échec du ping", "ru": "Пинг не удался", "de": "Ping fehlgeschlagen", "pt": "Falha no ping", "es": "Error de ping", "ko": "핑 실패", "it": "Ping fallito"},
    "Cannot reach {0}": {"zh": "无法连接 {0}", "ja": "{0} に接続できません", "fr": "Impossible d'atteindre {0}", "ru": "Недоступен {0}", "de": "{0} nicht erreichbar", "pt": "Não foi possível alcançar {0}", "es": "No se puede alcanzar {0}", "ko": "{0}에 연결할 수 없음", "it": "Impossibile raggiungere {0}"},
    "sent": {"zh": "发送", "ja": "送信", "fr": "envoyés", "ru": "отправлено", "de": "gesendet", "pt": "enviados", "es": "enviados", "ko": "전송", "it": "inviati"},
    "received": {"zh": "接收", "ja": "受信", "fr": "reçus", "ru": "получено", "de": "empfangen", "pt": "recebidos", "es": "recibidos", "ko": "수신", "it": "ricevuti"},
    "loss": {"zh": "丢包", "ja": "損失", "fr": "perte", "ru": "потери", "de": "Verlust", "pt": "perda", "es": "pérdida", "ko": "손실", "it": "perdita"},
    "min": {"zh": "最小", "ja": "最小", "fr": "min", "ru": "мин", "de": "min", "pt": "mín", "es": "mín", "ko": "최소", "it": "min"},
    "avg": {"zh": "平均", "ja": "平均", "fr": "moy", "ru": "сред", "de": "Ø", "pt": "méd", "es": "med", "ko": "평균", "it": "media"},
    "max": {"zh": "最大", "ja": "最大", "fr": "max", "ru": "макс", "de": "max", "pt": "máx", "es": "máx", "ko": "최대", "it": "max"},
    "Loss {0}%": {"zh": "丢包 {0}%", "ja": "損失 {0}%", "fr": "Perte {0}%", "ru": "Потери {0}%", "de": "Verlust {0}%", "pt": "Perda {0}%", "es": "Pérdida {0}%", "ko": "손실 {0}%", "it": "Perdita {0}%"},
    "Avg {0} ms, no loss": {"zh": "平均 {0} ms，无丢包", "ja": "平均 {0} ms、損失なし", "fr": "Moy {0} ms, sans perte", "ru": "Среднее {0} мс, без потерь", "de": "Ø {0} ms, kein Verlust", "pt": "Média {0} ms, sem perda", "es": "Media {0} ms, sin pérdida", "ko": "평균 {0} ms, 손실 없음", "it": "Media {0} ms, nessuna perdita"},
    "No dead pixel found": {"zh": "六色纯色观察未发现坏点", "ja": "デッドピクセルは見つかりませんでした", "fr": "Aucun pixel mort détecté", "ru": "Битых пикселей не найдено", "de": "Keine Pixelfehler gefunden", "pt": "Nenhum pixel morto encontrado", "es": "No se encontraron píxeles muertos", "ko": "불량 화소를 찾지 못함", "it": "Nessun pixel morto trovato"},
    "Dead pixel found, recommend replacement": {"zh": "发现坏点，建议更换屏幕或联系售后", "ja": "デッドピクセルを検出、交換を推奨", "fr": "Pixel mort détecté, remplacement recommandé", "ru": "Найден битый пиксель, рекомендуется замена", "de": "Pixelfehler gefunden, Austausch empfohlen", "pt": "Pixel morto, substituição recomendada", "es": "Píxel muerto, se recomienda reemplazo", "ko": "불량 화소 발견, 교체 권장", "it": "Pixel morto, sostituzione consigliata"},
}

_current = "zh"


class _Signals(QObject):
    changed = Signal(str)


_signals = _Signals()


def tr(text: str, *args: object) -> str:
    """Translate ``text`` into the current language, then apply ``str.format``."""
    table = TRANSLATIONS.get(text, {})
    result = table.get(_current, text)
    if args:
        result = result.format(*args)
    return result


def get_language() -> str:
    return _current


def set_language(code: str) -> None:
    global _current
    _current = code
    _signals.changed.emit(code)


def available_languages() -> list[tuple[str, str]]:
    return list(LANGUAGES)


def language_changed_signal() -> SignalInstance:
    return _signals.changed
