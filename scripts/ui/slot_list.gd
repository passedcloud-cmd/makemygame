class_name SlotList
extends PanelContainer
## 세이브 슬롯 고르는 창. open("save") 또는 open("load")로 연다.
## 불러오기 모드에서는 빈 슬롯을 고를 수 없다.

signal chosen(slot: int)
signal cancelled

var _title: Label
var _menu: MenuList


func _ready() -> void:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.067, 0.059, 0.094, 0.95)
	style.border_color = Color(0.72, 0.69, 0.8)
	style.set_border_width_all(2)
	style.set_corner_radius_all(6)
	style.set_content_margin_all(12)
	add_theme_stylebox_override("panel", style)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	add_child(box)
	_title = Label.new()
	box.add_child(_title)
	_menu = MenuList.new()
	_menu.add_theme_constant_override("separation", 6)
	box.add_child(_menu)
	_menu.chosen.connect(func(index: int) -> void: chosen.emit(index + 1))
	_menu.cancelled.connect(func() -> void: cancelled.emit())
	visible = false


func open(mode: String) -> void:
	_title.text = "어디에 저장할까?" if mode == "save" else "어떤 기록을 불러올까?"
	var items: Array = []
	for slot in range(1, SaveManager.SLOT_COUNT + 1):
		var empty := SaveManager.read_slot(slot).is_empty()
		items.append({"text": SaveManager.describe(slot), "enabled": mode == "save" or not empty})
	_menu.set_items(items)
	_menu.active = true
	visible = true


func close() -> void:
	_menu.active = false
	visible = false
