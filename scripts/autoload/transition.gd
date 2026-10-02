extends CanvasLayer
## 방 이동할 때 화면을 어둡게 했다가 밝게 하는 장면 전환.
## 어디서든 Transition.change_room("res://scenes/maps/방.tscn", "도착 지점 이름")으로 쓴다.

## 화면이 어두워지는 데 걸리는 시간 (초)
const FADE_TIME := 0.3

## 전환 중이면 true. 이동, 공격, 피격이 잠시 멈춘다.
var busy := false
## 새 방에서 주인공을 세울 지점 이름 (Room이 읽어 간다)
var spawn_name := ""
## 지점 이름 대신 정확한 위치로 세울 때 (세이브 불러오기). null이면 사용 안 함
var spawn_position: Variant = null
var spawn_facing := 0


func _ready() -> void:
	# 일시정지 중에도 화면 전환은 움직여야 한다.
	process_mode = Node.PROCESS_MODE_ALWAYS

@onready var _fade: ColorRect = $Fade


## 방을 옮기고 정확한 위치에 주인공을 세운다 (세이브 불러오기용).
func change_room_at(scene_path: String, pos: Vector2, facing: int) -> void:
	if busy:
		return
	spawn_position = pos
	spawn_facing = facing
	change_room(scene_path, "")


func change_room(scene_path: String, target_spawn: String) -> void:
	if busy:
		return
	busy = true
	spawn_name = target_spawn
	await _tween_alpha(1.0)
	get_tree().change_scene_to_file(scene_path)
	# 새 방이 준비될 때까지 두 프레임 기다린다.
	await get_tree().process_frame
	await get_tree().process_frame
	await _tween_alpha(0.0)
	busy = false


func _tween_alpha(target: float) -> void:
	var tween := create_tween()
	tween.tween_property(_fade, "color:a", target, FADE_TIME)
	await tween.finished
