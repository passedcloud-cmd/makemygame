extends Control
## 타이틀 화면. 처음부터 / 이어하기 / 게임 종료.

## 새 게임을 시작하면 들어갈 첫 방
const FIRST_ROOM := "res://scenes/maps/test_room.tscn"

@onready var _menu: MenuList = %Menu
@onready var _slots: SlotList = %Slots


func _ready() -> void:
	_menu.set_items([
		{"text": "처음부터"},
		{"text": "이어하기", "enabled": SaveManager.has_any_save()},
		{"text": "게임 종료"},
	])
	# 저장된 게 있으면 커서를 "이어하기"에 둔다
	if SaveManager.has_any_save():
		_menu.selected = 1
		_menu.set_items([
			{"text": "처음부터"},
			{"text": "이어하기"},
			{"text": "게임 종료"},
		], true)
	_menu.chosen.connect(_on_menu_chosen)
	_slots.chosen.connect(_on_slot_chosen)
	_slots.cancelled.connect(_close_slots)


func _on_menu_chosen(index: int) -> void:
	match index:
		0:
			_menu.active = false
			GameState.reset()
			Transition.change_room(FIRST_ROOM, "")
		1:
			_menu.active = false
			_slots.open("load")
		2:
			get_tree().quit()


func _close_slots() -> void:
	_slots.close()
	_menu.active = true


func _on_slot_chosen(slot: int) -> void:
	_slots.close()
	SaveManager.load_game(slot)
