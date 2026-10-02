extends CanvasLayer
## 대화창. 게임 어디서든 Dialogue.start("res://dialogue/파일.txt", "블록 이름")으로 연다.
## (프로젝트 설정의 자동 로드(Autoload)에 "Dialogue"라는 이름으로 등록돼 있다.)
##
## Z(확인) 키: 글자가 나오는 중이면 한 번에 다 보여주고, 다 나왔으면 다음 줄로.
## 선택지가 나오면 위/아래 키로 고르고 Z로 결정.

signal finished

## 1초에 나오는 글자 수
@export var chars_per_second := 35.0

## 대화 중이면 true. 주인공은 이게 true인 동안 움직이지 않는다.
var active := false

var _cache := {}          # 파일 경로 -> 읽어 둔 대본
var _blocks := {}         # 지금 대본의 블록들
var _cmds: Array = []     # 지금 실행 중인 블록의 명령들
var _index := 0
var _typing := false
var _type_time := 0.0
var _choices: Array = []
var _selected := 0
var _blink := 0.0
var _busy := false        # 시간이 걸리는 연출(암전, 컷인 등)을 기다리는 중

@onready var _root: Control = $Root
@onready var _stage: Control = %Stage
@onready var _text_panel: PanelContainer = %TextPanel
@onready var _name_tag: PanelContainer = %NameTag
@onready var _name_label: Label = %NameLabel
@onready var _portrait_frame: Control = %PortraitFrame
@onready var _portrait: TextureRect = %Portrait
@onready var _text: RichTextLabel = %Text
@onready var _next_mark: Label = %NextMark
@onready var _choice_panel: PanelContainer = %ChoicePanel
@onready var _choice_list: VBoxContainer = %ChoiceList


func _ready() -> void:
	_root.visible = false


## 대화를 시작한다. path = 대본 파일, block = 시작할 블록 이름 (== 뒤에 쓴 이름)
func start(path: String, block: String) -> void:
	if not _cache.has(path):
		_cache[path] = DialogueParser.parse_file(path)
	_blocks = _cache[path]
	if not _goto(block):
		return
	active = true
	_root.visible = true
	# 첫 대사가 나올 때까지는 대화창을 숨겨 둔다 (연출부터 시작할 수 있게)
	_text_panel.visible = false
	_name_tag.visible = false
	_next_mark.visible = false
	_next()


func _process(delta: float) -> void:
	if not active or _busy:
		return
	if _typing:
		_type_time += delta
		_text.visible_characters = int(_type_time * chars_per_second)
		if _text.visible_characters >= _text.get_total_character_count():
			_finish_typing()
	elif not _choices.is_empty():
		if Input.is_action_just_pressed("move_up"):
			_select(_selected - 1)
		elif Input.is_action_just_pressed("move_down"):
			_select(_selected + 1)
	else:
		# 다음으로 넘어갈 수 있다는 ▼ 표시를 깜빡이게
		_blink += delta
		_next_mark.visible = fmod(_blink, 0.8) < 0.5


func _unhandled_input(event: InputEvent) -> void:
	if not active or not event.is_action_pressed("confirm"):
		return
	get_viewport().set_input_as_handled()
	if _busy:
		return
	if _typing:
		_finish_typing()
	elif not _choices.is_empty():
		var target: String = _choices[_selected].target
		_hide_choices()
		if _goto(target):
			_next()
	else:
		_next()


## 다음 명령을 실행한다. 화면에 뭔가 보여주는 명령(대사, 선택지)이 나올 때까지 계속 진행.
func _next() -> void:
	while true:
		if _index >= _cmds.size():
			_close()
			return
		var cmd: Dictionary = _cmds[_index]
		_index += 1
		match cmd.type:
			"say":
				_show_line(cmd)
				return
			"choices":
				_show_choices(cmd.options)
				return
			"jump":
				if not _goto(cmd.target):
					return
			"set":
				_apply_set(cmd)
			"if":
				if _check(cmd) and not _goto(cmd.target):
					return
			"stage":
				_busy = true
				_next_mark.visible = false
				await _stage.run(cmd.command, cmd.args)
				_busy = false
			"end":
				_close()
				return


func _goto(block: String) -> bool:
	if not _blocks.has(block):
		push_error("대본에 '%s' 블록이 없음" % block)
		_close()
		return false
	_cmds = _blocks[block]
	_index = 0
	return true


func _show_line(cmd: Dictionary) -> void:
	var speaker: String = cmd.speaker
	var is_narration := speaker.is_empty()
	_text_panel.visible = true
	if not cmd.expression.is_empty():
		_stage.set_expression(speaker, cmd.expression)
	var on_stage: bool = _stage.on_speaker(speaker)
	_name_tag.visible = not is_narration
	if not is_narration:
		_name_label.text = Characters.display_name(speaker)
		var style := _name_tag.get_theme_stylebox("panel").duplicate() as StyleBoxFlat
		style.bg_color = Characters.color(speaker)
		_name_tag.add_theme_stylebox_override("panel", style)
	# 스탠딩 일러로 서 있는 캐릭터는 대화창 얼굴을 따로 보여주지 않는다.
	var face: Texture2D = null
	if not is_narration and not on_stage:
		face = Characters.portrait(speaker, cmd.expression)
	_portrait.texture = face
	_portrait_frame.visible = face != null

	_text.text = cmd.text
	_text.visible_characters = 0
	_type_time = 0.0
	_typing = true
	_next_mark.visible = false


func _finish_typing() -> void:
	_typing = false
	_text.visible_characters = -1
	_blink = 0.0


func _show_choices(options: Array) -> void:
	_choices = options
	for child in _choice_list.get_children():
		child.queue_free()
	for option in options:
		var label := Label.new()
		label.add_theme_color_override("font_color", Color("fffdf6"))
		_choice_list.add_child(label)
	_select(0)
	_choice_panel.visible = true
	_next_mark.visible = false


func _select(index: int) -> void:
	_selected = wrapi(index, 0, _choices.size())
	for i in _choices.size():
		var label: Label = _choice_list.get_child(i)
		var chosen := i == _selected
		label.text = ("▶ " if chosen else "   ") + _choices[i].text
		label.modulate = Color.WHITE if chosen else Color(1, 1, 1, 0.6)


func _hide_choices() -> void:
	_choices = []
	_choice_panel.visible = false


func _apply_set(cmd: Dictionary) -> void:
	var value := GameState.get_var(cmd.name)
	match cmd.op:
		"=": value = cmd.value
		"+": value += cmd.value
		"-": value -= cmd.value
	GameState.set_var(cmd.name, value)


func _check(cmd: Dictionary) -> bool:
	var value := GameState.get_var(cmd.name)
	match cmd.op:
		">=": return value >= cmd.value
		"<=": return value <= cmd.value
		">": return value > cmd.value
		"<": return value < cmd.value
		"==": return value == cmd.value
		"!=": return value != cmd.value
	return false


func _close() -> void:
	_hide_choices()
	_stage.clear()
	_busy = false
	_typing = false
	_root.visible = false
	if active:
		active = false
		finished.emit()
