class_name Room
extends Node2D
## 맵(방) 하나의 공통 스크립트.
## - 방 밝기(색감) 적용
## - 카메라가 방 밖(검은 화면)을 비추지 않도록 범위 제한
## - 다른 방에서 넘어왔으면 도착 지점(Spawns 아래의 SpawnPoint)에 주인공 세우기
## - 처음 들어왔을 때 한 번만 나오는 대화

const HUD_SCENE := preload("res://scenes/ui/hud.tscn")

## 방의 크기 (픽셀). 32의 배수로 맞추면 타일과 딱 맞는다.
@export var room_size := Vector2i(960, 544)
@export var camera: Camera2D
## 방 전체의 밝기와 색감. 흰색이면 그대로, 어두운 색일수록 방이 어두워진다.
## 맵마다 다르게 정해서 분위기를 바꿀 수 있다.
@export var ambient_color := Color(0.82, 0.8, 0.9)
## 체력 하트를 보여줄지
@export var show_hud := true
## 방에 처음 들어왔을 때 한 번만 보여줄 대화 (비워두면 없음)
@export_file("*.txt") var intro_dialogue := ""
@export var intro_block := ""


func _ready() -> void:
	var ambient := CanvasModulate.new()
	ambient.color = ambient_color
	add_child(ambient)
	if show_hud:
		add_child(HUD_SCENE.instantiate())
	if camera:
		camera.limit_left = 0
		camera.limit_top = 0
		camera.limit_right = room_size.x
		camera.limit_bottom = room_size.y
	_place_player()
	_play_intro_once()


func _place_player() -> void:
	if Transition.spawn_name.is_empty():
		return
	var spawn := get_node_or_null("Spawns/" + Transition.spawn_name) as SpawnPoint
	Transition.spawn_name = ""
	var player := get_tree().get_first_node_in_group("player") as Player
	if spawn and player:
		player.place_at(spawn.global_position, spawn.facing)


func _play_intro_once() -> void:
	if intro_dialogue.is_empty():
		return
	var seen_key := "intro_seen:" + scene_file_path
	if GameState.get_var(seen_key) > 0:
		return
	GameState.set_var(seen_key, 1)
	Dialogue.start.call_deferred(intro_dialogue, intro_block)
