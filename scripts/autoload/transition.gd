extends CanvasLayer
## 방 이동할 때 화면을 어둡게 했다가 밝게 하는 장면 전환.
## 어디서든 Transition.change_room("res://scenes/maps/방.tscn", "도착 지점 이름")으로 쓴다.

## 화면이 어두워지는 데 걸리는 시간 (초)
const FADE_TIME := 0.3

## 전환 중이면 true. 이동, 공격, 피격이 잠시 멈춘다.
var busy := false
## 새 방에서 주인공을 세울 지점 이름 (Room이 읽어 간다)
var spawn_name := ""

@onready var _fade: ColorRect = $Fade


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
