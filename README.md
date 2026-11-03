# keybi

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

Легковесный биндер для Windows: управляй мышью и запускай команды
с клавиатуры, зажав правый Alt.

## Возможности

- 🖱️ Движение курсора стрелками
- 🖱️ ЛКМ / ПКМ на любые клавиши
- 🖲️ Скролл колесом
- ⌨️ Эмуляция нажатий клавиш
- 🚀 Запуск программ по бинду
- ⚙️ Конфиг в JSON — легко добавлять свои бинды
- 🪟 Не зависит от раскладки (VK-коды)

## Установка

```bash
git clone https://github.com/hereip/keybi.git
cd keybi
pip install -r requirements.txt
```

## Запуск

```bash
python keybi.py
```

Зажми **правый Alt** и жми бинды из `keybi.json`.

## Бинды по умолчанию

| Клавиша (с правым Alt) | Действие |
|---|---|
| ← ↑ → ↓ | Движение мыши |
| A | ЛКМ |
| D | ПКМ |
| W / S | Скролл вверх / вниз |

## Свой конфиг

Отредактируй `keybi.json`:

```json
{
  "modifier": "alt_gr",
  "repeat_delay": 0.3,
  "repeat_rate": 0.05,
  "binds": {
    "a": { "action": "mouse_click", "button": "left" },
    "d": { "action": "mouse_click", "button": "right" },
    "enter": { "action": "run", "command": "notepad.exe" }
  }
}
```

### Типы действий

| action | Параметры | Описание |
|---|---|---|
| `mouse_move` | `dx`, `dy`, `repeat` | Двинуть курсор |
| `mouse_click` | `button` (`left`/`right`/`middle`) | Клик |
| `mouse_scroll` | `dx`, `dy`, `repeat` | Скролл |
| `key` | `key` | Нажать клавишу |
| `run` | `command` | Запустить команду |

## Лицензия

MIT — см. [LICENSE](LICENSE).
