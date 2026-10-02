extends CanvasLayer
## 게임 중 Esc를 누르면 나오는 일시정지 메뉴.
## (자동 로드에 "PauseMenu"로 등록돼 있다.)

const TITLE_SCENE := "res://scenes/ui/title.tscn"
const ITEMS := ["계속하기", "저장하기", "불러오기", "타이틀로 돌아가기"]

var _root: Control
var _menu: MenuList
var _slots: SlotList
var _toast: Label
var _slot_mode := ""


func _ready() -> void:
	layer = 15
	# 게임이 멈춰 있는 동안에도 이 메뉴는 움직여야 한다.
	process_mode = Node.PROCESS_MODE_ALWAYS

	_root = Control.new()
	_root.size = Vector2(640, 360)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	var dim := ColorRect.new()
	dim.color = Color(0.02, 0.016, 0.03, 0.7)
	dim.size = Vector2(640, 360)
	_root.add_child(dim)

	var title := Label.new()
	title.text = "- 일시정지 -"
	title.position = Vector2(48, 60)
	_root.add_child(title)

	_menu = MenuList.new()
	_menu.position = Vector2(48, 92)
	_menu.add_theme_constant_override("separation", 8)
	_root.add_child(_menu)
	_menu.chosen.connect(_on_menu_chosen)
	_menu.cancelled.connect(close)

	_slots = SlotList.new()
	_slots.position = Vector2(200, 92)
	_root.add_child(_slots)
	_slots.chosen.connect(_on_slot_chosen)
	_slots.cancelled.connect(_close_slots)

	_toast = Label.new()
	_toast.position = Vector2(48, 300)
	_root.add_child(_toast)

	_root.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if _root.visible or not event.is_action_pressed("menu"):
		return
	# 방 안에서, 대화나 화면 전환 중이 아닐 때만 열 수 있다.
	if not get_tree().current_scene is Room or Dialogue.active or Transition.busy:
		return
	get_viewport().set_input_as_handled()
	open()


func open() -> void:
	get_tree().paused = true
	_menu.set_items(ITEMS)
	_menu.active = true
	_slots.close()
	_toast.text = ""
	_root.visible = true


func close() -> void:
	_root.visible = false
	_slots.close()
	get_tree().paused = false


func _on_menu_chosen(index: int) -> void:
	match index:
		0:
			close()
		1:
			_open_slots("save")
		2:
			_open_slots("load")
		3:
			close()
			Transition.change_room(TITLE_SCENE, "")


func _open_slots(mode: String) -> void:
	_slot_mode = mode
	_menu.active = false
	_toast.text = ""
	_slots.open(mode)


func _close_slots() -> void:
	_slots.close()
	_menu.active = true


func _on_slot_chosen(slot: int) -> void:
	if _slot_mode == "save":
		var ok := SaveManager.save_game(slot)
		_toast.text = "슬롯 %d에 저장했어." % slot if ok else "저장하지 못했어..."
		_slots.open("save")   # 목록을 새로 고쳐서 방금 저장한 내용을 보여준다
	else:
		_root.visible = false
		_slots.close()
		SaveManager.load_game(slot)
