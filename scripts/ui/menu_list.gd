class_name MenuList
extends VBoxContainer
## 위/아래 키로 고르고 Z로 결정, X/Esc로 취소하는 세로 메뉴.
## 타이틀, 일시정지 메뉴, 세이브 슬롯 목록에서 같이 쓴다.

signal chosen(index: int)
signal cancelled

const TEXT_COLOR := Color(0.95, 0.93, 0.89)
const CURSOR := "▶ "

## false면 키 입력을 받지 않는다 (다른 창이 위에 떠 있을 때 등)
var active := true
var selected := 0
var _items: Array[Dictionary] = []


## 메뉴 항목을 정한다. 문자열 배열이나 {"text": ..., "enabled": false} 배열.
func set_items(items: Array, keep_selection := false) -> void:
	_items.clear()
	for child in get_children():
		remove_child(child)
		child.queue_free()
	for item in items:
		var entry: Dictionary = item if item is Dictionary else {"text": str(item)}
		_items.append({"text": entry.get("text", ""), "enabled": entry.get("enabled", true)})
		var label := Label.new()
		add_child(label)
	if not keep_selection or selected >= _items.size() or not _items[selected].enabled:
		selected = -1
		_move(1)
	_refresh()


func _unhandled_input(event: InputEvent) -> void:
	if not active or not is_visible_in_tree() or _items.is_empty():
		return
	if event.is_action_pressed("move_up"):
		_move(-1)
	elif event.is_action_pressed("move_down"):
		_move(1)
	elif event.is_action_pressed("confirm"):
		if selected >= 0 and _items[selected].enabled:
			get_viewport().set_input_as_handled()
			chosen.emit(selected)
			return
	elif event.is_action_pressed("cancel"):
		get_viewport().set_input_as_handled()
		cancelled.emit()
		return
	else:
		return
	get_viewport().set_input_as_handled()


## 다음(또는 이전) 고를 수 있는 항목으로 커서를 옮긴다. 비활성 항목은 건너뛴다.
func _move(direction: int) -> void:
	for step in range(1, _items.size() + 1):
		var index := wrapi(selected + direction * step, 0, _items.size())
		if _items[index].enabled:
			selected = index
			break
	_refresh()


func _refresh() -> void:
	for i in _items.size():
		var label: Label = get_child(i)
		var is_selected := i == selected
		label.text = (CURSOR if is_selected else "   ") + _items[i].text
		var color := TEXT_COLOR
		if not _items[i].enabled:
			color.a = 0.3
		elif not is_selected:
			color.a = 0.65
		label.add_theme_color_override("font_color", color)
