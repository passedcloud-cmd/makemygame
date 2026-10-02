extends Control
## 대화 연출 담당: 스탠딩 일러, CG, 회상 효과, 암전, 화면 흔들기, 컷인.
## 대본에서 @로 시작하는 줄이 여기로 온다. 명령어 목록은 dialogue/README.md 참고.

## 스탠딩 일러를 화면에 보여줄 높이 (게임 화면 640x360 기준).
## 그림 원본 크기와 상관없이 이 높이에 맞춰 늘리거나 줄인다.
const STANDING_HEIGHT := 240.0
## 스탠딩 일러의 발밑 위치 (대화창 뒤로 살짝 숨는다)
const STANDING_BOTTOM := 352.0
## 위치 이름 -> 화면 가로 위치 (가운데 기준)
const POSITIONS := {"left": 150.0, "center": 320.0, "right": 490.0}
## 말하지 않는 캐릭터는 이만큼 어둡게
const DIM_COLOR := Color(0.55, 0.55, 0.62)

var _standing := {}   # 캐릭터 id -> TextureRect
var _shake_time := 0.0
var _shake_total := 0.0
var _shake_strength := 0.0

@onready var _standing_layer: Control = $Standing
@onready var _cg: TextureRect = $CG
@onready var _flashback: ColorRect = $Flashback
@onready var _fade: ColorRect = $Fade
@onready var _cutin: Control = %Cutin
@onready var _cutin_band: Control = %CutinBand
@onready var _cutin_bg: ColorRect = %CutinBg
@onready var _cutin_face: TextureRect = %CutinFace


func _ready() -> void:
	clear()


## 연출 명령 하나를 실행한다. 시간이 걸리는 연출(암전, 컷인 등)은 끝날 때까지 기다린다.
func run(command: String, args: Array) -> void:
	match command:
		"show":
			_show(_arg(args, 0, ""), _arg(args, 1, ""), _arg(args, 2, ""))
		"hide":
			_hide(_arg(args, 0, "all"))
		"shake":
			_shake_strength = float(_arg(args, 0, "4"))
			_shake_total = float(_arg(args, 1, "0.4"))
			_shake_time = _shake_total
		"flashback":
			await _tween(_flashback.material, "shader_parameter/amount",
				1.0 if _arg(args, 0, "on") == "on" else 0.0, 0.6)
		"cg":
			await _show_cg(_arg(args, 0, "off"))
		"fade":
			var target := 1.0 if _arg(args, 0, "out") == "out" else 0.0
			await _tween(_fade, "color:a", target, float(_arg(args, 1, "0.5")))
		"wait":
			await get_tree().create_timer(float(_arg(args, 0, "0.5"))).timeout
		"cutin":
			await _play_cutin(_arg(args, 0, ""), _arg(args, 1, ""))
		_:
			push_error("모르는 연출 명령: @%s" % command)


## 누가 말하는지 알려주면, 그 캐릭터만 밝게 하고 나머지는 어둡게 한다.
## 말하는 캐릭터가 무대에 서 있으면 true를 돌려준다.
func on_speaker(id: String) -> bool:
	for key in _standing:
		var dim: bool = not id.is_empty() and key != id
		_standing[key].modulate = DIM_COLOR if dim else Color.WHITE
	return _standing.has(id)


## 표정이 바뀌면 무대 위 스탠딩 일러도 같이 바꾼다.
func set_expression(id: String, expression: String) -> void:
	if _standing.has(id):
		var tex := Characters.standing(id, expression)
		if tex:
			_standing[id].texture = tex


## 대화가 끝나면 무대를 깨끗이 치운다.
func clear() -> void:
	for key in _standing:
		_standing[key].queue_free()
	_standing.clear()
	_cg.modulate.a = 0.0
	_flashback.material.set("shader_parameter/amount", 0.0)
	_fade.color.a = 0.0
	_cutin.visible = false
	_shake_time = 0.0
	position = Vector2.ZERO
	var camera := get_viewport().get_camera_2d()
	if camera:
		camera.offset = Vector2.ZERO


func _process(delta: float) -> void:
	if _shake_time <= 0.0:
		return
	_shake_time -= delta
	var power := _shake_strength * maxf(_shake_time, 0.0) / _shake_total
	var offset := Vector2(randf_range(-1, 1), randf_range(-1, 1)) * power
	offset = offset.round()
	position = offset
	var camera := get_viewport().get_camera_2d()
	if camera:
		camera.offset = offset


func _show(id: String, where: String, expression: String) -> void:
	var tex := Characters.standing(id, expression)
	if tex == null:
		push_error("스탠딩 일러가 없음: %s" % id)
		return
	if where.is_empty() or not POSITIONS.has(where):
		where = "center"
	var rect: TextureRect = _standing.get(id)
	var is_new := rect == null
	if is_new:
		rect = TextureRect.new()
		rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		rect.stretch_mode = TextureRect.STRETCH_SCALE
		_standing_layer.add_child(rect)
		_standing[id] = rect
	rect.texture = tex
	var width := tex.get_width() * STANDING_HEIGHT / tex.get_height()
	rect.size = Vector2(width, STANDING_HEIGHT)
	var target := Vector2(POSITIONS[where] - width / 2.0, STANDING_BOTTOM - STANDING_HEIGHT)
	if is_new:
		# 아래에서 살짝 올라오면서 나타나기
		rect.position = target + Vector2(0, 10)
		rect.modulate.a = 0.0
		var tween := create_tween().set_parallel()
		tween.tween_property(rect, "position", target, 0.2)
		tween.tween_property(rect, "modulate:a", 1.0, 0.2)
	else:
		create_tween().tween_property(rect, "position", target, 0.25)


func _hide(id: String) -> void:
	var ids: Array = _standing.keys() if id == "all" else [id]
	for key in ids:
		if not _standing.has(key):
			continue
		var rect: TextureRect = _standing[key]
		_standing.erase(key)
		var tween := create_tween()
		tween.tween_property(rect, "modulate:a", 0.0, 0.2)
		tween.tween_callback(rect.queue_free)


func _show_cg(cg_name: String) -> void:
	if cg_name == "off":
		await _tween(_cg, "modulate:a", 0.0, 0.4)
		return
	var path := "res://art/cg/%s.png" % cg_name
	if not ResourceLoader.exists(path):
		push_error("CG 그림이 없음: %s" % path)
		return
	_cg.texture = load(path)
	await _tween(_cg, "modulate:a", 1.0, 0.4)


func _play_cutin(id: String, expression: String) -> void:
	_cutin_face.texture = Characters.portrait(id, expression)
	_cutin_bg.color = Characters.color(id).darkened(0.45)
	_cutin.visible = true
	var start_x := -_cutin_band.size.x
	var center_x := (640.0 - _cutin_band.size.x) / 2.0
	_cutin_band.position.x = start_x
	var tween := create_tween()
	tween.tween_property(_cutin_band, "position:x", center_x, 0.18) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_interval(0.8)
	tween.tween_property(_cutin_band, "position:x", 640.0, 0.18) \
		.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	await tween.finished
	_cutin.visible = false


func _tween(target: Object, property: String, value: Variant, time: float) -> void:
	if time <= 0.0:
		target.set_indexed(property, value)
		return
	var tween := create_tween()
	tween.tween_property(target, property, value, time)
	await tween.finished


func _arg(args: Array, index: int, default: String) -> String:
	return args[index] if index < args.size() else default
